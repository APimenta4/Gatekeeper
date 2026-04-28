from gatekeeper.parsers.baseParser import ParserFactory, ToolParser
from gatekeeper.parsers.model import (
    Finding, SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH, SEVERITY_CRITICAL,
)

_SEVERITY_MAP = {
    "LOW": SEVERITY_LOW,
    "MEDIUM": SEVERITY_MEDIUM,
    "HIGH": SEVERITY_HIGH,
    "CRITICAL": SEVERITY_CRITICAL,
}


@ParserFactory.register("Trivy")
class TrivyParser(ToolParser):
    def parse(self, data: dict) -> list[Finding]:
        findings = []
        for result in data.get("Results", []):
            target = result.get("Target", "")
            for vuln in result.get("Vulnerabilities", []) or []:
                raw = vuln.get("Severity", "MEDIUM").upper()
                findings.append(Finding(
                    tool="Trivy",
                    file=target,
                    line=0,
                    severity=_SEVERITY_MAP.get(raw, SEVERITY_MEDIUM),
                    message=f"{vuln.get('VulnerabilityID', '')} {vuln.get('PkgName', '')}: {vuln.get('Description', '')}",
                ))
        return findings
