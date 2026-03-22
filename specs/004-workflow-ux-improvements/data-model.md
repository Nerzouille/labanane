# Data Model: Workflow UX Improvements

**Feature**: 004-workflow-ux-improvements
**Date**: 2026-03-22

## Overview

This feature has no data model changes. All state is in-memory, session-scoped, and already typed in `$lib/workflow-types`.

---

## Existing Types (unchanged)

### `StepState`

```typescript
interface StepState {
  step_id: string;
  step_number: number;
  label: string;
  status: 'pending' | 'active' | 'processing' | 'complete' | 'confirmation' | 'error';
  component_type?: string;
  data?: Record<string, unknown>;
  tokens?: string;
  error?: string;
}
```

No new fields. No new status values.

The `validated` state for the confirmation step is **local component state** inside `StepConfirmation.svelte` and intentionally not promoted to `StepState`. It does not need to survive navigation or re-render outside the component.

### `WsStatus`

Unchanged: `'idle' | 'connecting' | 'open' | 'closed'`

### `workflowState` (in `+page.svelte`)

Unchanged shape:

```typescript
{
  status: WsStatus;
  description: string;   // cleared on reset — already implemented
  totalSteps: number;
  steps: StepState[];
  activeStepId: string;
  errorMsg: string;
  runId: string;
}
```

---

## Logic Changes (not data shape)

### `visibleSteps` derived value

**Before**:
```typescript
const visibleSteps = $derived(
  workflowState.steps.filter((s) => {
    if (HIDDEN_STEPS.has(s.step_id)) return false;
    const confirmStep = workflowState.steps.find((x) => x.step_id === 'keyword_confirmation');
    const isConfirmed = confirmStep?.status === 'complete';
    if ((s.step_id === 'keyword_refinement' || s.step_id === 'keyword_confirmation') && isConfirmed) {
      return false;   // ← REMOVED
    }
    return true;
  })
);
```

**After**:
```typescript
const visibleSteps = $derived(
  workflowState.steps.filter((s) => !HIDDEN_STEPS.has(s.step_id))
);
```

All other step management logic (`findOrCreateStep`, `updateStep`, `handleStepAction`, `reset`) is unchanged.
