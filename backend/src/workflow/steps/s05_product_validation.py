"""Step 5 — Product Validation (confirmation)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import ConfirmationRequestMessage, ServerMessage

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput


class ProductValidationStep(Step):
    @property
    def step_id(self) -> str:
        return "product_validation"

    @property
    def label(self) -> str:
        return "Product Validation"

    @property
    def step_type(self) -> str:
        return "confirmation"

    @property
    def component_type(self) -> str:
        return "confirmation"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        yield ConfirmationRequestMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={"prompt": "Are these products relevant to your market?"},
        )
