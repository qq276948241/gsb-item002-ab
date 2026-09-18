"""用已经读好的规则判断路径。"""

import re

from hulue.parse import load_rules


def _hit(rule, path: str, is_dir: bool) -> bool:
    del is_dir
    expr = rule.regex.pattern
    if rule.anchored:
        return re.search(r"(^|/)" + expr + r"($|/)", path) is not None
    return re.fullmatch(expr, path) is not None


def should_skip(path: str, is_dir: bool, rules_text: str) -> bool:
    path = path.replace("\\", "/").lstrip("/")
    while path.startswith("./"):
        path = path[2:]
    rules = load_rules(rules_text)
    ignored = False
    for rule in rules:
        if rule.negated:
            continue
        if _hit(rule, path, is_dir):
            ignored = True
    for rule in rules:
        if rule.negated and _hit(rule, path, is_dir):
            ignored = False
    return ignored
