from dataclasses import dataclass, field
from pathlib import Path

from gatekeeper.config.loader import GatekeeperConfig
from gatekeeper.parsers.model import Finding
from gatekeeper.policy.decision import Decision
from gatekeeper.utils.sast_tools import SastTool


@dataclass
class ScanContext:
    git_root: Path
    config: GatekeeperConfig
    verbose: bool
    no_report: bool
    show_details: bool = False
    # populated by filters
    sast_tools: set[SastTool] = field(default_factory=set)
    findings_file_path: str = ""
    raw_findings: dict = field(default_factory=dict)
    findings: list[Finding] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    violations: list[Finding] = field(default_factory=list)
