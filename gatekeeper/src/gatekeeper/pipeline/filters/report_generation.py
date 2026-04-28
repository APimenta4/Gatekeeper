import click

from gatekeeper.pipeline.base import ScanFilter
from gatekeeper.pipeline.context import ScanContext
from gatekeeper.reporting.html import generate_html_dashboard
from gatekeeper.utils.printer import cli_log


class ReportGenerationFilter(ScanFilter):
    def process(self, ctx: ScanContext) -> ScanContext:
        if ctx.no_report:
            return ctx
        dashboard_path = ctx.git_root / ".gatekeeper" / "report.html"
        generate_html_dashboard(ctx.findings, ctx.violations, dashboard_path)
        cli_log(f"HTML report: {click.style(str(dashboard_path.resolve()), fg='cyan')}")
        return ctx
