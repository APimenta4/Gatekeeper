import pytest

from gatekeeper.parsers.model import Finding, SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL
from gatekeeper.policy.engine import PolicyEngine
from gatekeeper.policy.rules import default_rules
from gatekeeper.policy.verdict import Verdict


def _finding(**kwargs) -> Finding:
    defaults = dict(tool="test", file="test.py", line=1, severity=SEVERITY_HIGH, message="msg")
    return Finding(**{**defaults, **kwargs})


engine = PolicyEngine(default_rules)


@pytest.mark.parametrize("cwe,severity,expected", [
    # GK-001: command injection always blocks
    ("CWE-78", SEVERITY_LOW, Verdict.BLOCK),
    ("CWE-78", SEVERITY_HIGH, Verdict.BLOCK),
    # GK-002: SQL injection high/critical → block
    ("CWE-89", SEVERITY_HIGH, Verdict.BLOCK),
    ("CWE-89", SEVERITY_CRITICAL, Verdict.BLOCK),
    # GK-003: SQL injection medium → warn
    ("CWE-89", SEVERITY_MEDIUM, Verdict.WARN),
    # GK-004: path traversal always blocks
    ("CWE-22", SEVERITY_LOW, Verdict.BLOCK),
    # GK-005: hardcoded credentials (both CWEs)
    ("CWE-798", SEVERITY_MEDIUM, Verdict.BLOCK),
    ("CWE-259", SEVERITY_LOW, Verdict.BLOCK),
    # GK-006: insecure deserialization
    ("CWE-502", SEVERITY_HIGH, Verdict.BLOCK),
    # GK-007: XSS → warn
    ("CWE-79", SEVERITY_HIGH, Verdict.WARN),
    # GK-008: weak crypto → warn
    ("CWE-327", SEVERITY_MEDIUM, Verdict.WARN),
    # no rule → allow
    ("CWE-999", SEVERITY_HIGH, Verdict.ALLOW),
    (None, SEVERITY_HIGH, Verdict.ALLOW),
])
def test_default_rule_verdicts(cwe, severity, expected):
    decision = engine.evaluate(_finding(cwe=cwe, severity=severity))
    assert decision.verdict == expected


def test_sql_injection_low_severity_is_allowed():
    decision = engine.evaluate(_finding(cwe="CWE-89", severity=SEVERITY_LOW))
    assert decision.verdict == Verdict.ALLOW


def test_block_finding_recorded_in_matched_rules():
    decision = engine.evaluate(_finding(cwe="CWE-78"))
    rule_ids = [r.id for r in decision.matched_rules]
    assert "GK-001" in rule_ids


def test_all_default_rules_have_required_fields():
    for rule in default_rules:
        assert rule.id
        assert rule.name
        assert rule.description
        assert callable(rule.predicate)
        assert rule.verdict in list(Verdict)


def test_minimum_five_rules_defined():
    assert len(default_rules) >= 5
