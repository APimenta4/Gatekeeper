from gatekeeper.parsers.baseParser import ParserFactory, ToolParser
from gatekeeper.parsers.model import Finding, SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH


@ParserFactory.register("Flawfinder")
class FlawfinderParser(ToolParser):
    def parse(self, data: list) -> list[Finding]:
        findings = []
        for item in data or []:
            level = int(item.get("level", 0))
            if level <= 1:
                sev = SEVERITY_LOW
            elif level <= 3:
                sev = SEVERITY_MEDIUM
            else:
                sev = SEVERITY_HIGH
            findings.append(Finding(
                tool="Flawfinder",
                file=item.get("filename", ""),
                line=int(item.get("line", 0)),
                severity=sev,
                message=item.get("warning", ""),
            ))
        return findings
