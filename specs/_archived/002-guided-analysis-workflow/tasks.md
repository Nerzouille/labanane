# Tasks: Guided Analysis Workflow

**Input**: Design documents from `/specs/002-guided-analysis-workflow/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, contracts/ ✓, quickstart.md ✓

**Tests**: TDD — test tasks are included. Write tests FIRST and ensure they FAIL before implementing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story (US1–US4)
- All paths are absolute relative to repo root

---

## Phase 1: Setup

**Purpose**: Create workflow module directories and register the new WebSocket route.

- [x] T001 Create backend workflow module directories: `backend/src/workflow/`, `backend/src/workflow/steps/`, `backend/src/tests/` (add `__init__.py` to each)
- [x] T002 Create frontend workflow route directory: `frontend/src/routes/workflow/` and component directories `frontend/src/lib/components/steps/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core shared infrastructure — WebSocket message contracts, abstract Step interface, and WorkflowRun state model. ALL user stories depend on this phase.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 [P] Implement all Pydantic WS server→client and client→server message models (WorkflowStartedMessage, StepActivatedMessage, StepProcessingMessage, StepStreamingTokenMessage, StepResultMessage, ConfirmationRequestMessage, StepErrorMessage, WorkflowCompleteMessage, StartMessage, ConfirmationMessage, RetryMessage, UserInputMessage) in `backend/src/workflow/messages.py`
- [x] T004 [P] Implement WorkflowRun dataclass with fields: run_id, status (WorkflowStatus enum: idle/running/awaiting_confirmation/complete/error), current_step_index, total_steps, confirmed_outputs dict, created_at in `backend/src/workflow/run.py`
- [x] T005 Implement abstract Step base class with abstract properties (step_id, label, step_type, component_type) and abstract execute() async generator method; implement StepError exception class in `backend/src/workflow/step_base.py` (depends on T003, T004)
- [x] T006 Register WebSocket route `/ws/workflow` in `backend/src/main.py` by importing and including the workflow router (router file will be created in Phase 3)
- [x] T007 [P] Implement Zod schemas for all server→client WS messages (WorkflowStartedSchema, StepActivatedSchema, StepProcessingSchema, StepStreamingTokenSchema, StepResultSchema, ConfirmationRequestSchema, StepErrorSchema, WorkflowCompleteSchema) and inferred TypeScript types in `frontend/src/lib/workflow-types.ts`
- [x] T008 Implement WebSocket client abstraction: `createWorkflowConnection(url, callbacks)` — opens WS, validates incoming messages with Zod, dispatches to typed callbacks, returns `{ send(msg), close() }` in `frontend/src/lib/ws.ts` (depends on T007)

**Checkpoint**: Foundation ready — user story phases can now begin.

---

## Phase 3: User Story 1 — Happy Path: Full 9-Step Run (Priority: P1) 🎯 MVP

**Goal**: A user can enter a product description, confirm keywords, confirm products, and receive a final report — all in one uninterrupted session with progress visible at every step.

**Independent Test**: Connect WebSocket, send `start`, confirm at steps 3 and 5, verify `workflow_complete` is received after 9 `step_activated` messages with step_numbers 1→9.

### Tests for User Story 1 (TDD — write FIRST, verify they FAIL)

- [x] T009 [P] [US1] Write WS contract test: assert `workflow_started` is first message after `start`, total_steps=9, step_ids array has 9 entries in `backend/src/tests/test_ws_contract.py`
- [x] T010 [P] [US1] Write happy path integration test: connect WS → start → confirm step 3 (yes) → confirm step 5 (yes) → assert all 9 step_activated messages received in order → assert workflow_complete in `backend/src/tests/test_ws_happy_path.py`

### Implementation for User Story 1

- [x] T011 [P] [US1] Implement ProductDescriptionStep (step_id: product_description, type: user_input, component_type: product_description_input) — yields step_result with the description data in `backend/src/workflow/steps/s01_description.py`
- [x] T012 [P] [US1] Implement KeywordRefinementStep stub (step_id: keyword_refinement, type: derivation, component_type: keyword_list) — yields step_result with 3 hardcoded keywords (NotImplementedError body, stub for now) in `backend/src/workflow/steps/s02_keyword_refinement.py`
- [x] T013 [P] [US1] Implement KeywordConfirmationStep (step_id: keyword_confirmation, type: confirmation, component_type: keyword_confirmation) — yields confirmation_request with prompt + keywords; engine pauses here in `backend/src/workflow/steps/s03_keyword_confirmation.py`
- [x] T014 [P] [US1] Implement ProductResearchStep stub (step_id: product_research, type: system_processing, component_type: product_list) — yields step_processing then step_result with 3 placeholder products in `backend/src/workflow/steps/s04_product_research.py`
- [x] T015 [P] [US1] Implement ProductValidationStep (step_id: product_validation, type: confirmation, component_type: product_confirmation) — yields confirmation_request with prompt + products in `backend/src/workflow/steps/s05_product_validation.py`
- [x] T016 [P] [US1] Implement MarketResearchStep stub (step_id: market_research, type: system_processing, component_type: market_data_summary) — yields step_processing then step_result with placeholder market data in `backend/src/workflow/steps/s06_market_research.py`
- [x] T017 [P] [US1] Implement AiAnalysisStep stub (step_id: ai_analysis, type: system_processing, component_type: analysis_stream) — yields step_processing then 3 step_streaming_token messages then step_result with complete=true in `backend/src/workflow/steps/s07_ai_analysis.py`
- [x] T018 [P] [US1] Implement FinalCriteriaStep stub (step_id: final_criteria, type: derivation, component_type: final_criteria) — yields step_result with placeholder go_no_go, key_risks, key_opportunities in `backend/src/workflow/steps/s08_final_criteria.py`
- [x] T019 [P] [US1] Implement ReportGenerationStep stub (step_id: report_generation, type: derivation, component_type: report) — yields step_result with run_id and markdown_available=false in `backend/src/workflow/steps/s09_report.py`
- [x] T020 [US1] Assemble PIPELINE list with all 9 step instances in `backend/src/workflow/registry.py` (depends on T011–T019)
- [x] T021 [US1] Implement WorkflowEngine.run(): iterate PIPELINE, send step_activated before each step, call step.execute(), pipe StepOutput to next step, send workflow_complete after last step; handle awaiting_confirmation pause (block until confirmation message arrives via asyncio.Queue) in `backend/src/workflow/engine.py` (depends on T005, T020)
- [x] T022 [US1] Implement WebSocket route: `@router.websocket("/ws/workflow")` — assign run_id UUID on connect, create WorkflowRun, feed incoming messages to asyncio.Queue, call WorkflowEngine.run(), handle WebSocketDisconnect cleanup in `backend/src/routes/workflow.py` (depends on T006, T021)
- [x] T023 [P] [US1] Create StepRenderer.svelte: static COMPONENTS map keyed by component_type string, use $derived to resolve current component, render it with data and onAction props in `frontend/src/lib/components/StepRenderer.svelte`
- [x] T024 [P] [US1] Create all non-confirmation step display components (StepDescriptionInput, StepKeywordList, StepProductList, StepMarketData, StepAnalysisStream, StepFinalCriteria, StepReport) as minimal Svelte 5 components receiving `data` and `onAction` props in `frontend/src/lib/components/steps/` directory
- [x] T025 [P] [US1] Create StepConfirmation.svelte: displays prompt + data summary, renders Yes/No buttons, calls onAction({ confirmed: true/false }) in `frontend/src/lib/components/steps/StepConfirmation.svelte`
- [x] T026 [US1] Create workflow page: Svelte 5 `let pageState = $state({...})`, connect WebSocket via ws.ts, dispatch incoming messages to pageState updates, render step list with StepRenderer for each step_result/confirmation_request, show step_number/total_steps progress in `frontend/src/routes/workflow/+page.svelte` (depends on T008, T023, T024, T025)

**Checkpoint**: Full 9-step workflow functional end-to-end — connect WebSocket, submit description, confirm twice, receive workflow_complete.

---

## Phase 4: User Story 2 — Keyword Refinement Loop (Priority: P2)

**Goal**: A user who rejects keyword suggestions at step 3 is returned to step 1 with their description pre-filled, and can generate new keywords.

**Independent Test**: Send start → reach step 3 confirmation → send `confirmed: false` → assert next `step_activated` has step_id=product_description and step_number=1.

### Tests for User Story 2 (TDD — write FIRST, verify they FAIL)

- [ ] T027 [US2] Write loop-back test: confirm=false at keyword_confirmation → assert step_activated(product_description, step_number=1) is next message; then resend user_input → workflow continues from step 1 in `backend/src/tests/test_ws_loops.py`

### Implementation for User Story 2

- [ ] T028 [US2] Add loop-back handling to WorkflowEngine: when confirmation(confirmed=false) is received for step_id=keyword_confirmation, reset current_step_index to 0 (product_description) and continue the run loop in `backend/src/workflow/engine.py`
- [ ] T029 [US2] Update workflow page to handle loop-back: when step_activated arrives with step_id=product_description after a prior confirmation, pre-fill the description input with previous value in `frontend/src/routes/workflow/+page.svelte`

**Checkpoint**: Keyword rejection loop works — user can loop back and re-enter description.

---

## Phase 5: User Story 3 — Product Validation Loop (Priority: P3)

**Goal**: A user who rejects product research results at step 5 triggers a fresh product research pass using the same confirmed keywords.

**Independent Test**: Reach step 5 → send `confirmed: false` → assert next `step_activated` has step_id=product_research and step_number=4 → new products are presented.

### Tests for User Story 3 (TDD — write FIRST, verify they FAIL)

- [ ] T030 [US3] Write product loop test: confirm=false at product_validation → assert step_activated(product_research, step_number=4); verify confirmed keywords from step 3 are still in WorkflowRun.confirmed_outputs in `backend/src/tests/test_ws_loops.py`

### Implementation for User Story 3

- [ ] T031 [US3] Add product validation loop-back to WorkflowEngine: when confirmation(confirmed=false) is received for step_id=product_validation, reset current_step_index to 3 (product_research) without clearing confirmed keyword output in `backend/src/workflow/engine.py`
- [ ] T032 [US3] Update workflow page: discard previous product_list step_result on loop-back (so stale products are not shown) and re-render fresh product results when new step_result arrives in `frontend/src/routes/workflow/+page.svelte`

**Checkpoint**: Both confirmation loops (step 3 and step 5) work correctly.

---

## Phase 6: User Story 4 — Workflow Step Insertion (Priority: P4)

**Goal**: A new step can be inserted at any position in PIPELINE and the workflow executes in the new order with correct step numbering and data piping.

**Independent Test**: Insert a stub FilterStep between index 3 and 4, run the workflow, assert step_number goes 1→2→3→4(new)→5→…→10, and each step receives the previous step's output as input.

### Tests for User Story 4 (TDD — write FIRST, verify they FAIL)

- [ ] T033 [US4] Write extensibility test: create a temporary PIPELINE with an extra FilterByPriceStep inserted at index 4, run WorkflowEngine with this pipeline, assert total_steps=10, assert step_number sequence is 1→2→3→4→5(new)→6→…→10, assert inserted step receives ProductResearchStep output as its input in `backend/src/tests/test_workflow_extensibility.py`

### Implementation for User Story 4

- [ ] T034 [P] [US4] Create FilterByPriceStep example stub (step_id: filter_by_price, type: system_processing, component_type: product_list) — passes through input products unchanged with a visible notice; demonstrates insertion pattern in `backend/src/workflow/steps/example_custom_step.py`
- [ ] T035 [US4] Verify WorkflowEngine derives total_steps from len(pipeline) at run-start (not hardcoded 9) and that step_number is i+1 for each PIPELINE index i; add docstring to registry.py explaining insertion pattern in `backend/src/workflow/engine.py` + `backend/src/workflow/registry.py`

**Checkpoint**: Step insertion works — workflow adapts to any PIPELINE length without engine changes.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Error handling, retry flow, progress indicators, and documentation.

- [ ] T036 Add scoped error + retry handling to WorkflowEngine: on StepError, send step_error message, set run.status=error, wait for retry or close; on retry, re-execute same step with same input; prior confirmed_outputs are never cleared on error in `backend/src/workflow/engine.py`
- [ ] T037 [P] Write step_error + retry flow test: simulate StepError on product_research → assert step_error received → send retry → assert step re-executes (step_activated again) → assert confirmed keywords unchanged in `backend/src/tests/test_ws_error_handling.py`
- [ ] T038 [P] Add step-level inline progress indicator to workflow page: when step_processing message arrives, show spinner on active step; spinner disappears on step_result; interface remains scrollable (non-blocking) in `frontend/src/routes/workflow/+page.svelte`
- [ ] T039 Add workflow WebSocket URL to README.md and verify run.sh exposes ws://localhost:8000/ws/workflow correctly in `README.md` + `run.sh`
- [ ] T040 [P] Add zero-results auto-loop to ProductResearchStep: if products list is empty, raise StepError("No products found — please refine your description.", retryable=False) so engine loops back to step 1 in `backend/src/workflow/steps/s04_product_research.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 Phase 3**: Depends on Phase 2 — MVP deliverable
- **US2 Phase 4**: Depends on Phase 3 (extends engine.py) — builds on US1
- **US3 Phase 5**: Depends on Phase 4 (extends engine.py again) — builds on US2
- **US4 Phase 6**: Depends on Phase 3 (needs engine + registry) — independent of US2/US3
- **Polish (Phase 7)**: Depends on US1–US4 complete

### Within Each User Story

- TDD tests MUST be written first and FAIL before implementation
- Step stubs before engine
- Engine before WebSocket route
- Backend route before frontend page
- Core loop-back logic before frontend loop-back UI

### Parallel Opportunities Per Phase

**Phase 2** — run T003, T004, T007 in parallel; T005 after T003+T004; T008 after T007

**Phase 3** — run T009+T010 in parallel (tests); T011–T019 all in parallel (different files); T020 after T011–T019; T021 after T005+T020; T022 after T006+T021; T023+T024+T025 in parallel; T026 after T008+T023+T024+T025

**Phase 4** — T027 (test first), then T028, then T029

**Phase 5** — T030 (test first), then T031, then T032

**Phase 6** — T033 (test first), T034+T035 in parallel

**Phase 7** — T036 before T037; T038+T039+T040 in parallel after T036

---

## Parallel Example: Phase 3 (US1)

```bash
# Step 1: All step stubs in parallel (T011–T019 — different files)
Task T011: ProductDescriptionStep in s01_description.py
Task T012: KeywordRefinementStep in s02_keyword_refinement.py
Task T013: KeywordConfirmationStep in s03_keyword_confirmation.py
Task T014: ProductResearchStep in s04_product_research.py
Task T015: ProductValidationStep in s05_product_validation.py
Task T016: MarketResearchStep in s06_market_research.py
Task T017: AiAnalysisStep in s07_ai_analysis.py
Task T018: FinalCriteriaStep in s08_final_criteria.py
Task T019: ReportGenerationStep in s09_report.py

# Step 2: After stubs complete
Task T020: registry.py

# Step 3: After registry
Task T021: engine.py
Task T022: route workflow.py

# Step 4: Frontend components in parallel
Task T023: StepRenderer.svelte
Task T024: All step display components
Task T025: StepConfirmation.svelte

# Step 5: After all components
Task T026: workflow +page.svelte
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (critical — blocks everything)
3. Complete Phase 3: US1 — happy path full run
4. **STOP and VALIDATE**: WebSocket connect → start → confirm twice → workflow_complete
5. Demo: full 9-step run in browser

### Incremental Delivery

1. Setup + Foundational → infra ready
2. US1 → end-to-end 9-step happy path (MVP demo)
3. US2 → keyword refinement loop
4. US3 → product validation loop
5. US4 → step insertion extensibility proof
6. Polish → error handling + progress indicators

---

## Notes

- Step stubs are intentional: they raise `NotImplementedError` or return placeholder data — real implementations (Amazon scraping, LLM calls) belong to feature 001's task list
- The WorkflowEngine is loop-back-aware: it resets `current_step_index`, not the entire `WorkflowRun`
- `confirmed_outputs` is append-only — loop-backs never delete confirmed data from earlier steps
- The `PIPELINE` list is the single extensibility point — no engine changes needed to add steps
- `step_number` in messages is always `current_step_index + 1` derived at runtime, never hardcoded
