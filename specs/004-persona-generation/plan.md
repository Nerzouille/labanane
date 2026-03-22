# Implementation Plan: Persona Generation Workflow Step

**Branch**: `004-persona-generation` | **Date**: 2026-03-22 | **Spec**: [spec.md](./spec.md)

---

## Summary

Insert a new `PersonaGenerationStep` (step 8 of 10) between AI Analysis and Final Criteria.
The step calls OpenHosta `emulate_async()` to generate exactly 3 distinct buyer personas from
the confirmed product list and AI analysis output. The frontend displays the 3 personas in a
card carousel (`StepPersona.svelte`). The Markdown export gains a `## Target Personas` section.
No new dependencies. Total step count increases from 9 to 10.

---

## Technical Context

**Language/Version**: Python 3.12 (backend) · TypeScript / Svelte 5 (frontend)
**Primary Dependencies** (all already installed):
- Backend: FastAPI, pydantic v2, uv, OpenHosta (`emulate_async`), weasyprint, python-markdown
- Frontend: SvelteKit, bun, shadcn-svelte

**Storage**: In-memory only — unchanged. PersonaSet stored in `WorkflowRun.confirmed_outputs["persona_generation"]`.
**Testing**: pytest (backend)
**Target Platform**: Desktop web — unchanged
**Performance Goal**: Persona generation ≤ 15s (one LLM call)
**Constraints**: No new external data sources. No new API calls beyond OpenHosta.
  One LLM call per workflow run for this step. Exactly 3 personas per run, no more, no less.

---

## Constitution Check

| Principle | Status | Notes |
|---|---|---|
| I. Streaming-First UX | ✅ | Progress indicator shown while generating. Full result displayed at once (no token streaming) — consistent with existing system steps. |
| II. Pipeline Resilience | ✅ | `StepError` raised if both products and AI analysis are unavailable. Retryable error surfaced to user. Graceful skip if step output missing at report time. |
| III. Stable Export Contracts | ✅ | New `## Target Personas` heading is stable. Existing headings unchanged. Delta documented in `contracts/export-schema-delta.md`. |
| IV. Simplicity & Hackathon Scope | ✅ | One LLM call. No new deps. Lightweight in-component carousel. No user confirmation gate. |
| V. Real Data Integrity | ✅ | Personas derived from real product data and AI analysis. No invented data. Step blocked if no real data available. |

---

## Project Structure

### Documentation (this feature)

```text
specs/004-persona-generation/
├── plan.md                   # This file
├── spec.md                   # Feature specification
├── research.md               # Phase 0 — all unknowns resolved
├── data-model.md             # Phase 1 — Persona/PersonaSet models + pipeline change
├── quickstart.md             # Phase 1 — dev notes, no new deps
├── contracts/
│   ├── ws-messages-delta.md  # WS contract additions (new step_result shape)
│   └── export-schema-delta.md # Markdown export additions (## Target Personas)
└── checklists/
    └── requirements.md
```

### Source Code Changes

```text
backend/
└── src/
    ├── models/
    │   └── report.py                        ← ADD: Persona, PersonaSet
    ├── logic/
    │   └── persona.py                       ← NEW: generate_personas()
    └── workflow/
        ├── registry.py                      ← MODIFY: insert PersonaGenerationStep at index 7
        └── steps/
            ├── s08_persona_generation.py    ← NEW
            ├── s09_final_criteria.py        ← RENAME from s08_final_criteria.py
            └── s10_report.py               ← RENAME from s09_report.py

backend/src/tests/
├── logic/
│   └── test_persona.py                      ← NEW
└── steps/
    ├── test_step_s08.py                     ← NEW (PersonaGenerationStep)
    └── test_step_s09.py                     ← RENAME from test_step_s08.py

frontend/src/
└── lib/
    ├── workflow-types.ts                    ← ADD: Persona, PersonaSetData types
    ├── components/
    │   ├── StepRenderer.svelte              ← ADD: persona_generation → StepPersona
    │   └── steps/
    │       └── StepPersona.svelte          ← NEW: 3-card carousel component
```

---

## Phase 0: Research

All unknowns resolved. See `research.md` for full decisions and rationale.

| Unknown | Decision |
|---------|----------|
| LLM integration | OpenHosta `emulate_async()` — same pattern as `logic/analysis.py` |
| Persona count | Exactly 3, requested in a single LLM call |
| Step insertion | Index 7 in PIPELINE (after AiAnalysisStep, before FinalCriteriaStep) |
| Carousel library | None — lightweight in-component Svelte 5 `$state` index |
| LLM output coercion | `_coerce_to_list()` + `_normalize_persona_list()` (same pattern as analysis.py) |
| Step file renames | s08→s09 (final_criteria), s09→s10 (report) — step_id strings unchanged |

---

## Phase 1: Design & Contracts

### Data Model

All entities defined. See `data-model.md`.

Key additions:
- `Persona` Pydantic model: `name`, `age_range`, `occupation`, `motivations`, `pain_points`
- `PersonaSet` Pydantic model: `personas: list[Persona]` (exactly 3)
- `PersonaSetData` TypeScript type for frontend
- `PersonaGenerationStep` step class: `step_id = "persona_generation"`, `component_type = "persona_generation"`
- Registry insertion: PersonaGenerationStep at PIPELINE index 7

### Contracts

| Contract | File | Change |
|---|---|---|
| WebSocket messages | `contracts/ws-messages-delta.md` | New step_result shape for `persona_generation`; `total_steps` = 10 |
| Export schema | `contracts/export-schema-delta.md` | New `## Target Personas` section with 3 sub-sections |

### Component Plan

| Component | Behaviour | Data source |
|---|---|---|
| `StepPersona.svelte` | 3-card carousel, dot navigator, prev/next buttons | `data.personas[activeIndex]` |

No charts needed for this component. The persona card is a structured text display.

---

## Constitution Check (post-design)

Re-evaluated after Phase 1. All principles remain satisfied.

- **Principle I**: `StepProcessingMessage` emitted before LLM call. Full result shown at once. Carousel controls are immediately interactive after result renders.
- **Principle II**: `StepError(retryable=True)` if LLM call fails. Products and AI analysis confirmed outputs are preserved (they are never mutated by this step).
- **Principle III**: `## Target Personas` heading is stable, documented, and consistent with the existing export heading style. Delta contract frozen in `contracts/export-schema-delta.md`.
- **Principle IV**: One LLM call, no new deps, ~50 lines of backend logic, ~80 lines of frontend. Well within hackathon scope.
- **Principle V**: Personas derived from confirmed products (real scraper data) and AI analysis (real trend + product data). If both inputs are empty, step raises a non-retryable error rather than generating from thin air.

---

## Next Step

Run `/speckit.tasks` to generate the implementation task list from this plan.
