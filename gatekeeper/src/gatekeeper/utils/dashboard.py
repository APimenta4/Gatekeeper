from datetime import datetime
from pathlib import Path

from gatekeeper.utils.findings_parser import Finding

_SEVERITY_COLORS = {
    "CRITICAL": "#c0392b",
    "HIGH": "#e67e22",
    "MEDIUM": "#f1c40f",
    "LOW": "#95a5a6",
}

_HTML_TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Gatekeeper Security Report</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; background: #f4f6f8; color: #2c3e50; }}
  .header {{ background: #2c3e50; color: #fff; padding: 24px 32px; }}
  .header h1 {{ margin: 0; font-size: 1.6rem; }}
  .header p {{ margin: 4px 0 0; opacity: 0.7; font-size: 0.9rem; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 24px 32px; }}
  .summary {{ display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }}
  .card {{ background: #fff; border-radius: 8px; padding: 16px 24px; box-shadow: 0 1px 4px rgba(0,0,0,.08); min-width: 130px; }}
  .card .value {{ font-size: 2rem; font-weight: 700; }}
  .card .label {{ font-size: 0.8rem; color: #7f8c8d; text-transform: uppercase; letter-spacing: .05em; }}
  .violations-banner {{ background: #fdecea; border-left: 4px solid #c0392b; padding: 12px 16px; border-radius: 4px; margin-bottom: 20px; font-weight: 600; color: #c0392b; }}
  .clean-banner {{ background: #eafaf1; border-left: 4px solid #27ae60; padding: 12px 16px; border-radius: 4px; margin-bottom: 20px; font-weight: 600; color: #27ae60; }}
  table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 4px rgba(0,0,0,.08); }}
  th {{ background: #34495e; color: #fff; text-align: left; padding: 12px 14px; font-size: 0.82rem; text-transform: uppercase; letter-spacing: .05em; }}
  td {{ padding: 10px 14px; border-bottom: 1px solid #ecf0f1; font-size: 0.88rem; word-break: break-word; }}
  tr:last-child td {{ border-bottom: none; }}
  tr:hover td {{ background: #f9fbfc; }}
  .badge {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 0.75rem; font-weight: 700; color: #fff; }}
  .footer {{ text-align: center; color: #bdc3c7; font-size: 0.8rem; margin-top: 32px; padding-bottom: 24px; }}
  .violation-row td {{ background: #fff9f9; }}
</style>
</head>
<body>
<div class="header">
  <h1>Gatekeeper Security Report</h1>
  <p>Generated {timestamp}</p>
</div>
<div class="container">
  <div class="summary">
    <div class="card"><div class="value">{total}</div><div class="label">Total Findings</div></div>
    <div class="card"><div class="value" style="color:{critical_color}">{critical}</div><div class="label">Critical</div></div>
    <div class="card"><div class="value" style="color:{high_color}">{high}</div><div class="label">High</div></div>
    <div class="card"><div class="value" style="color:{medium_color}">{medium}</div><div class="label">Medium</div></div>
    <div class="card"><div class="value" style="color:{low_color}">{low}</div><div class="label">Low</div></div>
    <div class="card"><div class="value" style="color:{violations_color}">{violations}</div><div class="label">Policy Violations</div></div>
  </div>
  {banner}
  <table>
    <thead>
      <tr>
        <th>Severity</th><th>Tool</th><th>File</th><th>Line</th><th>Message</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>
  <div class="footer">Gatekeeper &mdash; MESW SES 2025/2026 Group 3</div>
</div>
</body>
</html>
"""


def generate_html_dashboard(
    findings: list[Finding],
    violations: list[Finding],
    output_path: Path,
) -> None:
    violation_set = set(id(f) for f in violations)
    counts = {sev: sum(1 for f in findings if f.severity == sev) for sev in ("CRITICAL", "HIGH", "MEDIUM", "LOW")}

    rows = []
    sorted_findings = sorted(findings, key=lambda f: -["LOW", "MEDIUM", "HIGH", "CRITICAL"].index(f.severity) if f.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"] else 0)
    for f in sorted_findings:
        color = _SEVERITY_COLORS.get(f.severity, "#95a5a6")
        row_class = ' class="violation-row"' if id(f) in violation_set else ""
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

    html = _HTML_TEMPLATE.format(
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        total=len(findings),
        critical=counts["CRITICAL"],
        high=counts["HIGH"],
        medium=counts["MEDIUM"],
        low=counts["LOW"],
        violations=len(violations),
        critical_color=_SEVERITY_COLORS["CRITICAL"] if counts["CRITICAL"] else "#2c3e50",
        high_color=_SEVERITY_COLORS["HIGH"] if counts["HIGH"] else "#2c3e50",
        medium_color=_SEVERITY_COLORS["MEDIUM"] if counts["MEDIUM"] else "#2c3e50",
        low_color=_SEVERITY_COLORS["LOW"],
        violations_color=_SEVERITY_COLORS["HIGH"] if violations else "#27ae60",
        banner=banner,
        rows="\n".join(rows) if rows else '      <tr><td colspan="5" style="text-align:center;color:#7f8c8d">No findings</td></tr>',
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")


def _esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
