"""Step 8 — Persona Generation (OpenHosta LLM, 3 buyer personas)."""
from __future__ import annotations
from typing import TYPE_CHECKING, AsyncGenerator, Any
from ..step_base import Step, StepError
from ..messages import StepProcessingMessage, StepResultMessage, ServerMessage
from src.logic.persona import generate_personas

if TYPE_CHECKING:
    from ..run import WorkflowRun, StepOutput


class PersonaGenerationStep(Step):
    @property
    def step_id(self) -> str:
        return "persona_generation"

    @property
    def label(self) -> str:
        return "Persona Generation"

    @property
    def step_type(self) -> str:
        return "system_processing"

    @property
    def component_type(self) -> str:
        return "persona_generation"

    async def execute(
        self, input: "StepOutput | None", run: "WorkflowRun"
    ) -> AsyncGenerator[ServerMessage, Any]:
        yield StepProcessingMessage(step_id=self.step_id)

        products: list[dict] = run.get_output("product_research").get("products", [])
        ai_result: dict = run.get_output("ai_analysis")

        if not products and not ai_result:
            raise StepError(
                "Cannot generate personas: no product or analysis data available.",
                retryable=False,
            )

        result = await generate_personas(run.description, products, ai_result)

        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data=result.model_dump(),
        )
