import click

from gatekeeper.defaults import SCAN_ENGINE_FINDINGS_FILE_PATH
from gatekeeper.utils.git import (
    get_git_tracked_files_current_dir,
    raise_if_in_not_git_repository,
)
from gatekeeper.utils.printer import cli_log
from gatekeeper.utils.sast_tools import (
    GENERIC_SAST_TOOLS,
    SPECIFIC_SAST_TOOLS,
    SastTool,
    SpecificSastTool,
)


def scan() -> None:
    """Runs the SAST tools on the current repository immediately"""
    raise_if_in_not_git_repository()
    sast_tools = select_sast_tools_based_on_codebase()
    invoke_scanning_docker_engine(SCAN_ENGINE_FINDINGS_FILE_PATH, sast_tools)

    # do_things_with_log_file_like_print

    # delete_log_file()

    cli_log("dasd...")


def select_sast_tools_based_on_codebase() -> set[SastTool]:
    cli_log("Selecting SAST tools to use based on the codebase...")
    file_names = get_git_tracked_files_current_dir()
    file_extensions = _get_unique_files_extensions(file_names)
    tools = _get_tools_from_extensions(file_extensions).union(GENERIC_SAST_TOOLS)
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

    for tool in SPECIFIC_SAST_TOOLS:
        if tool.supported_file_extensions.intersection(file_extensions):
            to_be_used_tools.add(tool)

    return to_be_used_tools


def invoke_scanning_docker_engine(
    findings_file_path: str, sast_tools: set[SastTool]
) -> None:
    cli_log("Starting scan...")
    
