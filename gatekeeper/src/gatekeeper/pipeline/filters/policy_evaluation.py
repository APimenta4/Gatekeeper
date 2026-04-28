from gatekeeper.config.loader import evaluate_policy
from gatekeeper.pipeline.base import ScanFilter
from gatekeeper.pipeline.context import ScanContext


class PolicyEvaluationFilter(ScanFilter):
    def process(self, ctx: ScanContext) -> ScanContext:
        ctx.violations = evaluate_policy(ctx.findings, ctx.config.policy)
        return ctx
