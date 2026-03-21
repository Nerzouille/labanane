"""Step 2 — Keyword Refinement (derivation stub)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepResultMessage, ServerMessage

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput


class KeywordRefinementStep(Step):
    @property
    def step_id(self) -> str:
        return "keyword_refinement"

    @property
    def label(self) -> str:
        return "Keyword Refinement"

    @property
    def step_type(self) -> str:
        return "derivation"

    @property
    def component_type(self) -> str:
        return "keyword_list"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        # TODO: generate real keywords from run.description using LLM
        description = run.description or "product"
        words = description.split()[:2]
        keywords = [
            " ".join(words),
            " ".join(words) + " online",
            " ".join(words) + " market",
        ]
        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={"keywords": keywords},
        )
