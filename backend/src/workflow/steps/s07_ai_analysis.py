"""Step 7 — AI Analysis (system_processing stub with streaming tokens)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import (
    StepProcessingMessage,
    StepStreamingTokenMessage,
    StepResultMessage,
    ServerMessage,
)

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput

_STUB_TOKENS = ["Stub ", "analysis ", "result. ", "Not ", "yet ", "implemented."]


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
        return "analysis_stream"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        yield StepProcessingMessage(step_id=self.step_id)
        # TODO: call real LLM analysis
        for token in _STUB_TOKENS:
            yield StepStreamingTokenMessage(step_id=self.step_id, token=token)
        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={
                "complete": True,
                "content": "".join(_STUB_TOKENS),
                "viability_score": None,
                "persona": None,
            },
        )
