from enum import Enum


class Verdict(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    BLOCK = "BLOCK"


_PRECEDENCE = {Verdict.ALLOW: 0, Verdict.WARN: 1, Verdict.BLOCK: 2}


def worst(a: Verdict, b: Verdict) -> Verdict:
    return a if _PRECEDENCE[a] >= _PRECEDENCE[b] else b
