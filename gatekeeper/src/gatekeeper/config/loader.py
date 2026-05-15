import fnmatch
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from gatekeeper.defaults import USER_CONFIG_FILE_NAME

_DEFAULT_EXCLUDED_DIRS = [".venv", "node_modules", "dist", "build", "__pycache__", ".git"]


@dataclass
class GatekeeperConfig:
    excluded_dirs: list[str] = field(default_factory=lambda: list(_DEFAULT_EXCLUDED_DIRS))
    excluded_files: list[str] = field(default_factory=list)


def load_config(git_root: Path) -> GatekeeperConfig:
    """Load .gatekeeper.yaml from the target repo root and merge with defaults."""
    config = GatekeeperConfig()
    user_config_path = git_root / USER_CONFIG_FILE_NAME

    if not user_config_path.exists():
        return config

    raw = yaml.safe_load(user_config_path.read_text(encoding="utf-8")) or {}

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
