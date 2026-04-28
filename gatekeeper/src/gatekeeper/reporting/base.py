from abc import ABC, abstractmethod
from pathlib import Path

from gatekeeper.parsers.model import Finding

_SEVERITY_COLORS = {
    "CRITICAL": "#c0392b",
    "HIGH": "#e67e22",
    "MEDIUM": "#f1c40f",
    "LOW": "#95a5a6",
}


class DashboardRenderer(ABC):
    """Template Method: defines the dashboard render skeleton."""

    def render(self, findings: list[Finding], violations: list[Finding], output_path: Path) -> None:
        template = self._load_template()
        data = self._prepare_data(findings, violations)
        content = self._fill_template(template, data)
        self._write(content, output_path)

    @abstractmethod
    def _load_template(self) -> str: ...

    def _prepare_data(self, findings: list[Finding], violations: list[Finding]) -> dict:
        from datetime import datetime

        violation_ids = set(id(f) for f in violations)
        counts = {sev: sum(1 for f in findings if f.severity == sev) for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}

        severity_order = ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        sorted_findings = sorted(
            findings,
            key=lambda f: severity_order.index(f.severity) if f.severity in severity_order else len(severity_order),
        )

        rows = []
        for f in sorted_findings:
            color = _SEVERITY_COLORS.get(f.severity, "#95a5a6")
            row_class = ' class="violation-row"' if id(f) in violation_ids else ""
            rows.append(
                f'      <tr{row_class}>'
                f'<td><span class="badge" style="background:{color}">{f.severity}</span></td>'
                f"<td>{_esc(f.tool)}</td>"
                f"<td>{_esc(f.file)}</td>"
                f"<td>{f.line}</td>"
                f"<td>{_esc(f.message)}</td>"
                f"</tr>"
            )

        if violations:
            banner = f'<div class="violations-banner">&#9888; {len(violations)} policy violation(s) detected &mdash; commit blocked</div>'
        else:
            banner = '<div class="clean-banner">&#10003; No policy violations detected</div>'

        no_findings_row = '      <tr><td colspan="5" style="text-align:center;color:#7f8c8d">No findings</td></tr>'

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "total": len(findings),
            "critical": counts["CRITICAL"],
            "high": counts["HIGH"],
            "medium": counts["MEDIUM"],
            "low": counts["LOW"],
            "violations": len(violations),
            "critical_color": _SEVERITY_COLORS["CRITICAL"] if counts["CRITICAL"] else "#2c3e50",
            "high_color": _SEVERITY_COLORS["HIGH"] if counts["HIGH"] else "#2c3e50",
            "medium_color": _SEVERITY_COLORS["MEDIUM"] if counts["MEDIUM"] else "#2c3e50",
            "low_color": _SEVERITY_COLORS["LOW"],
            "violations_color": _SEVERITY_COLORS["HIGH"] if violations else "#27ae60",
            "banner": banner,
            "rows": "\n".join(rows) if rows else no_findings_row,
        }

    def _fill_template(self, template: str, data: dict) -> str:
        return template.format(**data)

    def _write(self, content: str, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
