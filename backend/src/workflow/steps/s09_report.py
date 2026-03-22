"""Step 9 — Report Generation."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepResultMessage, ServerMessage
from src.logic.export import render_markdown
from src.store import _reports

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput


class ReportGenerationStep(Step):
    @property
    def step_id(self) -> str:
        return "report_generation"

    @property
    def label(self) -> str:
        return "Report Generation"

    @property
    def step_type(self) -> str:
        return "derivation"

    @property
    def component_type(self) -> str:
        return "report"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        keywords: list[str] = run.get_output("keyword_confirmation").get("keywords", [])
        products: list[dict] = run.get_output("product_research").get("products", [])
        trends: dict = run.get_output("market_research").get("trends", {})
        ai_analysis: dict = run.get_output("ai_analysis")

        run_data = {
            "run_id": run.run_id,
            "description": run.description,
            "keywords": keywords,
            "products": products,
            "trends": trends,
            "ai_analysis": ai_analysis,
        }

        markdown = render_markdown(run_data)
        _reports[run.run_id] = markdown

        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={
                "run_id": run.run_id,
                "markdown_available": True,
            },
        )
