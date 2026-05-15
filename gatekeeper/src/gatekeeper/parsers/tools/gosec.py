from gatekeeper.parsers.baseParser import ParserFactory, ToolParser
from gatekeeper.parsers.model import Finding, SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH


@ParserFactory.register("gosec")
class GosecParser(ToolParser):
    def parse(self, data: dict) -> list[Finding]:
        findings = []
        for issue in data.get("Issues", []) or []:
            raw = issue.get("severity", SEVERITY_MEDIUM).upper()
            sev = raw if raw in (SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH) else SEVERITY_MEDIUM
            cwe_obj = issue.get("cwe") or {}
            cwe_id = cwe_obj.get("ID") if isinstance(cwe_obj, dict) else None
            findings.append(Finding(
                tool="gosec",
                file=issue.get("file", ""),
                line=int(issue.get("line", 0)),
                severity=sev,
                message=issue.get("details", ""),
                cwe=f"CWE-{cwe_id}" if cwe_id else None,
            ))
        return findings
