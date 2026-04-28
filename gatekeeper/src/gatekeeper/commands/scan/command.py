import json
import subprocess
from datetime import datetime
from pathlib import Path
from time import sleep

import click
from halo import Halo

from gatekeeper.defaults import SCAN_ENGINE_FINDINGS_FILE_NAME, TOOLS_CONFIG_PATH
from gatekeeper.utils.dashboard import generate_html_dashboard
from gatekeeper.utils.findings_parser import parse_findings
from gatekeeper.utils.git import (
    get_git_root_path,
    get_git_tracked_files_current_dir,
    raise_if_in_not_git_repository,
)
from gatekeeper.utils.policy import evaluate_policy, load_policy_config
from gatekeeper.utils.printer import CliException, LogLevel, cli_log
from gatekeeper.utils.sast_tools import (
    SastTool,
    SpecificSastTool,
    get_tools_from_config,
)


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
    _create_gitignored_gatekeeper_directory_if_not_exists()
    git_root_path = get_git_root_path()
    findings_file_path = str(
        Path(git_root_path) / ".gatekeeper" / SCAN_ENGINE_FINDINGS_FILE_NAME
    )
    sast_tools = select_sast_tools_based_on_codebase()
    invoke_scanning_docker_engine(SCAN_ENGINE_FINDINGS_FILE_NAME, sast_tools, git_root_path, verbose)

    raw = json.loads(Path(findings_file_path).read_text(encoding="utf-8"))
    findings = parse_findings(raw)
    cli_log(f"Parsed {click.style(str(len(findings)), bold=True)} finding(s) across all tools")

    policy = load_policy_config(TOOLS_CONFIG_PATH)
    violations = evaluate_policy(findings, policy)

    if not no_report:
        dashboard_path = Path(git_root_path) / ".gatekeeper" / "report.html"
        generate_html_dashboard(findings, violations, dashboard_path)
        cli_log(f"HTML report: {click.style(str(dashboard_path.resolve()), fg='cyan')}")

    if violations:
        cli_log(
            f"{len(violations)} finding(s) violate the policy "
            f"(fail_on_severity={click.style(policy.fail_on_severity, fg='red', bold=True)})",
            LogLevel.ERROR,
        )
        for v in violations:
            cli_log(
                f"  [{click.style(v.severity, fg='red', bold=True)}] "
                f"{v.tool} — {v.file}:{v.line} — {v.message}",
                LogLevel.ERROR,
            )
        raise SystemExit(1)

    cli_log(click.style("Scan completed — no policy violations!", fg="green", bold=True))


def _create_gitignored_gatekeeper_directory_if_not_exists() -> None:
    git_root_path = get_git_root_path()
    gatekeeper_dir = Path(git_root_path) / ".gatekeeper"
    gatekeeper_dir.mkdir(exist_ok=True)

    gitignore_path = gatekeeper_dir / ".gitignore"
    if not gitignore_path.exists():
        gitignore_path.write_text(
            "# This directory is used exclusively by Gatekeeper and should not "
            "be committed to version control\n# Please keep the whole directory gitignored\n*\n"
        )


def select_sast_tools_based_on_codebase() -> set[SastTool]:
    cli_log("Selecting SAST tools to use based on the codebase...")
    file_names = get_git_tracked_files_current_dir()
    file_extensions = _get_unique_files_extensions(file_names)

    specific_tools = _get_tools_from_extensions(file_extensions)
    generic_tools, _ = get_tools_from_config()

    tools = specific_tools.union(generic_tools)
    cli_log(
        f"Selected {', '.join(click.style(tool.name, fg='green', bold=True) for tool in tools)}"
    )
    return tools


def _get_unique_files_extensions(file_names: list[str]) -> set[str]:
    file_suffixes = set()

    for file_name in file_names:
        if "." not in file_name:
            continue
        _, ext = file_name.rsplit(".", 1)
        file_suffixes.add(f".{ext}")

    return file_suffixes


def _get_tools_from_extensions(
    file_extensions: set[str],
) -> set[SpecificSastTool]:
    to_be_used_tools = set()

    _, specific_tools = get_tools_from_config()
    for tool in specific_tools:
        if tool.supported_file_extensions.intersection(file_extensions):
            to_be_used_tools.add(tool)

    return to_be_used_tools


def invoke_scanning_docker_engine(
    findings_file_name: str, sast_tools: set[SastTool], git_root_path: str, verbose: bool = False
) -> None:
    tool_names = ",".join(tool.name for tool in sast_tools)

    cli_log("Starting scanning docker engine...")

    container_output_path = f"/repo/.gatekeeper/{findings_file_name}"

    docker_cmd = [
        "docker",
        "run",
        "--rm",
        "-v",
        f"{git_root_path}:/repo",
        "gatekeeper-scanner",
        "--tools",
        tool_names,
        "--output",
        container_output_path,
    ]

    if verbose:
        cli_log("Attaching engine's container shell...")
        sleep(2)
    else:
        docker_cmd.insert(3, "--quiet")
        cli_log("Running engine in quiet mode...")

    try:
        if verbose:
            subprocess.run(
                docker_cmd,
                check=True,
                stdout=None,
                stderr=None,
            )
        else:
            _start_scan_with_spinner(docker_cmd)
    except subprocess.CalledProcessError as e:
        raise CliException(
            f"Error occurred while running the scanning engine: {e}",
        )


def _start_scan_with_spinner(docker_cmd: list[str]) -> None:
    start_time = datetime.now()
    spinner_prefix = (
        click.style(f"[{datetime.now().strftime('%H:%M:%S')}] ", fg="green")
        + click.style("[Gatekeeper] ", fg="cyan", bold=True)
        + click.style("[INFO] ", fg="green", bold=True)
    )
    spinner = Halo(
        text=spinner_prefix + click.style("Scanning repository", fg="green", bold=True),
        spinner="dots",
        placement="right",
    )
    spinner.start()

    process = subprocess.Popen(
        docker_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    while process.poll() is None:
        elapsed = (datetime.now() - start_time).seconds
        spinner.text = (
            spinner_prefix
            + click.style("Scanning repository", fg="green", bold=True)
            + click.style(f" {elapsed} seconds elapsed", fg="yellow")
        )
        sleep(1)

    if process.returncode == 0:
        spinner.succeed(
            spinner_prefix
            + click.style("Done", fg="green", bold=True)
            + click.style(
                f" (took {(datetime.now() - start_time).seconds} seconds)",
                fg="yellow",
            )
        )
    else:
        spinner.fail(
            spinner_prefix
            + click.style("Scan failed", fg="red", bold=True)
            + click.style(
                f" after {(datetime.now() - start_time).seconds} seconds",
                fg="yellow",
            )
        )
        raise subprocess.CalledProcessError(process.returncode, docker_cmd)
