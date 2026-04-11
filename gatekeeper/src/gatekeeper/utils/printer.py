from datetime import datetime
from enum import Enum
from typing import IO, Any

import click


class LogLevel(Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


def cli_log(message: str, level: LogLevel = LogLevel.INFO) -> None:
    """Logs a message to the CLI with a timestamp, log level, and consistent formatting."""

    timestamp = click.style(f"[{datetime.now().strftime("%H:%M:%S")}]", fg="green")
    cli_prefix = click.style("[Gatekeeper]", fg="cyan", bold=True)
    level_tag = _get_level_tag(level)
    click.echo(f"{timestamp} {cli_prefix} {level_tag} {message}")


class CliException(click.ClickException):
    """Thin wrapper around ClickException to allow for custom formatting of error messages."""

    def show(self, file: IO[Any] | None = None) -> None:
        cli_log(f"Aborting: {self.format_message()}", LogLevel.ERROR)


def _get_level_tag(level: LogLevel) -> str:
    level_tags = {
        LogLevel.DEBUG: click.style("[DEBUG]", fg="blue", bold=True),
        LogLevel.INFO: click.style("[INFO]", fg="green", bold=True),
        LogLevel.WARNING: click.style("[WARNING]", fg="yellow", bold=True),
        LogLevel.ERROR: click.style("[ERROR]", fg="red", bold=True),
    }
    return level_tags.get(level, "")
