"""Step 6 — Market Research (system_processing stub)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepProcessingMessage, StepResultMessage, ServerMessage

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput


class MarketResearchStep(Step):
    @property
    def step_id(self) -> str:
        return "market_research"

    @property
    def label(self) -> str:
        return "Market Research"

    @property
    def step_type(self) -> str:
        return "system_processing"

    @property
    def component_type(self) -> str:
        return "market_data_summary"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        yield StepProcessingMessage(step_id=self.step_id)
        # TODO: call real market research pipeline
        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={
                "sources_available": ["amazon"],
                "sources_unavailable": [],
                "trend_summary": "Stub: trend data not yet implemented.",
                "sentiment_summary": "Stub: sentiment data not yet implemented.",
            },
        )
