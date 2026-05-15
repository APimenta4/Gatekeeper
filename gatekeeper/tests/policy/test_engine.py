import pytest

from gatekeeper.parsers.model import Finding, SEVERITY_HIGH
from gatekeeper.policy.engine import PolicyEngine
from gatekeeper.policy.rule import Rule
from gatekeeper.policy.verdict import Verdict


def _finding(**kwargs) -> Finding:
    defaults = dict(tool="test", file="test.py", line=1, severity=SEVERITY_HIGH, message="msg")
    return Finding(**{**defaults, **kwargs})


@pytest.fixture
def block_rule():
    return Rule(
        id="T-001", name="Block rule", description="",
        predicate=lambda f: f.cwe == "CWE-78",
        verdict=Verdict.BLOCK,
    )


@pytest.fixture
def warn_rule():
    return Rule(
        id="T-002", name="Warn rule", description="",
        predicate=lambda f: f.cwe == "CWE-79",
        verdict=Verdict.WARN,
    )


def test_no_rules_yields_allow():
    engine = PolicyEngine([])
    decision = engine.evaluate(_finding(cwe="CWE-78"))
    assert decision.verdict == Verdict.ALLOW
    assert decision.matched_rules == []


def test_single_block_rule_matches(block_rule):
    engine = PolicyEngine([block_rule])
    decision = engine.evaluate(_finding(cwe="CWE-78"))
    assert decision.verdict == Verdict.BLOCK
    assert block_rule in decision.matched_rules


def test_single_block_rule_no_match(block_rule):
    engine = PolicyEngine([block_rule])
    decision = engine.evaluate(_finding(cwe="CWE-89"))
    assert decision.verdict == Verdict.ALLOW
    assert decision.matched_rules == []


def test_all_rules_run_worst_wins(block_rule, warn_rule):
    engine = PolicyEngine([warn_rule, block_rule])
    decision = engine.evaluate(_finding(cwe="CWE-78"))
    assert decision.verdict == Verdict.BLOCK
    assert block_rule in decision.matched_rules


def test_multiple_matching_rules_recorded(block_rule, warn_rule):
    always_warn = Rule(
        id="T-003", name="Always warn", description="",
        predicate=lambda f: True,
        verdict=Verdict.WARN,
    )
    engine = PolicyEngine([always_warn, block_rule])
    decision = engine.evaluate(_finding(cwe="CWE-78"))
    assert decision.verdict == Verdict.BLOCK
    assert len(decision.matched_rules) == 2


def test_evaluate_all_returns_one_decision_per_finding(block_rule):
    engine = PolicyEngine([block_rule])
    findings = [_finding(cwe="CWE-78"), _finding(cwe="CWE-89"), _finding(cwe=None)]
    decisions = engine.evaluate_all(findings)
    assert len(decisions) == 3
    assert decisions[0].verdict == Verdict.BLOCK
    assert decisions[1].verdict == Verdict.ALLOW
    assert decisions[2].verdict == Verdict.ALLOW
