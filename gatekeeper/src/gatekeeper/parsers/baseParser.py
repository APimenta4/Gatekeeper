from abc import ABC, abstractmethod

from gatekeeper.parsers.model import Finding
from gatekeeper.utils.printer import LogLevel, cli_log


class ToolParser(ABC):
    @abstractmethod
    def parse(self, data: dict | list) -> list[Finding]: ...


class ParserFactory:
    _registry: dict[str, type[ToolParser]] = {}

    @classmethod
    def register(cls, tool_name: str):
        """Class decorator: @ParserFactory.register("ToolName")"""
        def decorator(parser_cls: type[ToolParser]) -> type[ToolParser]:
            cls._registry[tool_name] = parser_cls
            return parser_cls
        return decorator

    @classmethod
    def get(cls, tool_name: str) -> ToolParser | None:
        parser_cls = cls._registry.get(tool_name)
        return parser_cls() if parser_cls else None


def parse_findings(raw: dict) -> list[Finding]:
    """Dispatch raw per-tool JSON (keyed by tool name) to registered parsers."""
    all_findings: list[Finding] = []
    for tool_name, tool_output in raw.items():
        parser = ParserFactory.get(tool_name)
        if parser is None:
            cli_log(f"No parser registered for tool '{tool_name}', skipping", LogLevel.WARNING)
            continue
        try:
            all_findings.extend(parser.parse(tool_output))
        except Exception as e:
            cli_log(f"Parser failed for '{tool_name}': {e}", LogLevel.WARNING)
    return all_findings
