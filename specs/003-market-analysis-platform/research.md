# Research: Labanane — Guided Market Analysis Platform

**Feature**: 003-market-analysis-platform
**Date**: 2026-03-21
**Phase**: 0 — Unknowns resolved

---

## 1. Google Trends Data Access

**Decision**: Use `pytrends` (unofficial Google Trends API wrapper)
**Rationale**: Battle-tested, zero auth required, returns structured DataFrames directly usable as chart data. Supports `interest_over_time()`, `interest_by_region()`, and `related_queries()` — all needed for the chart requirements.
**Alternatives considered**:
- Direct scraping of trends.google.com → brittle, rate-limited aggressively
- SerpAPI Trends endpoint → paid, adds external dependency

**Key shapes returned by pytrends**:
- `interest_over_time()` → DataFrame indexed by datetime, one column per keyword, values 0–100
- `interest_by_region()` → DataFrame indexed by geo code, one column per keyword, values 0–100
- `related_queries()` → dict per keyword: `{ top: DataFrame(query, value), rising: DataFrame(query, value_percent) }`
- Rate limit: ~5 req/min; backoff strategy required

---

## 2. Amazon Scraping

**Decision**: `httpx` async HTTP client + `BeautifulSoup` HTML parser + OpenHosta LLM for structured extraction
**Rationale**: Already partially implemented in codebase (`scraper.py`). `httpx` is non-blocking, essential for async FastAPI. LLM extraction handles Amazon's varied HTML structure better than brittle CSS selectors.
**Alternatives considered**:
- Playwright headless browser → more reliable but heavy; adds startup latency
- ScrapeOps/ScrapingBee proxy → paid, adds external dependency

**Rate-limit handling**: Detect 503/CAPTCHA responses → silent retry with randomised 2–5s delay → max 2 retries → then surface error to user.

**Headers strategy**: Rotate User-Agent strings, add Accept-Language header, mimic browser request profile.

---

## 3. LLM Integration

**Decision**: OpenHosta `emulate_async()` pattern already in codebase; wire real OpenAI API via `settings.openai_api_key`
**Rationale**: Pattern already established; OpenHosta handles structured Pydantic output deserialization. No streaming needed (step-by-step model: step completes fully, shows result).
**Model**: `gpt-4o-mini` (fast, cheap, sufficient for structured JSON extraction and analysis)

---

## 4. Chart Library

**Decision**: `layerchart` via existing shadcn-svelte `chart` component wrappers already present in the codebase
**Rationale**: Already installed and in use (`StepFinalCriteria.svelte`, `ViabilityScoreChart.svelte`). No new dependencies needed.
**Chart types needed**:
- Line chart: keyword interest over time (52-week rolling window)
- Bar chart (horizontal): interest by country (top 10)
- Bar chart (vertical): related queries / breakout terms
- Bar chart: scoring criteria breakdown (already in StepFinalCriteria)
- Donut/gauge: viability score (already in ViabilityScoreChart)
- Bar chart: product rating comparison
- Bar chart: product review count comparison

---

## 5. PDF Export

**Decision**: `weasyprint` Python library
**Rationale**: Converts HTML/CSS to PDF server-side; no headless browser required; good Markdown-to-HTML-to-PDF pipeline via `markdown` + `weasyprint`.
**Alternatives considered**:
- `pdfkit` (wkhtmltopdf) → requires binary, not easily containerised
- `reportlab` → imperative layout, verbose for structured documents
- Client-side (browser print) → no server control, inconsistent output

**Pipeline**: Markdown string → `markdown` library renders to HTML → styled with minimal CSS → `weasyprint` outputs PDF bytes → served as download.

---

## 6. Architecture Separation (FR-028/029)

**Decision**: Three strict directories in backend:
- `backend/src/workflow/engine.py` — orchestration only (already exists)
- `backend/src/workflow/steps/` — step wiring only (already exists, needs cleanup)
- `backend/src/logic/` — NEW: pure business logic functions
  - `logic/scraper.py` → `fetch_html()`, `parse_marketplace_data()`
  - `logic/trends.py` → `fetch_trends()` returning typed `TrendsData`
  - `logic/analysis.py` → `generate_search_queries()`, `generate_market_analysis()`
  - `logic/export.py` → `render_markdown()`, `render_pdf()`

**Rationale**: Current `scraper.py` at root of `src/` mixes LLM calls, HTML parsing, and mock fetching. Moving to `logic/` enforces clean separation and makes each function unit-testable independently.

---

## 7. Cross-Step Data Access

**Decision**: Add `get_output(step_id: str) -> dict` method to `WorkflowRun`
**Rationale**: Steps 7 and 9 need outputs from non-adjacent steps (keywords, products, market data). Currently requires manual dict access with string keys. A typed helper method on `WorkflowRun` is the sanctioned path (FR-026/027).
**Behaviour**: Returns `{}` (empty dict) if step has no confirmed output — safe for optional upstream reads.
