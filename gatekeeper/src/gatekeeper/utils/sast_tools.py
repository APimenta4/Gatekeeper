from dataclasses import dataclass, fields
from functools import cache
from typing import Tuple

import click
import yaml

from gatekeeper.defaults import TOOLS_CONFIG_PATH
from gatekeeper.utils.printer import LogLevel, cli_log


@dataclass(frozen=True)
class SastTool:
    """Represents a generic SAST tool that will be run on any codebase,
    regardless of the programming languages used."""

    name: str


@dataclass(frozen=True)
class SpecificSastTool(SastTool):
    """Represents a SAST tool that will only be run if certain
    programming languages are detected in the codebase."""

    supported_file_extensions: frozenset[str]


@cache
def get_tools_from_config() -> Tuple[frozenset[SastTool], frozenset[SpecificSastTool]]:
    def _add_tool(group: set, config: dict, generic: bool = False) -> None:
        """Safely parses a tool based on a dictionary config, skipping malformed ones."""
        target_class = SastTool if generic else SpecificSastTool

        valid_fields = {f.name for f in fields(target_class)}
        filtered_config = {k: v for k, v in config.items() if k in valid_fields}

        if "supported_file_extensions" in filtered_config:
            filtered_config["supported_file_extensions"] = frozenset(
                filtered_config["supported_file_extensions"]
            )

        try:
            group.add(target_class(**filtered_config))
        except Exception as e:
            cli_log(
                f"Skipping malformed SAST tool: "
                f"{click.style(str(config.get('name', 'unknown')), 'magenta', bold=True)}. "
                f"Error: {click.style(str(e), 'red', bold=True)}",
                level=LogLevel.WARNING,
            )

    with open(TOOLS_CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    generic_tools = set()
    for tool_config in config.get("generic_tools", []):
        _add_tool(generic_tools, tool_config, generic=True)

    specific_tools = set()
    for tool_config in config.get("specific_tools", []):
        _add_tool(specific_tools, tool_config, generic=False)

    return frozenset(generic_tools), frozenset(specific_tools)
