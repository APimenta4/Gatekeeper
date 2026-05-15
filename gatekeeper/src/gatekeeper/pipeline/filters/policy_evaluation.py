from gatekeeper.pipeline.base import ScanFilter
from gatekeeper.pipeline.context import ScanContext
from gatekeeper.policy import PolicyEngine, Verdict, default_rules


class PolicyEvaluationFilter(ScanFilter):
    def process(self, ctx: ScanContext) -> ScanContext:
        engine = PolicyEngine(default_rules)
        ctx.decisions = engine.evaluate_all(ctx.findings)
        ctx.violations = [d.finding for d in ctx.decisions if d.verdict == Verdict.BLOCK]
        return ctx
