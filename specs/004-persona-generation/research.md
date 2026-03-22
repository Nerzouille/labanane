# Research: Persona Generation Workflow Step

**Feature**: 004-persona-generation
**Date**: 2026-03-22
**Branch**: 004-persona-generation

All unknowns resolved. No blocking questions remain.

---

## Decision Log

### 1 — LLM Integration: OpenHosta `emulate_async()`

**Decision**: Use `emulate_async()` from OpenHosta for persona generation, following
the exact same pattern as `generate_market_analysis()` in `logic/analysis.py`.

**Rationale**: Mandated by the user. Already proven in the codebase. Single LLM call,
returns a structured object the caller validates. Avoids any new dependency.

**Alternatives considered**: Direct OpenAI SDK call (more code, already abstracted away
by OpenHosta), streamed token output (out of scope per spec 003 FR-017b pattern).

**Risk**: OpenHosta may return a string instead of a dict (known behaviour, already
mitigated by `_coerce_to_dict()` in `logic/analysis.py` — same pattern applied here).

---

### 2 — Persona count: exactly 3

**Decision**: A single LLM call requests exactly 3 distinct buyer personas as a JSON
array of 3 objects. The prompt explicitly forbids fewer or more.

**Rationale**: Three personas give enough coverage of a market segment without
overwhelming the user. The carousel UI is designed for exactly this count.

**Alternatives considered**: Dynamic count (1–5, user-selectable) — rejected as over-
engineering for a hackathon. One persona — rejected, too narrow to be useful.

---

### 3 — Step insertion position

**Decision**: PersonaGenerationStep is inserted at index 7 (0-based) in PIPELINE, between
`AiAnalysisStep` (index 6) and `FinalCriteriaStep` (index 7 → shifts to 8).
The step file is named `s08_persona_generation.py`; old s08/s09 rename to s09/s10.

**Rationale**: Persona generation requires the AI analysis output as input
(`run.get_output("ai_analysis")`). Final criteria should follow persona generation to
optionally incorporate the persona context. The step counter displayed to the user updates
automatically because the engine reads `len(PIPELINE)` at run-start (FR-003, registry.py).

**Step numbering after change**:

| Old name | Old slot | New name | New slot |
|----------|----------|----------|----------|
| AiAnalysisStep | s07 | AiAnalysisStep | s07 (unchanged) |
| *(new)* PersonaGenerationStep | — | s08 | s08 |
| FinalCriteriaStep | s08 | FinalCriteriaStep | s09 |
| ReportGenerationStep | s09 | ReportGenerationStep | s10 |

Total steps changes from 9 to 10.

---

### 4 — Carousel implementation

**Decision**: Build a lightweight in-component carousel in `StepPersona.svelte` using
Svelte 5 runes (`$state`) to track the active index. No external carousel library needed.
Navigation: previous/next buttons + dot indicator showing current position (e.g., "2 / 3").

**Rationale**: The carousel holds exactly 3 cards — simple enough for a manual `$state`
index. Adding a dependency (e.g., Embla, Splide) for 3 static cards would be over-
engineering. The UI pattern matches the existing step card visual language.

**Alternatives considered**: Tab navigation (less visually compelling), showing all 3
simultaneously in a grid (wastes vertical space, loses focus).

---

### 5 — Input contract for PersonaGenerationStep

**Decision**: Reads two sources from `run.get_output()`:
- `run.get_output("product_research").get("products", [])` — list of product dicts
- `run.get_output("ai_analysis")` — full AI analysis dict

Both are passed to the business logic function. If both are empty the step raises a
non-retryable `StepError` (same pattern as `AiAnalysisStep`). If only one is available
the step proceeds with the available data.

**Rationale**: Mirrors the exact pattern in `s07_ai_analysis.py` for source availability
handling. No new engine changes needed.

---

### 6 — Output / cross-step consumption

**Decision**: `PersonaGenerationStep` stores its output under `step_id = "persona_generation"`.
The `ReportGenerationStep` reads this with `run.get_output("persona_generation")` to include
personas in the Markdown export. `FinalCriteriaStep` does NOT need to change (it reads
`ai_analysis` directly).

**Rationale**: Adding a new step between AI Analysis and Final Criteria should require
no changes to Final Criteria — this validates the three-layer architecture (FR-028/029).

---

### 7 — Export schema change

**Decision**: The export schema (`contracts/export-schema.md`) gains a new `## Target Personas`
section inserted after `## Go / No-Go` and before `## Target Persona` (the existing single-
persona field from AI Analysis). The existing `## Target Persona` section from the AI analysis
is retained as a summary; the new `## Target Personas` section lists all 3 detailed profiles.

**Rationale**: Backwards-compatible: no existing sections are removed or renamed. The
`## Target Personas` heading is stable for automated parsing.

---

### 8 — Normalisation of LLM output

**Decision**: Follow the `_normalize_market_analysis_dict` / `_coerce_to_dict` pattern
already established in `logic/analysis.py`. Implement a `_normalize_persona_list()` helper
in `logic/persona.py` that coerces the LLM output to `list[dict]` and fills missing fields
with safe defaults (e.g., empty list for motivations/pain_points, "Unknown" for name).

**Rationale**: OpenHosta is known to return strings instead of Python objects (see memory
note `openhosta_emulate_async_behavior.md`). Defensive normalisation prevents silent failures.
