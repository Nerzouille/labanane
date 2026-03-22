# Quickstart: Labanane — Guided Market Analysis Platform

**Feature**: 003-market-analysis-platform
**Date**: 2026-03-21

---

## Prerequisites

- Python 3.12 + `uv`
- Node.js (via `bun`)
- `OPENAI_API_KEY` environment variable set

---

## Backend

```bash
cd backend
uv sync
cp .env.example .env        # set OPENAI_API_KEY
uv run uvicorn src.main:app --reload --port 8000
```

Health check: `curl http://localhost:8000/health`

WebSocket endpoint: `ws://localhost:8000/ws/workflow`

Export endpoints (available after workflow completes):
- `GET http://localhost:8000/api/export/{run_id}/markdown`
- `GET http://localhost:8000/api/export/{run_id}/pdf`

---

## Frontend

```bash
cd frontend
bun install
bun run dev
```

Open `http://localhost:5173`

---

## Run tests

```bash
cd backend
uv run pytest src/tests/ -v
```

---

## Architecture at a glance

```
backend/src/
├── workflow/
│   ├── engine.py          # orchestration only
│   ├── step_base.py       # Step abstract class + StepError
│   ├── run.py             # WorkflowRun + get_output()
│   ├── messages.py        # Pydantic server/client message models
│   ├── registry.py        # PIPELINE assembly
│   └── steps/
│       ├── s01_description.py
│       ├── s02_keyword_refinement.py
│       ├── s03_keyword_confirmation.py
│       ├── s04_product_research.py
│       ├── s05_product_validation.py
│       ├── s06_market_research.py
│       ├── s07_ai_analysis.py
│       ├── s08_final_criteria.py
│       └── s09_report.py
├── logic/                 # pure business logic — no workflow state
│   ├── scraper.py         # fetch_html, parse_marketplace_data, clean_html_for_llm
│   ├── trends.py          # fetch_trends → TrendsData
│   ├── analysis.py        # generate_search_queries, generate_market_analysis
│   └── export.py          # render_markdown, render_pdf
├── models/
│   ├── report.py          # Product, MarketAnalysis, Criterion, etc.
│   └── workflow_models.py # TrendsData, KeywordTrends, etc.
├── routes/
│   ├── workflow.py        # WebSocket /ws/workflow
│   └── export.py          # GET /api/export/{run_id}/markdown|pdf
└── main.py

frontend/src/
├── routes/
│   └── workflow/+page.svelte
├── lib/
│   ├── ws.ts                      # WebSocket client
│   ├── workflow-types.ts          # Zod schemas (derived from ws-messages.md)
│   └── components/
│       ├── StepRenderer.svelte
│       ├── steps/
│       │   ├── StepProductList.svelte    # + rating/review charts
│       │   ├── StepMarketData.svelte     # line + bar charts
│       │   ├── StepFinalCriteria.svelte  # donut + criteria bar
│       │   ├── StepKeywordList.svelte
│       │   ├── StepConfirmation.svelte
│       │   ├── StepReport.svelte         # export download buttons
│       │   └── StepAiAnalysis.svelte     # new: wraps full analysis display
│       ├── charts/
│       │   ├── ViabilityScoreChart.svelte
│       │   ├── InterestOverTimeChart.svelte   # new: line chart
│       │   ├── InterestByRegionChart.svelte   # new: horizontal bar
│       │   └── RelatedQueriesChart.svelte     # new: horizontal bar
│       └── ui/                              # shadcn-svelte components
```

---

## Key rules reminder

1. Steps call `run.get_output("step_id")` — never access `run.confirmed_outputs` directly.
2. All scraping, LLM calls, and data transformation live in `backend/src/logic/` only.
3. `step_streaming_token` message type does not exist — do not implement it.
4. Export endpoints require `run_id` from `workflow_complete` message.
