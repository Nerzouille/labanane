"""WebSocket message models — server→client and client→server.

Frozen contract per contracts/ws-messages.md.
"""
from __future__ import annotations
from typing import Literal, Any
from pydantic import BaseModel


# ── Server → Client ────────────────────────────────────────────────────────


class WorkflowStartedMessage(BaseModel):
    type: Literal["workflow_started"] = "workflow_started"
    total_steps: int
    step_ids: list[str]


class StepActivatedMessage(BaseModel):
    type: Literal["step_activated"] = "step_activated"
    step_id: str
    step_number: int  # 1-based
    total_steps: int
    label: str


class StepProcessingMessage(BaseModel):
    type: Literal["step_processing"] = "step_processing"
    step_id: str


class StepStreamingTokenMessage(BaseModel):
    type: Literal["step_streaming_token"] = "step_streaming_token"
    step_id: str
    token: str


class StepResultMessage(BaseModel):
    type: Literal["step_result"] = "step_result"
    step_id: str
    component_type: str
    data: dict[str, Any] = {}


class ConfirmationRequestMessage(BaseModel):
    type: Literal["confirmation_request"] = "confirmation_request"
    step_id: str
    component_type: str
    data: dict[str, Any] = {}


class StepErrorMessage(BaseModel):
    type: Literal["step_error"] = "step_error"
    step_id: str
    error: str
    retryable: bool = True


class WorkflowCompleteMessage(BaseModel):
    type: Literal["workflow_complete"] = "workflow_complete"
    run_id: str


ServerMessage = (
    WorkflowStartedMessage
    | StepActivatedMessage
    | StepProcessingMessage
    | StepStreamingTokenMessage
    | StepResultMessage
    | ConfirmationRequestMessage
    | StepErrorMessage
    | WorkflowCompleteMessage
)
