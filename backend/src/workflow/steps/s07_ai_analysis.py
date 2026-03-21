"""Step 7 — AI Analysis (OpenHosta market analysis)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepProcessingMessage, StepResultMessage, ServerMessage
from src.scraper import generate_market_analysis, MarketAnalysis

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput


class AiAnalysisStep(Step):
    @property
    def step_id(self) -> str:
        return "ai_analysis"

    @property
    def label(self) -> str:
        return "AI Analysis"

    @property
    def step_type(self) -> str:
        return "system_processing"

    @property
    def component_type(self) -> str:
        return "final_criteria"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        yield StepProcessingMessage(step_id=self.step_id)

        product_output = run.confirmed_outputs.get("product_research")
        products: list[dict] = product_output.data.get("products", []) if product_output else []

        result_dict = await generate_market_analysis(run.description, products)
        result = MarketAnalysis.model_validate(result_dict)

        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data=result.model_dump(),
        )
