from abc import ABC, abstractmethod

from gatekeeper.pipeline.context import ScanContext


class ScanFilter(ABC):
    @abstractmethod
    def process(self, ctx: ScanContext) -> ScanContext: ...


class ScanPipeline:
    def __init__(self, filters: list[ScanFilter]) -> None:
        self._filters = filters

    def run(self, ctx: ScanContext) -> ScanContext:
        for f in self._filters:
            ctx = f.process(ctx)
        return ctx
