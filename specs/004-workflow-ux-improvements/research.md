# Research: Workflow UX Improvements

**Feature**: 004-workflow-ux-improvements
**Date**: 2026-03-22
**Status**: Complete — no NEEDS CLARIFICATION items remain

## Summary

This feature is entirely frontend, touching three files. All design decisions were resolved by reading the existing codebase. No external API research required.

---

## Decision Log

### D1 — Near-bottom scroll threshold

- **Decision**: 100px threshold (`window.innerHeight + window.scrollY >= document.body.scrollHeight - 100`)
- **Rationale**: Industry standard for chat UIs (Slack, Discord). Catches near-bottom positions without forcing the user to be at the exact last pixel.
- **Alternatives**: `IntersectionObserver` sentinel (more robust but over-engineered for a single page); container-scoped scroll (requires layout refactor).

### D2 — Auto-scroll trigger location

- **Decision**: Single `$effect` in `+page.svelte` watching `visibleSteps.length` and last step's status, firing after `tick()`.
- **Rationale**: Centralises scroll logic; removes per-component scroll calls. `StepProductList`'s existing per-product scroll effect is superseded and removed.
- **Alternatives**: Per-step `scrollIntoView` (already partially in place, inconsistent) — rejected.

### D3 — Skeleton replacement strategy

- **Decision**: Repurpose `StepSkeleton.svelte` to render a centered `<Spinner>` (from `$lib/components/ui/spinner`). Keep file and prop API identical to avoid touching import in `+page.svelte`.
- **Rationale**: Zero import-graph changes. Spinner already in use in `StepProductList`.
- **Alternatives**: Inline spinner in `+page.svelte`, delete `StepSkeleton.svelte` — functionally identical, marginally more diff.

### D4 — Confirmation validated state implementation

- **Decision**: Local `$state(false)` variable `validated` inside `StepConfirmation.svelte`. Set to `true` on confirm before calling `onAction`. Render checkmark + "Validated" text when true.
- **Rationale**: The parent already keeps `StepConfirmation` mounted after `status: complete` (because `component_type` stays `confirmation`). Local state is the minimal change.
- **Alternatives**: New `validated` status in `StepState` + branch in `+page.svelte` — more invasive, not necessary.

### D5 — Step persistence: remove keyword filter

- **Decision**: Delete the `visibleSteps` filter block that hides `keyword_refinement` and `keyword_confirmation` once confirmed.
- **Rationale**: These steps must persist per FR-002/FR-003. The filter was a deliberate UX choice (clean up after confirmation) that the new spec explicitly reverses.
- **Alternatives**: Collapse/fade rather than remove — rejected; spec says steps never disappear.

### D6 — Reset input field on refusal

- **Decision**: No code change required. The existing `reset()` function in `+page.svelte` already sets `workflowState.description = ''`.
- **Rationale**: Verified by reading `+page.svelte` lines 155–161: `workflowState = { ..., description: '', ... }`.

### D7 — Remove per-product scroll in StepProductList

- **Decision**: Remove the `$effect` on lines 35–45 of `StepProductList.svelte` that calls `window.scrollTo` on each new product.
- **Rationale**: The centralised scroll handler in `+page.svelte` (D2) handles all scroll events. Keeping both would cause double-scroll on product updates.
