"""WorkflowRun — tracks a single execution instance."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class WorkflowStatus(str, Enum):
    idle = "idle"
    running = "running"
    awaiting_confirmation = "awaiting_confirmation"
    awaiting_input = "awaiting_input"
    complete = "complete"
    error = "error"


@dataclass
class StepOutput:
    step_id: str
    data: dict
    confirmed: bool = True


@dataclass
class WorkflowRun:
    run_id: str
    total_steps: int
    description: str = ""
    status: WorkflowStatus = WorkflowStatus.idle
    current_step_index: int = 0
    confirmed_outputs: dict[str, StepOutput] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
