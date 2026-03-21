# Research: Market Intelligence AI — Hackathon MVP

**Branch**: `001-market-intelligence-mvp` | **Date**: 2026-03-21

---

## 1. SvelteKit + FastAPI SSE BFF Pattern

**Decision**: SvelteKit acts as a Backend-for-Frontend (BFF), proxying the SSE
stream from FastAPI via a server route (`/api/sse/+server.ts`). The browser's
`EventSource` connects to SvelteKit, never directly to FastAPI.

**Rationale**: Follows the established pattern from `tests/sveltekit+fastapi/`.
Hides the FastAPI origin from the browser (future-proofs API key addition), avoids
CORS complexity, and allows SvelteKit to add auth headers if needed post-MVP.

**Implementation pattern** (from test example):
```
Browser EventSource('/api/sse?keyword=xxx')
  → SvelteKit +server.ts
    → fetch('http://localhost:8000/stream?keyword=xxx')
      → FastAPI StreamingResponse(event_generator())
```

The SvelteKit proxy uses a `ReadableStream` pipe to forward chunks without
buffering. Response headers: `Content-Type: text/event-stream`,
`Cache-Control: no-cache`, `X-Accel-Buffering: no`.

**Alternatives considered**: Direct browser EventSource to FastAPI (rejected:
CORS complexity, leaks backend URL).

---

## 2. Package Managers

**Decision**: `uv` for Python backend, `bun` for SvelteKit frontend.

**uv**:
- Project setup: `uv init backend && uv add fastapi uvicorn[standard] ...`
- Running: `uv run uvicorn src.main:app --reload --port 8000`
- Lock file: `uv.lock` (committed)
- Python version pinned via `.python-version` file or `pyproject.toml`

**bun**:
- Project setup: `bun create svelte@latest frontend` then `bunx shadcn-svelte@latest init`
- Running: `bun run dev` (SvelteKit dev server on port 5173)
- Lock file: `bun.lockb` (binary, committed)

**Alternatives considered**: npm/pip (rejected: user preference for uv/bun).

---

## 3. Data Sources & Libraries

### 3a. Amazon (marketplace products)

**Decision**: `httpx` + `BeautifulSoup4` for direct scraping of Amazon search results.

**Approach**:
- Endpoint: `https://www.amazon.com/s?k={keyword}`
- Use realistic `User-Agent` header to reduce bot detection
- Parse product cards: title (`.a-size-medium`), price (`.a-price-whole`),
  ASIN from URL for product link
- Extract 5–10 products per keyword
- 10-second hard timeout via `httpx` `timeout=10.0`

**Known risk**: Amazon's bot-detection (Captcha/503). Mitigation: retry with
different User-Agent; if blocked, emit `source_unavailable` event and continue
pipeline. Emergency fallback: pre-seeded mock data (demo only).

**Alternatives considered**:
- Amazon Product Advertising API (rejected: requires approval + complex setup for hackathon)
- SerpAPI (rejected: paid, adds dependency)
- `amazon-product-api` libraries (rejected: unmaintained)

### 3b. Google Trends

**Decision**: `pytrends` library (`pip install pytrends`).

**Approach**:
- `TrendReq(hl='en-US', tz=360)`
- `build_payload([keyword], timeframe='today 12-m')`
- Extract interest-over-time data + related queries
- 10-second timeout via `asyncio.wait_for`

**Data extracted**: Interest trend values (0–100 scale), top related queries,
rising related queries.

**Alternatives considered**: Direct Google Trends scraping (rejected: more brittle
than pytrends).

### 3c. Reddit

**Decision**: Reddit's public JSON API (no authentication required).

**Approach**:
- Endpoint: `https://www.reddit.com/search.json?q={keyword}&sort=relevance&limit=25`
- Parse: post titles, scores (upvotes), comment counts, subreddit names
- User-Agent header required: `'Market-Intelligence-Bot/1.0'`
- 10-second timeout via `httpx`

**Data extracted**: Post sentiment proxies (score, comment volume), relevant
subreddits, recurring themes in titles.

**Rationale**: No PRAW/OAuth needed for public search data. Simpler, no credentials.

**Alternatives considered**: PRAW (rejected: requires OAuth app registration,
unnecessary for read-only public search).

---

## 4. LLM Integration — OpenHosta

**Decision**: Use `openhosta` for all LLM-powered analysis sections.

**OpenHosta** is a Python library providing a Pythonic interface for LLM calls
with typed inputs/outputs. It supports streaming responses, making it well-suited
for token-by-token SSE emission.

**Installation**: `uv add openhosta`

**Pattern for streaming analysis sections**:
```python
# OpenHosta streaming example (conceptual)
from openhosta import LLM

llm = LLM(model="gpt-4o-mini")  # or configured model

async def stream_viability_score(aggregated_data: dict):
    async for token in llm.stream(
        system="You are a market analyst...",
        user=f"Analyse this data: {aggregated_data}"
    ):
        yield token
```

**LLM model**: Configurable via `OPENAI_API_KEY` + model name in `config.py`.
Default: `gpt-4o-mini` (fast, cost-effective for hackathon).

**Sections powered by LLM**:
1. Viability score (0–100) + explanation
2. Target persona description
3. Differentiation angles (bullet list)
4. Competitive overview

**Grounding constraint**: LLM is only invoked after data aggregation. If no source
data is available, the section emits an error event rather than hallucinating.

---

## 5. SSE Streaming Architecture

**Decision**: Single `/stream` endpoint emits all events in sequence. LLM sections
use a `status: "streaming"` / `status: "complete"` pattern within the same
stable event name.

**Event emission order** (frozen per Constitution Principle III):
1. `marketplace_products` (complete, no streaming — immediate after scrape)
2. `viability_score` (streaming tokens then complete)
3. `target_persona` (streaming tokens then complete)
4. `differentiation_angles` (streaming tokens then complete)
5. `competitive_overview` (streaming tokens then complete)
6. `export_ready` (complete — signals export buttons can be enabled)

**Token streaming pattern**:
```
event: viability_score
data: {"status": "streaming", "token": "The"}

event: viability_score
data: {"status": "streaming", "token": " market"}

event: viability_score
data: {"status": "complete", "score": 74, "content": "The market shows..."}
```

**Source unavailability pattern**:
```
event: source_unavailable
data: {"source": "amazon", "message": "Source timed out after 10s"}
```

**LLM interruption pattern** (per clarification Q1):
```
event: viability_score
data: {"status": "error", "partial_content": "The market...", "message": "Generation interrupted"}
```

---

## 6. Export Generation

**Decision**: In-memory export generation triggered by `/export/md` and
`/export/pdf` endpoints after the analysis completes. Report state stored in
process memory for the duration of the session (single active analysis).

**Markdown**: Generated server-side by assembling section content with the frozen
schema (see `contracts/export-schema.md`). Served as file download.

**PDF**: Generated from Markdown using `weasyprint` or `reportlab`.
- `weasyprint`: HTML→PDF, good formatting, requires system dependencies
- Alternative: `fpdf2` (pure Python, lighter)
- **Decision**: `fpdf2` (simpler install for hackathon, no system deps)

**Alternatives considered**: Client-side PDF (rejected: layout control harder,
export contract must be server-authoritative).

---

## 7. run.sh Launch Script

**Decision**: Single `run.sh` at repo root launches both services.

**Pattern** (following test example):
```bash
#!/bin/bash
# Start FastAPI backend
cd backend && uv run uvicorn src.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start SvelteKit frontend
cd frontend && bun run dev &
FRONTEND_PID=$!

# Cleanup on Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
```

**Ports**: Backend 8000, Frontend 5173 (matching test example and SvelteKit default).

---

## 8. shadcn-svelte Component Strategy

**Decision**: Use `shadcn-svelte` for base UI components and charts.

**Installation**: `bunx shadcn-svelte@latest init` in the frontend directory.

**Components used**:
- `Card` — wraps each dashboard section
- `Progress` — shows analysis pipeline progress
- `Badge` — viability score display
- `Skeleton` — loading state placeholders (FR-005, FR-021)
- `Button` — export buttons, New Analysis button
- `Chart` (if needed for trend visualization)

**Svelte 5 runes pattern** (from test example):
```svelte
<script lang="ts">
  let state = $state({ conn: 'idle', sections: {} })
  let isComplete = $derived(state.conn === 'complete')
</script>
```

Variable containing "state" in name is required due to svelte-check 4.4.5 bug
(matches pattern in test example).
