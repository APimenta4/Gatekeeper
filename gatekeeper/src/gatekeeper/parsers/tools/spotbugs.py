from gatekeeper.parsers.baseParser import ParserFactory, ToolParser
from gatekeeper.parsers.model import Finding, SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH

_PRIORITY_MAP = {"1": SEVERITY_HIGH, "2": SEVERITY_MEDIUM, "3": SEVERITY_LOW}


@ParserFactory.register("SpotBugs")
class SpotBugsParser(ToolParser):
    def parse(self, data: list) -> list[Finding]:
        findings = []
        for item in data or []:
            findings.append(Finding(
                tool="SpotBugs",
                file=item.get("class", ""),
                line=0,
                severity=_PRIORITY_MAP.get(str(item.get("priority", "2")), SEVERITY_MEDIUM),
                message=f"{item.get('bugType', '')}: {item.get('message', '')}",
            ))
        return findings
