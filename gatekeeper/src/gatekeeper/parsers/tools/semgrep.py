from gatekeeper.parsers.baseParser import ParserFactory, ToolParser
from gatekeeper.parsers.model import Finding, SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH

_SEVERITY_MAP = {"INFO": SEVERITY_LOW, "WARNING": SEVERITY_MEDIUM, "ERROR": SEVERITY_HIGH}


@ParserFactory.register("Semgrep")
class SemgrepParser(ToolParser):
    def parse(self, data: dict) -> list[Finding]:
        findings = []
        for r in data.get("results", []):
            raw = r.get("extra", {}).get("severity", "WARNING").upper()
            findings.append(Finding(
                tool="Semgrep",
                file=r.get("path", ""),
                line=r.get("start", {}).get("line", 0),
                severity=_SEVERITY_MAP.get(raw, SEVERITY_MEDIUM),
                message=r.get("extra", {}).get("message", ""),
            ))
        return findings
