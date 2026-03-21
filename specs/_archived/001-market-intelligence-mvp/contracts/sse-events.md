# SSE Event Contract

**Branch**: `001-market-intelligence-mvp` | **Date**: 2026-03-21
**Stability**: FROZEN — event names are a stable contract per Constitution Principle III.
Any change to event names requires a MAJOR constitution version bump.

---

## Transport

- Protocol: Server-Sent Events (text/event-stream)
- Endpoint: `GET /stream?keyword={keyword}` (FastAPI backend)
- BFF proxy: `GET /api/sse?keyword={keyword}` (SvelteKit — browser connects here)
- Direction: Server → Client (unidirectional)
- Encoding: UTF-8 JSON in the `data:` field

SSE wire format:
```
event: {event_name}\n
data: {json_payload}\n
\n
```

---

## Event Sequence

Events MUST be emitted in this order:

```
source_unavailable?   (0..3 times, emitted as sources time out — interleaved with collection)
marketplace_products  (1 time — first visible event, < 5s after request)
viability_score       (N streaming tokens + 1 complete event)
target_persona        (N streaming tokens + 1 complete event)
differentiation_angles (N streaming tokens + 1 complete event)
competitive_overview  (N streaming tokens + 1 complete event)
export_ready          (1 time — signals report complete)
```

---

## Event Definitions

### `source_unavailable`

Emitted when a data source times out (>10s) or returns an error.
May be emitted 0–3 times (once per source maximum).

```json
{
  "source": "amazon",
  "message": "Source timed out after 10s"
}
```

| Field | Type | Values |
|-------|------|--------|
| `source` | string | `"amazon"` \| `"google_trends"` \| `"reddit"` |
| `message` | string | Human-readable error description |

---

### `marketplace_products`

Emitted once after Amazon scraping completes (or is skipped due to timeout).
Always emitted within 5 seconds of request start (Constitution NFR-1).

```json
{
  "status": "complete",
  "products": [
    {
      "title": "Eco Bamboo Face Wash",
      "price": "$14.99",
      "url": "https://www.amazon.com/dp/B0XXXXXXX"
    }
  ]
}
```

| Field | Type | Notes |
|-------|------|-------|
| `status` | `"complete"` | Always `complete` |
| `products` | array | May be empty if Amazon was unavailable |
| `products[].title` | string | Product title |
| `products[].price` | string | Formatted price or `"N/A"` |
| `products[].url` | string | Absolute Amazon product URL |

---

### `viability_score`

Emitted multiple times during LLM streaming, then once as `complete`.

**Streaming token** (emitted N times):
```json
{
  "status": "streaming",
  "token": "The"
}
```

**Complete** (emitted once, after all tokens):
```json
{
  "status": "complete",
  "score": 74,
  "content": "The market shows moderate opportunity. Demand is growing at 12% YoY..."
}
```

**Error** (emitted once if LLM interrupted mid-generation):
```json
{
  "status": "error",
  "partial_content": "The market shows moderate",
  "message": "Generation interrupted"
}
```

| Field | Type | Present when |
|-------|------|-------------|
| `status` | `"streaming"` \| `"complete"` \| `"error"` | Always |
| `token` | string | `status = "streaming"` |
| `score` | integer (0–100) | `status = "complete"` |
| `content` | string | `status = "complete"` |
| `partial_content` | string | `status = "error"` |
| `message` | string | `status = "error"` |

**Export format**: The score MUST appear in the MD export as `Score: {score}/100`
on its own line.

---

### `target_persona`

Same streaming/complete/error pattern as `viability_score`.

**Complete**:
```json
{
  "status": "complete",
  "content": "Urban women aged 25–35, environmentally conscious, moderate-to-high income..."
}
```

| Field | Type | Present when |
|-------|------|-------------|
| `status` | `"streaming"` \| `"complete"` \| `"error"` | Always |
| `token` | string | `status = "streaming"` |
| `content` | string | `status = "complete"` |
| `partial_content` | string | `status = "error"` |
| `message` | string | `status = "error"` |

---

### `differentiation_angles`

Same streaming/complete/error pattern.

**Complete**:
```json
{
  "status": "complete",
  "content": "1. Zero-waste packaging certified by...\n2. B-Corp certification as trust signal...\n3. Price point 20% below premium competitors..."
}
```

---

### `competitive_overview`

Same streaming/complete/error pattern.

**Complete**:
```json
{
  "status": "complete",
  "content": "The market is moderately competitive with 3 dominant players..."
}
```

---

### `export_ready`

Emitted once when all sections are complete (or have errored). Signals that
the client can enable export buttons.

```json
{
  "status": "complete"
}
```

---

## Error Handling Notes

- If ALL sources are unavailable, the pipeline emits `source_unavailable` for each,
  then emits `export_ready` with `status: "complete"` (empty report). The client
  must handle empty sections gracefully.
- If the LLM fails, affected section events carry `status: "error"`. Unaffected
  sections complete normally.
- The stream connection itself closing unexpectedly is handled client-side
  (EventSource reconnect behaviour or error state).
