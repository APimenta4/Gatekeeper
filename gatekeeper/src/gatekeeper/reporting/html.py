from pathlib import Path

from gatekeeper.parsers.model import Finding
from gatekeeper.reporting.base import DashboardRenderer


class HtmlDashboardRenderer(DashboardRenderer):
    def _load_template(self) -> str:
        template_path = Path(__file__).parent.parent / "templates" / "report.html"
        return template_path.read_text(encoding="utf-8")


def generate_html_dashboard(
    findings: list[Finding],
    violations: list[Finding],
    output_path: Path,
) -> None:
    HtmlDashboardRenderer().render(findings, violations, output_path)
