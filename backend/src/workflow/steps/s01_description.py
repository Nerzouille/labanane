"""Step 1 — Product Description (user_input)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepResultMessage, ServerMessage

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput


class ProductDescriptionStep(Step):
    @property
    def step_id(self) -> str:
        return "product_description"

    @property
    def label(self) -> str:
        return "Product Description"

    @property
    def step_type(self) -> str:
        return "user_input"

    @property
    def component_type(self) -> str:
        return "product_description_input"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={"text": run.description},
        )
