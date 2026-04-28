import click

from gatekeeper.pipeline.base import ScanFilter
from gatekeeper.pipeline.context import ScanContext
from gatekeeper.utils.git import get_git_tracked_files_current_dir
from gatekeeper.utils.printer import cli_log
from gatekeeper.utils.sast_tools import SastTool, get_tools_from_config


class ToolSelectionFilter(ScanFilter):
    def process(self, ctx: ScanContext) -> ScanContext:
        cli_log("Selecting SAST tools to use based on the codebase...")
        file_names = get_git_tracked_files_current_dir()
        extensions = _get_unique_extensions(file_names)

        generic_tools, specific_tools_config = get_tools_from_config()
        selected_specific: set[SastTool] = {
            t for t in specific_tools_config
            if t.supported_file_extensions.intersection(extensions)
        }

        ctx.sast_tools = selected_specific.union(generic_tools)
        cli_log(
            f"Selected {', '.join(click.style(t.name, fg='green', bold=True) for t in ctx.sast_tools)}"
        )
        return ctx


def _get_unique_extensions(file_names: list[str]) -> set[str]:
    extensions = set()
    for name in file_names:
        if "." in name:
            _, ext = name.rsplit(".", 1)
            extensions.add(f".{ext}")
    return extensions
