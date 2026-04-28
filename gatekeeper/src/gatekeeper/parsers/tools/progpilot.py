from gatekeeper.parsers.baseParser import ParserFactory, ToolParser
from gatekeeper.parsers.model import Finding, SEVERITY_MEDIUM


@ParserFactory.register("Progpilot")
class ProgpilotParser(ToolParser):
    def parse(self, data: list) -> list[Finding]:
        findings = []
        for item in data or []:
            findings.append(Finding(
                tool="Progpilot",
                file=item.get("source_name", ""),
                line=int(item.get("source_line", 0)),
                severity=SEVERITY_MEDIUM,
                message=item.get("vuln_name", ""),
            ))
        return findings
