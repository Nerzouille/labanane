# Tasks: Workflow UX Improvements

**Input**: Design documents from `/specs/004-workflow-ux-improvements/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅

**Tests**: Not requested — no test tasks generated.

**Organization**: Tasks are grouped by user story. All changes are frontend-only across 4 files.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to
- All paths are under `frontend/src/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new dependencies or files needed — all changes are edits to existing frontend files. No setup tasks required.

> Skip directly to user story phases.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No cross-story prerequisites — all user stories affect distinct code sections or distinct files and can proceed independently.

> Skip directly to user story phases.

---

## Phase 3: User Story 1 — Auto-Scroll on New Content (Priority: P1) 🎯 MVP

**Goal**: The page automatically scrolls to newly appeared content when the user is near the bottom, mimicking a chat experience. When the user has scrolled up, their position is preserved.

**Independent Test**: Start a workflow, stay at the bottom, trigger steps — page should scroll automatically. Scroll up manually, trigger a new step — page should NOT scroll.

### Implementation for User Story 1

- [x] T001 [US1] Add centralized auto-scroll `$effect` to `frontend/src/routes/workflow/+page.svelte` that fires after `tick()` on each `visibleSteps` or last-step-status change, scrolls with `window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })` only when `window.innerHeight + window.scrollY >= document.body.scrollHeight - 100`
- [x] T002 [P] [US1] Remove the per-product auto-scroll `$effect` (lines ~35–45) from `frontend/src/lib/components/steps/StepProductList.svelte` — the new central handler in `+page.svelte` supersedes it

**Checkpoint**: After T001 + T002, launch a workflow and verify the page scrolls to each new step automatically while near the bottom, and does not scroll when scrolled up.

---

## Phase 4: User Story 2 — Persistent Workflow Steps (Priority: P1)

**Goal**: All workflow steps remain visible once shown. Keyword validation and confirmation steps do not disappear after the user confirms.

**Independent Test**: Complete the keyword confirmation step — `keyword_refinement` and `keyword_confirmation` steps should remain visible on screen above the next steps.

### Implementation for User Story 2

- [x] T003 [US2] Simplify the `visibleSteps` derived declaration in `frontend/src/routes/workflow/+page.svelte` — replace the entire multi-condition filter body with a single `!HIDDEN_STEPS.has(s.step_id)` check, removing the `isConfirmed` / keyword step filter entirely. Also remove the now-unused `isConfirmed` and `confirmStep` local variables from the filter.

**Checkpoint**: After T003, confirm the keyword steps, then verify both `keyword_refinement` and `keyword_confirmation` are still visible on screen alongside subsequent steps.

---

## Phase 5: User Story 3 — Spinner-Only Loading State Across All Steps (Priority: P2)

**Goal**: No skeleton placeholders appear anywhere in the workflow at any time. Every loading or waiting state shows only a spinner.

**Independent Test**: Start a workflow, observe each step transition — no animated skeleton rows or placeholder shapes should appear; only a spinner should be visible while each step is loading.

### Implementation for User Story 3

- [x] T004 [P] [US3] Replace the entire body of `frontend/src/lib/components/steps/StepSkeleton.svelte` with a centered `<Spinner>` from `$lib/components/ui/spinner`. Keep the `stepId` prop in the script block (for API compatibility with the call site in `+page.svelte`) but do not use it in the template. Remove all skeleton `div` branches and the `{#if stepId === ...}` conditional tree.

**Checkpoint**: After T004, trigger any workflow step and confirm only a spinner appears during loading — no `bg-muted animate-pulse` skeleton shapes anywhere.

---

## Phase 6: User Story 4 — Confirmation Refusal Resets the Analysis (Priority: P2)

**Goal**: When the user clicks "No, redo" at any confirmation step, the entire analysis resets: all steps are cleared, the input field is emptied, and the connection is closed. The user sees a blank page ready for a new analysis.

**Independent Test**: Run a full workflow to the confirmation step, click "No, redo" — the page should return to its initial blank state with the input field empty.

### Implementation for User Story 4

- [x] T005 [US4] Update `handleStepAction` in `frontend/src/routes/workflow/+page.svelte` so that when `a.type === 'confirmation'` and `a.confirmed === false`, it calls `reset()` instead of `updateStep`. The WebSocket message is still sent before reset (so the backend is notified), then `reset()` is called immediately after `conn?.send(action)`.

**Checkpoint**: After T005, click "No, redo" at the confirmation step — the page fully clears (steps, input, connection) and the idle/blank state is shown.

---

## Phase 7: User Story 5 — Confirmation Approval Transitions to Validated State (Priority: P2)

**Goal**: When the user clicks "Yes, continue" at the confirmation step, the confirmation UI transitions to a visible "Validated" state — showing a checkmark and success label — rather than disappearing or staying as-is.

**Independent Test**: Run a workflow to the confirmation step, click "Yes, continue" — the confirmation card should show a validated state (checkmark icon + "Validated" text) inline.

### Implementation for User Story 5

- [x] T006 [P] [US5] Update `frontend/src/lib/components/steps/StepConfirmation.svelte`:
  1. Add `let validated = $state(false)` in the script block
  2. In the `confirm(confirmed: boolean)` function, when `confirmed === true`, set `validated = true` before calling `onAction`
  3. Wrap the current button UI in an `{#if !validated}` block
  4. Add an `{:else}` block rendering the validated state: a `CheckmarkCircle01Icon` (or `Tick01Icon`) from `@hugeicons/core-free-icons` alongside a `"Validated"` text label, styled distinctly (e.g., `text-green-600` or `text-primary`)

**Checkpoint**: After T006, click "Yes, continue" at the confirmation step — the two buttons are replaced by a checkmark + "Validated" indicator within the same card. The step remains visible.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Verify all stories work together end-to-end as a cohesive chat-like flow.

- [x] T007 Manual end-to-end walkthrough: start workflow → observe auto-scroll → confirm keyword step stays visible → observe spinner-only loading → confirm analysis → verify validated state appears → start new analysis → verify full reset
- [x] T008 [P] Verify `StepProductList.svelte` no longer calls `window.scrollTo` (scroll effect removed in T002) — search for `scrollTo` in `frontend/src/lib/components/steps/StepProductList.svelte` and confirm it is absent

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 3 (US1)**: No dependencies — start immediately
- **Phase 4 (US2)**: No dependencies — can start immediately or in parallel with Phase 3 (different derived declaration in same file; best done sequentially to avoid conflict)
- **Phase 5 (US3)**: No dependencies — fully parallel with all other phases (different file)
- **Phase 6 (US4)**: No dependencies — fully parallel with US3/US5 (different section of `+page.svelte`; sequential after US2 to avoid file conflicts)
- **Phase 7 (US5)**: No dependencies — fully parallel with US3 (different file)
- **Phase 8 (Polish)**: Depends on all previous phases

### User Story Dependencies

- **US1 (P1)**: Independent — `+page.svelte` (new `$effect`) + `StepProductList.svelte` (remove old scroll)
- **US2 (P1)**: Independent — `+page.svelte` (`visibleSteps` filter); best after US1 to avoid `+page.svelte` conflicts
- **US3 (P2)**: Independent — `StepSkeleton.svelte` only; fully parallel with all others
- **US4 (P2)**: Independent — `+page.svelte` (`handleStepAction`); sequence after US1+US2
- **US5 (P2)**: Independent — `StepConfirmation.svelte` only; fully parallel with US3

### Parallel Opportunities

```bash
# Can run in parallel (different files):
T002 (StepProductList.svelte) || T004 (StepSkeleton.svelte) || T006 (StepConfirmation.svelte)

# Must be sequential (same file +page.svelte):
T001 → T003 → T005
```

---

## Implementation Strategy

### MVP First (US1 + US2 — both P1)

1. T001 — Add auto-scroll `$effect` to `+page.svelte`
2. T002 — Remove per-product scroll from `StepProductList.svelte` (parallel with T001)
3. T003 — Simplify `visibleSteps` filter in `+page.svelte`
4. **STOP and VALIDATE**: The core chat-like experience works (scroll + persistence)
5. Proceed to P2 stories

### Incremental Delivery

1. T001 + T002 → US1 done (auto-scroll works)
2. T003 → US2 done (steps persist)
3. T004 → US3 done (no skeletons anywhere)
4. T005 → US4 done (refusal resets everything)
5. T006 → US5 done (confirmation shows validated state)
6. T007 + T008 → Polish verified

### Parallel Team Strategy

With two developers:

- **Dev A**: T001 → T003 → T005 (all `+page.svelte` changes, sequentially)
- **Dev B**: T002 → T004 → T006 (StepProductList, StepSkeleton, StepConfirmation — all different files, parallel)

---

## Notes

- [P] tasks edit different files and have no blocking dependencies between them
- `+page.svelte` changes (T001, T003, T005) must be sequential to avoid merge conflicts
- No new components, no new dependencies, no new routes
- `StepSkeleton.svelte` keeps its filename and prop signature for zero-diff at the call site
- The `reset()` function already clears `workflowState.description` — US4 (T005) requires no changes to `reset()` itself
- The `out:slide` transition on the step wrapper div in `+page.svelte` can remain — it will never fire now that steps are not filtered out, so it causes no visual regression
