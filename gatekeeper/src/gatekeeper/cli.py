import click

from gatekeeper.utils.printer import cli_print

from .commands import all_cli_commands


@click.group()
@click.version_option(None, "-v", "--version")
def main():
    """Gatekeeper CLI"""
    cli_print("Starting Gatekeeper...")


for cli_command in all_cli_commands:
    main.command(cli_command)
