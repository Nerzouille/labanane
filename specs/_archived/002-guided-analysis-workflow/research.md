# Research: Guided Analysis Workflow

**Feature**: 002-guided-analysis-workflow
**Date**: 2026-03-21

---

## Decision 1: WebSocket transport (FastAPI)

**Decision**: Use FastAPI's native `websockets` support via `@app.websocket("/ws/workflow")` with `WebSocket.receive_json()` / `WebSocket.send_json()`.

**Rationale**: The workflow requires server→client streaming (tokens, progress) AND client→server messages (confirmations, retries) on the same connection. SSE only goes one way. Polling would require a separate REST call per confirmation step and would lose session binding.

**Alternatives considered**:
- SSE + REST for confirmations: Adds coordination complexity (matching session IDs across two channels); rejected.
- Long-polling: Higher latency, more complex cleanup; rejected.
- gRPC streaming: Overkill for a hackathon; browser support requires grpc-web proxy; rejected.

---

## Decision 2: Step interface as abstract Python base class

**Decision**: Define `Step` as an abstract base class (`abc.ABC`) with three abstract methods: `execute()` → async generator, `get_step_id()` → str, `get_component_type()` → str.

**Rationale**: `abc.ABC` enforces the contract at import time. Each step file is self-contained (no framework coupling). Inserting a step = adding a class + inserting it in `registry.py`. The async generator return type for `execute()` allows streaming tokens from LLM steps while keeping the interface uniform across all 9 step types.

**Alternatives considered**:
- Dataclass with callable field: Less type-safe, no enforcement; rejected.
- Protocol (structural typing): Does not enforce at import time; rejected.
- Plugin registry with decorators: Adds metaprogramming complexity without benefit at MVP scale; rejected.

---

## Decision 3: Pipeline assembly in `registry.py`

**Decision**: `registry.py` exports `PIPELINE: list[Step]` — a plain ordered list instantiated at module load.

**Rationale**: Zero magic. Inserting a step at position N is a one-line change. The `WorkflowEngine` iterates the list; it has no knowledge of step semantics. Step count is `len(PIPELINE)`, automatically correct.

**Alternatives considered**:
- YAML/JSON config: Adds a parse layer, a validation layer, and a deploy artifact; rejected.
- Runtime UI for step editing: Out of scope per spec clarification; rejected.
- Numbered file discovery (`s01_*.py`): Implicit ordering; can break on rename; rejected.

---

## Decision 4: Session state as in-memory dict

**Decision**: `WorkflowRun` objects stored in a module-level dict `_runs: dict[str, WorkflowRun]` keyed by a UUID generated at connection open. Cleaned up on `WebSocketDisconnect`.

**Rationale**: No database required per constitution Principle IV (hackathon scope). Single-user, single-session. No cross-request state needed beyond the open WebSocket connection lifetime.

**Alternatives considered**:
- Redis: Network dependency, more setup; overkill; rejected.
- SQLite: Adds migration concerns; rejected.
- Browser `sessionStorage` only: Cannot store server-computed results; rejected.

---

## Decision 5: Dynamic Svelte component mounting via `component_type`

**Decision**: Server messages include a `component_type` string field. `StepRenderer.svelte` imports all step components in a static map and mounts the matching one reactively.

**Rationale**: Avoids dynamic imports (which complicate SSR and bundling in SvelteKit). The map is explicit, statically analyzable, and treeshakeable. Adding a new step = adding one entry to the map.

**Svelte 5 pattern**:
```svelte
<script lang="ts">
  import StepDescriptionInput from './steps/StepDescriptionInput.svelte'
  // ... other imports

  const COMPONENTS: Record<string, Component> = {
    product_description_input: StepDescriptionInput,
    // ...
  }

  let { componentType, data, onAction } = $props()
  const Component = $derived(COMPONENTS[componentType])
</script>

<Component {data} {onAction} />
```

**Alternatives considered**:
- Dynamic `import()` per `component_type`: Async, adds loading states per component; rejected.
- `{#if}` chain: Unscalable with 9+ component types; rejected.

---

## Decision 6: Zod validation on all incoming WS messages (frontend)

**Decision**: All messages received by the browser are validated against Zod schemas before being dispatched to the UI layer.

**Rationale**: Consistent with feature 001's SSE approach. Catches backend protocol regressions at the boundary. Type inference from Zod gives TypeScript types for free.

---

## Decision 7: WorkflowRun state machine

**States**: `idle` → `running` → `awaiting_confirmation` → `running` → `complete` | `error`

**Transition rules**:
- `idle` → `running`: on `start` message
- `running` → `awaiting_confirmation`: when a confirmation-type step emits `confirmation_request`
- `awaiting_confirmation` → `running`: on `confirmation` message (yes or no)
- `running` → `error`: on unrecoverable step failure
- `running` → `complete`: after step 9 completes

**Loop-back**: When user rejects at step 3 → engine resets step index to 1 (description). When user rejects at step 5 → engine resets step index to 4 (product research). No state is lost for confirmed steps before the loop-back point.
