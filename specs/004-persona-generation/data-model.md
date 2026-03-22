# Data Model: Persona Generation Workflow Step

**Feature**: 004-persona-generation
**Date**: 2026-03-22
**Extends**: 003-market-analysis-platform/data-model.md

---

## Pipeline Change

Step 8 (new) is inserted between AI Analysis (step 7) and Final Criteria (formerly 8).
Total steps: **10** (was 9).

```
Step 1  ProductDescriptionStep    → data: ProductDescription
Step 2  KeywordRefinementStep     → data: KeywordSet
Step 3  KeywordConfirmationStep   → confirmed KeywordSet (or loops to step 1)
Step 4  ProductResearchStep       → data: ProductBatch
Step 5  ProductValidationStep     → confirmed ProductBatch (or re-runs step 4)
Step 6  MarketResearchStep        → data: MarketDataResult
Step 7  AiAnalysisStep            → data: MarketAnalysis (unchanged)
Step 8  PersonaGenerationStep     → data: PersonaSetData        ← NEW
Step 9  FinalCriteriaStep         → data: FinalCriteriaData     (renamed from s08)
Step 10 ReportGenerationStep      → data: ReportData            (renamed from s09)
```

---

## New Backend Models (Pydantic)

### Persona

```python
class Persona(BaseModel):
    name: str                       # archetype label, e.g. "The Weekend Creator"
    age_range: str                  # e.g. "25–35"
    occupation: str                 # e.g. "Freelance designer"
    motivations: list[str]          # 2–3 items
    pain_points: list[str]          # 2–3 items
```

Added to `backend/src/models/report.py`.

---

### PersonaSet

```python
class PersonaSet(BaseModel):
    personas: list[Persona]         # always exactly 3 items
```

Added to `backend/src/models/report.py`.

---

### PersonaSetData (step output dict shape)

Serialised output stored in `WorkflowRun.confirmed_outputs["persona_generation"].data`:

```python
{
    "personas": [
        {
            "name": str,
            "age_range": str,
            "occupation": str,
            "motivations": list[str],   # 2–3 items
            "pain_points": list[str],   # 2–3 items
        },
        # ... (3 total)
    ]
}
```

---

## New Logic Layer

### `backend/src/logic/persona.py`

Pure async functions. No workflow state, no WebSocket access.

```python
async def generate_personas(
    product_description: str,
    products: list[dict],
    ai_analysis: dict,
) -> PersonaSet:
    """
    Generate exactly 3 distinct buyer personas for the described product.
    Uses: product titles, prices, features, viability data, target segment from ai_analysis.
    Returns a PersonaSet with exactly 3 Persona objects.
    """
    result = await emulate_async()   # OpenHosta call
    raw = _coerce_to_list(result)    # str → list[dict] coercion
    normalised = _normalize_persona_list(raw)
    return PersonaSet.model_validate({"personas": normalised})
```

Helper functions (same pattern as `logic/analysis.py`):

```python
def _coerce_to_list(value: object) -> list:
    """Coerce emulate_async() output to list. JSON/ast fallback if str returned."""

def _normalize_persona_list(raw: list) -> list[dict]:
    """Ensure exactly 3 persona dicts, each with required fields.
    Fills missing fields with safe defaults. Trims to 3 if more returned."""
```

---

## New Step

### `backend/src/workflow/steps/s08_persona_generation.py`

```python
class PersonaGenerationStep(Step):
    step_id      = "persona_generation"
    label        = "Persona Generation"
    step_type    = "system_processing"
    component_type = "persona_generation"

    async def execute(self, input, run):
        yield StepProcessingMessage(step_id=self.step_id)

        products  = run.get_output("product_research").get("products", [])
        ai_result = run.get_output("ai_analysis")

        if not products and not ai_result:
            raise StepError("Cannot generate personas: no product or analysis data.", retryable=False)

        result = await generate_personas(run.description, products, ai_result)

        yield StepResultMessage(
            step_id=self.step_id,
            component_type=self.component_type,
            data=result.model_dump(),
        )
```

---

## Registry Change

`backend/src/workflow/registry.py` — insert PersonaGenerationStep at index 7:

```python
PIPELINE: list[Step] = [
    ProductDescriptionStep(),       # s01
    KeywordRefinementStep(),        # s02
    KeywordConfirmationStep(),      # s03
    ProductResearchStep(),          # s04
    ProductValidationStep(),        # s05
    MarketResearchStep(),           # s06
    AiAnalysisStep(),               # s07
    PersonaGenerationStep(),        # s08 ← NEW
    FinalCriteriaStep(),            # s09 (was s08)
    ReportGenerationStep(),         # s10 (was s09)
]
```

The engine reads `len(PIPELINE)` at run-start — no engine changes needed.

---

## Step File Renames

| Old filename | New filename | Reason |
|---|---|---|
| `s08_final_criteria.py` | `s09_final_criteria.py` | Step slot shift |
| `s09_report.py` | `s10_report.py` | Step slot shift |

Step IDs (`step_id` property) remain unchanged: `"final_criteria"`, `"report_generation"`.
Only the filenames change for clarity. The `step_id` string is the stable identifier.

---

## Frontend Types (TypeScript / Zod)

New types in `frontend/src/lib/workflow-types.ts`:

```typescript
type Persona = {
  name: string           // archetype label
  age_range: string
  occupation: string
  motivations: string[]  // 2–3 items
  pain_points: string[]  // 2–3 items
}

type PersonaSetData = {
  personas: Persona[]    // always 3
}
```

---

## New Frontend Component

### `StepPersona.svelte`

Location: `frontend/src/lib/components/steps/StepPersona.svelte`

```
Props: { data: PersonaSetData, stepId: string, status?: string, onAction: ... }

Internal state (Svelte 5 runes):
  let activeIndex = $state(0)   // 0 | 1 | 2

Layout:
  ┌─────────────────────────────────────┐
  │  Persona 1 / 3      ← active label │
  │                                     │
  │  [Card: name, age, occupation]      │
  │  Motivations: • ... • ...           │
  │  Pain points:  • ... • ...          │
  │                                     │
  │  ●  ○  ○   ← dot navigator         │
  │  [‹ Prev]           [Next ›]        │
  └─────────────────────────────────────┘
```

Navigation: clicking Prev/Next wraps around (index modulo 3).
Dot navigator: clicking a dot jumps to that persona directly.

---

## StepRenderer Change

`frontend/src/lib/components/StepRenderer.svelte` — add one entry:

```typescript
import StepPersona from './steps/StepPersona.svelte';

const COMPONENTS = {
  // ... existing entries ...
  persona_generation: StepPersona,
};
```

---

## Export Schema Change

The Markdown report gains a `## Target Personas` section inserted after `## Go / No-Go`
and before the existing `## Target Persona` section. See `contracts/export-schema-delta.md`.

Each persona appears as a sub-section:

```markdown
## Target Personas

### Persona 1: {name}

- **Age range**: {age_range}
- **Occupation**: {occupation}
- **Motivations**: {motivation 1}; {motivation 2}
- **Pain points**: {pain_point 1}; {pain_point 2}
```
