"""用已经读好的规则判断路径。"""

from hulue.parse import GLOBSTAR, load_rules


def _match_name(pattern: str, name: str) -> bool:
    """单层名字匹配：星号只代表本层里的一段，不会钻过斜杠。"""
    pi = ni = 0
    star = -1
    mark = 0

    def literal_at(index):
        if pattern[index] == "\\" and index + 1 < len(pattern):
            return pattern[index + 1], index + 2
        return pattern[index], index + 1

    while ni < len(name):
        if pi < len(pattern):
            token, next_pi = literal_at(pi)
            if token == "*" and next_pi == pi + 1:
                star = pi
                mark = ni
                pi = next_pi
            elif token == name[ni]:
                pi = next_pi
                ni += 1
            elif star >= 0:
                pi = literal_at(star)[1]
                mark += 1
                ni = mark
            else:
                return False
        elif star >= 0:
            pi = literal_at(star)[1]
            mark += 1
            ni = mark
        else:
            return False
    while pi < len(pattern) and pattern[pi] == "*":
        pi += 1
    return pi == len(pattern)


def _match_segments(pattern_segments, path_segments) -> bool:
    """整段路径匹配：双星号段代表零层或任意多层。"""
    matched = [True] + [False] * len(path_segments)
    for part in pattern_segments:
        if part == GLOBSTAR:
            for index in range(1, len(matched)):
                matched[index] = matched[index] or matched[index - 1]
            continue
        next_matched = [False]
        for index, name in enumerate(path_segments, start=1):
            next_matched.append(matched[index - 1] and _match_name(part, name))
        matched = next_matched
    return matched[-1]


def _match_prefix(pattern_segments, path_segments) -> bool:
    """规则是路径的前缀就算，双星号能吃掉零层或任意多层。"""
    matched = [True] + [False] * len(path_segments)
    for part in pattern_segments:
        if part == GLOBSTAR:
            started = False
            for index in range(len(matched)):
                if matched[index]:
                    started = True
                matched[index] = started
            continue
        next_matched = [False]
        for index, name in enumerate(path_segments, start=1):
            next_matched.append(matched[index - 1] and _match_name(part, name))
        matched = next_matched
    for matched_len, reachable in enumerate(matched):
        if not reachable:
            continue
        if matched_len < len(path_segments):
            return True
        if matched_len == len(path_segments):
            return None
    return False


def _hit(rule, segments, is_dir: bool) -> bool:
    # 一条单独的 ** 能对上任意路径。
    if rule.segments == [GLOBSTAR]:
        return True

    if rule.anchored:
        if rule.dir_only:
            prefix = _match_prefix(rule.segments, segments)
            return prefix is True or (prefix is None and is_dir)
        return _match_segments(rule.segments, segments)

    # 规则里没有斜杠：名字出现在任意一层都算。
    if len(rule.segments) == 1:
        part = rule.segments[0]
        if part == GLOBSTAR:
            return True
        if rule.dir_only:
            for index, name in enumerate(segments):
                if _match_name(part, name):
                    if index < len(segments) - 1:
                        return True
                    if is_dir:
                        return True
            return False
        return any(_match_name(part, name) for name in segments)

    # 不带前导斜杠、但规则自身含斜杠：从路径开头比。
    if rule.dir_only:
        prefix = _match_prefix(rule.segments, segments)
        return prefix is True or (prefix is None and is_dir)
    return _match_segments(rule.segments, segments)


def should_skip(path: str, is_dir: bool, rules_text: str) -> bool:
    path = path.lstrip("/")
    while path.startswith("./"):
        path = path[2:]
    segments = [part for part in path.split("/") if part != ""]
    rules = load_rules(rules_text)
    ignored = False
    for rule in rules:
        if _hit(rule, segments, is_dir):
            ignored = not rule.negated
    return ignored
