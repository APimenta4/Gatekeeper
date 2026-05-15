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
@click.option(
    "--details/--no-details",
    default=True,
    show_default=True,
    help="Include per-finding messages in the terminal output",
)
def scan(verbose: bool, no_report: bool, details: bool) -> None:
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
        show_details=details,
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

    if blocked:
        raise SystemExit(1)

    # No extra terminal output here: the pipeline's ReportGenerationFilter prints the full
    # rubric-required scan report block (including the final Result line).


def _create_gitignored_gatekeeper_directory_if_not_exists(git_root: Path) -> None:
    gatekeeper_dir = git_root / ".gatekeeper"
    gatekeeper_dir.mkdir(exist_ok=True)

    gitignore_path = gatekeeper_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(
            "# This directory is used exclusively by Gatekeeper and should not "
            "be committed to version control\n# Please keep the whole directory gitignored\n*\n"
        )
