"""Step 8 — Final Criteria (extracts verdict subset from AI analysis)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepResultMessage, ServerMessage

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput


class FinalCriteriaStep(Step):
    @property
    def step_id(self) -> str:
        return "final_criteria"

    @property
    def label(self) -> str:
        return "Final Criteria"

    @property
    def step_type(self) -> str:
        return "derivation"

    @property
    def component_type(self) -> str:
        return "final_criteria"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        ai = run.get_output("ai_analysis")
        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={
                "summary": ai.get("summary", "No analysis available."),
                "go_no_go": ai.get("go_no_go", "conditional"),
                "key_risks": ai.get("key_risks", []),
                "key_opportunities": ai.get("key_opportunities", []),
            },
        )
