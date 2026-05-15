from dataclasses import dataclass, field

from gatekeeper.parsers.model import Finding
from gatekeeper.policy.rule import Rule
from gatekeeper.policy.verdict import Verdict


@dataclass
class Decision:
    finding: Finding
    verdict: Verdict
    matched_rules: list[Rule] = field(default_factory=list)
