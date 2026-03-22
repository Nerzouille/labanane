"""Step 7 — AI Analysis (OpenHosta market analysis)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step, StepError
from ..messages import StepProcessingMessage, StepResultMessage, ServerMessage
from src.logic.analysis import generate_market_analysis
from src.models.report import MarketAnalysis

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
        return "ai_analysis"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        yield StepProcessingMessage(step_id=self.step_id)

        products: list[dict] = run.get_output("product_research").get("products", [])
        trends: dict = run.get_output("market_research").get("trends", {})

        if not products and not trends:
            raise StepError(
                "Cannot generate analysis: no product data and no trend data available. "
                "Please refine your search and try again.",
                retryable=False,
            )

        result = await generate_market_analysis(run.description, products, trends)

        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data=result.model_dump(),
        )
