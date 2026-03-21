"""Step 9 — Report Generation (derivation stub)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step
from ..messages import StepResultMessage, ServerMessage

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
        # TODO: generate real Markdown + PDF report
        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data={
                "run_id": run.run_id,
                "markdown_available": False,
                "note": "Report stub — not yet implemented.",
            },
        )
