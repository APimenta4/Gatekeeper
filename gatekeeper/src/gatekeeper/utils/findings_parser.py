from dataclasses import dataclass

from gatekeeper.utils.printer import LogLevel, cli_log

SEVERITY_LOW = "LOW"
SEVERITY_MEDIUM = "MEDIUM"
SEVERITY_HIGH = "HIGH"
SEVERITY_CRITICAL = "CRITICAL"


@dataclass
class Finding:
    tool: str
    file: str
    line: int
    severity: str
    message: str


def parse_findings(raw: dict) -> list[Finding]:
    """Dispatch raw per-tool JSON (keyed by tool name) to per-tool parsers."""
    parsers = {
        "Bandit": _parse_bandit,
        "Semgrep": _parse_semgrep,
        "Trivy": _parse_trivy,
        "gosec": _parse_gosec,
        "ESLint": _parse_eslint,
        "Flawfinder": _parse_flawfinder,
        "Progpilot": _parse_progpilot,
        "SpotBugs": _parse_spotbugs,
    }

    all_findings: list[Finding] = []
    for tool_name, tool_output in raw.items():
        parser = parsers.get(tool_name)
        if parser is None:
            cli_log(f"No parser for tool '{tool_name}', skipping findings", LogLevel.WARNING)
            continue
        try:
            all_findings.extend(parser(tool_output))
        except Exception as e:
            cli_log(f"Failed to parse findings for '{tool_name}': {e}", LogLevel.WARNING)

    return all_findings


def _normalize_bandit_severity(sev: str) -> str:
    return sev.upper() if sev.upper() in (SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH) else SEVERITY_MEDIUM


def _parse_bandit(data: dict) -> list[Finding]:
    findings = []
    for r in data.get("results", []):
        findings.append(Finding(
            tool="Bandit",
            file=r.get("filename", ""),
            line=int(r.get("line_number", 0)),
            severity=_normalize_bandit_severity(r.get("issue_severity", SEVERITY_MEDIUM)),
            message=r.get("issue_text", ""),
        ))
    return findings


def _parse_semgrep(data: dict) -> list[Finding]:
    _semgrep_map = {"INFO": SEVERITY_LOW, "WARNING": SEVERITY_MEDIUM, "ERROR": SEVERITY_HIGH}
    findings = []
    for r in data.get("results", []):
        raw_sev = r.get("extra", {}).get("severity", "WARNING").upper()
        findings.append(Finding(
            tool="Semgrep",
            file=r.get("path", ""),
            line=r.get("start", {}).get("line", 0),
            severity=_semgrep_map.get(raw_sev, SEVERITY_MEDIUM),
            message=r.get("extra", {}).get("message", ""),
        ))
    return findings


def _parse_trivy(data: dict) -> list[Finding]:
    _trivy_map = {
        "LOW": SEVERITY_LOW,
        "MEDIUM": SEVERITY_MEDIUM,
        "HIGH": SEVERITY_HIGH,
        "CRITICAL": SEVERITY_CRITICAL,
    }
    findings = []
    for result in data.get("Results", []):
        target = result.get("Target", "")
        for vuln in result.get("Vulnerabilities", []) or []:
            raw_sev = vuln.get("Severity", "MEDIUM").upper()
            findings.append(Finding(
                tool="Trivy",
                file=target,
                line=0,
                severity=_trivy_map.get(raw_sev, SEVERITY_MEDIUM),
                message=f"{vuln.get('VulnerabilityID', '')} {vuln.get('PkgName', '')}: {vuln.get('Description', '')}",
            ))
    return findings


def _parse_gosec(data: dict) -> list[Finding]:
    findings = []
    for issue in data.get("Issues", []) or []:
        raw_sev = issue.get("severity", SEVERITY_MEDIUM).upper()
        sev = raw_sev if raw_sev in (SEVERITY_LOW, SEVERITY_MEDIUM, SEVERITY_HIGH) else SEVERITY_MEDIUM
        findings.append(Finding(
            tool="gosec",
            file=issue.get("file", ""),
            line=int(issue.get("line", 0)),
            severity=sev,
            message=issue.get("details", ""),
        ))
    return findings


def _parse_eslint(data: list) -> list[Finding]:
    _eslint_sev = {1: SEVERITY_MEDIUM, 2: SEVERITY_HIGH}
    findings = []
    for file_result in data or []:
        file_path = file_result.get("filePath", "")
        for msg in file_result.get("messages", []):
            findings.append(Finding(
                tool="ESLint",
                file=file_path,
                line=msg.get("line", 0),
                severity=_eslint_sev.get(msg.get("severity", 1), SEVERITY_MEDIUM),
                message=msg.get("message", ""),
            ))
    return findings


def _parse_flawfinder(data: list) -> list[Finding]:
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


def _parse_progpilot(data: list) -> list[Finding]:
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


def _parse_spotbugs(data: list) -> list[Finding]:
    _priority_map = {"1": SEVERITY_HIGH, "2": SEVERITY_MEDIUM, "3": SEVERITY_LOW}
    findings = []
    for item in data or []:
        findings.append(Finding(
            tool="SpotBugs",
            file=item.get("class", ""),
            line=0,
            severity=_priority_map.get(str(item.get("priority", "2")), SEVERITY_MEDIUM),
            message=f"{item.get('bugType', '')}: {item.get('message', '')}",
        ))
    return findings
