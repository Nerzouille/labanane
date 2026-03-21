# Implementation Plan: Market Intelligence AI — Hackathon MVP

**Branch**: `001-market-intelligence-mvp` | **Date**: 2026-03-21 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-market-intelligence-mvp/spec.md`

## Summary

Build a streaming market intelligence dashboard where a user enters a keyword and
watches a progressive analysis build in real time. The backend (FastAPI + uv) runs
a parallel data-collection pipeline across three sources (Amazon, Google Trends,
Reddit), aggregates results, and streams LLM-generated insights section by section
via SSE. The frontend (SvelteKit + Svelte 5 + bun) proxies the SSE stream from
FastAPI using the BFF pattern and renders each section as it arrives using
shadcn-svelte components. The full analysis delivers within 60 seconds; the first
marketplace products appear within 5 seconds.

## Technical Context

**Language/Version**: Python 3.12 (backend) · TypeScript / Svelte 5 (frontend)
**Primary Dependencies**:
- Backend: FastAPI, uvicorn, pydantic-settings, httpx, pytrends, praw, beautifulsoup4, openhosta
- Frontend: SvelteKit 2, Svelte 5, shadcn-svelte, zod, bits-ui
**Storage**: None — stateless, no persistence beyond active HTTP session
**Testing**: None mandated for hackathon MVP
**Target Platform**: Desktop web browser (Chrome/Firefox/Safari latest)
**Project Type**: Web service (FastAPI backend) + Web application (SvelteKit frontend)
**Performance Goals**: First SSE event < 5s · Full report < 60s · No LLM pause > 3s
**Constraints**: No auth · No DB · Desktop-first · 3 sources only · uv for Python · bun for Node
**Scale/Scope**: Single-user hackathon demo · No concurrent-user load requirements

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Gate | Status |
|-----------|------|--------|
| I. Streaming-First UX | Amazon products emitted as first SSE event; LLM sections streamed token-by-token; skeleton state shown on launch; event names match stable contract | ✅ PASS |
| II. Pipeline Resilience | Each source has 10s timeout; pipeline continues on timeout; partial results shown with user notice; no silent data fabrication | ✅ PASS |
| III. Stable Export Contracts | SSE event names frozen per constitution; MD export schema defined and frozen; score field parsable (`Score: 74/100`) | ✅ PASS |
| IV. Simplicity & Hackathon Scope | No auth, no DB, desktop-first, 3 sources, stateless, < 60s completion target | ✅ PASS |
| V. Real Data Integrity | All scraping uses live sources; LLM synthesis grounded on aggregated real data; LLM not invoked if no data available | ✅ PASS |

**Result: All gates pass. Proceeding to Phase 0.**

## Project Structure

### Documentation (this feature)

```text
specs/001-market-intelligence-mvp/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── sse-events.md    # SSE event contract (stable — see constitution Principle III)
│   └── export-schema.md # Markdown export schema contract
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
backend/
├── pyproject.toml           # uv project definition + dependencies
├── src/
│   ├── main.py              # FastAPI app factory, CORS, router mounting
│   ├── config.py            # pydantic-settings config (env vars, timeouts)
│   ├── models/
│   │   ├── sse.py           # Pydantic SSE event models (all 6 event types)
│   │   └── report.py        # Report / export models
│   ├── routes/
│   │   ├── stream.py        # GET /stream — main SSE endpoint
│   │   └── export.py        # GET /export/md · GET /export/pdf
│   └── pipeline/
│       ├── orchestrator.py  # Parallel source fetch + LLM chain + SSE emission
│       ├── sources/
│       │   ├── amazon.py    # Amazon scraper (bs4 + httpx, 10s timeout)
│       │   ├── trends.py    # Google Trends via pytrends (10s timeout)
│       │   └── reddit.py    # Reddit JSON API (10s timeout, no auth required)
│       └── analysis/
│           ├── scorer.py    # Viability score + explanation via OpenHosta
│           ├── persona.py   # Target persona via OpenHosta
│           ├── angles.py    # Differentiation angles via OpenHosta
│           └── competitive.py # Competitive overview via OpenHosta

frontend/
├── package.json             # bun project · SvelteKit + Svelte 5 + shadcn-svelte
├── bun.lockb
├── svelte.config.js
├── vite.config.ts
├── src/
│   ├── app.html
│   ├── app.d.ts
│   ├── lib/
│   │   ├── types.ts         # Zod schemas for all SSE event payloads
│   │   ├── sse.ts           # EventSource wrapper (same BFF pattern as test)
│   │   └── components/
│   │       ├── ui/          # shadcn-svelte base components
│   │       ├── SearchForm.svelte
│   │       ├── Dashboard.svelte
│   │       ├── ExportButtons.svelte
│   │       └── sections/
│   │           ├── MarketplaceProducts.svelte
│   │           ├── ViabilityScore.svelte
│   │           ├── TargetPersona.svelte
│   │           ├── DifferentiationAngles.svelte
│   │           └── CompetitiveOverview.svelte
│   └── routes/
│       ├── +page.svelte     # Main page (Svelte 5 runes)
│       └── api/
│           ├── sse/
│           │   └── +server.ts   # BFF SSE proxy → FastAPI /stream
│           └── export/
│               └── +server.ts   # BFF export proxy → FastAPI /export/*

run.sh                       # Launch script: starts backend (uv run) + frontend (bun run dev)
```

**Structure Decision**: Web application (Option 2 variant). FastAPI backend at
`backend/`, SvelteKit frontend at `frontend/`. Both at repo root. Single `run.sh`
launches both. No monorepo tooling needed for MVP.

## Complexity Tracking

> No constitution violations — section not applicable.
