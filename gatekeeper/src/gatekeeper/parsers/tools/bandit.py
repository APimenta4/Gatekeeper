from gatekeeper.parsers.baseParser import ParserFactory, ToolParser
from gatekeeper.parsers.model import Finding, SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH


@ParserFactory.register("Bandit")
class BanditParser(ToolParser):
    def parse(self, data: dict) -> list[Finding]:
        findings = []
        for r in data.get("results", []):
            raw = r.get("issue_severity", SEVERITY_MEDIUM).upper()
            sev = raw if raw in (SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH) else SEVERITY_MEDIUM
            cwe_data = r.get("issue_cwe") or {}
            cwe_id = cwe_data.get("id")
            findings.append(Finding(
                tool="Bandit",
                file=r.get("filename", ""),
                line=int(r.get("line_number", 0)),
                severity=sev,
                message=r.get("issue_text", ""),
                cwe=f"CWE-{cwe_id}" if cwe_id else None,
            ))
        return findings
