from datetime import datetime

import click


def cli_print(message: str) -> None:
    timestamp = click.style(f"[{datetime.now().strftime("%H:%M:%S")}]", fg="green")
    cli_prefix = click.style("[Gatekeeper]", fg="cyan", bold=True)
    click.echo(f"{timestamp} {cli_prefix} {message}")
