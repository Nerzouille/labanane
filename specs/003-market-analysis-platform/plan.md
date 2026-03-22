# Implementation Plan: Labanane — Guided Market Analysis Platform

**Branch**: `003-market-analysis-platform` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-market-analysis-platform/spec.md`

---

## Summary

Unified 9-step guided market analysis workflow. Each step is a self-contained module that delegates all computation to a dedicated business logic layer. Data sources: Amazon (product scraping + LLM extraction) and Google Trends (trend analytics; Reddit removed). No intra-step token streaming — each step completes fully and shows its result at once. Rich chart visualisations via layerchart (shadcn-svelte) are the primary vehicle for market data presentation. Export via REST endpoints (Markdown + PDF).

---

## Technical Context

**Language/Version**: Python 3.12 (backend) · TypeScript / Svelte 5 (frontend)
**Primary Dependencies**:
- Backend: FastAPI, pydantic v2, uv, OpenHosta (LLM), pytrends (Google Trends), httpx (scraping), weasyprint (PDF), python-markdown
- Frontend: SvelteKit, bun, shadcn-svelte, layerchart (charts), zod

**Storage**: In-memory only — `WorkflowRun` dict keyed by `run_id`; deleted on WebSocket disconnect. Report markdown stored in-memory keyed by `run_id` until disconnect.
**Testing**: pytest (backend)
**Target Platform**: Desktop web (Chrome/Firefox/Safari latest); FastAPI on Linux
**Project Type**: Full-stack web application
**Performance Goals**: Keyword refinement ≤5s · Product research ≤15s · Market research ≤20s · AI analysis ≤30s
**Constraints**: No persistent storage · No auth · One active run per WebSocket connection · Desktop-first layout
**Scale/Scope**: Hackathon — small concurrent user count; multiple fully isolated sessions supported

---

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked post-design.*

| Principle | Status | Notes |
|---|---|---|
| I. Streaming-First UX | ✅ Adapted | Token streaming removed per clarification session. Step-by-step node completion replaces it. Progress indicators on all system steps satisfy the "no blank screen" intent. |
| II. Pipeline Resilience | ✅ | Amazon rate-limit: auto-retry (FR-012d). Source unavailability: partial results notice + workflow continues (FR-016c). |
| III. Stable Export Contracts | ✅ | MD schema frozen in `contracts/export-schema.md`. `Score: NN/100` field guaranteed. Heading hierarchy stable. |
| IV. Simplicity & Hackathon Scope | ✅ | Reddit removed. No new features. No auth. Desktop only. YAGNI enforced. |
| V. Real Data Integrity | ✅ | Amazon scraping + LLM extraction. Google Trends via pytrends. AI analysis only runs with real data (FR-018c). |

**Post-design re-check**: All principles satisfied. No violations requiring justification.

---

## Project Structure

### Documentation (this feature)

```text
specs/003-market-analysis-platform/
├── plan.md              # This file
├── research.md          # Phase 0 — all unknowns resolved
├── data-model.md        # Phase 1 — entities and chart mappings
├── quickstart.md        # Phase 1 — dev setup
├── contracts/
│   ├── ws-messages.md   # WebSocket message protocol (source of truth)
│   ├── step-interface.md # Three-layer architecture + step contract
│   └── export-schema.md  # MD/PDF export schema
└── tasks.md             # Phase 2 — /speckit.tasks output (not yet created)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── workflow/
│   │   ├── engine.py          # Orchestration only (no business logic)
│   │   ├── step_base.py       # Step ABC + StepError
│   │   ├── run.py             # WorkflowRun + get_output() method
│   │   ├── messages.py        # Pydantic server/client message models
│   │   ├── registry.py        # PIPELINE list assembly
│   │   └── steps/
│   │       ├── s01_description.py
│   │       ├── s02_keyword_refinement.py
│   │       ├── s03_keyword_confirmation.py
│   │       ├── s04_product_research.py
│   │       ├── s05_product_validation.py
│   │       ├── s06_market_research.py
│   │       ├── s07_ai_analysis.py
│   │       ├── s08_final_criteria.py
│   │       └── s09_report.py
│   ├── logic/                 # NEW — pure business logic, no workflow state
│   │   ├── scraper.py         # fetch_html, clean_html_for_llm, parse_marketplace_data
│   │   ├── trends.py          # fetch_trends → TrendsData
│   │   ├── analysis.py        # generate_search_queries, generate_market_analysis
│   │   └── export.py          # render_markdown, render_pdf
│   ├── models/
│   │   ├── report.py          # Product, MarketAnalysis, Criterion, etc.
│   │   └── workflow_models.py # TrendsData, KeywordTrends, data classes
│   ├── routes/
│   │   ├── workflow.py        # WebSocket /ws/workflow
│   │   └── export.py          # GET /api/export/{run_id}/markdown|pdf (NEW)
│   ├── config.py
│   └── main.py
└── tests/
    ├── test_ws_happy_path.py
    ├── test_ws_contract.py
    └── logic/
        ├── test_scraper.py
        ├── test_trends.py
        ├── test_analysis.py
        └── test_export.py

frontend/
└── src/
    ├── routes/
    │   └── workflow/+page.svelte
    └── lib/
        ├── ws.ts
        ├── workflow-types.ts              # Zod schemas — derived from ws-messages.md
        └── components/
            ├── StepRenderer.svelte
            ├── steps/
            │   ├── StepProductList.svelte      # + rating/review charts (updated)
            │   ├── StepMarketData.svelte        # line + bar charts (updated)
            │   ├── StepFinalCriteria.svelte     # donut + criteria bar (updated)
            │   ├── StepKeywordList.svelte
            │   ├── StepConfirmation.svelte
            │   ├── StepAiAnalysis.svelte        # new component
            │   └── StepReport.svelte            # export download buttons (updated)
            ├── charts/
            │   ├── ViabilityScoreChart.svelte   # existing
            │   ├── InterestOverTimeChart.svelte # NEW — line chart (layerchart)
            │   ├── InterestByRegionChart.svelte # NEW — horizontal bar (layerchart)
            │   └── RelatedQueriesChart.svelte   # NEW — horizontal bar (layerchart)
            └── ui/                              # shadcn-svelte (existing)
```

**Structure Decision**: Web application (backend + frontend). Logic layer is a new module within `backend/src/logic/` — not a separate project.

---

## Phase 0: Research

All unknowns resolved. See `research.md` for full decisions and rationale.

| Unknown | Decision |
|---------|----------|
| Google Trends access | `pytrends` library |
| Amazon scraping | `httpx` + BeautifulSoup + OpenHosta LLM |
| Amazon rate-limit | Auto-retry ×2, randomised 2–5s delay, then surface error |
| LLM integration | OpenHosta `emulate_async()` → real OpenAI API call |
| PDF export | `weasyprint` via Markdown → HTML → PDF pipeline |
| Chart library | `layerchart` (already installed via shadcn-svelte) |
| Architecture separation | `backend/src/logic/` new module for all pure functions |
| Cross-step data access | `WorkflowRun.get_output(step_id)` new method |

---

## Phase 1: Design & Contracts

### Contracts

All contracts defined. See `/contracts/` directory.

| Contract | File | Changes from 002 |
|---|---|---|
| WebSocket messages | `ws-messages.md` | Removed `step_streaming_token`; enriched `ProductListData` with rating/review fields; new `MarketDataResult` shape with full Trends data; new `AiAnalysisData` shape |
| Step interface + architecture | `step-interface.md` | Added three-layer architecture diagram; added `run.get_output()` contract; moved logic layer contracts here |
| Export schema | `export-schema.md` | Stable MD schema with `Score: NN/100` anchor; PDF note (charts not included) |

### Data Model

All entities defined. See `data-model.md`.

Key additions vs 002:
- `Product` enriched with `rating_stars`, `rating_count`, `main_features`
- `TrendsData` / `KeywordTrends` new types (replaces vague `trend_data: dict`)
- `MarketDataResult` typed message shape for step 6
- `WorkflowRun.get_output()` method
- Frontend Zod types with chart-ready array shapes
- Component → chart mapping table

### Component & Chart Plan

| Component | Charts (layerchart) | Data field |
|---|---|---|
| `StepProductList` | Rating comparison bar | `products[].rating_stars` |
| `StepProductList` | Review volume bar | `products[].rating_count` |
| `StepMarketData` | Interest over time line (multi-series) | `trends[kw].interest_over_time` |
| `StepMarketData` | Interest by country horizontal bar | `trends[kw].interest_by_region` |
| `StepMarketData` | Related queries horizontal bar | `trends[kw].related_queries_top` |
| `StepMarketData` | Breakout query callout cards | `trends[kw].related_queries_rising` |
| `StepAiAnalysis` / `StepFinalCriteria` | Viability score donut/gauge | `viability_score` |
| `StepAiAnalysis` / `StepFinalCriteria` | Scoring criteria horizontal bar | `criteria[]` |

---

## Constitution Check (post-design)

Re-evaluated after Phase 1. All principles remain satisfied.

- **Principle I**: Progress indicators on all system steps. No blank screens.
- **Principle II**: Amazon rate-limit auto-retry in `logic/scraper.py`. Google Trends unavailability handled gracefully in `logic/trends.py`.
- **Principle III**: Export schema frozen and documented. `Score: NN/100` anchor field stable.
- **Principle IV**: No scope additions. Charts are within the data-visibility goal stated by the user. Reddit confirmed excluded.
- **Principle V**: All analysis grounded in real data. FR-018c enforced in `AiAnalysisStep`.

---

## Next Step

Run `/speckit.tasks` to generate the implementation task list from this plan.
