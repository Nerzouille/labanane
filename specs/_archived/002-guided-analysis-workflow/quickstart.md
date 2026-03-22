# Quickstart: Guided Analysis Workflow

**Feature**: 002-guided-analysis-workflow
**Date**: 2026-03-21

Integration scenarios for TDD. These describe the observable behavior at the WebSocket boundary — use these to write tests before implementing.

---

## Scenario 1: Happy path — full 9-step run (no loops)

**Setup**: Connect to `ws://localhost:8000/ws/workflow`

**Sequence**:
```
CLIENT: {"type": "start", "description": "ergonomic desk mats for remote workers"}

SERVER: {"type": "workflow_started", "total_steps": 9, "step_ids": [...]}
SERVER: {"type": "step_activated", "step_id": "product_description", "step_number": 1, ...}
SERVER: {"type": "step_result", "step_id": "product_description", "component_type": "product_description_input", "data": {...}}
SERVER: {"type": "step_activated", "step_id": "keyword_refinement", "step_number": 2, ...}
SERVER: {"type": "step_result", "step_id": "keyword_refinement", "component_type": "keyword_list", "data": {"keywords": ["ergonomic desk mat", "office accessories", "wrist rest"]}}
SERVER: {"type": "step_activated", "step_id": "keyword_confirmation", "step_number": 3, ...}
SERVER: {"type": "confirmation_request", "step_id": "keyword_confirmation", ...}

CLIENT: {"type": "confirmation", "step_id": "keyword_confirmation", "confirmed": true}

SERVER: {"type": "step_activated", "step_id": "product_research", "step_number": 4, ...}
SERVER: {"type": "step_processing", "step_id": "product_research"}
SERVER: {"type": "step_result", "step_id": "product_research", "component_type": "product_list", "data": {"products": [...]}}
SERVER: {"type": "step_activated", "step_id": "product_validation", "step_number": 5, ...}
SERVER: {"type": "confirmation_request", "step_id": "product_validation", ...}

CLIENT: {"type": "confirmation", "step_id": "product_validation", "confirmed": true}

SERVER: {"type": "step_activated", "step_id": "market_research", "step_number": 6, ...}
SERVER: {"type": "step_processing", "step_id": "market_research"}
SERVER: {"type": "step_result", "step_id": "market_research", ...}
SERVER: {"type": "step_activated", "step_id": "ai_analysis", "step_number": 7, ...}
SERVER: {"type": "step_processing", "step_id": "ai_analysis"}
SERVER: {"type": "step_streaming_token", "step_id": "ai_analysis", "token": "The"}
SERVER: {"type": "step_streaming_token", "step_id": "ai_analysis", "token": " market"}
... (more tokens)
SERVER: {"type": "step_result", "step_id": "ai_analysis", "component_type": "analysis_stream", "data": {"complete": true, "content": "..."}}
SERVER: {"type": "step_activated", "step_id": "final_criteria", "step_number": 8, ...}
SERVER: {"type": "step_result", "step_id": "final_criteria", "component_type": "final_criteria", "data": {...}}
SERVER: {"type": "step_activated", "step_id": "report_generation", "step_number": 9, ...}
SERVER: {"type": "step_result", "step_id": "report_generation", "component_type": "report", "data": {"run_id": "...", "markdown_available": true}}
SERVER: {"type": "workflow_complete", "run_id": "..."}
```

**Test assertions**:
- `workflow_started` is the first message after `start`
- `step_activated` is sent before each step
- `step_number` increments 1→9
- `confirmation_request` is sent at steps 3 and 5
- After `confirmed: true`, engine advances to next step
- `workflow_complete` is the last message

---

## Scenario 2: Keyword refinement loop (reject at step 3)

```
CLIENT: {"type": "start", "description": "coffee gadgets"}

SERVER: ... (steps 1–2 as above)
SERVER: {"type": "confirmation_request", "step_id": "keyword_confirmation", ...}

CLIENT: {"type": "confirmation", "step_id": "keyword_confirmation", "confirmed": false}

SERVER: {"type": "step_activated", "step_id": "product_description", "step_number": 1, "total_steps": 9, ...}
```

**Test assertions**:
- After `confirmed: false` at `keyword_confirmation`, next message is `step_activated` with `step_id: "product_description"` and `step_number: 1`
- `total_steps` remains 9 (no change)
- Prior keyword suggestions are not re-sent until new input arrives

---

## Scenario 3: Product validation loop (reject at step 5)

```
(... steps 1–4 complete, user rejects at step 5)

CLIENT: {"type": "confirmation", "step_id": "product_validation", "confirmed": false}

SERVER: {"type": "step_activated", "step_id": "product_research", "step_number": 4, "total_steps": 9, ...}
SERVER: {"type": "step_processing", "step_id": "product_research"}
SERVER: {"type": "step_result", "step_id": "product_research", "component_type": "product_list", "data": {"products": [...]}}
```

**Test assertions**:
- After `confirmed: false` at `product_validation`, engine loops to `product_research`
- New `step_activated` with `step_id: "product_research"` is sent
- Previously confirmed keywords from step 3 are still used (not lost)

---

## Scenario 4: Step error and retry

```
(... step 3 confirmed, engine starts step 4)

SERVER: {"type": "step_activated", "step_id": "product_research", ...}
SERVER: {"type": "step_processing", "step_id": "product_research"}
SERVER: {"type": "step_error", "step_id": "product_research", "error": "Source unavailable", "retryable": true}

CLIENT: {"type": "retry", "step_id": "product_research"}

SERVER: {"type": "step_activated", "step_id": "product_research", "step_number": 4, ...}
SERVER: {"type": "step_processing", "step_id": "product_research"}
SERVER: {"type": "step_result", ...}
```

**Test assertions**:
- After `step_error` with `retryable: true`, engine waits for `retry` message
- After `retry`, step re-executes with same input (confirmed keywords still intact)
- `step_number` is the same as the failed attempt

---

## Scenario 5: Invalid start message (empty description)

```
CLIENT: {"type": "start", "description": "   "}

SERVER: {"type": "step_error", "step_id": "product_description", "error": "Description cannot be empty", "retryable": false}
```

**Test assertions**:
- No `workflow_started` is sent
- `step_error` with `retryable: false` indicates the user must send a valid `user_input`

---

## Backend test integration points

```python
# backend/src/tests/test_ws_contract.py

# 1. Connect and send start → assert workflow_started received
# 2. Assert step_activated for each step 1–9
# 3. Assert confirmation_request at steps 3 and 5
# 4. Assert engine loops back on confirmed=false
# 5. Assert step_error on step failure; assert engine resumes on retry
# 6. Assert workflow_complete after step 9

# Use FastAPI TestClient with websocket_connect()
# Use asyncio.Queue to feed client messages in test
```

## Running the workflow locally

```bash
# Start backend
cd backend
uv run uvicorn src.main:app --reload --port 8000

# Test WebSocket directly
# Use wscat or browser DevTools → ws://localhost:8000/ws/workflow

# Run tests
cd backend
uv run pytest src/tests/test_ws_contract.py -v
```
