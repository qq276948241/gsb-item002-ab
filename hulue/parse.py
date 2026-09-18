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


def _compile_segment(segment: str) -> str:
    """编译不包含斜杠的一段：* 只匹配同层的一段名字。"""
    pieces = []
    index = 0
    while index < len(segment):
        char = segment[index]
        if char == "*":
            pieces.append("[^/]*")
            index += 1
            continue
        if char == "\\" and index + 1 < len(segment) and segment[index + 1] in "#!":
            pieces.append(re.escape(segment[index + 1]))
            index += 2
            continue
        pieces.append(re.escape(char))
        index += 1
    return "".join(pieces)


def _compile(body: str) -> re.Pattern:
    """编译规则正文，** 只有单独成段才能跨层，且允许中间零层。"""
    pieces = []
    segments = body.split("/")
    for index, segment in enumerate(segments):
        last = index == len(segments) - 1
        if segment == "**":
            if last:
                pieces.append(".*")
            else:
                pieces.append("(?:[^/]+/)*")
        else:
            pieces.append(_compile_segment(segment))
            if not last:
                pieces.append("/")
    return re.compile("".join(pieces))


def load_rules(text: str):
    rules = []
    if not text:
        return rules
    for raw in text.splitlines():
        if raw.strip() == "":
            continue
        line = raw.strip()
        if line.startswith("#"):
            continue
        negated = False
        if line.startswith("!"):
            negated = True
            line = line[1:]
        elif line.startswith(("\\#", "\\!")):
            line = line[1:]
        dir_only = False
        if line.endswith("/"):
            dir_only = True
            line = line[:-1]
        anchored = False
        if line.startswith("/"):
            anchored = True
            line = line[1:]
        elif "/" in line:
            anchored = True
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
