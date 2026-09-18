"""把纯文本规则读成内部结构。"""

from dataclasses import dataclass

GLOBSTAR = object()


@dataclass
class Rule:
    negated: bool
    dir_only: bool
    anchored: bool
    segments: list
    body: str


def load_rules(text: str):
    rules = []
    if not text:
        return rules
    for line in text.splitlines():
        line = line.strip()
        if line == "" or line.startswith("#"):
            continue
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

        parts = [part for part in line.split("/") if part != ""]
        segments = [GLOBSTAR if part == "**" else part for part in parts]
        body = "/".join("**" if part is GLOBSTAR else part for part in segments)
        if not segments:
            continue
        rules.append(
            Rule(
                negated=negated,
                dir_only=dir_only,
                anchored=anchored,
                segments=segments,
                body=body,
            )
        )
    return rules
