import re

from gatekeeper.parsers.baseParser import ParserFactory, ToolParser
from gatekeeper.parsers.model import Finding, SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH

_SEVERITY_MAP = {"INFO": SEVERITY_LOW, "WARNING": SEVERITY_MEDIUM, "ERROR": SEVERITY_HIGH}


def _extract_cwe(meta: dict) -> str | None:
    raw = meta.get("cwe")
    if not raw:
        return None
    if isinstance(raw, list):
        raw = raw[0] if raw else None
    if not raw:
        return None
    m = re.search(r"CWE-\d+", str(raw))
    return m.group(0) if m else None


@ParserFactory.register("Semgrep")
class SemgrepParser(ToolParser):
    def parse(self, data: dict) -> list[Finding]:
        findings = []
        for r in data.get("results", []):
            extra = r.get("extra", {})
            raw = extra.get("severity", "WARNING").upper()
            meta = extra.get("metadata", {}) or {}
            findings.append(Finding(
                tool="Semgrep",
                file=r.get("path", ""),
                line=r.get("start", {}).get("line", 0),
                severity=_SEVERITY_MAP.get(raw, SEVERITY_MEDIUM),
                message=extra.get("message", ""),
                cwe=_extract_cwe(meta),
            ))
        return findings
