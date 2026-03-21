"""Step 3 — Keyword Confirmation (confirmation)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import ConfirmationRequestMessage, ServerMessage

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput


class KeywordConfirmationStep(Step):
    @property
    def step_id(self) -> str:
        return "keyword_confirmation"

    @property
    def label(self) -> str:
        return "Keyword Confirmation"

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
            data={"prompt": "Do these keywords look correct for your product idea?"},
        )
