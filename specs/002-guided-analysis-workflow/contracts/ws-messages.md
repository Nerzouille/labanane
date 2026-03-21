# Contract: WebSocket Message Protocol

**Feature**: 002-guided-analysis-workflow
**Status**: Frozen
**Transport**: WebSocket — `ws://localhost:8000/ws/workflow`

This contract is the source of truth for the bidirectional WebSocket message format between browser and FastAPI. Both Pydantic models (backend) and Zod schemas (frontend) MUST be derived from this document.

---

## Connection lifecycle

1. Browser opens WebSocket to `ws://localhost:8000/ws/workflow`
2. Server assigns a `run_id` (UUID) and waits
3. Browser sends `start` with a product description
4. Server sends `workflow_started`, then begins executing steps
5. For each step: `step_activated` → (processing messages) → `step_result` or `confirmation_request`
6. For confirmation steps: browser sends `confirmation`; server resumes or loops back
7. After step 9: server sends `workflow_complete`
8. Browser closes the connection

**Error recovery**: If a system step fails, server sends `step_error`. Browser may send `retry` for the same `step_id`. Server re-executes that step with the same input (prior confirmed outputs intact).

---

## Server → Client Messages

All server messages are JSON objects with a `type` discriminator.

### `workflow_started`

Sent immediately after `start` is received. Signals the workflow is beginning.

```json
{
  "type": "workflow_started",
  "total_steps": 9,
  "step_ids": [
    "product_description",
    "keyword_refinement",
    "keyword_confirmation",
    "product_research",
    "product_validation",
    "market_research",
    "ai_analysis",
    "final_criteria",
    "report_generation"
  ]
}
```

---

### `step_activated`

Sent when the engine advances to a new step. Used to update the progress indicator.

```json
{
  "type": "step_activated",
  "step_id": "keyword_refinement",
  "step_number": 2,
  "total_steps": 9,
  "label": "Keyword Refinement"
}
```

---

### `step_processing`

Sent at the start of any system-processing step (product research, market research, AI analysis). Shows the inline progress indicator.

```json
{
  "type": "step_processing",
  "step_id": "product_research"
}
```

---

### `step_streaming_token`

Sent for each LLM token during AI analysis (step 7). Multiple tokens are sent for a single step.

```json
{
  "type": "step_streaming_token",
  "step_id": "ai_analysis",
  "token": " saturated"
}
```

---

### `step_result`

Sent when a non-confirmation step completes. The `component_type` field tells the frontend which Svelte component to mount. The `data` field is the component's props payload.

```json
{
  "type": "step_result",
  "step_id": "keyword_refinement",
  "component_type": "keyword_list",
  "data": {
    "keywords": ["ergonomic desk mat", "office desk accessories", "wrist rest pad"]
  }
}
```

**`component_type` → `data` shape mapping**:

| `component_type` | `data` fields |
|---|---|
| `keyword_list` | `{ keywords: string[] }` |
| `product_list` | `{ products: Product[] }` |
| `market_data_summary` | `{ sources_available: string[], sources_unavailable: string[], trend_summary: string, sentiment_summary: string }` |
| `analysis_stream` | `{ complete: boolean, content: string }` (final, after streaming) |
| `final_criteria` | `{ summary: string, go_no_go: "go"|"no-go"|"conditional", key_risks: string[], key_opportunities: string[] }` |
| `report` | `{ run_id: string, markdown_available: boolean }` |

Where `Product` is:
```json
{ "title": "string", "price": "string", "url": "string" }
```

---

### `confirmation_request`

Sent at confirmation gates (steps 3 and 5). Uses a single `"confirmation"` component type — the data to confirm (keywords, products) is already displayed by the preceding step's component. The gate only needs to present a prompt and Yes/No buttons.

```json
{
  "type": "confirmation_request",
  "step_id": "keyword_confirmation",
  "component_type": "confirmation",
  "data": {
    "prompt": "Do these keywords look correct for your product idea?"
  }
}
```

Step 5 (product validation) follows the same shape:
```json
{
  "type": "confirmation_request",
  "step_id": "product_validation",
  "component_type": "confirmation",
  "data": {
    "prompt": "Are these products relevant to your market?"
  }
}
```

---

### `step_error`

Sent when a step fails. `retryable: true` means the browser may send a `retry` message.

```json
{
  "type": "step_error",
  "step_id": "product_research",
  "error": "One or more data sources are unavailable. Results may be partial.",
  "retryable": true
}
```

---

### `workflow_complete`

Sent after step 9 completes successfully.

```json
{
  "type": "workflow_complete",
  "run_id": "a1b2c3d4-..."
}
```

---

## Client → Server Messages

All client messages are JSON objects with a `type` discriminator.

### `start`

Initiates the workflow run. The description must be non-empty.

```json
{ "type": "start", "description": "I want to sell ergonomic desk mats online" }
```

**Validation**: `description` must be a non-empty, non-whitespace-only string. Server sends `step_error` on invalid input.

---

### `confirmation`

Sent in response to a `confirmation_request`. `confirmed: true` advances the workflow; `confirmed: false` triggers a loop-back.

```json
{ "type": "confirmation", "step_id": "keyword_confirmation", "confirmed": true }
```

```json
{ "type": "confirmation", "step_id": "product_validation", "confirmed": false }
```

Loop-back targets:
- `keyword_confirmation` rejected → resets to `product_description` (step 1)
- `product_validation` rejected → re-runs `product_research` (step 4)

---

### `retry`

Sent to re-execute a failed step. Step re-runs with the same input as the previous attempt.

```json
{ "type": "retry", "step_id": "product_research" }
```

---

### `user_input`

Sent for steps that require user text input (e.g., revised product description after loop-back).

```json
{
  "type": "user_input",
  "step_id": "product_description",
  "data": { "description": "I want to sell standing desk converters for home offices" }
}
```

---

## Error handling rules

1. Unknown `type` values: server ignores silently; browser logs a warning.
2. Malformed JSON: connection is kept open; a `step_error` with `retryable: false` is sent.
3. Description empty/whitespace: server sends `step_error` on `product_description` step with `retryable: false`; user must send valid `user_input`.
4. Product research returns zero results: server automatically loops back to `product_description` and sends `step_error` with message "No products found — please refine your description."
