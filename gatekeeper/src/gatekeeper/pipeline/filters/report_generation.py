import click

from gatekeeper.pipeline.base import ScanFilter
from gatekeeper.pipeline.context import ScanContext
from gatekeeper.policy import Verdict
from gatekeeper.reporting.html import generate_html_dashboard


def _normalize_cwe(cwe: str) -> str:
    value = cwe.strip()
    if not value:
        return value
    if value.isdigit():
        return f"CWE-{value}"
    if value.upper().startswith("CWE ") and value[4:].strip().isdigit():
        return f"CWE-{value[4:].strip()}"
    return value


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    value = hex_color.strip().lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


_BLOCKED_FG = _hex_to_rgb("#c0392b")
_WARNING_FG = _hex_to_rgb("#f1c40f")

_CWE_FG = _hex_to_rgb("#9b59b6")  # purple-ish

def _style_padded(text: str, width: int, *, fg: str | tuple[int, int, int] | None = None) -> str:
    padded = f"{text:<{width}}"
    return click.style(padded, fg=fg) if fg else padded


def _style_verdict_label(label: str) -> str:
    if label == "BLOCKED":
        return click.style(label, fg=_BLOCKED_FG, bold=True)
    if label == "WARNING":
        return click.style(label, fg=_WARNING_FG, bold=True)
    if label == "ALLOWED":
        return click.style(label, fg="blue", bold=True)
    return label


def _style_verdict_label_padded(label: str, width: int) -> str:
    padded = f"{label:<{width}}"
    if label == "BLOCKED":
        return click.style(padded, fg=_BLOCKED_FG, bold=True)
    if label == "WARNING":
        return click.style(padded, fg=_WARNING_FG, bold=True)
    if label == "ALLOWED":
        return click.style(padded, fg="blue", bold=True)
    return padded


def _format_finding_line(
    *,
    prefix: str,
    label: str,
    cwe: str | None,
    location: str,
    message: str,
    show_details: bool,
) -> str:
    cwe_text = f"[{_normalize_cwe(cwe)}]" if cwe else ""
    styled_cwe = _style_padded(cwe_text, 13, fg=_CWE_FG) if cwe_text else _style_padded("", 12)
    styled_location = _style_padded(location, 20, fg='cyan')
    styled_label = _style_verdict_label_padded(label, 7)
    if not show_details:
        return f"{prefix}{styled_label}  {styled_cwe}  {styled_location}"
    return f"{prefix}{styled_label}  {styled_cwe}  {styled_location}  {message}"


def _plural(n: int, singular: str, plural: str | None = None) -> str:
    if n == 1:
        return singular
    return plural or f"{singular}s"


def _print_terminal_report(ctx: ScanContext) -> None:
    decisions = ctx.decisions or []
    blocked = [d for d in decisions if d.verdict == Verdict.BLOCK]
    warned = [d for d in decisions if d.verdict == Verdict.WARN]
    allowed = [d for d in decisions if d.verdict == Verdict.ALLOW]

    click.echo("")
    click.echo(click.style("=========================================", fg="yellow"))
    click.echo(
        click.style("= ", fg="yellow") + click.style("🔍 ") + click.style("Security Gatekeeper", fg="blue", bold=True)
        + click.style(" | ", fg="yellow")
        + click.style("Scan Results", fg="green", bold=True) + click.style(" =", fg="yellow")
    )
    click.echo(click.style("=========================================", fg="yellow"))
    click.echo("")

    for d in blocked:
        f = d.finding
        click.echo(
            _format_finding_line(
                prefix="❌ ",
                label="BLOCKED",
                cwe=f.cwe,
                location=f"{f.file}:{f.line}",
                message=f.message,
                show_details=ctx.show_details,
            )
        )
        click.echo("")

    for d in warned:
        f = d.finding
        click.echo(
            _format_finding_line(
                prefix="⚠️  ",
                label="WARNING",
                cwe=f.cwe,
                location=f"{f.file}:{f.line}",
                message=f.message,
                show_details=ctx.show_details,
            )
        )
        click.echo("")

    if allowed:
        severities = {d.finding.severity for d in allowed}
        severity_label = "/".join(sorted(severities))
        click.echo(
            f"ℹ️  {_style_verdict_label('ALLOWED')} {len(allowed)} "
            f"{_plural(len(allowed), 'finding')}: severity {severity_label}, policy set to allow"
        )
        click.echo("")
    elif not decisions:
        click.echo(f"ℹ️  {_style_verdict_label('ALLOWED')} 0 findings")
        click.echo("")

    click.echo("")

    if blocked:
        click.echo(
            f"Result: {_style_verdict_label('BLOCKED')}, fix {len(blocked)} {_plural(len(blocked), 'critical issue')} before committing."
        )
    elif warned:
        click.echo(
            f"Result: {_style_verdict_label('WARNING')}, review {len(warned)} {_plural(len(warned), 'warning')} before committing."
        )
    else:
        click.echo(f"Result: {_style_verdict_label('ALLOWED')}, no policy violations found.")


class ReportGenerationFilter(ScanFilter):
    def process(self, ctx: ScanContext) -> ScanContext:
        _print_terminal_report(ctx)

        if ctx.no_report:
            return ctx

        dashboard_path = ctx.git_root / ".gatekeeper" / "report.html"
        generate_html_dashboard(ctx.findings, ctx.violations, dashboard_path)
        click.echo(f"📋{click.style('[HTML report]', fg='yellow')}: {click.style(str(dashboard_path.resolve()), fg='cyan')}")
        return ctx
