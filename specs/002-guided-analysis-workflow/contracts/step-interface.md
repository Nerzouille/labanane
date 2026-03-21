# Contract: Step Interface

**Feature**: 002-guided-analysis-workflow
**Status**: Frozen

This is the shared interface that every workflow step MUST implement. The `WorkflowEngine` only interacts with steps through this interface — it has no knowledge of step-specific logic.

---

## Abstract Step class

```python
# backend/src/workflow/step_base.py

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any
from src.workflow.messages import ServerMessage, StepOutput

class Step(ABC):
    """
    Base class for all workflow steps.

    Every step MUST:
    1. Have a unique `step_id` across the pipeline
    2. Declare its `step_type` and `component_type`
    3. Implement `execute()` as an async generator yielding ServerMessage objects
    4. Accept the previous step's StepOutput (or None for step 1) as input

    Steps MUST NOT:
    - Persist state between runs (use WorkflowRun for state)
    - Communicate with each other directly
    - Access the WebSocket connection directly
    """

    @property
    @abstractmethod
    def step_id(self) -> str:
        """Unique slug. Example: 'keyword_refinement'"""
        ...

    @property
    @abstractmethod
    def label(self) -> str:
        """Human-readable display name. Example: 'Keyword Refinement'"""
        ...

    @property
    @abstractmethod
    def step_type(self) -> str:
        """One of: 'user_input', 'system_processing', 'confirmation'"""
        ...

    @property
    @abstractmethod
    def component_type(self) -> str:
        """
        Frontend component identifier.
        Maps to a key in StepRenderer.svelte's COMPONENTS map.
        Example: 'keyword_list'
        """
        ...

    @abstractmethod
    async def execute(
        self,
        input: StepOutput | None,
        run: "WorkflowRun",
    ) -> AsyncGenerator[ServerMessage, None]:
        """
        Execute this step's logic.

        - Must yield at least one ServerMessage.
        - System steps should yield `step_processing` before long operations.
        - Confirmation steps should yield `confirmation_request` and then wait
          (the engine pauses execution until a confirmation message arrives).
        - On unrecoverable failure, raise StepError(message, retryable=True|False).
        - The engine wraps exceptions into `step_error` messages automatically.

        Args:
            input: Output of the previous step, or None for the first step.
            run: The current WorkflowRun for accessing confirmed outputs.

        Yields:
            ServerMessage objects (step_processing, step_streaming_token,
            step_result, confirmation_request).
        """
        ...
```

---

## StepType values

| Value | Description | Example steps |
|---|---|---|
| `user_input` | Waits for user to provide text | Step 1 (product description) |
| `system_processing` | Runs automatically, shows progress indicator | Steps 4, 6, 7 |
| `confirmation` | Presents results and waits for Yes/No | Steps 3, 5 |
| `derivation` | Transforms data deterministically, no user input | Steps 2, 8, 9 |

---

## StepError

Raised by `execute()` to signal a recoverable or unrecoverable failure.

```python
class StepError(Exception):
    def __init__(self, message: str, retryable: bool = True):
        super().__init__(message)
        self.retryable = retryable
```

The `WorkflowEngine` catches `StepError` and converts it to a `step_error` WebSocket message. It does NOT re-raise; the run status is set to `error` and the engine awaits a `retry` message (if `retryable=True`).

---

## Pipeline assembly contract (`registry.py`)

```python
# backend/src/workflow/registry.py

from src.workflow.steps.s01_description import ProductDescriptionStep
from src.workflow.steps.s02_keyword_refinement import KeywordRefinementStep
# ... (all 9 imports)

PIPELINE: list[Step] = [
    ProductDescriptionStep(),
    KeywordRefinementStep(),
    KeywordConfirmationStep(),
    ProductResearchStep(),
    ProductValidationStep(),
    MarketResearchStep(),
    AiAnalysisStep(),
    FinalCriteriaStep(),
    ReportGenerationStep(),
]
```

**Rules**:
- `PIPELINE` is the single source of truth for step order and total count.
- Inserting a step = add the import + insert the instance at the desired index.
- The `WorkflowEngine` reads `len(PIPELINE)` at run start for `total_steps`.
- No step ID may appear twice in `PIPELINE`.

---

## WorkflowEngine contract

```python
class WorkflowEngine:
    """
    Drives a WorkflowRun through the PIPELINE.

    Responsibilities:
    - Iterate through PIPELINE steps in order
    - Pipe each step's output as the next step's input
    - Send step_activated before each step
    - Handle loop-backs (set current_step_index to loop target)
    - Handle confirmation gates (pause until confirmation message)
    - Handle step errors (set run.status = 'error', wait for retry or close)
    - Send workflow_complete after the last step

    The engine is stateless between runs.
    Each WorkflowRun holds all run-specific state.
    """

    async def run(
        self,
        run: WorkflowRun,
        ws: WebSocket,
        incoming: asyncio.Queue,  # client messages arrive here
    ) -> None: ...
```

---

## Input/output flow example

```
PIPELINE[0].execute(input=None, run) → yields step_result with ProductDescription data
    └─ StepOutput(step_id="product_description", data={"text": "desk mats"})

PIPELINE[1].execute(input=StepOutput(product_description), run) → yields step_result with KeywordSet
    └─ StepOutput(step_id="keyword_refinement", data={"keywords": [...]})

PIPELINE[2].execute(input=StepOutput(keyword_refinement), run) → yields confirmation_request
    Engine pauses. Client sends confirmation(confirmed=True).
    └─ StepOutput(step_id="keyword_confirmation", data={"keywords": [...]}, confirmed=True)

PIPELINE[3].execute(input=StepOutput(keyword_confirmation), run) → yields step_processing, then step_result
    ...
```
