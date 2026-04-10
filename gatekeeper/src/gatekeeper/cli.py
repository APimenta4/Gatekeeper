import shutil
from typing import List

import click

from gatekeeper.utils.printer import LogLevel, cli_log

from .commands import all_cli_commands


@click.group()
@click.version_option(None, "-v", "--version")
def main():
    """Gatekeeper CLI"""
    cli_log("Starting Gatekeeper...")
    _warn_missing_dependencies()


for cli_command in all_cli_commands:
    main.command(cli_command)


def _warn_missing_dependencies() -> None:
    required_tools = ["docker", "pre-commit", "fk", "nigga"]
    missing_tools: List[str] = []

    for tool in required_tools:
        if shutil.which(tool) is None:
            missing_tools.append(tool)

    if missing_tools:
        missing_str = ", ".join(missing_tools)
        missing_str = click.style(missing_str, fg="red", bold=True)
        cli_log(
            f"Gatekeeper depends on and could not verify that the following tools are installed: {missing_str}. "
            f"Please ensure they are installed and available in your PATH.",
            LogLevel.WARNING,
        )
