from pathlib import Path

import click

from gatekeeper.config import load_config
from gatekeeper.pipeline import ScanContext, ScanPipeline
from gatekeeper.pipeline.filters import (
    DockerScanFilter,
    FindingsParsingFilter,
    PolicyEvaluationFilter,
    ReportGenerationFilter,
    ToolSelectionFilter,
)
from gatekeeper.policy import Verdict
from gatekeeper.utils.git import get_git_root_path, raise_if_in_not_git_repository
from gatekeeper.utils.printer import LogLevel, cli_log


@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Attach container shell for real-time scan visualization and debugging",
)
@click.option(
    "--no-report",
    is_flag=True,
    help="Skip generating the HTML report",
)
def scan(verbose: bool, no_report: bool) -> None:
    """Runs the SAST tools on the current repository immediately"""
    raise_if_in_not_git_repository()
    git_root = Path(get_git_root_path())

    _create_gitignored_gatekeeper_directory_if_not_exists(git_root)

    config = load_config(git_root)

    ctx = ScanContext(
        git_root=git_root,
        config=config,
        verbose=verbose,
        no_report=no_report,
    )

    pipeline = ScanPipeline([
        ToolSelectionFilter(),
        DockerScanFilter(),
        FindingsParsingFilter(),
        PolicyEvaluationFilter(),
        ReportGenerationFilter(),
    ])

    ctx = pipeline.run(ctx)

    blocked = [d for d in ctx.decisions if d.verdict == Verdict.BLOCK]
    warned = [d for d in ctx.decisions if d.verdict == Verdict.WARN]

    if warned:
        for d in warned:
            rules_label = ", ".join(r.id for r in d.matched_rules) or "—"
            cwe_label = f" [{d.finding.cwe}]" if d.finding.cwe else ""
            cli_log(
                f"  [WARN]{cwe_label} {d.finding.tool} — "
                f"{d.finding.file}:{d.finding.line} ({rules_label}) — {d.finding.message}",
                LogLevel.WARNING,
            )

    if blocked:
        for d in blocked:
            rules_label = ", ".join(r.id for r in d.matched_rules) or "—"
            cwe_label = f" [{d.finding.cwe}]" if d.finding.cwe else ""
            cli_log(
                f"  [BLOCK]{cwe_label} {d.finding.tool} — "
                f"{d.finding.file}:{d.finding.line} ({rules_label}) — {d.finding.message}",
                LogLevel.ERROR,
            )
        cli_log(
            f"{len(blocked)} finding(s) BLOCKED by policy — fix before committing.",
            LogLevel.ERROR,
        )
        raise SystemExit(1)

    if warned:
        cli_log(
            click.style(f"Scan completed — {len(warned)} warning(s), no blockers.", fg="yellow", bold=True)
        )
    else:
        cli_log(click.style("Scan completed — no policy violations!", fg="green", bold=True))


def _create_gitignored_gatekeeper_directory_if_not_exists(git_root: Path) -> None:
    gatekeeper_dir = git_root / ".gatekeeper"
    gatekeeper_dir.mkdir(exist_ok=True)

    gitignore_path = gatekeeper_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(
            "# This directory is used exclusively by Gatekeeper and should not "
            "be committed to version control\n# Please keep the whole directory gitignored\n*\n"
        )
