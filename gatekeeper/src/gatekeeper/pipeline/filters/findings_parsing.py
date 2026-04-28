import json
from pathlib import Path

import click

from gatekeeper.config.loader import apply_exclusions
from gatekeeper.parsers import parse_findings
from gatekeeper.pipeline.base import ScanFilter
from gatekeeper.pipeline.context import ScanContext
from gatekeeper.utils.printer import cli_log


class FindingsParsingFilter(ScanFilter):
    def process(self, ctx: ScanContext) -> ScanContext:
        ctx.raw_findings = json.loads(Path(ctx.findings_file_path).read_text(encoding="utf-8"))
        all_findings = parse_findings(ctx.raw_findings)
        ctx.findings = apply_exclusions(all_findings, ctx.config)

        excluded_count = len(all_findings) - len(ctx.findings)
        msg = f"Parsed {click.style(str(len(ctx.findings)), bold=True)} finding(s) across all tools"
        if excluded_count:
            msg += f" ({excluded_count} excluded by config)"
        cli_log(msg)
        return ctx
