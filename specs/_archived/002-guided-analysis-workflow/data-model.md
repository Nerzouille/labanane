# Data Model: Guided Analysis Workflow

**Feature**: 002-guided-analysis-workflow
**Date**: 2026-03-21

---

## Entities

### WorkflowRun

Tracks a single execution of the 9-step pipeline for one user session.

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | `str` (UUID) | Unique identifier, generated on WebSocket connect |
| `status` | `WorkflowStatus` | `idle \| running \| awaiting_confirmation \| complete \| error` |
| `current_step_index` | `int` | 0-based index into the pipeline list |
| `total_steps` | `int` | `len(PIPELINE)` at run start |
| `confirmed_outputs` | `dict[str, StepOutput]` | Keyed by `step_id`; stores confirmed results per step |
| `created_at` | `datetime` | UTC timestamp of connection open |

**State transitions**:
- Created on WS connect → `idle`
- `start` message received → `running`, `current_step_index = 0`
- System step executing → `running`
- Confirmation step reached → `awaiting_confirmation`
- Confirmation received (yes) → `running`, advance index
- Confirmation received (no, loop-back) → `running`, reset index to loop target
- Step 9 complete → `complete`
- Unrecoverable error → `error`

---

### Step (abstract)

Defines the contract every concrete step implements.

| Field/Method | Type | Description |
|---|---|---|
| `step_id` | `str` | Unique slug (e.g., `keyword_refinement`) |
| `label` | `str` | Display name shown in progress (e.g., `"Keyword Refinement"`) |
| `step_type` | `StepType` | `user_input \| system_processing \| confirmation` |
| `component_type` | `str` | Maps to a frontend Svelte component (see plan.md) |
| `execute(input, run)` | `AsyncGenerator[ServerMessage, None]` | Yields server messages; receives prior step's output as `input` |

**Validation rules**:
- `step_id` must be unique across all steps in the pipeline
- `execute()` must yield at least one message
- System-processing steps must yield `step_processing` before long operations

---

### StepOutput

The typed output produced by a completed step, passed as input to the next.

```python
class StepOutput(BaseModel):
    step_id: str
    data: dict  # step-specific payload
    confirmed: bool = True
```

---

### ProductDescription

Produced by Step 1.

| Field | Type | Validation |
|---|---|---|
| `text` | `str` | non-empty, not whitespace-only |

---

### KeywordSet

Produced by Step 2, confirmed at Step 3.

| Field | Type | Validation |
|---|---|---|
| `keywords` | `list[str]` | length 3–5; each keyword non-empty |
| `source_description` | `str` | The product description that generated these |

---

### ProductBatch

Produced by Step 4, confirmed at Step 5.

| Field | Type | Validation |
|---|---|---|
| `products` | `list[MarketplaceProduct]` | length ≥ 1 (empty triggers loop-back automatically) |
| `source_keywords` | `list[str]` | The keywords used for this research pass |

*`MarketplaceProduct` is defined in `backend/src/models/report.py`.*

---

### MarketData

Produced by Step 6.

| Field | Type | Description |
|---|---|---|
| `products` | `list[MarketplaceProduct]` | Confirmed products from Step 5 |
| `trend_data` | `dict` | Raw trend signals per keyword |
| `sentiment_data` | `dict` | Community sentiment signals |
| `sources_available` | `list[str]` | Which sources returned data |
| `sources_unavailable` | `list[str]` | Sources that timed out |

---

### AnalysisResult

Produced by Step 7.

| Field | Type | Description |
|---|---|---|
| `viability_score` | `ViabilityScore` | 0–100 score + explanation |
| `target_persona` | `TargetPersona` | Primary customer segment |
| `differentiation_angles` | `DifferentiationAngles` | Actionable differentiation |
| `competitive_overview` | `CompetitiveOverview` | Existing players summary |

*All sub-types (`ViabilityScore`, `TargetPersona`, `DifferentiationAngles`, `CompetitiveOverview`) are defined in `backend/src/models/report.py`.*

---

### FinalCriteria

Produced by Step 8.

| Field | Type | Description |
|---|---|---|
| `summary` | `str` | 2–4 sentence synthesis |
| `go_no_go` | `Literal["go", "no-go", "conditional"]` | Recommendation |
| `key_risks` | `list[str]` | Top 3–5 identified risks |
| `key_opportunities` | `list[str]` | Top 3–5 identified opportunities |

---

### Report

Produced by Step 9. Final artefact.

| Field | Type | Description |
|---|---|---|
| `run_id` | `str` | Associated WorkflowRun |
| `keyword` | `str` | Original product description |
| `analysis` | `AnalysisResult` | Full analysis output |
| `final_criteria` | `FinalCriteria` | Step 8 output |
| `products` | `list[MarketplaceProduct]` | Confirmed product batch |
| `markdown` | `str \| None` | Pre-rendered Markdown (populated at step 9) |

---

## WebSocket Message Models

### Server → Client

```python
class WorkflowStartedMessage(BaseModel):
    type: Literal["workflow_started"]
    total_steps: int
    step_ids: list[str]

class StepActivatedMessage(BaseModel):
    type: Literal["step_activated"]
    step_id: str
    step_number: int      # 1-based
    total_steps: int
    label: str

class StepProcessingMessage(BaseModel):
    type: Literal["step_processing"]
    step_id: str

class StepStreamingTokenMessage(BaseModel):
    type: Literal["step_streaming_token"]
    step_id: str
    token: str

class StepResultMessage(BaseModel):
    type: Literal["step_result"]
    step_id: str
    component_type: str
    data: dict

class ConfirmationRequestMessage(BaseModel):
    type: Literal["confirmation_request"]
    step_id: str
    component_type: str   # e.g. "keyword_confirmation"
    data: dict            # the content to display before asking

class StepErrorMessage(BaseModel):
    type: Literal["step_error"]
    step_id: str
    error: str
    retryable: bool = True

class WorkflowCompleteMessage(BaseModel):
    type: Literal["workflow_complete"]
    run_id: str
```

### Client → Server

```python
class StartMessage(BaseModel):
    type: Literal["start"]
    description: str      # must be non-empty

class ConfirmationMessage(BaseModel):
    type: Literal["confirmation"]
    step_id: str
    confirmed: bool

class RetryMessage(BaseModel):
    type: Literal["retry"]
    step_id: str

class UserInputMessage(BaseModel):
    type: Literal["user_input"]
    step_id: str
    data: dict
```

---

## Entity Relationships

```
WorkflowRun
  ├── confirmed_outputs[step_id] → StepOutput
  │     └── data (step-specific)
  └── current_step → Step
        └── execute() → yields ServerMessage*

Step 1 output → ProductDescription
Step 2 output → KeywordSet
Step 3 (confirmation) → confirmed KeywordSet
Step 4 output → ProductBatch
Step 5 (confirmation) → confirmed ProductBatch
Step 6 output → MarketData
Step 7 output → AnalysisResult
Step 8 output → FinalCriteria
Step 9 output → Report
```
