# Step Prompts & Output Contracts

**Feature**: 002-guided-analysis-workflow
**Date**: 2026-03-21
**Status**: Authoritative — changes here must be reflected in step implementations.

---

## Step 2 — Keyword Refinement

**LLM client**: OpenHosta wrapping `gpt-4o-mini`
**Output model**: `KeywordSet` from `backend/src/models/workflow_models.py`

**System prompt**:
```
You are a market research assistant. Given a product description, generate 3 to 5
concise Amazon-style search keywords that a buyer would type to find this product.
Return ONLY a JSON array of strings, no explanation, no markdown.
```

**User message**: `"{description}"`

**Expected response**: `["ergonomic desk mat", "anti-fatigue desk pad", "office desk accessories"]`

**Validation**:
- Array length must be 3–5
- Each string must be non-empty and under 80 characters

**Error handling**:
- On LLM error or JSON parse failure: raise `StepError("Keyword generation failed.", retryable=True)`

---

## Step 4 — Product Research

**Approach**: httpx + BeautifulSoup4, Amazon search URL
**Output model**: `ProductBatch` from `backend/src/models/workflow_models.py`

**Search URL**: `https://www.amazon.com/s?k={keyword}&ref=nb_sb_noss`
**Keyword selection**: First keyword from confirmed `KeywordSet`
**Result quantity**: Up to 10 products from first result page
**Data fields per product**: `title` (str), `price` (str, e.g. `"$14.99"` or `"N/A"`), `url` (full Amazon product URL)
**Timeout**: 15 seconds

**Error handling**:
- Zero results: raise `StepError("No products found — please refine your description.", retryable=False)` → engine loops back to step 1
- Timeout/network error: raise `StepError("Product research failed. Please retry.", retryable=True)`

---

## Step 6 — Market Research

**Approach**: Parallel async data collection
**Output model**: `MarketData` from `backend/src/models/workflow_models.py`

**Data sources** (priority order):
1. Google Trends via `pytrends` — interest-over-time (12 months) for each confirmed keyword
2. Reddit via `praw` — top 10 posts from r/entrepreneur and r/smallbusiness matching confirmed keywords

**Execution**: `asyncio.gather(fetch_trends(), fetch_reddit(), return_exceptions=True)`
Sources that timeout are listed in `sources_unavailable`; partial results are returned.
Only raise `StepError` if ALL sources fail.

**Output shape**:
```python
MarketData(
    products=[...],              # from Step 5 confirmed ProductBatch
    trend_data={"keyword": [...]},   # or None if unavailable
    sentiment_data={"posts": [...]}, # or None if unavailable
    sources_available=["google_trends"],
    sources_unavailable=["reddit"]
)
```

---

## Step 7 — AI Analysis

**LLM client**: OpenHosta wrapping `gpt-4o-mini`, streaming enabled
**Output model**: `AnalysisResult` from `backend/src/models/workflow_models.py`

**Streaming**: yield `step_streaming_token` for each LLM token during generation

**System prompt**:
```
You are a market intelligence analyst. Analyze the following market data and produce
a structured market intelligence report. Be concise and actionable.
```

**User message** (assembled from `MarketData`):
```
Product keywords: {keywords}
Products found: {product_list}
Trend signal: {trend_summary}
Community sentiment: {sentiment_summary}

Provide:
1. Viability score (0-100 integer) and one-sentence explanation
2. Target persona (2-3 sentences)
3. Top 3 differentiation angles (numbered list)
4. Competitive landscape overview (2-3 sentences)
```

**Final `step_result` data shape**:
```json
{
  "complete": true,
  "viability_score": 72,
  "viability_explanation": "Strong demand signal with moderate competition.",
  "persona": "Urban professionals aged 28-40 working from home...",
  "differentiation_angles": "1. Eco-certified materials\n2. Custom sizing...",
  "competitive_overview": "3 dominant players with commodity pricing..."
}
```

---

## Step 8 — Final Criteria

**Approach**: Deterministic derivation from Step 7 output (no LLM call)
**Output model**: `FinalCriteria` from `backend/src/models/workflow_models.py`

**Go/No-Go threshold**:
- `score >= 65` → `"go"`
- `score >= 40` → `"conditional"`
- `score < 40` → `"no-go"`

**Risks & Opportunities**: Parsed from AI analysis content. If parsing fails, derive from `competitive_overview` and `differentiation_angles` text (simple sentence splitting).

**Output shape**:
```python
FinalCriteria(
    summary="First 2 sentences of the analysis content.",
    go_no_go="go",               # | "conditional" | "no-go"
    key_risks=["Risk 1", ...],   # 3-5 items
    key_opportunities=["Opp 1", ...]  # 3-5 items
)
```

---

## Step 9 — Report Generation

**Approach**: Render Markdown from all confirmed step outputs
**Output model**: `Report` from `backend/src/models/workflow_models.py`
**Export schema**: See `contracts/export-schema.md`

Uses `Report.markdown` field populated from the template in `export-schema.md`.
