from gatekeeper.parsers.baseParser import ParserFactory, ToolParser
from gatekeeper.parsers.model import Finding, SEVERITY_MEDIUM, SEVERITY_HIGH

_SEVERITY_MAP = {1: SEVERITY_MEDIUM, 2: SEVERITY_HIGH}


@ParserFactory.register("ESLint")
class ESLintParser(ToolParser):
    def parse(self, data: list) -> list[Finding]:
        findings = []
        for file_result in data or []:
            file_path = file_result.get("filePath", "")
            for msg in file_result.get("messages", []):
                findings.append(Finding(
                    tool="ESLint",
                    file=file_path,
                    line=msg.get("line", 0),
                    severity=_SEVERITY_MAP.get(msg.get("severity", 1), SEVERITY_MEDIUM),
                    message=msg.get("message", ""),
                ))
        return findings
