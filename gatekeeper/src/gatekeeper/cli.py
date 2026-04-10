import click

from .commands import all_cli_commands


@click.group()
@click.version_option(None, "-v", "--version")
def main():
    """Gatekeeper CLI"""


for cli_command in all_cli_commands:
    main.command(cli_command)
