# Tasks: Labanane — Guided Market Analysis Platform

**Input**: Design documents from `/specs/003-market-analysis-platform/`
**Prerequisites**: plan.md ✅ spec.md ✅ data-model.md ✅ contracts/ ✅ research.md ✅ quickstart.md ✅

**Testing strategy**: TDD-oriented. Each business logic function and each workflow step node has its own dedicated test task. Test tasks appear **before** their implementation counterpart. All logic layer functions are independently testable (no workflow state). All step nodes are individually testable with mocked logic dependencies.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies on incomplete tasks)
- **[Story]**: Which user story this task belongs to (US1–US4)
- All paths relative to repository root

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project directories, test infrastructure, and dependency validation.

- [x] T001 Create `backend/src/logic/` directory with `__init__.py`, `scraper.py`, `trends.py`, `analysis.py`, `export.py` stubs
- [x] T002 [P] Create `backend/tests/logic/` and `backend/tests/steps/` directories with `__init__.py` files
- [x] T003 [P] Add `pytrends`, `weasyprint`, `python-markdown` to `backend/pyproject.toml` and run `uv sync`
- [x] T004 [P] Create `backend/tests/conftest.py` with shared pytest fixtures: mock WorkflowRun, mock StepOutput, async test client for FastAPI app

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, engine infrastructure, and WebSocket plumbing. MUST be complete before any user story work begins.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T005 Implement `WorkflowStatus` enum and `WorkflowRun` dataclass (with `get_output()` method returning `{}` for missing steps) in `backend/src/workflow/run.py`
- [x] T006 Implement `StepOutput` dataclass in `backend/src/workflow/run.py`
- [x] T007 [P] Implement `Step` ABC and `StepError(message, retryable)` in `backend/src/workflow/step_base.py`
- [x] T008 [P] Implement all Pydantic server→client message models (`WorkflowStartedMessage`, `StepActivatedMessage`, `StepProcessingMessage`, `StepResultMessage`, `ConfirmationRequestMessage`, `StepErrorMessage`, `WorkflowCompleteMessage`) in `backend/src/workflow/messages.py`
- [x] T009 [P] Implement all Pydantic client→server message models (`StartMessage`, `ConfirmationMessage`, `RetryMessage`, `UserInputMessage`) in `backend/src/workflow/messages.py`
- [x] T010 [P] Implement `Product`, `KeywordSet`, `ProductBatch`, `Criterion`, `MarketAnalysis`, `FinalCriteriaData`, `ReportData` Pydantic models in `backend/src/models/report.py`
- [x] T011 [P] Implement `TimePoint`, `RegionPoint`, `QueryPoint`, `RisingPoint`, `KeywordTrends`, `TrendsData`, `MarketDataResult` dataclasses/models in `backend/src/models/workflow_models.py`
- [x] T012 [P] Implement `backend/src/config.py` with `Settings` (pydantic BaseSettings) reading `OPENAI_API_KEY` from env
- [x] T013 [P] Implement in-memory report store `ReportStore` (dict keyed by `run_id`, with `set()`, `get()`, `delete()` methods) in `backend/src/store.py`
- [x] T014 Implement `WorkflowEngine` in `backend/src/workflow/engine.py`: step sequencing, `step_activated` dispatch, loop-back routing, error recovery, WebSocket message dispatch (no business logic inline)
- [x] T015 [P] Implement `PIPELINE` list in `backend/src/workflow/registry.py` with all 9 step stubs instantiated in order
- [x] T016 [P] Implement WebSocket route handler in `backend/src/routes/workflow.py` (`/ws/workflow`): assign `run_id`, await `start`, hand off to engine
- [x] T017 [P] Implement export REST route stubs in `backend/src/routes/export.py` (`GET /api/export/{run_id}/markdown` and `GET /api/export/{run_id}/pdf`, returning 501 until US4)
- [x] T018 [P] Register all routes in `backend/src/main.py` (WebSocket + export REST + `/health`)
- [x] T019 [P] Update Zod schemas in `frontend/src/lib/workflow-types.ts` to match all shapes in `contracts/ws-messages.md` (all server message types, all data payload shapes)
- [x] T020 [P] Implement WebSocket client manager in `frontend/src/lib/ws.ts`: connect, send, receive typed messages, handle `close` event with "Connection lost" notice
- [x] T021 [P] Implement `StepRenderer.svelte` with `COMPONENTS` map routing `component_type` → Svelte component, progress indicator on `step_processing`, error display on `step_error` in `frontend/src/lib/components/StepRenderer.svelte`
- [x] T022 Unit test `WorkflowRun.get_output()`: returns `{}` for missing step, returns `data` for confirmed step, does not expose `confirmed_outputs` directly in `backend/tests/test_workflow_run.py`

**Checkpoint**: Foundation ready — user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 — Happy Path: Full Analysis from Idea to Report (Priority: P1) 🎯 MVP

**Goal**: A user can enter a product description, pass both confirmation gates without looping, and receive a final exportable report — all in one uninterrupted session.

**Independent Test**: Run the backend, open WebSocket, send `start`, confirm keywords, confirm products, observe all 9 `step_result` messages and a final `workflow_complete`.

### Tests — Logic Layer (business logic functions, individually)

> **Write these tests FIRST. Ensure they FAIL before implementing the logic functions.**

- [x] T023 [P] [US1] Test `clean_html_for_llm`: strips `<script>` and `<style>` tags, injects href text, returns non-empty string — in `backend/tests/logic/test_scraper.py`
- [x] T024 [P] [US1] Test `fetch_html`: mocked `httpx.AsyncClient` returns 200 → returns HTML string — in `backend/tests/logic/test_scraper.py`
- [x] T025 [P] [US1] Test `fetch_html`: mocked client returns 503 → retries once → success on second attempt — in `backend/tests/logic/test_scraper.py`
- [x] T026 [P] [US1] Test `parse_marketplace_data`: mocked OpenHosta LLM returns valid JSON → returns `list[Product]` with all required fields (`title`, `price`, `url`, `rating_stars`, `rating_count`, `main_features`) — in `backend/tests/logic/test_scraper.py`
- [x] T027 [P] [US1] Test `parse_marketplace_data`: `rating_stars` is float 0.0–5.0, `rating_count` is int ≥ 0, `main_features` has exactly 3 strings — in `backend/tests/logic/test_scraper.py`
- [x] T028 [P] [US1] Test `fetch_trends`: mocked `pytrends.TrendReq` returns DataFrames → result has `keywords`, `trends` dict keyed by keyword, each value is `KeywordTrends` with all 4 list fields — in `backend/tests/logic/test_trends.py`
- [x] T029 [P] [US1] Test `fetch_trends`: `interest_over_time` values are int 0–100, `interest_by_region` entries have `geo`, `name`, `value` — in `backend/tests/logic/test_trends.py`
- [x] T030 [P] [US1] Test `fetch_trends`: mocked rate-limit error (`ResponseError`) triggers backoff and retry — in `backend/tests/logic/test_trends.py`
- [x] T031 [P] [US1] Test `generate_search_queries`: mocked OpenHosta returns 3 strings → result is `list[str]` with 3–5 non-empty entries — in `backend/tests/logic/test_analysis.py`
- [x] T032 [P] [US1] Test `generate_market_analysis`: mocked LLM returns valid JSON → result is `MarketAnalysis` with `viability_score` in 0–100, `go_no_go` in `{"go","no-go","conditional"}`, `criteria` list has 3–5 items each with `label` and `score` — in `backend/tests/logic/test_analysis.py`
- [x] T033 [P] [US1] Test `generate_market_analysis`: `key_risks` and `key_opportunities` each have exactly 3 items — in `backend/tests/logic/test_analysis.py`
- [x] T034 [P] [US1] Test `generate_market_analysis`: `target_persona.description` is non-empty string, `differentiation_angles.content` is non-empty, `competitive_overview.content` is non-empty — in `backend/tests/logic/test_analysis.py`

### Tests — Workflow Step Nodes (each step individually)

> **Each step is tested in isolation with mocked logic dependencies and a fake WorkflowRun.**

- [x] T035 [P] [US1] Test `ProductDescriptionStep.execute()`: given `user_input` message with non-empty description, yields one `StepResultMessage` with `component_type="keyword_list"` placeholder — in `backend/tests/steps/test_step_s01.py`
- [x] T036 [P] [US1] Test `ProductDescriptionStep.execute()`: step `step_type` is `"user_input"` and `step_id` is `"product_description"` — in `backend/tests/steps/test_step_s01.py`
- [x] T037 [P] [US1] Test `KeywordRefinementStep.execute()`: mocked `generate_search_queries` → yields `StepProcessingMessage` then `StepResultMessage` with `keywords` list — in `backend/tests/steps/test_step_s02.py`
- [x] T038 [P] [US1] Test `KeywordRefinementStep.execute()`: `step_type` is `"derivation"`, passes product description from `run.description` to logic function — in `backend/tests/steps/test_step_s02.py`
- [x] T039 [P] [US1] Test `KeywordConfirmationStep.execute()`: yields `ConfirmationRequestMessage` with `step_id="keyword_confirmation"` and non-empty `prompt` — in `backend/tests/steps/test_step_s03.py`
- [x] T040 [P] [US1] Test `KeywordConfirmationStep`: `step_type` is `"confirmation"`, `component_type` is `"confirmation"` — in `backend/tests/steps/test_step_s03.py`
- [x] T041 [P] [US1] Test `ProductResearchStep.execute()`: yields `StepProcessingMessage` before `StepResultMessage` — in `backend/tests/steps/test_step_s04.py`
- [x] T042 [P] [US1] Test `ProductResearchStep.execute()`: mocked `fetch_html` + `parse_marketplace_data` → `StepResultMessage` `data` contains `products` list and `source_keywords` from `run.get_output("keyword_confirmation")` — in `backend/tests/steps/test_step_s04.py`
- [x] T043 [P] [US1] Test `ProductResearchStep`: calls `run.get_output("keyword_confirmation")` to retrieve keywords (never accesses `run.confirmed_outputs` directly) — in `backend/tests/steps/test_step_s04.py`
- [x] T044 [P] [US1] Test `ProductValidationStep.execute()`: yields `ConfirmationRequestMessage` with `step_id="product_validation"` — in `backend/tests/steps/test_step_s05.py`
- [x] T045 [P] [US1] Test `MarketResearchStep.execute()`: yields `StepProcessingMessage` before `StepResultMessage` — in `backend/tests/steps/test_step_s06.py`
- [x] T046 [P] [US1] Test `MarketResearchStep.execute()`: mocked `fetch_trends` → `StepResultMessage` `data` is `MarketDataResult` with `keywords`, `sources_available`, `sources_unavailable`, `trends` dict — in `backend/tests/steps/test_step_s06.py`
- [x] T047 [P] [US1] Test `MarketResearchStep`: reads keywords from `run.get_output("keyword_confirmation")`, not inline — in `backend/tests/steps/test_step_s06.py`
- [x] T048 [P] [US1] Test `AiAnalysisStep.execute()`: yields `StepProcessingMessage` before `StepResultMessage` — in `backend/tests/steps/test_step_s07.py`
- [x] T049 [P] [US1] Test `AiAnalysisStep.execute()`: reads `keywords` from `run.get_output("keyword_confirmation")` and `products` from `run.get_output("product_validation")` — in `backend/tests/steps/test_step_s07.py`
- [x] T050 [P] [US1] Test `AiAnalysisStep.execute()`: mocked `generate_market_analysis` → `StepResultMessage` `data` is `AiAnalysisData` with `viability_score`, `go_no_go`, `criteria`, `target_persona`, `differentiation_angles`, `competitive_overview` — in `backend/tests/steps/test_step_s07.py`
- [x] T051 [P] [US1] Test `FinalCriteriaStep.execute()`: reads `ai_analysis` output from prior step input, yields `StepResultMessage` with `FinalCriteriaData` containing `summary`, `go_no_go`, `key_risks`, `key_opportunities` — in `backend/tests/steps/test_step_s08.py`
- [x] T052 [P] [US1] Test `FinalCriteriaStep`: `step_type` is `"derivation"`, no external logic calls — in `backend/tests/steps/test_step_s08.py`
- [x] T053 [P] [US1] Test `ReportGenerationStep.execute()`: calls `render_markdown` with full run data, writes to `ReportStore`, yields `StepResultMessage` with `markdown_available=True` — in `backend/tests/steps/test_step_s09.py`
- [x] T054 [P] [US1] Test `ReportGenerationStep`: report stored under correct `run_id` in `ReportStore` and is non-empty string — in `backend/tests/steps/test_step_s09.py`

### Tests — Integration

- [x] T055 [P] [US1] Integration test: full happy-path WebSocket session (start → confirm keywords → confirm products → workflow_complete), all 9 `step_activated` messages emitted in order with correct `step_id` values — in `backend/tests/test_ws_happy_path.py`
- [x] T056 [P] [US1] Integration test: all `step_result` messages have a `component_type` matching the contract table in `ws-messages.md` — in `backend/tests/test_ws_contract.py`
- [x] T057 [P] [US1] Integration test: `workflow_complete` message carries the correct `run_id` matching the session UUID — in `backend/tests/test_ws_contract.py`

### Implementation — Logic Layer

- [x] T058 [US1] Implement `clean_html_for_llm(raw_html: str) -> str` (strip script/style, inject link text) and `fetch_html(source: str, query: str) -> str` (async httpx, silent retry on 503) in `backend/src/logic/scraper.py`
- [x] T059 [US1] Implement `parse_marketplace_data(cleaned_html: str) -> list[Product]` (OpenHosta `emulate_async()` → structured `list[Product]`) in `backend/src/logic/scraper.py`
- [x] T060 [US1] Implement `fetch_trends(keywords: list[str]) -> TrendsData` (async pytrends with backoff, returns typed `TrendsData` with all 4 per-keyword series) in `backend/src/logic/trends.py`
- [x] T061 [US1] Implement `generate_search_queries(description: str) -> list[str]` (OpenHosta LLM → 3–5 keywords) in `backend/src/logic/analysis.py`
- [x] T062 [US1] Implement `generate_market_analysis(description, products, trends) -> MarketAnalysis` (OpenHosta LLM → structured `MarketAnalysis` with all sub-models) in `backend/src/logic/analysis.py`

### Implementation — Workflow Steps

- [x] T063 [US1] Implement `ProductDescriptionStep` (step_type: user_input, stores description in run) in `backend/src/workflow/steps/s01_description.py`
- [x] T064 [US1] Implement `KeywordRefinementStep` (step_type: derivation, calls `generate_search_queries`, yields step_result) in `backend/src/workflow/steps/s02_keyword_refinement.py`
- [x] T065 [US1] Implement `KeywordConfirmationStep` (step_type: confirmation, yields confirmation_request) in `backend/src/workflow/steps/s03_keyword_confirmation.py`
- [x] T066 [US1] Implement `ProductResearchStep` (step_type: system_processing, reads keywords via `run.get_output`, calls `fetch_html` + `parse_marketplace_data`, yields step_processing then step_result) in `backend/src/workflow/steps/s04_product_research.py`
- [x] T067 [US1] Implement `ProductValidationStep` (step_type: confirmation, yields confirmation_request) in `backend/src/workflow/steps/s05_product_validation.py`
- [x] T068 [US1] Implement `MarketResearchStep` (step_type: system_processing, reads keywords via `run.get_output`, calls `fetch_trends`, serialises to `MarketDataResult`, yields step_processing then step_result) in `backend/src/workflow/steps/s06_market_research.py`
- [x] T069 [US1] Implement `AiAnalysisStep` (step_type: system_processing, reads keywords + products via `run.get_output`, calls `generate_market_analysis`, yields step_processing then step_result) in `backend/src/workflow/steps/s07_ai_analysis.py`
- [x] T070 [US1] Implement `FinalCriteriaStep` (step_type: derivation, extracts `FinalCriteriaData` from step 7 output, yields step_result) in `backend/src/workflow/steps/s08_final_criteria.py`
- [x] T071 [US1] Implement `ReportGenerationStep` (step_type: derivation, collects all prior outputs, calls `render_markdown`, writes to `ReportStore`, yields step_result with `markdown_available=True`) in `backend/src/workflow/steps/s09_report.py`

### Implementation — Frontend

- [x] T072 [P] [US1] Implement `StepKeywordList.svelte`: renders keyword chips from `keywords` array in `frontend/src/lib/components/steps/StepKeywordList.svelte`
- [x] T073 [P] [US1] Implement `StepConfirmation.svelte`: Yes/No buttons, sends `confirmation` message via `ws.ts` in `frontend/src/lib/components/steps/StepConfirmation.svelte`
- [x] T074 [P] [US1] Implement `InterestOverTimeChart.svelte`: layerchart `Line` chart with multi-keyword series from `interest_over_time` in `frontend/src/lib/components/charts/InterestOverTimeChart.svelte`
- [x] T075 [P] [US1] Implement `InterestByRegionChart.svelte`: layerchart horizontal `Bar` chart from `interest_by_region` top 10 in `frontend/src/lib/components/charts/InterestByRegionChart.svelte`
- [x] T076 [P] [US1] Implement `RelatedQueriesChart.svelte`: layerchart horizontal `Bar` chart from `related_queries_top` in `frontend/src/lib/components/charts/RelatedQueriesChart.svelte`
- [x] T077 [P] [US1] Implement `StepProductList.svelte`: product cards with title/price/URL/features + rating comparison bar chart + review volume bar chart (layerchart) in `frontend/src/lib/components/steps/StepProductList.svelte`
- [x] T078 [P] [US1] Implement `StepMarketData.svelte`: integrates `InterestOverTimeChart`, `InterestByRegionChart`, `RelatedQueriesChart`, and rising query callout cards in `frontend/src/lib/components/steps/StepMarketData.svelte`
- [x] T079 [P] [US1] Implement `StepAiAnalysis.svelte`: displays viability score donut, criteria bar chart, summary, persona, differentiation angles, competitive overview in `frontend/src/lib/components/steps/StepAiAnalysis.svelte`
- [x] T080 [P] [US1] Implement `StepFinalCriteria.svelte`: go/no-go badge, summary, key risks, key opportunities, viability donut and criteria bar in `frontend/src/lib/components/steps/StepFinalCriteria.svelte`
- [x] T081 [P] [US1] Implement `StepReport.svelte`: inline report markdown preview, export buttons (disabled until `markdown_available=true`) in `frontend/src/lib/components/steps/StepReport.svelte`
- [x] T082 [US1] Implement `frontend/src/routes/workflow/+page.svelte`: step progress bar (current/total), step history panel, WS lifecycle (connect on mount, disconnect notice on close), dispatch to `StepRenderer`

**Checkpoint**: User Story 1 fully functional. End-to-end happy path should work with real LLM + scraping calls.

---

## Phase 4: User Story 2 — Keyword Refinement Loop (Priority: P2)

**Goal**: A user can reject keyword suggestions, edit their description, and receive a fresh set — without losing their place in the workflow.

**Independent Test**: Send `confirmation(keyword_confirmation, confirmed=false)` → engine resets to step 1 → send revised `user_input` → new `step_result` with new keywords appears.

### Tests — Keyword Loop Behaviour

- [x] T083 [P] [US2] Test engine routes `confirmation(keyword_confirmation, confirmed=false)` to loop-back: resets `current_step_index` to `product_description` step index — in `backend/tests/test_engine.py`
- [x] T084 [P] [US2] Test `KeywordConfirmationStep`: when engine processes rejection, no `StepError` is raised and loop-back target is `product_description` — in `backend/tests/steps/test_step_s03.py`
- [x] T085 [P] [US2] Test WebSocket session: reject keywords → send new description via `user_input` → new `step_result` with fresh `keywords` list (previous keywords replaced) — in `backend/tests/test_ws_keyword_loop.py`
- [x] T086 [P] [US2] Test WebSocket session: after 3 keyword rejections, engine includes a hint string in the next `step_activated` or `step_result` message — in `backend/tests/test_ws_keyword_loop.py`
- [x] T087 [P] [US2] Test frontend: on loop-back to step 1, `user_input` message from server carries current description pre-filled — in `backend/tests/test_ws_keyword_loop.py`

### Implementation — Keyword Loop

- [x] T088 [US2] Implement keyword_confirmation rejection loop-back in `backend/src/workflow/engine.py`: on `confirmed=false`, reset `current_step_index` to `product_description`, preserve `run.description`
- [x] T089 [US2] Implement 3-rejection hint logic in engine: after 3 rejections of keyword_confirmation, append hint field to next step message in `backend/src/workflow/engine.py`
- [ ] T090 [US2] Update `frontend/src/routes/workflow/+page.svelte` to pre-fill description textarea when engine loops back to product_description step

**Checkpoint**: Users can refine keywords. US1 happy path still passes.

---

## Phase 5: User Story 3 — Product Validation Loop (Priority: P3)

**Goal**: A user can reject found products and trigger a fresh product research pass with the same confirmed keywords.

**Independent Test**: Send `confirmation(product_validation, confirmed=false)` → engine re-runs `product_research` with original keywords → new `step_result` with fresh product batch.

### Tests — Product Validation Loop Behaviour

- [x] T091 [P] [US3] Test engine routes `confirmation(product_validation, confirmed=false)` to re-run: resets `current_step_index` to `product_research` step index — in `backend/tests/test_engine.py`
- [x] T092 [P] [US3] Test engine: confirmed keywords from `keyword_confirmation` are NOT cleared when product_validation is rejected — in `backend/tests/test_engine.py`
- [x] T093 [P] [US3] Test `ProductResearchStep` on re-run: reads keywords from `run.get_output("keyword_confirmation")` (same confirmed keywords), ignores prior `product_research` output — in `backend/tests/steps/test_step_s04.py`
- [x] T094 [P] [US3] Test WebSocket session: reject products → engine re-emits `step_activated(product_research)` + `step_processing` → new `step_result` with fresh products list — in `backend/tests/test_ws_product_loop.py`
- [x] T095 [P] [US3] Test WebSocket session: confirm fresh products → market research starts with new product set, not previous rejected batch — in `backend/tests/test_ws_product_loop.py`

### Implementation — Product Validation Loop

- [x] T096 [US3] Implement product_validation rejection loop-back in `backend/src/workflow/engine.py`: on `confirmed=false`, reset `current_step_index` to `product_research`, preserve `keyword_confirmation` output
- [x] T097 [US3] Update `StepProductList.svelte` to display refreshed product batch on re-run, clearing previous results in `frontend/src/lib/components/steps/StepProductList.svelte`

**Checkpoint**: Users can reject and redo product research. US1 + US2 still pass.

---

## Phase 6: User Story 4 — Export the Report (Priority: P4)

**Goal**: After a completed workflow, the user can download the report as a Markdown file and as a PDF.

**Independent Test**: Complete a full workflow, then `GET /api/export/{run_id}/markdown` → 200 with `Score: NN/100` line; `GET /api/export/{run_id}/pdf` → 200 `application/pdf`.

### Tests — Export Logic

- [x] T098 [P] [US4] Test `render_markdown`: output starts with `# Market Analysis: {description}` heading — in `backend/tests/logic/test_export.py`
- [x] T099 [P] [US4] Test `render_markdown`: output contains `Score: {viability_score}/100` on its own line (machine-parseable, starts exactly with `Score: `) — in `backend/tests/logic/test_export.py`
- [x] T100 [P] [US4] Test `render_markdown`: output contains all required section headings: `Keywords Used`, `Marketplace Products`, `Market Trends`, `Viability Score`, `Go / No-Go`, `Target Persona`, `Differentiation Angles`, `Competitive Overview`, `Key Risks`, `Key Opportunities`, `Scoring Criteria` — in `backend/tests/logic/test_export.py`
- [x] T101 [P] [US4] Test `render_markdown`: products table has `Product`, `Price`, `Rating`, `Reviews` columns — in `backend/tests/logic/test_export.py`
- [x] T102 [P] [US4] Test `render_markdown`: `**Verdict**: go|no-go|conditional` field present in header block — in `backend/tests/logic/test_export.py`
- [x] T103 [P] [US4] Test `render_pdf`: returns `bytes` starting with `%PDF` magic bytes for valid markdown input — in `backend/tests/logic/test_export.py`
- [x] T104 [P] [US4] Test `render_pdf`: returns non-empty bytes for empty but syntactically valid markdown string — in `backend/tests/logic/test_export.py`

### Tests — Export REST Endpoints

- [x] T105 [P] [US4] Test `GET /api/export/{run_id}/markdown` returns 200 with `Content-Type: text/markdown` and `Content-Disposition: attachment` for a completed run — in `backend/tests/test_export_endpoints.py`
- [x] T106 [P] [US4] Test `GET /api/export/{run_id}/pdf` returns 200 with `Content-Type: application/pdf` for a completed run — in `backend/tests/test_export_endpoints.py`
- [x] T107 [P] [US4] Test export endpoints return 404 for unknown `run_id` — in `backend/tests/test_export_endpoints.py`
- [x] T108 [P] [US4] Test export endpoints return 404 when workflow has not yet reached `complete` status (report not yet in store) — in `backend/tests/test_export_endpoints.py`
- [x] T109 [P] [US4] Test `ReportStore.delete()` is called when WebSocket disconnects (report discarded on session end) — in `backend/tests/test_export_endpoints.py`

### Implementation — Export

- [x] T110 [US4] Implement `render_markdown(run_data: dict) -> str` following the exact schema in `contracts/export-schema.md` in `backend/src/logic/export.py`
- [x] T111 [US4] Implement `render_pdf(markdown: str) -> bytes` (markdown → python-markdown HTML → weasyprint PDF bytes, with "Charts available in browser" header note) in `backend/src/logic/export.py`
- [x] T112 [US4] Implement `GET /api/export/{run_id}/markdown` endpoint (reads from `ReportStore`, returns `text/markdown` with `Content-Disposition: attachment; filename="analysis-{run_id}.md"`) in `backend/src/routes/export.py`
- [x] T113 [US4] Implement `GET /api/export/{run_id}/pdf` endpoint (renders PDF from stored markdown, returns `application/pdf` attachment) in `backend/src/routes/export.py`
- [x] T114 [US4] Update WebSocket disconnect handler to call `ReportStore.delete(run_id)` in `backend/src/routes/workflow.py`
- [x] T115 [US4] Update `StepReport.svelte` export buttons to fetch from `/api/export/{run_id}/markdown` and `/api/export/{run_id}/pdf` and trigger browser download in `frontend/src/lib/components/steps/StepReport.svelte`

**Checkpoint**: Full export working. All 4 user stories independently testable.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Resilience, error handling, and end-to-end validation per spec edge cases.

### Resilience Tests

- [x] T116 [P] Test Amazon auto-retry: mocked `httpx` returns 503 twice then 200 → `fetch_html` succeeds without surfacing error — in `backend/tests/logic/test_scraper.py`
- [x] T117 [P] Test Amazon retry exhausted: mocked `httpx` returns 503 three times → `ProductResearchStep` raises `StepError(retryable=True)` — in `backend/tests/steps/test_step_s04.py`
- [x] T118 [P] Test Google Trends unavailable: mocked pytrends raises `ResponseError` → `fetch_trends` returns `TrendsData` with empty `trends` dict — in `backend/tests/logic/test_trends.py`
- [x] T119 [P] Test `MarketResearchStep` with unavailable Trends: yields `step_result` with `sources_unavailable=["google_trends"]` and empty `trends` dict — in `backend/tests/steps/test_step_s06.py`
- [x] T120 [P] Test zero products found: `ProductResearchStep` raises `StepError` with message "No products found — please refine your description" — in `backend/tests/steps/test_step_s04.py`
- [x] T121 [P] Test engine auto-loops to `product_description` on zero-products `StepError` from `product_research` — in `backend/tests/test_engine.py`
- [x] T122 [P] Test `AiAnalysisStep` raises `StepError(retryable=False)` when both `products` and `trends` are empty (FR-018c: no analysis without real data) — in `backend/tests/steps/test_step_s07.py`

### Resilience Implementation

- [ ] T123 Implement 2× silent retry with randomised 2–5s delay on 503/CAPTCHA responses in `backend/src/logic/scraper.py`
- [x] T124 Implement Google Trends unavailability handling: catch `ResponseError`, return empty `TrendsData`, populate `sources_unavailable` in `backend/src/logic/trends.py`
- [ ] T125 Implement zero-products auto-loop in `backend/src/workflow/engine.py`: catch `StepError` from `product_research` with "No products found" → emit `step_error` → loop to `product_description`
- [x] T126 Enforce FR-018c in `AiAnalysisStep`: raise `StepError(retryable=False)` if both products and trends are empty in `backend/src/workflow/steps/s07_ai_analysis.py`
- [x] T127 [P] Implement partial-results notice in `StepMarketData.svelte` when `sources_unavailable` is non-empty in `frontend/src/lib/components/steps/StepMarketData.svelte`
- [ ] T128 [P] Implement Retry button in `StepRenderer.svelte` for `step_error` messages with `retryable=true` in `frontend/src/lib/components/StepRenderer.svelte`
- [ ] T129 [P] Implement WebSocket `close` event handler in `frontend/src/lib/ws.ts` displaying "Connection lost — please start a new analysis"
- [x] T130 Run `uv run pytest backend/tests/ -v` and confirm all tests pass with zero failures

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **User Stories (Phases 3–6)**: All depend on Phase 2
  - US1 (P1) → must complete before US2/US3 (they extend it)
  - US2 (P2) and US3 (P3) depend on US1 engine loop-back work
  - US4 (P4) depends on US1 (report step must exist)
- **Polish (Phase 7)**: Depends on all user stories complete

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2 — no dependency on other stories
- **US2 (P2)**: Starts after US1 — extends engine with loop-back; re-uses step wiring
- **US3 (P3)**: Starts after US1 — extends engine with product re-run; can be done in parallel with US2
- **US4 (P4)**: Starts after US1 — depends on `ReportGenerationStep` and `ReportStore` from US1

### Within Each Story

- Tests (prefixed before implementation) MUST be written and FAIL before implementation
- Logic layer → Step layer → Routes → Frontend
- Core step → Error handling → Integration test

### Parallel Opportunities

- T002, T003, T004 can run together (Phase 1)
- T005–T021 (Phase 2) — all except T005 (WorkflowRun) and T014 (engine) can run in parallel once T005 is done
- T023–T057 (US1 tests) all marked [P] — launch all at once after foundational phase
- T063–T071 (US1 step implementations) run sequentially (each step may depend on prior model)
- T072–T081 (US1 frontend components) all marked [P] — run in parallel
- US2 tests (T083–T087) and US3 tests (T091–T095) can run in parallel after US1 engine implementation

---

## Parallel Example: User Story 1 Logic Tests

```bash
# All logic layer tests can be written and run in parallel (different files):
Task: T023–T027 → backend/tests/logic/test_scraper.py
Task: T028–T030 → backend/tests/logic/test_trends.py
Task: T031–T034 → backend/tests/logic/test_analysis.py

# All step tests can be written in parallel (each in its own file):
Task: T035–T036 → backend/tests/steps/test_step_s01.py
Task: T037–T038 → backend/tests/steps/test_step_s02.py
Task: T039–T040 → backend/tests/steps/test_step_s03.py
Task: T041–T043 → backend/tests/steps/test_step_s04.py
Task: T044       → backend/tests/steps/test_step_s05.py
Task: T045–T047 → backend/tests/steps/test_step_s06.py
Task: T048–T050 → backend/tests/steps/test_step_s07.py
Task: T051–T052 → backend/tests/steps/test_step_s08.py
Task: T053–T054 → backend/tests/steps/test_step_s09.py
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — blocks all stories)
3. Complete Phase 3: User Story 1 (T023–T082)
4. **STOP and VALIDATE**: Run pytest, open browser, complete full happy path
5. Demo if ready

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. User Story 1 → test independently → Demo (MVP!)
3. User Story 2 → keyword loop works → Demo
4. User Story 3 → product redo works → Demo
5. User Story 4 → export downloads → Demo
6. Polish → all edge cases handled → Production-ready

### Suggested MVP Scope

**US1 only** — covers: description → keywords → confirmation → products → confirmation → market data → AI analysis → criteria → report (inline view).

Export (US4) is the second most valuable addition; US2 and US3 are quality gates that protect the analysis output.

---

## Notes

- [P] = different files, no incomplete task dependencies — safe to parallelise
- Each step test file is fully independent — mock `WorkflowRun`, mock logic functions, collect generator output
- Logic functions are pure async — test with `pytest-asyncio`, mock `httpx` and `pytrends` via `unittest.mock.patch`
- Confirm `pytest-asyncio` is in dev dependencies in `backend/pyproject.toml`
- `step_streaming_token` message type does NOT exist — do not implement
- Steps MUST call `run.get_output("step_id")` — never `run.confirmed_outputs[key]` directly
- All scraping, LLM calls, and data transformation MUST live in `backend/src/logic/` only
- Export endpoints require `run_id` from `workflow_complete` WebSocket message
