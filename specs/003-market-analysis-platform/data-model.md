# Data Model: Labanane — Guided Market Analysis Platform

**Feature**: 003-market-analysis-platform
**Date**: 2026-03-21
**Supersedes**: 002-guided-analysis-workflow/data-model.md

---

## Entity Relationship Overview

```
WorkflowRun (in-memory, per WebSocket connection)
  ├── confirmed_outputs[step_id] → StepOutput
  │     └── data: step-specific typed dict
  └── get_output(step_id) → dict  ← sanctioned access method

Pipeline:
  Step 1  ProductDescriptionStep  → data: ProductDescription
  Step 2  KeywordRefinementStep   → data: KeywordSet
  Step 3  KeywordConfirmationStep → confirmed KeywordSet (or loops to step 1)
  Step 4  ProductResearchStep     → data: ProductBatch
  Step 5  ProductValidationStep   → confirmed ProductBatch (or re-runs step 4)
  Step 6  MarketResearchStep      → data: MarketDataResult
  Step 7  AiAnalysisStep          → data: AiAnalysisData
  Step 8  FinalCriteriaStep       → data: FinalCriteriaData
  Step 9  ReportGenerationStep    → data: ReportData (triggers export availability)
```

---

## Backend Models (Pydantic)

### WorkflowRun

```python
@dataclass
class WorkflowRun:
    run_id: str                                      # UUID, assigned on WS connect
    total_steps: int                                 # len(PIPELINE)
    description: str                                 # current product description
    status: WorkflowStatus                           # see transitions below
    current_step_index: int                          # 0-based index into PIPELINE
    confirmed_outputs: dict[str, StepOutput]         # keyed by step_id
    created_at: datetime                             # UTC

    def get_output(self, step_id: str) -> dict:
        """Sanctioned cross-step data access. Returns {} if not found."""
```

**WorkflowStatus transitions**:
```
idle → running (on `start` message)
running → awaiting_confirmation (confirmation gate reached)
awaiting_confirmation → running (confirmation received)
running → error (StepError raised)
error → running (retry received)
running → complete (step 9 done)
* → idle (WebSocket closed → run deleted)
```

---

### StepOutput

```python
@dataclass
class StepOutput:
    step_id: str
    data: dict      # typed per step — see step data shapes below
    confirmed: bool = True
```

---

### Product (scraper output, enriched)

```python
class Product(BaseModel):
    title: str
    price: str           # formatted, e.g. "EUR 14.99" or "N/A"
    url: str             # absolute product URL
    rating_stars: float  # 0.0–5.0
    rating_count: int    # total review count
    main_features: list[str]  # exactly 3 strings
```

**Used in**: `ProductBatch.products`, `Report.products`
**Chart data for**: rating comparison bar chart, review volume bar chart

---

### KeywordSet

```python
class KeywordSet(BaseModel):
    keywords: list[str]         # 3–5 items, each non-empty
    source_description: str     # product description that generated these
```

---

### ProductBatch

```python
class ProductBatch(BaseModel):
    products: list[Product]     # ≥1; empty triggers auto-loop to product_description
    source_keywords: list[str]  # keywords used for this research pass
```

---

### TrendsData (logic layer)

```python
@dataclass
class TimePoint:
    date: str    # ISO date string "YYYY-MM-DD"
    value: int   # 0–100 relative interest

@dataclass
class RegionPoint:
    geo: str     # ISO 3166-1 alpha-2 country code
    name: str    # human-readable country name
    value: int   # 0–100 relative interest

@dataclass
class QueryPoint:
    query: str
    value: int   # absolute relative value

@dataclass
class RisingPoint:
    query: str
    value: str   # e.g. "+850%", "Breakout"

@dataclass
class KeywordTrends:
    interest_over_time: list[TimePoint]        # 52 weekly points (past 12 months)
    interest_by_region: list[RegionPoint]      # top 10 countries
    related_queries_top: list[QueryPoint]      # top 10
    related_queries_rising: list[RisingPoint]  # top 5 breakouts

@dataclass
class TrendsData:
    keywords: list[str]
    trends: dict[str, KeywordTrends]  # keyed by keyword string
```

---

### MarketDataResult (step 6 output, serialised to dict)

```python
class MarketDataResult(BaseModel):
    keywords: list[str]
    sources_available: list[str]    # e.g. ["google_trends"]
    sources_unavailable: list[str]  # e.g. [] or ["google_trends"]
    trends: dict[str, dict]         # serialised KeywordTrends per keyword
```

**Charts rendered from this shape**:
- Line chart: `interest_over_time` per keyword (multi-line, 52 points)
- Horizontal bar chart: `interest_by_region` top 10 countries
- Horizontal bar chart: `related_queries_top`
- Callout cards: `related_queries_rising`

---

### MarketAnalysis (LLM output, logic/analysis.py)

```python
class Criterion(BaseModel):
    label: str   # e.g. "Market size"
    score: int   # 0–100

class MarketAnalysis(BaseModel):
    viability_score: int            # 0–100
    go_no_go: Literal["go", "no-go", "conditional"]
    summary: str                    # 1-sentence verdict
    analysis: str                   # 2–3 sentence analysis
    key_risks: list[str]            # top 3
    key_opportunities: list[str]    # top 3
    criteria: list[Criterion]       # 3–5 scoring dimensions
    target_persona: TargetPersona
    differentiation_angles: DifferentiationAngles
    competitive_overview: CompetitiveOverview
```

**Charts rendered from this shape**:
- Donut/gauge: `viability_score`
- Horizontal bar chart: `criteria` scores

---

### FinalCriteriaData (step 8 output)

```python
class FinalCriteriaData(BaseModel):
    summary: str
    go_no_go: Literal["go", "no-go", "conditional"]
    key_risks: list[str]
    key_opportunities: list[str]
```

---

### ReportData (step 9 output)

```python
class ReportData(BaseModel):
    run_id: str
    markdown_available: bool   # True when export endpoints are ready
```

The full markdown content is generated by `logic/export.py` and stored in-memory keyed by `run_id` for download via REST endpoint. Discarded on WebSocket disconnect.

---

## Frontend Types (Zod / TypeScript)

All frontend types are derived from the `data` payloads in the WS message contract.
Zod schemas live in `frontend/src/lib/workflow-types.ts`.

```typescript
// Key shapes

type TimePoint = { date: string; value: number }
type RegionPoint = { geo: string; name: string; value: number }
type QueryPoint = { query: string; value: number }
type RisingPoint = { query: string; value: string }

type KeywordTrends = {
  interest_over_time: TimePoint[]      // → Line chart
  interest_by_region: RegionPoint[]   // → Horizontal bar chart
  related_queries_top: QueryPoint[]   // → Horizontal bar chart
  related_queries_rising: RisingPoint[] // → Callout cards
}

type MarketDataResult = {
  keywords: string[]
  sources_available: string[]
  sources_unavailable: string[]
  trends: Record<string, KeywordTrends>
}

type Product = {
  title: string
  price: string
  url: string
  rating_stars: number    // → Rating bar chart
  rating_count: number    // → Review volume chart
  main_features: string[]
}

type Criterion = { label: string; score: number }

type AiAnalysisData = {
  viability_score: number              // → Donut chart
  go_no_go: 'go' | 'no-go' | 'conditional'
  summary: string
  analysis: string
  key_risks: string[]
  key_opportunities: string[]
  criteria: Criterion[]                // → Bar chart
  target_persona: { description: string }
  differentiation_angles: { content: string }
  competitive_overview: { content: string }
}
```

---

## Component → Chart mapping

| Component | Chart | Data source |
|-----------|-------|-------------|
| `StepProductList` | Rating comparison bar | `products[].rating_stars` |
| `StepProductList` | Review volume bar | `products[].rating_count` |
| `StepMarketData` | Interest over time line | `trends[kw].interest_over_time` |
| `StepMarketData` | Interest by country bar | `trends[kw].interest_by_region` |
| `StepMarketData` | Related queries bar | `trends[kw].related_queries_top` |
| `StepFinalCriteria` | Viability score donut | `viability_score` |
| `StepFinalCriteria` | Scoring criteria bar | `criteria[]` |
