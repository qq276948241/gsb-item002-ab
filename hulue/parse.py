"""把纯文本规则读成内部结构。"""

import re
from dataclasses import dataclass


@dataclass
class Rule:
    negated: bool
    dir_only: bool
    anchored: bool
    regex: re.Pattern
    body: str


def _compile(body: str) -> re.Pattern:
    pieces = []
    index = 0
    while index < len(body):
        if body.startswith("**", index):
            pieces.append(".+")
            index += 2
            if index < len(body) and body[index] == "/":
                pieces.append("/")
                index += 1
            continue
        if body[index] == "*":
            pieces.append(".*")
            index += 1
            continue
        pieces.append(re.escape(body[index]))
        index += 1
    return re.compile("".join(pieces))


def load_rules(text: str):
    rules = []
    if not text:
        return rules
    for raw in text.splitlines():
        if raw.startswith("#") or raw.strip() == "":
            continue
        if raw.lstrip().startswith("#"):
            raw = raw.lstrip()[1:].strip()
            if raw == "":
                continue
        line = raw.strip()
        negated = False
        if line.startswith("!"):
            negated = True
            line = line[1:]
        dir_only = False
        if line.endswith("/"):
            dir_only = True
            line = line[:-1]
        anchored = False
        if line.startswith("/"):
            anchored = True
            line = line[1:]
        if line == "":
            continue
        rules.append(
            Rule(
                negated=negated,
                dir_only=dir_only,
                anchored=anchored,
                regex=_compile(line),
                body=line,
            )
        )
    return rules
