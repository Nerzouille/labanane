---

description: "Task list for Market Intelligence AI — Hackathon MVP"
---

# Tasks: Market Intelligence AI — Hackathon MVP

**Input**: Design documents from `/specs/001-market-intelligence-mvp/`
**Prerequisites**: plan.md ✅ · spec.md ✅ · research.md ✅ · data-model.md ✅ · contracts/ ✅ · quickstart.md ✅

**Tests**: Not requested — no test tasks generated.

**Organization**: Tasks are grouped by user story to enable independent
implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Paths: `backend/src/` for Python · `frontend/src/` for SvelteKit

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Initialize both projects, install dependencies, configure environment.

- [x] T001 Create `backend/` directory with `uv init` and add all dependencies: `fastapi uvicorn[standard] pydantic-settings httpx beautifulsoup4 pytrends praw openhosta fpdf2`
- [x] T002 Create `frontend/` directory with `bun create svelte@latest` (Svelte 5, TypeScript, SvelteKit)
- [ ] T003 [P] Run `bunx shadcn-svelte@latest init` in `frontend/` to set up shadcn-svelte
- [x] T004 [P] Create `backend/.env.example` with all required env vars: `APP_OPENAI_API_KEY`, `APP_LLM_MODEL`, `APP_CORS_ORIGINS`, `APP_SOURCE_TIMEOUT`
- [x] T005 [P] Create `frontend/.env.example` with `PUBLIC_API_BASE=http://localhost:8000`
- [x] T006 Create `run.sh` at repo root that starts FastAPI on port 8000 (`uv run uvicorn`) and SvelteKit on port 5173 (`bun run dev`) with `trap` cleanup on Ctrl+C
- [x] T007 [P] Create `backend/src/config.py` — pydantic-settings `Settings` class with: `openai_api_key`, `llm_model` (default `gpt-4o-mini`), `cors_origins`, `source_timeout` (default `10`), env_prefix `APP_`
- [x] T008 [P] Create `backend/src/main.py` — FastAPI app factory with `CORSMiddleware`, health endpoint `GET /health → {"status": "ok"}`, router mounting for `/stream` and `/export`
- [x] T009 [P] Create `backend/src/models/sse.py` — Pydantic models for all SSE event payloads: `MarketplaceProductsEvent`, `LLMTokenEvent`, `LLMCompleteEvent`, `LLMErrorEvent`, `SourceUnavailableEvent`, `ExportReadyEvent`
- [x] T010 [P] Create `backend/src/models/report.py` — Pydantic models: `MarketplaceProduct`, `SourceResult`, `AggregatedData`, `AnalysisReport`, `ViabilityScore`, `TargetPersona`, `DifferentiationAngles`, `CompetitiveOverview`
- [x] T011 [P] Create `frontend/src/lib/types.ts` — Zod schemas for all SSE event payloads matching `contracts/sse-events.md`: `MarketplaceProductsEventSchema`, `LLMTokenEventSchema`, `LLMCompleteEventSchema`, `LLMErrorEventSchema`, `SourceUnavailableEventSchema`, `ExportReadyEventSchema` + union `AnySSEEvent`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core pipeline infrastructure that ALL user stories depend on.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T012 Create `backend/src/pipeline/sources/amazon.py` — stub with `NotImplementedError` (TDD: test_sources.py RED)
- [x] T013 [P] Create `backend/src/pipeline/sources/trends.py` — stub with `NotImplementedError` (TDD: test_sources.py RED)
- [x] T014 [P] Create `backend/src/pipeline/sources/reddit.py` — stub with `NotImplementedError` (TDD: test_sources.py RED)
- [x] T015 Create `backend/src/pipeline/orchestrator.py` — stub pipeline emitting placeholder marketplace_products + export_ready
- [x] T016 Create `backend/src/routes/stream.py` — `GET /stream?keyword={kw}` endpoint wired to orchestrator stub
- [x] T017 Create `frontend/src/lib/sse.ts` — `createAnalysisStream` with named SSE event dispatching
- [x] T018 Create `frontend/src/routes/api/sse/+server.ts` — BFF SSE proxy with keyword forwarding

**Checkpoint**: Foundation ready — pipeline fetches data, emits SSE, frontend proxy works.

---

## Phase 3: User Story 1 — Live Market Analysis Dashboard (Priority: P1) 🎯 MVP

**Goal**: User enters keyword → watches dashboard build section by section in real time
with marketplace products, viability score, persona, differentiation angles, and competitive overview.

**Independent Test**: Enter "eco-friendly bamboo skincare", click Analyse. Verify:
first products appear < 5s; all 5 sections build progressively with skeleton → streaming → complete
states; no section waits for another; full report done < 60s.

### Implementation for User Story 1

- [ ] T019 [P] [US1] Create `backend/src/pipeline/analysis/scorer.py` — async `stream_viability_score(data: AggregatedData) → AsyncGenerator[LLMTokenEvent | LLMCompleteEvent | LLMErrorEvent, None]`; uses OpenHosta to stream analysis; yields `LLMTokenEvent` per token; yields `LLMCompleteEvent(score=int, content=str)` at end; catches exceptions and yields `LLMErrorEvent(partial_content, message)`
- [ ] T020 [P] [US1] Create `backend/src/pipeline/analysis/persona.py` — same streaming pattern as scorer.py; async `stream_persona(data: AggregatedData) → AsyncGenerator`; yields `target_persona` tokens then complete event
- [ ] T021 [P] [US1] Create `backend/src/pipeline/analysis/angles.py` — same streaming pattern; async `stream_angles(data: AggregatedData) → AsyncGenerator`; yields `differentiation_angles` tokens then complete event
- [ ] T022 [P] [US1] Create `backend/src/pipeline/analysis/competitive.py` — same streaming pattern; async `stream_competitive(data: AggregatedData) → AsyncGenerator`; yields `competitive_overview` tokens then complete event
- [ ] T023 [US1] Wire LLM analysis chain into `backend/src/pipeline/orchestrator.py` — after building `AggregatedData`, call scorer → persona → angles → competitive sequentially; yield each event with correct SSE `event:` name; emit `export_ready` event after all sections complete; store completed `AnalysisReport` in process-local state keyed by `session_id`
- [ ] T024 [P] [US1] Create `frontend/src/lib/components/sections/MarketplaceProducts.svelte` — Svelte 5 component; accepts `products` prop (array); renders product cards with title, price, and clickable URL link; shows skeleton state when `status === "loading"`; uses shadcn-svelte `Card` and `Skeleton` components
- [ ] T025 [P] [US1] Create `frontend/src/lib/components/sections/ViabilityScore.svelte` — Svelte 5 component; accepts `status`, `streamingContent`, `score`, `explanation` props; renders `Badge` with score; shows inline streaming text as tokens arrive; transitions from skeleton → streaming → complete; shows error notice if `status === "error"`
- [ ] T026 [P] [US1] Create `frontend/src/lib/components/sections/TargetPersona.svelte` — same pattern as ViabilityScore; renders persona description with streaming text; skeleton → streaming → complete states
- [ ] T027 [P] [US1] Create `frontend/src/lib/components/sections/DifferentiationAngles.svelte` — same pattern; renders angles as list; streaming text while generating; complete list when done
- [ ] T028 [P] [US1] Create `frontend/src/lib/components/sections/CompetitiveOverview.svelte` — same pattern; renders overview text with streaming; complete when done
- [ ] T029 [P] [US1] Create `frontend/src/lib/components/SearchForm.svelte` — Svelte 5 component; text input + Analyse button; validates non-empty input client-side; disables input and button while analysis is in progress (FR-033); emits `submit` event with keyword
- [ ] T030 [US1] Create `frontend/src/lib/components/Dashboard.svelte` — Svelte 5 component; orchestrates all 5 section components; manages section states (`hidden | loading | streaming | complete | error`) via `$state`; shows `Progress` component for overall pipeline progress; renders `source_unavailable` notice banners (FR-010)
- [ ] T031 [US1] Create `frontend/src/routes/+page.svelte` — main page; Svelte 5 runes; `let pageState = $state({phase: 'input', keyword: '', sections: {}})` (variable name must contain "state" — svelte-check bug workaround); handles SSE stream lifecycle via `createSSEStream`; shows `SearchForm` in input phase; shows `Dashboard` during/after analysis; transitions to complete phase on `export_ready` event

**Checkpoint**: User Story 1 fully functional — complete streaming dashboard works end-to-end.

---

## Phase 4: User Story 2 — Export & Share the Report (Priority: P2)

**Goal**: After analysis completes, user can download Markdown (stable schema) and PDF exports.
"New analysis" button resets page to input state with no confirmation prompt.

**Independent Test**: After full analysis, click "Export Markdown" → verify `.md` download
contains `Score: {n}/100` on its own line and all section headings per `contracts/export-schema.md`.
Click "Export PDF" → verify PDF downloads. Click "New analysis" → verify immediate reset.

### Implementation for User Story 2

- [ ] T032 [US2] Create `backend/src/routes/export.py` — `GET /export/md?keyword={kw}` and `GET /export/pdf?keyword={kw}` endpoints; retrieves completed `AnalysisReport` from process-local state; returns 404 if report not found; MD endpoint generates Markdown from frozen schema in `contracts/export-schema.md` (score line: `Score: {n}/100`); PDF endpoint generates PDF via `fpdf2` from same content
- [ ] T033 [US2] Create `backend/src/pipeline/export_generator.py` — `generate_markdown(report: AnalysisReport) → str` following schema in `contracts/export-schema.md` exactly: heading order, score format `Score: {n}/100`, partial report flag line, N/A handling for missing sections
- [ ] T034 [US2] Create `backend/src/pipeline/pdf_generator.py` — `generate_pdf(markdown_content: str) → bytes` using `fpdf2`; renders all sections with appropriate heading sizes and body text
- [ ] T035 [P] [US2] Create `frontend/src/routes/api/export/+server.ts` — BFF proxy; `GET /api/export/md?keyword={kw}` and `GET /api/export/pdf?keyword={kw}`; forwards to FastAPI `/export/*`; passes through `Content-Disposition` header for file download
- [ ] T036 [US2] Create `frontend/src/lib/components/ExportButtons.svelte` — Svelte 5 component; renders "Export Markdown" and "Export PDF" buttons (hidden until `export_ready` received — FR-031); triggers download via anchor `href` to `/api/export/md` and `/api/export/pdf`; renders "New analysis" button that calls reset callback (no confirmation — FR-034)
- [ ] T037 [US2] Integrate `ExportButtons` into `frontend/src/routes/+page.svelte` — show below dashboard when `pageState.phase === 'complete'`; wire reset callback to reset `pageState` to initial input state

**Checkpoint**: User Stories 1 AND 2 functional — streaming dashboard + exports + new analysis reset.

---

## Phase 5: User Story 3 — Resilient Analysis under Source Unavailability (Priority: P3)

**Goal**: When one or more sources time out, the pipeline continues, delivers partial results,
and clearly informs the user which source was unavailable.

**Independent Test**: Mock Amazon timeout in backend config; enter keyword; verify
`source_unavailable` banner appears for Amazon; verify remaining sections (from Trends + Reddit)
still generate; verify export MD contains `**Partial report**: Sources unavailable: amazon`.

### Implementation for User Story 3

- [ ] T038 [US3] Verify `backend/src/pipeline/orchestrator.py` emits `source_unavailable` event for each timed-out source before emitting `marketplace_products`; verify pipeline does NOT abort when a source times out; verify `AggregatedData.unavailable_sources` is populated correctly
- [ ] T039 [US3] Verify `backend/src/pipeline/orchestrator.py` handles the case where ALL sources time out: emits `source_unavailable` × 3, then emits `export_ready` without invoking LLM; does NOT fabricate data (FR-016)
- [ ] T040 [US3] Add `source_unavailable` banner rendering to `frontend/src/lib/components/Dashboard.svelte` — accumulate `source_unavailable` events in `$state`; render one dismissible notice per unavailable source (FR-010); use shadcn-svelte `Alert` or `Badge` component
- [ ] T041 [US3] Verify `backend/src/pipeline/export_generator.py` `generate_markdown()` includes `**Partial report**: Sources unavailable: {list}` line when `report.is_partial === True` per `contracts/export-schema.md`; verify score is `Score: N/A` when viability section errored

**Checkpoint**: All 3 user stories functional — resilient pipeline with user-facing notices.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final integration, UX refinements, and validation against quickstart.

- [ ] T042 [P] Add LLM failure handling to `backend/src/pipeline/orchestrator.py` — if LLM raises mid-section, emit `LLMErrorEvent` for that section and continue to next section (FR-032 from clarification Q1); do not abort remaining sections
- [ ] T043 [P] Add visual "generation interrupted" error state to all 5 section components in `frontend/src/lib/components/sections/` — if section receives `status: "error"` event, show partial content + error notice inline (FR-032)
- [ ] T044 [P] Style dashboard for desktop readability — apply shadcn-svelte `Card` layout, consistent spacing between sections, typography scale using Svelte 5 class directives
- [ ] T045 [P] Add overall pipeline progress tracking to `frontend/src/lib/components/Dashboard.svelte` — derive progress percentage from sections completed (0% → 100%); render with shadcn-svelte `Progress` component (FR-004)
- [ ] T046 Add input validation error display to `frontend/src/lib/components/SearchForm.svelte` — show inline error message if user submits empty field (FR-003)
- [ ] T047 Run `quickstart.md` validation end-to-end: `./run.sh`, enter "eco-friendly bamboo skincare", verify all 6 acceptance criteria from quickstart.md pass; fix any integration issues found

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately; T001–T011 mostly parallel
- **Foundational (Phase 2)**: Depends on Phase 1 completion — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — all analysis + UI components can run in parallel (T019–T028), then wire together (T029–T031)
- **US2 (Phase 4)**: Depends on Phase 2 (export routes) + Phase 3 complete state (`export_ready` event); T032–T035 parallel, then T036–T037 sequential
- **US3 (Phase 5)**: Depends on Phase 2 — verify/patch existing orchestrator + frontend; all tasks independent
- **Polish (Phase 6)**: Depends on Phases 3–5 complete

### Within Each User Story

- Backend analysis modules (T019–T022) → parallel, then wire into orchestrator (T023)
- Frontend section components (T024–T028) → parallel, then wire into Dashboard (T030), then page (T031)
- Export: generator (T033–T034) → routes (T032) → frontend proxy (T035) → buttons (T036) → page integration (T037)

### Parallel Opportunities

```bash
# Phase 1 — launch all in parallel:
T001 (backend init) · T002 (frontend init) — sequential within each project
T003 T004 T005 T006 T007 T008 T009 T010 T011 — all parallel after T001/T002

# Phase 2 — parallel source scrapers, then orchestrator:
T012 T013 T014 — parallel
T015 T016 — depends on T012–T014 (orchestrator + route)
T017 T018 — parallel (frontend, independent of backend)

# Phase 3 — parallel analysis modules + parallel section components:
T019 T020 T021 T022 — parallel
T024 T025 T026 T027 T028 T029 — parallel
T023 — depends on T019–T022 (wire LLM chain)
T030 — depends on T024–T028 (Dashboard wires sections)
T031 — depends on T023 T029 T030 (main page)

# Phase 4 — parallel backend, then frontend:
T033 T034 — parallel
T032 — depends on T033 T034
T035 — parallel (frontend proxy)
T036 — depends on T035 (export buttons)
T037 — depends on T036 (page integration)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (pipeline + SSE proxy)
3. Complete Phase 3: User Story 1 (full streaming dashboard)
4. **STOP and VALIDATE**: Run quickstart.md steps 1–5 (without export step)
5. Demo if ready

### Incremental Delivery

1. Setup + Foundational → infrastructure ready
2. User Story 1 → streaming dashboard (primary demo value) 🎯
3. User Story 2 → exports + new analysis reset
4. User Story 3 → source resilience (verify/patch, mostly done by Phase 2)
5. Polish → visual finishing

### Parallel Team Strategy

With two developers after Phase 2:
- Dev A: T019–T023 (backend LLM analysis chain)
- Dev B: T024–T031 (frontend section components + main page)

---

## Notes

- `[P]` tasks = different files, no blocking dependencies — safe to parallelise
- `[Story]` label maps task to its user story for traceability
- All section component tasks (T024–T028) share the same skeleton/streaming/complete/error pattern — build one first, copy pattern
- Variable containing "state" in Svelte component names required due to svelte-check bug — use `let pageState = $state(...)` not `let data = $state(...)`
- Amazon scraping (T012) is the highest-risk task — test independently first; have mock data ready if blocked
- SSE event names are FROZEN per constitution — do not rename even for "better" names
- Export MD score line MUST be exactly `Score: {n}/100` (machine-parsable contract)
