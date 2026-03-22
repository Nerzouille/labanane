# Report Export Schema

**Feature**: 002-guided-analysis-workflow
**Date**: 2026-03-21
**Status**: Frozen — changes here require updating Step 9 implementation and tests.

---

## Markdown Template

```markdown
# Market Intelligence Report: {keyword}
Generated: {generated_at} | Run ID: {run_id}

## Go / No-Go
**Recommendation**: {go_no_go}

{summary}

## Viability Score
Score: {viability_score}/100
{viability_explanation}

## Target Persona
{persona}

## Differentiation Angles
{differentiation_angles}

## Competitive Overview
{competitive_overview}

## Product Research
{product_list}

## Key Risks
{key_risks}

## Key Opportunities
{key_opportunities}
```

---

## Field Definitions

| Placeholder | Source | Format |
|-------------|--------|--------|
| `{keyword}` | `WorkflowRun.description` | Plain string |
| `{generated_at}` | UTC timestamp at step 9 execution | `YYYY-MM-DD HH:MM UTC` |
| `{run_id}` | `WorkflowRun.run_id` | UUID string |
| `{go_no_go}` | `FinalCriteria.go_no_go` | `Go` / `No-Go` / `Conditional` (title case) |
| `{summary}` | `FinalCriteria.summary` | Plain paragraph |
| `{viability_score}` | `AnalysisResult.viability_score.score` | Integer 0–100 |
| `{viability_explanation}` | `AnalysisResult.viability_score.explanation` | Plain sentence |
| `{persona}` | `AnalysisResult.target_persona.description` | Plain paragraph |
| `{differentiation_angles}` | `AnalysisResult.differentiation_angles.content` | Pre-formatted (numbered list from LLM) |
| `{competitive_overview}` | `AnalysisResult.competitive_overview.content` | Plain paragraph |
| `{product_list}` | `ProductBatch.products` | Bullet list: `- {title} — {price} ({url})` |
| `{key_risks}` | `FinalCriteria.key_risks` | Numbered list: `1. {risk}` |
| `{key_opportunities}` | `FinalCriteria.key_opportunities` | Numbered list: `1. {opportunity}` |

---

## Machine-Parsable Anchors

The following lines are stable and machine-parsable:

- `Score: {n}/100` — viability score (integer, 0–100)
- `**Recommendation**: {value}` — go/no-go decision (`Go`, `No-Go`, `Conditional`)
- `# Market Intelligence Report:` — document type identifier
- `Run ID: {uuid}` — unique run identifier

These anchors MUST NOT change format between versions.
