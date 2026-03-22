# Contract: Export Schema

**Feature**: 003-market-analysis-platform
**Status**: Active

---

## REST Endpoints

```
GET /api/export/{run_id}/markdown   → 200 text/markdown; attachment; filename="analysis-{run_id}.md"
GET /api/export/{run_id}/pdf        → 200 application/pdf; attachment; filename="analysis-{run_id}.pdf"
```

Both endpoints are only available after the workflow reaches `complete` status (step 9 done).
`run_id` is the UUID assigned at WebSocket connect and returned in `workflow_complete`.

---

## Markdown Schema

The Markdown export MUST follow this heading hierarchy exactly.
The `Score: NN/100` line on the viability score MUST be machine-parsable (stable, no surrounding text on that line).

```markdown
# Market Analysis: {product_description}

**Date**: YYYY-MM-DD
**Run ID**: {run_id}
**Verdict**: go | no-go | conditional

---

## Keywords Used

- keyword 1
- keyword 2
- keyword 3

---

## Marketplace Products

| Product | Price | Rating | Reviews |
|---------|-------|--------|---------|
| {title} | {price} | {rating_stars}/5 | {rating_count} |

---

## Market Trends (Google Trends)

*(Trend data is descriptive text — charts are browser-only)*

- **{keyword}**: Peak interest in {month}, strongest in {country}.

---

## Viability Score

Score: {viability_score}/100

{explanation}

---

## Go / No-Go: {go_no_go}

{summary}

---

## Target Persona

{description}

---

## Differentiation Angles

{content}

---

## Competitive Overview

{content}

---

## Key Risks

- {risk 1}
- {risk 2}
- {risk 3}

---

## Key Opportunities

- {opportunity 1}
- {opportunity 2}
- {opportunity 3}

---

## Scoring Criteria

| Criterion | Score |
|-----------|-------|
| {label}   | {score}/100 |
```

**Machine-parseable fields**:
- `Score: NN/100` — viability score (line starts exactly with `Score: `)
- `**Verdict**: go|no-go|conditional` — go/no-go field
- All section headings are stable and MUST NOT change without a constitution amendment

---

## PDF

PDF is generated from the Markdown via:
`markdown_string → HTML (python-markdown) → PDF (weasyprint)`

No additional content beyond the Markdown schema. Charts are not included in the PDF (browser-only rendering). A note is added to the PDF header: *"Charts available in the interactive browser view."*
