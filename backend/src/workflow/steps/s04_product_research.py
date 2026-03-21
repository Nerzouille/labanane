"""Step 4 — Product Research (system_processing stub)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepProcessingMessage, StepResultMessage, ServerMessage

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput


class ProductResearchStep(Step):
    @property
    def step_id(self) -> str:
        return "product_research"

    @property
    def label(self) -> str:
        return "Product Research"

    @property
    def step_type(self) -> str:
        return "system_processing"

    @property
    def component_type(self) -> str:
        return "product_list"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        yield StepProcessingMessage(step_id=self.step_id)
        # TODO: call real product research pipeline using confirmed keywords
        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={
                "products": [
                    {"title": "Stub Product A", "price": "$29.99", "url": "https://example.com/a"},
                    {"title": "Stub Product B", "price": "$39.99", "url": "https://example.com/b"},
                ]
            },
        )
