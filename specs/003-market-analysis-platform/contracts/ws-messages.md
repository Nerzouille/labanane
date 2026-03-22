# Contract: WebSocket Message Protocol

**Feature**: 003-market-analysis-platform
**Status**: Active
**Supersedes**: 002-guided-analysis-workflow/contracts/ws-messages.md
**Transport**: WebSocket — `ws://localhost:8000/ws/workflow`

This contract is the source of truth for the bidirectional WebSocket message format.
Both Pydantic models (backend) and Zod schemas (frontend) MUST be derived from this document.

---

## Connection lifecycle

1. Browser opens WebSocket to `ws://localhost:8000/ws/workflow`
2. Server assigns a `run_id` (UUID) and waits
3. Browser sends `start` with a product description
4. Server sends `workflow_started`, then begins executing steps
5. For each step: `step_activated` → `step_processing` (system steps only) → `step_result` or `confirmation_request`
6. For confirmation steps: browser sends `confirmation`; server advances or loops back
7. After step 9: server sends `workflow_complete`
8. Browser closes the connection

**Error recovery**: On step failure the server sends `step_error`. Browser may send `retry` for the same `step_id`. Server re-executes the step with the same input (prior confirmed outputs intact, including auto-retry for rate-limited sources per FR-012d).

**Disconnection**: Run state is discarded on WebSocket close. No reconnection support. Frontend MUST handle the `close` event and show "Connection lost — please start a new analysis."

---

## Removed from 002

- `step_streaming_token` — removed. No intra-step token streaming. Steps complete fully and emit one `step_result`.

---

## Server → Client Messages

All server messages are JSON objects with a `type` discriminator field.

### `workflow_started`

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

Sent when the engine advances to a new step.

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

Sent at the start of any `system_processing` step to trigger the progress indicator.

```json
{
  "type": "step_processing",
  "step_id": "product_research"
}
```

---

### `step_result`

Sent when a non-confirmation step completes. `component_type` maps to a Svelte component.
The `data` field is the component's complete props payload.

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

#### `component_type` → `data` shape reference

| `component_type` | Description | `data` shape |
|---|---|---|
| `keyword_list` | Suggested search keywords | `KeywordListData` |
| `product_list` | Marketplace products with ratings | `ProductListData` |
| `market_data` | Google Trends charts | `MarketDataResult` |
| `ai_analysis` | Full LLM market analysis | `AiAnalysisData` |
| `final_criteria` | Go/no-go verdict with charts | `FinalCriteriaData` |
| `report` | Export download links | `ReportData` |

---

#### `KeywordListData`

```json
{
  "keywords": ["string"]
}
```

---

#### `ProductListData`

```json
{
  "products": [
    {
      "title": "string",
      "price": "string",
      "url": "string",
      "rating_stars": 4.3,
      "rating_count": 1247,
      "main_features": ["string", "string", "string"]
    }
  ],
  "source_keywords": ["string"]
}
```

`rating_stars`: float 0–5. `rating_count`: int. `main_features`: exactly 3 strings.
These fields enable: rating comparison bar chart, review volume bar chart.

---

#### `MarketDataResult`

```json
{
  "keywords": ["ergonomic desk mat", "office desk accessories"],
  "sources_available": ["google_trends"],
  "sources_unavailable": [],
  "trends": {
    "ergonomic desk mat": {
      "interest_over_time": [
        { "date": "2025-03-01", "value": 72 },
        { "date": "2025-03-08", "value": 68 }
      ],
      "interest_by_region": [
        { "geo": "US", "name": "United States", "value": 100 },
        { "geo": "GB", "name": "United Kingdom", "value": 71 }
      ],
      "related_queries_top": [
        { "query": "desk mat large", "value": 100 },
        { "query": "gaming desk mat", "value": 87 }
      ],
      "related_queries_rising": [
        { "query": "ergonomic desk pad with wrist rest", "value": "+850%" }
      ]
    }
  }
}
```

`interest_over_time`: 52 weekly data points (past 12 months), values 0–100.
`interest_by_region`: top 10 countries, values 0–100 (relative to highest country = 100).
`related_queries_top`: top 10 stable queries, absolute values.
`related_queries_rising`: top 5 breakout queries, percent-change strings.

Charts enabled by this shape:
- Line chart: interest over time per keyword (multi-series)
- Horizontal bar chart: interest by country (top 10)
- Horizontal bar chart: related queries (top 10)
- Callout cards: breakout/rising queries

---

#### `AiAnalysisData`

```json
{
  "viability_score": 74,
  "go_no_go": "conditional",
  "summary": "Solid niche with moderate competition.",
  "analysis": "Demand is consistent year-round with a modest Q4 spike...",
  "key_risks": ["string"],
  "key_opportunities": ["string"],
  "criteria": [
    { "label": "Market size", "score": 80 },
    { "label": "Competition", "score": 55 },
    { "label": "Differentiation potential", "score": 70 }
  ],
  "target_persona": {
    "description": "Remote workers aged 28–45 setting up a home office..."
  },
  "differentiation_angles": {
    "content": "1. Bundle with cable management tray...\n2. Sustainable materials..."
  },
  "competitive_overview": {
    "content": "Top competitors include Logitech Desk Mat and Orbitkey..."
  }
}
```

`go_no_go`: one of `"go"`, `"no-go"`, `"conditional"`.
`criteria`: 3–5 items, each with `label` (str) and `score` (int 0–100). Enables scoring criteria bar chart.

---

#### `FinalCriteriaData`

```json
{
  "summary": "string",
  "go_no_go": "go",
  "key_risks": ["string"],
  "key_opportunities": ["string"]
}
```

---

#### `ReportData`

```json
{
  "run_id": "uuid-string",
  "markdown_available": true
}
```

Export downloads are served from REST endpoints (not WebSocket):
- `GET /api/export/{run_id}/markdown` → `text/markdown` download
- `GET /api/export/{run_id}/pdf` → `application/pdf` download

---

### `confirmation_request`

Sent at confirmation gates (steps 3 and 5). The preceding `step_result` already rendered the data to confirm; this message only provides the prompt text.

```json
{
  "type": "confirmation_request",
  "step_id": "keyword_confirmation",
  "component_type": "confirmation",
  "data": {
    "prompt": "Do these keywords look right for your product idea?"
  }
}
```

Step 5:
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

```json
{
  "type": "step_error",
  "step_id": "product_research",
  "error": "Amazon rate-limited — retrying...",
  "retryable": true
}
```

`retryable: true` → browser shows "Retry" button.
`retryable: false` → browser shows error only (workflow terminal unless engine loops back).

---

### `workflow_complete`

```json
{
  "type": "workflow_complete",
  "run_id": "a1b2c3d4-..."
}
```

---

## Client → Server Messages

### `start`

```json
{ "type": "start", "description": "I want to sell ergonomic desk mats online" }
```

`description` must be non-empty, non-whitespace. Server sends `step_error(retryable: false)` on invalid input.

---

### `confirmation`

```json
{ "type": "confirmation", "step_id": "keyword_confirmation", "confirmed": true }
```

Loop-back targets:
- `keyword_confirmation` rejected → resets to `product_description` (step 1)
- `product_validation` rejected → re-runs `product_research` (step 4)

---

### `retry`

```json
{ "type": "retry", "step_id": "product_research" }
```

---

### `user_input`

Sent for the product description step on loop-back.

```json
{
  "type": "user_input",
  "step_id": "product_description",
  "data": { "description": "I want to sell standing desk converters for home offices" }
}
```

---

## Error handling rules

1. Unknown `type`: server ignores silently; browser logs warning.
2. Malformed JSON: server sends `step_error(retryable: false)`; connection kept open.
3. Empty description: `step_error(retryable: false)` on `product_description`.
4. Zero products found: engine auto-loops to `product_description`; sends `step_error` with message "No products found — please refine your description."
5. Rate-limit on Amazon: engine auto-retries (up to 2 times, silent) before emitting `step_error(retryable: true)`.
6. Frontend `step_error` display: mark step `status: 'error'`; show error inline on step card (not global modal); show Retry button if retryable; leave prior steps intact.
