# Tasks: Persona Generation Workflow Step

**Branch**: `004-persona-generation` | **Date**: 2026-03-22
**Plan**: [plan.md](./plan.md) | **Spec**: [spec.md](./spec.md)
**Total tasks**: 17 | **Total user stories**: 2

---

## Dependency Graph

```
Phase 1 (Setup)
  └─▶ Phase 2 (Foundational models)
        ├─▶ Phase 3 (US1 — happy path backend + frontend)
        │     └─▶ Phase 4 (US2 — report integration)
        │             └─▶ Phase 5 (Tests)
        │                     └─▶ Final Phase (Polish)
        └─▶ Phase 5 (Tests — logic unit tests can start here)
```

US1 and US2 are **sequential** (US2 depends on the persona_generation output existing).
Within Phase 3: T006, T007, T008 are sequential (step file → registry). T009 and T010 are parallelizable with T006–T008 (different files, no shared dependency until T010).

---

## Implementation Strategy

**MVP scope**: Complete Phase 1 + Phase 2 + Phase 3.
This gives a fully working in-session persona carousel (US1) without the report integration.

Phase 4 (US2) adds the export section and is safe to do immediately after US1.
Phase 5 (tests) can partially run in parallel with Phase 3 after Phase 2 completes.

---

## Phase 1: Setup — File Renames

*Rename existing step files to shift numbering. No logic changes.*

- [x] T001 Rename `backend/src/workflow/steps/s08_final_criteria.py` → `s09_final_criteria.py` (step_id string `"final_criteria"` and all internal imports remain unchanged)
- [x] T002 Rename `backend/src/workflow/steps/s09_report.py` → `s10_report.py` (step_id string `"report_generation"` and all internal imports remain unchanged)
- [x] T003 Rename `backend/src/tests/steps/test_step_s08.py` → `test_step_s09.py` and update the import line from `s08_final_criteria` to `s09_final_criteria`

---

## Phase 2: Foundational — Models & Types

*Shared data models required by all subsequent phases. Safe to parallelize T004 and T005.*

- [x] T004 [P] Add `Persona` and `PersonaSet` Pydantic models to `backend/src/models/report.py`:
  ```python
  class Persona(BaseModel):
      name: str
      age_range: str
      occupation: str
      motivations: list[str]   # 2–3 items
      pain_points: list[str]   # 2–3 items

  class PersonaSet(BaseModel):
      personas: list[Persona]  # exactly 3
  ```
- [x] T005 [P] Add `Persona` and `PersonaSetData` TypeScript types to `frontend/src/lib/workflow-types.ts`:
  ```typescript
  type Persona = {
    name: string
    age_range: string
    occupation: string
    motivations: string[]  // 2–3 items
    pain_points: string[]  // 2–3 items
  }
  type PersonaSetData = {
    personas: Persona[]    // 3 items
  }
  ```

---

## Phase 3: User Story 1 — Persona Displayed After AI Analysis

**Goal**: After AI Analysis completes, the workflow automatically runs a Persona Generation
step, calls OpenHosta to generate 3 distinct personas, and displays them in a carousel.

**Independent test**: Run a full workflow to completion. After step 7 (AI Analysis) finishes,
step 8 should auto-start and display "Persona Generation" in the step progress indicator.
When the step completes, a card with carousel navigation (‹ 1/3 ›) should appear with
name, age range, occupation, motivations, and pain points for the first persona.
Clicking "Next" should show the second persona, then the third.

- [x] T006 [US1] Create `backend/src/logic/persona.py` with:
  - `_coerce_to_list(value: object) -> list` — coerces `emulate_async()` output to list (JSON/ast fallback if str returned, same pattern as `_coerce_to_dict` in `logic/analysis.py`)
  - `_normalize_persona_list(raw: list) -> list[dict]` — ensures exactly 3 persona dicts, each with keys `name`, `age_range`, `occupation`, `motivations`, `pain_points`; fills missing fields with safe defaults (`"Unknown"` for strings, `[]` for lists); trims to 3 if more returned, pads with placeholder if fewer
  - `async def generate_personas(product_description: str, products: list[dict], ai_analysis: dict) -> PersonaSet` — calls `emulate_async()` with a docstring prompt requesting exactly 3 distinct buyer personas as a JSON array; coerces and normalises the result; returns a validated `PersonaSet`

  Prompt docstring for `generate_personas` (inside the function body, used by OpenHosta):
  ```
  Generate exactly 3 distinct buyer personas for the described product.
  Each persona should target a meaningfully different buyer profile (age, use case, or motivation).
  Return a JSON array of exactly 3 objects. Each object must have:
    - name: string (archetype label, e.g. "The Weekend Creator")
    - age_range: string (e.g. "25–35")
    - occupation: string (e.g. "Freelance graphic designer")
    - motivations: array of 2–3 short strings
    - pain_points: array of 2–3 short strings
  Do not return fewer or more than 3 objects. Do not include explanations, only the array.
  ```

- [x] T007 [US1] Create `backend/src/workflow/steps/s08_persona_generation.py`:
  ```python
  from src.logic.persona import generate_personas
  from src.models.report import PersonaSet

  class PersonaGenerationStep(Step):
      step_id        = "persona_generation"
      label          = "Persona Generation"
      step_type      = "system_processing"
      component_type = "persona_generation"

      async def execute(self, input, run):
          yield StepProcessingMessage(step_id=self.step_id)
          products  = run.get_output("product_research").get("products", [])
          ai_result = run.get_output("ai_analysis")
          if not products and not ai_result:
              raise StepError(
                  "Cannot generate personas: no product or analysis data available.",
                  retryable=False,
              )
          result = await generate_personas(run.description, products, ai_result)
          yield StepResultMessage(
              step_id=self.step_id,
              component_type=self.component_type,
              data=result.model_dump(),
          )
  ```

- [x] T008 [US1] Update `backend/src/workflow/registry.py`:
  - Add import: `from .steps.s08_persona_generation import PersonaGenerationStep`
  - Update import for FinalCriteriaStep: `from .steps.s09_final_criteria import FinalCriteriaStep`
  - Update import for ReportGenerationStep: `from .steps.s10_report import ReportGenerationStep`
  - Insert `PersonaGenerationStep()` at index 7 (after `AiAnalysisStep()`, before `FinalCriteriaStep()`):
    ```python
    PIPELINE = [
        ProductDescriptionStep(),
        KeywordRefinementStep(),
        KeywordConfirmationStep(),
        ProductResearchStep(),
        ProductValidationStep(),
        MarketResearchStep(),
        AiAnalysisStep(),
        PersonaGenerationStep(),   # ← new at index 7
        FinalCriteriaStep(),
        ReportGenerationStep(),
    ]
    ```

- [x] T009 [P] [US1] Create `frontend/src/lib/components/steps/StepPersona.svelte` — Svelte 5 component with carousel:
  ```svelte
  <svelte:options runes={true} />
  <script lang="ts">
    import type { PersonaSetData, Persona } from '$lib/workflow-types';
    let { data }: { data: PersonaSetData } = $props();
    let activeIndex = $state(0);
    const personas: Persona[] = $derived(data.personas ?? []);
    const current: Persona = $derived(personas[activeIndex]);
    const total = $derived(personas.length);
    function prev() { activeIndex = (activeIndex - 1 + total) % total; }
    function next() { activeIndex = (activeIndex + 1) % total; }
  </script>

  <!-- Render: header "Persona {activeIndex+1} / {total}", card with current persona
       fields (name, age_range, occupation, motivations as bullet list, pain_points as
       bullet list), dot navigator (clicking dot i sets activeIndex = i), prev/next buttons.
       Use shadcn-svelte Card, Badge components for visual consistency with StepAiAnalysis. -->
  ```
  The component must:
  - Show exactly one persona card at a time
  - Display all 5 fields with clear labels (Name, Age Range, Occupation, Motivations, Pain Points)
  - Show "1 / 3" style position indicator
  - Provide clickable dots (one per persona) for direct navigation
  - Provide Prev / Next buttons that wrap around

- [x] T010 [US1] Update `frontend/src/lib/components/StepRenderer.svelte`:
  - Add import: `import StepPersona from './steps/StepPersona.svelte';`
  - Add entry to `COMPONENTS` map: `persona_generation: StepPersona,`

---

## Phase 4: User Story 2 — Persona Visible in Final Report

**Goal**: The Markdown export contains a `## Target Personas` section with all 3 personas.

**Independent test**: Complete a full 10-step workflow, then click "Export Markdown".
Open the downloaded `.md` file and verify:
1. `## Target Personas` heading is present
2. Three sub-sections `### Persona 1:`, `### Persona 2:`, `### Persona 3:` follow it
3. Each sub-section contains Age range, Occupation, Motivations, Pain points

- [x] T011 [US2] Update `backend/src/logic/export.py` — add `## Target Personas` section to `render_markdown()`:
  - Add `personas` as a new key read from `run_data`: `personas: list[dict] = run_data.get("personas", [])`
  - Insert the section after the `## Go / No-Go` block and before the `## Target Persona` block:
    ```python
    if personas:
        lines.append("## Target Personas")
        lines.append("")
        for i, p in enumerate(personas, 1):
            lines.append(f"### Persona {i}: {p.get('name', 'Unknown')}")
            lines.append("")
            lines.append(f"- **Age range**: {p.get('age_range', 'N/A')}")
            lines.append(f"- **Occupation**: {p.get('occupation', 'N/A')}")
            motivations = " · ".join(p.get("motivations", []))
            lines.append(f"- **Motivations**: {motivations}")
            pain_points = " · ".join(p.get("pain_points", []))
            lines.append(f"- **Pain points**: {pain_points}")
            lines.append("")
        lines.append("---")
        lines.append("")
    ```

- [x] T012 [US2] Update `backend/src/workflow/steps/s10_report.py` — pass persona data into `render_markdown()`:
  - Read persona data: `persona_data = run.get_output("persona_generation").get("personas", [])`
  - Pass it as a key in the `run_data` dict passed to `render_markdown()`: `"personas": persona_data`
  - The function call should already collect other step outputs; add `"personas"` alongside them

---

## Phase 5: Tests

*Unit and step-level tests. T013 and T014 are parallelizable once Phase 2 is done.*

- [x] T013 [P] Create `backend/src/tests/logic/test_persona.py` — unit tests for `logic/persona.py`:
  - `test_coerce_to_list_passthrough_real_list` — real list passes through unchanged
  - `test_coerce_to_list_json_string` — `'[{"name":"X"}]'` → list with one dict
  - `test_coerce_to_list_python_repr_string` — `"[{'name':'X'}]"` → list with one dict
  - `test_coerce_to_list_invalid_returns_empty` — garbage string → `[]`
  - `test_normalize_persona_list_returns_exactly_3` — input of 5 items → trimmed to 3
  - `test_normalize_persona_list_pads_to_3_when_fewer` — input of 1 item → padded to 3
  - `test_normalize_persona_list_fills_missing_name_with_unknown` — dict without `name` → `name = "Unknown"`
  - `test_normalize_persona_list_fills_missing_lists_with_empty` — dict without `motivations` → `motivations = []`
  - `test_generate_personas_returns_persona_set` — mock `emulate_async` with valid list → returns `PersonaSet`
  - `test_generate_personas_has_exactly_3_personas` — result always has `len(result.personas) == 3`
  - `test_generate_personas_each_persona_has_name` — each persona has non-empty `name`
  - `test_generate_personas_handles_string_response` — mock returns JSON string `"[...]"` → still returns `PersonaSet`

- [x] T014 [P] Create `backend/src/tests/steps/test_step_s08.py` — unit tests for `PersonaGenerationStep` (mirror pattern from `test_step_s07.py`):
  - `test_step_id_is_persona_generation`
  - `test_step_type_is_system_processing`
  - `test_component_type_is_persona_generation`
  - `test_execute_yields_step_processing_first` — mock `generate_personas`, verify first message type is `"step_processing"`
  - `test_execute_yields_step_result_with_persona_data` — verify `step_result` has `component_type == "persona_generation"`
  - `test_execute_step_result_data_has_personas_array` — verify `"personas"` key exists in result data and is a list
  - `test_execute_step_result_personas_has_3_items` — `len(data["personas"]) == 3`
  - `test_execute_raises_step_error_when_no_products_and_no_ai_analysis` — empty confirmed_outputs → `StepError` raised with `retryable=False`

  SAMPLE constant for test file:
  ```python
  SAMPLE_PERSONA_SET = PersonaSet(personas=[
      Persona(name="The Weekend Creator", age_range="25–35",
              occupation="Freelance designer",
              motivations=["Professional look", "Aesthetic tools"],
              pain_points=["Cheap materials", "Wrong sizes"]),
      Persona(name="The Remote Professional", age_range="30–45",
              occupation="Software engineer",
              motivations=["Ergonomic surface", "Minimal design"],
              pain_points=["Mouse skip", "Cable mess"]),
      Persona(name="The Student Hustler", age_range="18–24",
              occupation="University student",
              motivations=["Gaming aesthetic", "Budget value"],
              pain_points=["Too expensive", "Too large"]),
  ])
  ```

- [x] T015 [P] Update `backend/src/tests/logic/test_export.py` — add test for the new `## Target Personas` section:
  - `test_render_markdown_includes_target_personas_section_when_personas_present` — pass `run_data` with `"personas"` list of 3 dicts → verify `"## Target Personas"` appears in output
  - `test_render_markdown_target_personas_section_absent_when_personas_empty` — pass `run_data` with `"personas": []` → verify `"## Target Personas"` does NOT appear in output
  - `test_render_markdown_persona_names_appear_in_output` — each persona's `name` appears in the output string

---

## Final Phase: Polish & Cross-Cutting

- [x] T016 Verify the complete test suite passes: `cd backend && uv run pytest` — fix any import errors or assertion failures caused by step file renames (T001–T003) before closing
- [x] T017 Perform a manual end-to-end smoke test: start the full stack (`run.sh` or equivalent), run a workflow, confirm:
  - Step progress shows "8 / 10" when Persona Generation is running
  - Carousel displays 3 distinct persona cards; Prev/Next and dot navigation work
  - Export Markdown contains `## Target Personas` with 3 sub-sections

---

## Parallel Execution Opportunities

| Group | Tasks | Can run simultaneously |
|---|---|---|
| Foundation | T004, T005 | Yes — different languages/files |
| US1 backend + frontend | T006–T008 (backend), T009 (frontend) | T009 starts after T004/T005; T006–T008 are sequential |
| Tests | T013, T014, T015 | Yes — independent test files |

---

## Summary

| Phase | Tasks | Story |
|---|---|---|
| Phase 1: Setup | T001–T003 | — |
| Phase 2: Foundational | T004–T005 | — |
| Phase 3: US1 Happy Path | T006–T010 | US1 |
| Phase 4: US2 Report | T011–T012 | US2 |
| Phase 5: Tests | T013–T015 | — |
| Final: Polish | T016–T017 | — |
| **Total** | **17** | |

**Parallelizable tasks**: T004, T005, T009, T013, T014, T015
