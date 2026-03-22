"""Step 6 — Market Research (Google Trends via pytrends)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepProcessingMessage, StepResultMessage, ServerMessage
from src.logic.trends import fetch_trends

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
        return "market_data"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        yield StepProcessingMessage(step_id=self.step_id)

        keywords: list[str] = run.get_output("keyword_refinement").get("keywords", [])
        if not keywords and input:
            keywords = input.data.get("keywords", [])

        trends_data = await fetch_trends(keywords)

        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={
                "keywords": trends_data.keywords,
                "sources_available": ["google_trends"] if trends_data.trends else [],
                "sources_unavailable": [] if trends_data.trends else ["google_trends"],
                "trends": trends_data.to_dict()["trends"],
            },
        )
