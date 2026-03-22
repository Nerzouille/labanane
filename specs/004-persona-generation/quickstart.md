# Quickstart: Persona Generation Step

**Feature**: 004-persona-generation
**Date**: 2026-03-22
**Base quickstart**: 003-market-analysis-platform/quickstart.md (unchanged — no new deps)

---

## What changes in this feature

1. **New backend file**: `backend/src/logic/persona.py` — pure business logic for persona generation
2. **New backend file**: `backend/src/workflow/steps/s08_persona_generation.py`
3. **Renamed**: `s08_final_criteria.py` → `s09_final_criteria.py`
4. **Renamed**: `s09_report.py` → `s10_report.py`
5. **Modified**: `backend/src/workflow/registry.py` — insert PersonaGenerationStep
6. **Modified**: `backend/src/models/report.py` — add Persona, PersonaSet models
7. **Modified**: `backend/src/logic/export.py` — add Target Personas section to Markdown
8. **New frontend file**: `frontend/src/lib/components/steps/StepPersona.svelte`
9. **Modified**: `frontend/src/lib/components/StepRenderer.svelte` — register `persona_generation`
10. **Modified**: `frontend/src/lib/workflow-types.ts` — add Persona, PersonaSetData types

---

## No new dependencies

No new Python packages or npm packages are required. OpenHosta is already installed.

---

## Running the app (unchanged from 003)

```bash
# Backend
cd backend
uv run uvicorn src.main:app --reload

# Frontend (separate terminal)
cd frontend
bun dev
```

---

## Running tests

```bash
cd backend
uv run pytest
```

New test file to add: `src/tests/steps/test_step_s08.py` (persona generation step).
New test file to add: `src/tests/logic/test_persona.py` (logic/persona.py unit tests).

Note: existing `test_step_s08.py` covers FinalCriteriaStep — rename to `test_step_s09.py`.

---

## Verifying the new step end-to-end

1. Start the app (backend + frontend)
2. Open the workflow in browser
3. Run a full workflow — the progress indicator should show "Step 8 of 10"
4. After AI Analysis completes, the Persona Generation step auto-starts
5. A carousel with 3 persona cards appears when the step completes
6. Export Markdown — verify `## Target Personas` section is present with 3 sub-sections
