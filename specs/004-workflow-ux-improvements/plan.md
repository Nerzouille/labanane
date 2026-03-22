# Implementation Plan: Workflow UX Improvements

**Branch**: `004-workflow-ux-improvements` | **Date**: 2026-03-22 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/004-workflow-ux-improvements/spec.md`

## Summary

Replace all skeleton loading states with a spinner throughout the workflow, make all steps persist on screen once shown (including keyword validation), implement smart auto-scroll (near-bottom only), add a validated state to the confirmation step, and reset everything (steps + input) on refusal.

All changes are **frontend-only** — no backend modifications required.

## Technical Context

**Language/Version**: TypeScript / Svelte 5 (runes mode)
**Primary Dependencies**: SvelteKit, shadcn-svelte, `@hugeicons/svelte`, Svelte built-in transitions (`fly`, `slide`, `fade`)
**Storage**: N/A — in-memory state only (`workflowState` in `+page.svelte`)
**Testing**: Browser-based E2E (Playwright or manual); no unit test infrastructure for Svelte components at this time
**Target Platform**: Desktop web (SvelteKit, SSR/SPA hybrid)
**Performance Goals**: Scroll animation smooth at 60fps; spinner renders within one frame of step activation
**Constraints**: Reuse existing `Spinner` component (`$lib/components/ui/spinner`); no new UI primitives
**Scale/Scope**: Single workflow page, 6–8 steps per run

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I — Streaming-First UX | ⚠️ **OVERRIDE JUSTIFIED** | Constitution FR5 mandates a skeleton between pipeline launch and first SSE event. This feature **replaces skeletons with spinners** across all loading states. The intent of FR5 (signal that the system is working) is preserved by the spinner; the skeleton form is the only element removed. Justified by user experience evidence that skeletons mislead when content shape is unknown. |
| II — Pipeline Resilience | ✅ Clear | No pipeline changes; error states are preserved inline (FR-009). |
| III — Stable Export Contracts | ✅ Clear | No SSE event names or MD schema touched. |
| IV — Simplicity & Hackathon Scope | ✅ Clear | Changes are minimal, frontend-only, reuse existing components. |
| V — Real Data Integrity | ✅ Clear | No data sourcing or display logic changes. |

**Override rationale (Principle I / FR5)**: Skeleton screens imply known content shapes — appropriate for content where layout is predictable (e.g., feed of cards). The workflow steps have heterogeneous, unpredictable content. A spinner is semantically more honest and visually consistent with the `StepProductList` spinner already in production. No constitution amendment required; this is a refinement within the spirit of the principle, not a contradiction of its rationale.

## Project Structure

### Documentation (this feature)

```text
specs/004-workflow-ux-improvements/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (files touched)

```text
frontend/src/
├── routes/workflow/
│   └── +page.svelte                          # Main changes: auto-scroll, step persistence, reset
└── lib/components/
    ├── StepRenderer.svelte                   # No change
    └── steps/
        ├── StepSkeleton.svelte               # REPLACE body with spinner
        └── StepConfirmation.svelte           # ADD validated state
```

**Structure Decision**: Frontend-only, no new files. `StepSkeleton.svelte` is repurposed (name kept for minimal diff) to render a centered spinner instead of skeleton shapes. `StepConfirmation.svelte` gains an internal `validated` reactive state.

## Complexity Tracking

No constitution violations requiring justification beyond the Principle I override documented above.

---

## Phase 0: Research

### Decision 1 — "Near bottom" scroll threshold

**Decision**: Treat the user as "near bottom" when `window.innerHeight + window.scrollY >= document.body.scrollHeight - 100` (100px threshold).

**Rationale**: 100px is the standard threshold used by Slack, Discord, and most chat UIs. It catches the case where the user is at the bottom but hasn't quite reached the very last pixel. Already partially validated by `StepProductList.svelte` which calls `window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })` — we generalize this pattern.

**Alternatives considered**: `IntersectionObserver` on a sentinel div (more robust but adds complexity not warranted for a single page), `scrollTop + clientHeight >= scrollHeight - threshold` on a specific scroll container (would require refactoring the page layout).

### Decision 2 — Where to trigger auto-scroll

**Decision**: Trigger in a Svelte `$effect` in `+page.svelte` that watches `visibleSteps.length` and the last step's status. After each DOM update (`tick()`), check proximity to bottom and scroll if within threshold.

**Rationale**: Centralizing scroll logic in the page component avoids each step component managing scroll independently (the existing `StepProductList` per-product scroll is an exception that will be removed in favour of the central handler).

**Alternatives considered**: Per-step `scrollIntoView` in each component (already partially done in `StepProductList`) — rejected because it produces inconsistent behaviour across steps and can't apply the near-bottom guard.

### Decision 3 — StepSkeleton replacement

**Decision**: Replace the entire body of `StepSkeleton.svelte` with a centered `<Spinner>` component. Keep the file and export name unchanged to avoid touching the import in `+page.svelte`.

**Rationale**: Zero-change to the import graph. The `Spinner` component (`$lib/components/ui/spinner`) already exists and is used in `StepProductList`.

**Alternatives considered**: Deleting `StepSkeleton.svelte` and inlining a `<Spinner>` in `+page.svelte` — equivalent outcome but marginally more diff; not worth it.

### Decision 4 — Confirmation validated state

**Decision**: Add a local `let validated = $state(false)` in `StepConfirmation.svelte`. When the user clicks "Yes, continue", set `validated = true` before calling `onAction`. Render a distinct validated UI (checkmark icon + "Validated" text) when `validated` is true.

**Rationale**: The parent `+page.svelte` already sets the step status to `complete` via `handleStepAction` → `updateStep(a.step_id, { status: 'complete' })`. However, `StepRenderer` continues to render `StepConfirmation` (since `component_type` is still `confirmation`) — meaning the confirmation card stays on screen. Adding local state inside `StepConfirmation` to show a validated UI is the smallest change that achieves the spec requirement.

**Alternatives considered**: Adding a `validated` status to `StepState` and branching in `+page.svelte` — more invasive; the local state approach is sufficient.

### Decision 5 — Step persistence (remove keyword filter)

**Decision**: Remove the `visibleSteps` filter that hides `keyword_refinement` and `keyword_confirmation` once confirmed. Both steps will remain visible at all times.

**Rationale**: The spec (FR-002, FR-003) requires all steps to persist. The current filter was added to clean up the UI after confirmation — this contradicts the new chat-like model where the history is the UX.

**Alternatives considered**: Keeping the filter but adding a "collapsed" visual state — rejected as unnecessary complexity; the spec is clear that steps must remain visible.

### Decision 6 — Reset clears description input

**Decision**: The existing `reset()` function already sets `workflowState.description = ''` as part of the full state reset — no change required.

**Rationale**: Reading `reset()` in `+page.svelte` (line 155–161) confirms `workflowState = { ..., description: '', ... }`. The spec requirement (FR-005, clear input on refusal) is already satisfied by the existing reset path triggered when the user refuses at confirmation.

---

## Phase 1: Design & Contracts

### Data Model

#### `StepState` (existing, in `$lib/workflow-types`)

No new fields required. The `validated` state for confirmation lives as local component state in `StepConfirmation.svelte`, not in the shared `StepState` type. This keeps the data model minimal.

Existing status values: `pending | active | processing | complete | confirmation | error`
No new status values added.

#### `visibleSteps` filter (in `+page.svelte`)

Current logic (to be removed):
```
if ((s.step_id === 'keyword_refinement' || s.step_id === 'keyword_confirmation') && isConfirmed) return false;
```

New logic: no keyword-based filtering. Steps are filtered only by `HIDDEN_STEPS` (existing set: `product_description`, `ai_analysis`).

### UI Contracts

#### `StepSkeleton.svelte` — Loading placeholder

**Before**: Renders skeleton shapes (animated `bg-muted` divs) specific to each `stepId`.

**After**: Renders a single centered spinner, regardless of `stepId`.

```svelte
<!-- New contract: always a spinner, stepId prop preserved for API compatibility -->
<div class="flex justify-center py-4">
  <Spinner class="size-5 text-muted-foreground" />
</div>
```

The `stepId` prop is kept to avoid breaking the call site in `+page.svelte` (`<StepSkeleton stepId={step.step_id} />`), but it is no longer used.

#### `StepConfirmation.svelte` — Confirmation + Validated state

**New internal state**: `let validated = $state(false)`

**Confirmed render** (when `validated === true`):
```
[✓ checkmark icon]  Validated
```
Visually distinct from the pending state (confirmed action buttons replaced by success indicator).

**Prop contract**: unchanged — `{ data, onAction, stepId }`.

#### `+page.svelte` — Auto-scroll

**New reactive effect** (added after existing step management):

```
$effect(() => {
  const _ = visibleSteps.length;             // track length change
  const last = visibleSteps.at(-1)?.status; // track last step status change
  tick().then(() => {
    const nearBottom =
      window.innerHeight + window.scrollY >= document.body.scrollHeight - 100;
    if (nearBottom) {
      window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });
    }
  });
});
```

**Removed**: The per-product scroll effect inside `StepProductList.svelte` (lines 35–45) — superseded by the central handler.

### Agent Context Update
