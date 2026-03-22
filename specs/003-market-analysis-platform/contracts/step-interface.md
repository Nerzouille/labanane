# Contract: Step Interface & Architecture Layers

**Feature**: 003-market-analysis-platform
**Status**: Active
**Supersedes**: 002-guided-analysis-workflow/contracts/step-interface.md

---

## Three-Layer Architecture (FR-028/029)

```
┌─────────────────────────────────────────────┐
│  ENGINE LAYER  backend/src/workflow/engine.py│
│  Orchestration only. No business logic.      │
│  Drives WorkflowRun through PIPELINE.        │
└────────────────────┬────────────────────────┘
                     │ calls step.execute(input, run)
┌────────────────────▼────────────────────────┐
│  STEP LAYER  backend/src/workflow/steps/     │
│  Wiring only. Declares identity + contracts. │
│  Delegates ALL computation to logic layer.   │
└────────────────────┬────────────────────────┘
                     │ calls logic functions
┌────────────────────▼────────────────────────┐
│  LOGIC LAYER  backend/src/logic/             │
│  Pure async functions. No workflow state.    │
│  No WebSocket. Independently testable.       │
│  logic/scraper.py · logic/trends.py          │
│  logic/analysis.py · logic/export.py         │
└─────────────────────────────────────────────┘
```

**Rule**: A change to a business logic function MUST NOT require any modification to engine.py or any step file other than its direct caller.

---

## Abstract Step class

```python
# backend/src/workflow/step_base.py

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Any
from src.workflow.messages import ServerMessage
from src.workflow.run import WorkflowRun, StepOutput

class StepError(Exception):
    def __init__(self, message: str, retryable: bool = True):
        super().__init__(message)
        self.retryable = retryable

class Step(ABC):
    """
    Base class for all workflow steps.

    Steps MUST:
    - Have a unique step_id across the pipeline
    - Declare step_type and component_type
    - Implement execute() as an async generator yielding ServerMessage objects
    - Delegate ALL domain computation to backend/src/logic/ functions

    Steps MUST NOT:
    - Contain scraping logic, LLM calls, or data transformation inline
    - Access the WebSocket connection directly
    - Persist state between runs (WorkflowRun holds all run state)
    - Communicate with each other directly
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
        """One of: 'user_input', 'system_processing', 'confirmation', 'derivation'"""
        ...

    @property
    @abstractmethod
    def component_type(self) -> str:
        """Frontend component key. Maps to COMPONENTS in StepRenderer.svelte."""
        ...

    @abstractmethod
    async def execute(
        self,
        input: StepOutput | None,
        run: WorkflowRun,
    ) -> AsyncGenerator[ServerMessage, Any]:
        """
        Execute this step.

        - Must yield at least one ServerMessage.
        - system_processing steps: yield step_processing first, then step_result.
        - confirmation steps: yield confirmation_request; engine handles the pause.
        - On failure: raise StepError(message, retryable=True|False).

        Cross-step data access:
        - Use run.get_output("step_id") to read any prior confirmed step output.
        - Returns {} if that step has no confirmed output — safe for optional reads.
        - Do NOT access run.confirmed_outputs directly.
        """
        ...
        yield  # satisfy type checker
```

---

## WorkflowRun (updated)

```python
# backend/src/workflow/run.py

@dataclass
class WorkflowRun:
    run_id: str
    total_steps: int
    description: str = ""
    status: WorkflowStatus = WorkflowStatus.idle
    current_step_index: int = 0
    confirmed_outputs: dict[str, StepOutput] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def get_output(self, step_id: str) -> dict:
        """
        Returns the confirmed data dict for the given step_id.
        Returns {} if the step has no confirmed output.
        MUST be the sole way for steps to read prior confirmed outputs.
        """
        out = self.confirmed_outputs.get(step_id)
        return out.data if out else {}
```

---

## StepType values

| Value | Description | Steps |
|---|---|---|
| `user_input` | Waits for user text | Step 1 — Product Description |
| `system_processing` | Runs automatically, shows progress indicator | Steps 4, 6, 7 |
| `confirmation` | Waits for Yes/No | Steps 3, 5 |
| `derivation` | Transforms data deterministically, no user interaction | Steps 2, 8, 9 |

---

## Logic layer contracts

### `logic/scraper.py`

```python
async def fetch_html(source: str, query: str) -> str:
    """Fetch raw HTML from marketplace. Handles rate-limit with silent retry."""
    ...

async def parse_marketplace_data(cleaned_html: str) -> list[Product]:
    """Extract structured Product list from cleaned HTML via LLM."""
    ...

def clean_html_for_llm(raw_html: str) -> str:
    """Strip noise, inject href text. Pure function."""
    ...
```

### `logic/trends.py`

```python
async def fetch_trends(keywords: list[str]) -> TrendsData:
    """
    Fetch Google Trends data for the given keywords.
    Returns TrendsData with interest_over_time, interest_by_region,
    related_queries_top, related_queries_rising per keyword.
    Handles pytrends rate-limit with backoff.
    """
    ...

@dataclass
class TrendsData:
    keywords: list[str]
    interest_over_time: dict[str, list[TimePoint]]   # keyword → [{date, value}]
    interest_by_region: dict[str, list[RegionPoint]] # keyword → [{geo, name, value}]
    related_queries_top: dict[str, list[QueryPoint]] # keyword → [{query, value}]
    related_queries_rising: dict[str, list[RisingPoint]] # keyword → [{query, value}]
```

### `logic/analysis.py`

```python
async def generate_search_queries(description: str) -> list[str]:
    """Generate 3 marketplace search keywords via LLM."""
    ...

async def generate_market_analysis(
    description: str,
    products: list[dict],
    trends: dict,
) -> MarketAnalysis:
    """Generate full market analysis via LLM. Returns structured MarketAnalysis."""
    ...
```

### `logic/export.py`

```python
def render_markdown(run_data: dict) -> str:
    """Render a completed WorkflowRun into the stable MD export schema."""
    ...

def render_pdf(markdown: str) -> bytes:
    """Convert markdown string to PDF bytes via weasyprint."""
    ...
```

---

## Pipeline assembly (registry.py — unchanged shape)

```python
# backend/src/workflow/registry.py

PIPELINE: list[Step] = [
    ProductDescriptionStep(),    # step 1 — user_input
    KeywordRefinementStep(),     # step 2 — derivation
    KeywordConfirmationStep(),   # step 3 — confirmation
    ProductResearchStep(),       # step 4 — system_processing
    ProductValidationStep(),     # step 5 — confirmation
    MarketResearchStep(),        # step 6 — system_processing
    AiAnalysisStep(),            # step 7 — system_processing
    FinalCriteriaStep(),         # step 8 — derivation
    ReportGenerationStep(),      # step 9 — derivation
]
```

---

## Example: step reading prior outputs

```python
# backend/src/workflow/steps/s07_ai_analysis.py

class AiAnalysisStep(Step):
    async def execute(self, input, run):
        yield StepProcessingMessage(step_id=self.step_id)

        # Read outputs from non-adjacent prior steps via sanctioned method
        keywords   = run.get_output("keyword_confirmation").get("keywords", [])
        products   = run.get_output("product_validation").get("products", [])
        market     = input.data if input else {}  # direct predecessor (step 6)

        result = await generate_market_analysis(
            description=run.description,
            products=products,
            trends=market.get("trends", {}),
        )
        yield StepResultMessage(
            step_id=self.step_id,
            component_type="ai_analysis",
            data=result.model_dump(),
        )
```
