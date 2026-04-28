import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from gatekeeper.defaults import USER_CONFIG_FILE_NAME

_DEFAULT_EXCLUDED_DIRS = [".venv", "node_modules", "dist", "build", "__pycache__", ".git"]


@dataclass
class PolicyConfig:
    fail_on_severity: str = "HIGH"
    max_findings: int | None = None
    ignored_tools: list[str] = field(default_factory=list)
    ignored_files: list[str] = field(default_factory=list)


@dataclass
class GatekeeperConfig:
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    excluded_dirs: list[str] = field(default_factory=lambda: list(_DEFAULT_EXCLUDED_DIRS))
    excluded_files: list[str] = field(default_factory=list)


SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


def load_config(git_root: Path) -> GatekeeperConfig:
    """Load .gatekeeper.yaml from the target repo root and merge with defaults."""
    config = GatekeeperConfig()
    user_config_path = git_root / USER_CONFIG_FILE_NAME

    if not user_config_path.exists():
        return config

    raw = yaml.safe_load(user_config_path.read_text(encoding="utf-8")) or {}

    if "policy" in raw:
        p = raw["policy"] or {}
        config.policy = PolicyConfig(
            fail_on_severity=p.get("fail_on_severity", config.policy.fail_on_severity).upper(),
            max_findings=p.get("max_findings", config.policy.max_findings),
            ignored_tools=p.get("ignored_tools", config.policy.ignored_tools) or [],
            ignored_files=p.get("ignored_files", config.policy.ignored_files) or [],
        )

    if "excluded_dirs" in raw:
        config.excluded_dirs = raw["excluded_dirs"] or []

    if "excluded_files" in raw:
        config.excluded_files = raw["excluded_files"] or []

    return config


def apply_exclusions(findings: list, config: GatekeeperConfig) -> list:
    """Filter out findings whose file is inside an excluded dir or matches an excluded file pattern."""
    if not config.excluded_dirs and not config.excluded_files:
        return findings

    result = []
    for f in findings:
        file_path = f.file.replace("\\", "/")

        if any(
            file_path.startswith(d + "/") or ("/" + d + "/") in file_path
            for d in config.excluded_dirs
        ):
            continue

        if any(fnmatch.fnmatch(file_path, pattern) for pattern in config.excluded_files):
            continue

        result.append(f)

    return result


def evaluate_policy(findings: list, policy: PolicyConfig) -> list:
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
