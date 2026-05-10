from collections.abc import Callable
from dataclasses import dataclass

from gatekeeper.parsers.model import Finding
from gatekeeper.policy.verdict import Verdict


@dataclass(frozen=True)
class Rule:
    id: str
    name: str
    description: str
    predicate: Callable[[Finding], bool]
    verdict: Verdict
