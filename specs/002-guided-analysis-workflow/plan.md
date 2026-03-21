# Implementation Plan: Guided Analysis Workflow

**Branch**: `002-guided-analysis-workflow` | **Date**: 2026-03-21 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/002-guided-analysis-workflow/spec.md`

## Summary

A 9-step guided analysis workflow with user confirmation loops (keyword refinement, product validation) and extensible modular step architecture. Communication uses WebSocket (bidirectional) between browser and FastAPI directly — no SvelteKit BFF — to support server→client streaming AND client→server confirmations within the same connection. Each step is an independent Python module with a shared interface, assembled into an ordered pipeline in code.

## Technical Context

**Language/Version**: Python 3.12 (backend), TypeScript / Svelte 5 (frontend)
**Primary Dependencies**: FastAPI (WebSocket), pydantic v2, uv (backend); SvelteKit, bun, shadcn-svelte (frontend)
**Storage**: In-memory session state only (no database); `WorkflowRun` dict keyed by session ID
**Testing**: pytest + pytest-asyncio (backend); vitest (frontend)
**Target Platform**: Desktop web browser (Chrome/Firefox/Safari); local dev server
**Project Type**: Web application — existing monorepo with `backend/` + `frontend/`
**Performance Goals**: Confirmation actions register within 1 second; full 9-step run < 5 minutes active interaction
**Constraints**: Single-session, no persistence after disconnect; one active workflow per WebSocket connection
**Scale/Scope**: Hackathon MVP; single user per session; no multi-user or team collaboration

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| **I — Streaming-First UX** | ✅ PASS (justified deviation) | Constitution specifies SSE; this feature uses WebSocket. Justification: SSE is unidirectional — it cannot receive client confirmation messages (Yes/No at steps 3 and 5). WebSocket maintains the streaming-first spirit (server pushes tokens + progress in real time) while adding the bidirectional channel needed for confirmation loops. No other mechanism meets both requirements. |
| **II — Pipeline Resilience** | ✅ PASS | All system-processing steps (product research, market research, AI analysis) share the same scoped error+retry pattern. Prior confirmed data is never discarded on step failure. |
| **III — Stable Export Contracts** | ✅ PASS | Report generated at step 9 uses the same Markdown export schema defined in `contracts/export-schema.md` (feature 001). The `Score: {n}/100` format and section headings are preserved. |
| **IV — Simplicity & Hackathon Scope** | ✅ PASS | No config file, no runtime step editor, no database. Steps are plain Python classes; the pipeline is a list assembled in `registry.py`. |
| **V — Real Data Integrity** | ✅ PASS | Steps 4–8 reuse the same data collection and analysis stubs from feature 001; no fabricated data. |

**Complexity Tracking**:

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| WebSocket instead of SSE | Confirmation loops require client→server messages (Yes/No) mid-stream | SSE is unidirectional; polling would require a separate REST endpoint per step and lose the session binding |

## WebSocket Message Protocol

### Server → Client messages

```typescript
// Workflow lifecycle
{ type: "workflow_started", total_steps: number, step_ids: string[] }
{ type: "workflow_complete", run_id: string }

// Step state
{ type: "step_activated", step_id: string, step_number: number, total_steps: number, label: string }
{ type: "step_processing", step_id: string }  // spinner on
{ type: "step_result", step_id: string, component_type: StepComponentType, data: object }

// Streaming (for LLM steps)
{ type: "step_streaming_token", step_id: string, token: string }

// Confirmation gate
{ type: "confirmation_request", step_id: string, component_type: ConfirmationComponentType, data: object }

// Error / recovery
{ type: "step_error", step_id: string, error: string, retryable: boolean }
```

### Client → Server messages

```typescript
{ type: "start", description: string }               // kick off step 1
{ type: "confirmation", step_id: string, confirmed: boolean }  // Yes / No at gates
{ type: "retry", step_id: string }                    // retry failed step
{ type: "user_input", step_id: string, data: object } // for steps requiring text re-entry
```

### `component_type` values (drives dynamic Svelte component mounting)

| value | frontend component | when used |
|---|---|---|
| `product_description_input` | `StepDescriptionInput.svelte` | Step 1 — free-text entry |
| `keyword_list` | `StepKeywordList.svelte` | Step 2 — display 3–5 keywords |
| `confirmation` | `StepConfirmation.svelte` | Steps 3 & 5 — Yes/No gate (data already displayed by prior step) |
| `product_list` | `StepProductList.svelte` | Step 4 — product cards |
| `market_data_summary` | `StepMarketData.svelte` | Step 6 — market research results |
| `analysis_stream` | `StepAnalysisStream.svelte` | Step 7 — streamed AI text |
| `final_criteria` | `StepFinalCriteria.svelte` | Step 8 — structured criteria |
| `report` | `StepReport.svelte` | Step 9 — full report + export |

## Project Structure

### Documentation (this feature)

```text
specs/002-guided-analysis-workflow/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── ws-messages.md   # WebSocket message schemas
│   └── step-interface.md # Step base class contract
└── tasks.md             # Phase 2 output (via /speckit.tasks)
```

### Source Code

```text
backend/
├── src/
│   ├── workflow/
│   │   ├── __init__.py
│   │   ├── step_base.py          # Abstract Step class + shared interface
│   │   ├── engine.py             # WorkflowEngine (drives the pipeline)
│   │   ├── registry.py           # Assembles the ordered step list
│   │   ├── messages.py           # Pydantic models for all WS message types
│   │   └── steps/
│   │       ├── __init__.py
│   │       ├── s01_description.py
│   │       ├── s02_keyword_refinement.py
│   │       ├── s03_keyword_confirmation.py
│   │       ├── s04_product_research.py
│   │       ├── s05_product_validation.py
│   │       ├── s06_market_research.py
│   │       ├── s07_ai_analysis.py
│   │       ├── s08_final_criteria.py
│   │       └── s09_report.py
│   ├── routes/
│   │   ├── stream.py             # existing SSE route (feature 001)
│   │   ├── export.py             # existing export route (feature 001)
│   │   └── workflow.py           # NEW: WebSocket endpoint ws://localhost:8000/ws/workflow
│   └── tests/
│       ├── test_workflow_engine.py
│       ├── test_workflow_steps.py
│       └── test_ws_contract.py

frontend/
├── src/
│   ├── lib/
│   │   ├── ws.ts                 # WebSocket client + message dispatcher
│   │   ├── types.ts              # existing SSE types (feature 001)
│   │   ├── workflow-types.ts     # NEW: WS message Zod schemas
│   │   └── components/
│   │       ├── StepRenderer.svelte       # dynamic mount by component_type
│   │       └── steps/
│   │           ├── StepDescriptionInput.svelte
│   │           ├── StepKeywordList.svelte
│   │           ├── StepConfirmation.svelte
│   │           ├── StepProductList.svelte
│   │           ├── StepMarketData.svelte
│   │           ├── StepAnalysisStream.svelte
│   │           ├── StepFinalCriteria.svelte
│   │           └── StepReport.svelte
│   └── routes/
│       ├── +page.svelte           # existing analysis dashboard (feature 001)
│       └── workflow/
│           └── +page.svelte       # NEW: guided workflow page

tests/
└── (backend tests in backend/src/tests/)
```

**Structure Decision**: Web application — extends the existing `backend/` + `frontend/` monorepo. The workflow module is a new sibling to the existing pipeline module inside `backend/src/`. The frontend adds a `/workflow` route alongside the existing `/` dashboard.

## Technology Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Transport | WebSocket (FastAPI native) | Bidirectional: server streams tokens, client sends confirmations |
| Session state | In-memory dict (WorkflowRun keyed by session ID) | No persistence required; hackathon scope |
| Step interface | Abstract Python base class | Enforces input/output contract; enables registry pattern |
| Pipeline assembly | List in `registry.py` | Simple, readable, zero config; insert step = insert list item |
| Frontend routing | New `/workflow` SvelteKit route | Keeps feature 001 dashboard isolated |
| Component dispatch | `component_type` field in messages | Decouples server step logic from frontend rendering |
| Message validation | Pydantic (backend) + Zod (frontend) | Shared schema discipline; same pattern as feature 001 |

## Phase 0: Research

See `research.md` for resolved decisions on:
- FastAPI WebSocket session management patterns
- Abstract base class design for modular steps
- Svelte 5 dynamic component mounting
- WorkflowRun state machine design

## Phase 1: Design Artifacts

- `data-model.md` — WorkflowRun, Step, StepResult, ConfirmationGate, KeywordSet, ProductBatch, MarketData, AnalysisResult, FinalCriteria, Report entities
- `contracts/ws-messages.md` — Full WS message schema (server→client + client→server)
- `contracts/step-interface.md` — Abstract Step base class contract
- `quickstart.md` — Integration scenarios for TDD
