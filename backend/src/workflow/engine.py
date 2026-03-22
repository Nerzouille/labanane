"""WorkflowEngine — drives a WorkflowRun through the PIPELINE.

Architecture-only implementation. Steps are stubs; business logic lives in steps/.
"""
from __future__ import annotations
import asyncio
from fastapi import WebSocket

from .messages import (
    WorkflowStartedMessage,
    StepActivatedMessage,
    StepErrorMessage,
    WorkflowCompleteMessage,
)
from .run import WorkflowRun, WorkflowStatus, StepOutput
from .step_base import Step, StepError

# step_id → step_id to loop back to on rejection (confirmation steps)
LOOP_TARGETS: dict[str, str] = {
    "keyword_confirmation": "product_description",
    "product_validation": "product_research",
}

# step_id → step_id to loop back to on non-retryable StepError
ERROR_LOOP_TARGETS: dict[str, str] = {
    "product_research": "product_description",
}


class WorkflowEngine:
    """Drives a WorkflowRun through an ordered list of steps.

    Responsibilities:
    - Iterate pipeline steps in order
    - Pipe each step's output as the next step's input
    - Send step_activated before each step
    - Handle confirmation pauses (awaiting_confirmation state)
    - Handle user_input pauses on loop-back (awaiting_input state)
    - Handle loop-backs by resetting current_step_index
    - Handle step errors (scoped, retryable)
    - Send workflow_complete after the last step
    """

    def __init__(self, pipeline: list[Step]) -> None:
        self.pipeline = pipeline

    def _step_index(self, step_id: str) -> int:
        return next(i for i, s in enumerate(self.pipeline) if s.step_id == step_id)

    def _prev_output(self, run: WorkflowRun) -> StepOutput | None:
        if run.current_step_index == 0:
            return None
        prev_step = self.pipeline[run.current_step_index - 1]
        return run.confirmed_outputs.get(prev_step.step_id)

    async def run(
        self,
        run: WorkflowRun,
        ws: WebSocket,
        incoming: asyncio.Queue,
    ) -> None:
        run.status = WorkflowStatus.running
        run.total_steps = len(self.pipeline)

        await ws.send_json(
            WorkflowStartedMessage(
                total_steps=run.total_steps,
                step_ids=[s.step_id for s in self.pipeline],
            ).model_dump()
        )

        while run.current_step_index < len(self.pipeline):
            step = self.pipeline[run.current_step_index]
            prev_output = self._prev_output(run)

            await ws.send_json(
                StepActivatedMessage(
                    step_id=step.step_id,
                    step_number=run.current_step_index + 1,
                    total_steps=run.total_steps,
                    label=step.label,
                ).model_dump()
            )

            # For user_input steps on a loop-back, wait for fresh input
            if step.step_type == "user_input" and step.step_id in run.confirmed_outputs:
                run.status = WorkflowStatus.awaiting_input
                while True:
                    client_msg = await incoming.get()
                    if (
                        client_msg.get("type") == "user_input"
                        and client_msg.get("step_id") == step.step_id
                    ):
                        run.description = client_msg.get("data", {}).get(
                            "description", run.description
                        )
                        run.status = WorkflowStatus.running
                        break

            loop_back_step_id: str | None = None
            step_result_data: dict = {}

            try:
                async for msg in step.execute(prev_output, run):
                    msg_dict = msg.model_dump()
                    await ws.send_json(msg_dict)

                    if msg_dict.get("type") == "confirmation_request":
                        run.status = WorkflowStatus.awaiting_confirmation
                        client_msg = await incoming.get()
                        run.status = WorkflowStatus.running

                        if (
                            client_msg.get("type") == "confirmation"
                            and not client_msg.get("confirmed", True)
                        ):
                            loop_back_step_id = LOOP_TARGETS.get(step.step_id)

                    elif msg_dict.get("type") == "step_result":
                        step_result_data = msg_dict.get("data", {})

            except StepError as exc:
                await ws.send_json(
                    StepErrorMessage(
                        step_id=step.step_id,
                        error=str(exc),
                        retryable=exc.retryable,
                    ).model_dump()
                )
                if not exc.retryable:
                    # Check if there's an automatic loop-back target for this error
                    error_loop_target = ERROR_LOOP_TARGETS.get(step.step_id)
                    if error_loop_target:
                        run.current_step_index = self._step_index(error_loop_target)
                        run.status = WorkflowStatus.running
                        continue
                    run.status = WorkflowStatus.error
                    return

                # Wait for retry
                run.status = WorkflowStatus.error
                while True:
                    client_msg = await incoming.get()
                    if (
                        client_msg.get("type") == "retry"
                        and client_msg.get("step_id") == step.step_id
                    ):
                        run.status = WorkflowStatus.running
                        break
                continue  # re-run same step

            except Exception as exc:
                await ws.send_json(
                    StepErrorMessage(
                        step_id=step.step_id,
                        error=str(exc),
                        retryable=False,
                    ).model_dump()
                )
                run.status = WorkflowStatus.error
                return

            if loop_back_step_id:
                run.current_step_index = self._step_index(loop_back_step_id)
            else:
                run.confirmed_outputs[step.step_id] = StepOutput(
                    step_id=step.step_id,
                    data=step_result_data,
                )
                run.current_step_index += 1

        run.status = WorkflowStatus.complete
        await ws.send_json(
            WorkflowCompleteMessage(run_id=run.run_id).model_dump()
        )
