import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from gatekeeper.utils.findings_parser import Finding

SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


@dataclass
class PolicyConfig:
    fail_on_severity: str = "HIGH"
    max_findings: int | None = None
    ignored_tools: list[str] = field(default_factory=list)
    ignored_files: list[str] = field(default_factory=list)


def load_policy_config(config_path: Path) -> PolicyConfig:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    raw = config.get("policy", {}) or {}
    return PolicyConfig(
        fail_on_severity=raw.get("fail_on_severity", "HIGH").upper(),
        max_findings=raw.get("max_findings"),
        ignored_tools=raw.get("ignored_tools", []) or [],
        ignored_files=raw.get("ignored_files", []) or [],
    )


def evaluate_policy(findings: list[Finding], policy: PolicyConfig) -> list[Finding]:
    """Return findings that violate the configured policy."""
    threshold = SEVERITY_ORDER.get(policy.fail_on_severity, 2)
    violations = []

    for f in findings:
        if f.tool in policy.ignored_tools:
            continue
        if any(fnmatch.fnmatch(f.file, pattern) for pattern in policy.ignored_files):
            continue
        if SEVERITY_ORDER.get(f.severity, 0) >= threshold:
            violations.append(f)

    if policy.max_findings is not None and len(findings) > policy.max_findings:
        for f in findings:
            if f not in violations:
                violations.append(f)

    return violations
