"""用已经读好的规则判断路径。"""

from hulue.parse import load_rules


def _matches_path(rule, path: str, is_dir: bool) -> bool:
    if rule.dir_only and not is_dir:
        return False
    if rule.anchored:
        return rule.regex.fullmatch(path) is not None
    return any(rule.regex.fullmatch(part) for part in path.split("/"))


def _hit(rule, path: str, is_dir: bool) -> bool:
    """路径本身或它的任一祖先目录命中规则，都算这条规则覆盖到它。"""
    if _matches_path(rule, path, is_dir):
        return True
    parts = path.split("/")
    for depth in range(1, len(parts)):
        ancestor = "/".join(parts[:depth])
        if _matches_path(rule, ancestor, True):
            return True
    return False


def should_skip(path: str, is_dir: bool, rules_text: str) -> bool:
    path = path.replace("\\", "/").lstrip("/")
    while path.startswith("./"):
        path = path[2:]
    if path.endswith("/"):
        path = path[:-1]
    rules = load_rules(rules_text)
    ignored = False
    for rule in rules:
        if _hit(rule, path, is_dir):
            ignored = not rule.negated
    return ignored
