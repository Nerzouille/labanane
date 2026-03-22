"""Step 2 — Keyword Refinement (LLM-powered via OpenHosta)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepProcessingMessage, StepResultMessage, ServerMessage
from src.logic.analysis import generate_search_queries

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
        yield StepProcessingMessage(step_id=self.step_id)
        keywords = await generate_search_queries(run.description)
        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={"keywords": keywords},
        )
