"""Abstract Step base class — every workflow step implements this interface.

Frozen contract per contracts/step-interface.md.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, AsyncGenerator, Any

from .messages import ServerMessage

if TYPE_CHECKING:
    from .run import WorkflowRun, StepOutput


class StepError(Exception):
    """Raised by Step.execute() to signal a step failure."""

    def __init__(self, message: str, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


class Step(ABC):
    """Base class for all workflow steps.

    Each step is a self-contained module with:
    - A unique step_id
    - A declared step_type (user_input | system_processing | confirmation | derivation)
    - A component_type that maps to a Svelte component
    - An execute() async generator that yields ServerMessage objects
    """

    @property
    @abstractmethod
    def step_id(self) -> str:
        """Unique slug. Example: 'keyword_refinement'"""
        ...

    @property
    @abstractmethod
    def label(self) -> str:
        """Human-readable name. Example: 'Keyword Refinement'"""
        ...

    @property
    @abstractmethod
    def step_type(self) -> str:
        """One of: 'user_input', 'system_processing', 'confirmation', 'derivation'"""
        ...

    @property
    @abstractmethod
    def component_type(self) -> str:
        """Frontend component identifier. Maps to COMPONENTS map in StepRenderer.svelte."""
        ...

    @abstractmethod
    async def execute(
        self,
        input: "StepOutput | None",
        run: "WorkflowRun",
    ) -> AsyncGenerator[ServerMessage, Any]:
        """Execute this step and yield server messages.

        - Must yield at least one ServerMessage.
        - System steps yield step_processing before long ops.
        - Confirmation steps yield confirmation_request (engine handles the pause).
        - Raise StepError on failure.
        """
        ...
        yield  # make type checker happy
