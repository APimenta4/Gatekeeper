from functools import reduce

from gatekeeper.parsers.model import Finding
from gatekeeper.policy.decision import Decision
from gatekeeper.policy.rule import Rule
from gatekeeper.policy.verdict import Verdict, worst


class PolicyEngine:
    def __init__(self, rules: list[Rule]) -> None:
        self.rules = rules

    def evaluate(self, finding: Finding) -> Decision:
        matched = [r for r in self.rules if r.predicate(finding)]
        verdict = reduce(worst, (r.verdict for r in matched), Verdict.ALLOW)
        return Decision(finding=finding, verdict=verdict, matched_rules=matched)

    def evaluate_all(self, findings: list[Finding]) -> list[Decision]:
        return [self.evaluate(f) for f in findings]
