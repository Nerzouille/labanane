# Contract Delta: Export Schema — Persona Generation Step

**Feature**: 004-persona-generation
**Base contract**: 003-market-analysis-platform/contracts/export-schema.md
**Date**: 2026-03-22

---

## Change: New `## Target Personas` section

A new `## Target Personas` section is inserted into the Markdown export between
`## Go / No-Go` and `## Target Persona` (the existing single-persona field from
the AI Analysis output).

### Insertion point in full schema

```
## Go / No-Go: {go_no_go}
...
--- ← existing separator

## Target Personas               ← NEW SECTION
...
---

## Target Persona                ← existing (unchanged)
...
```

### New section format

```markdown
## Target Personas

### Persona 1: {personas[0].name}

- **Age range**: {personas[0].age_range}
- **Occupation**: {personas[0].occupation}
- **Motivations**: {personas[0].motivations joined with " · "}
- **Pain points**: {personas[0].pain_points joined with " · "}

### Persona 2: {personas[1].name}

- **Age range**: {personas[1].age_range}
- **Occupation**: {personas[1].occupation}
- **Motivations**: {personas[1].motivations joined with " · "}
- **Pain points**: {personas[1].pain_points joined with " · "}

### Persona 3: {personas[2].name}

- **Age range**: {personas[2].age_range}
- **Occupation**: {personas[2].occupation}
- **Motivations**: {personas[2].motivations joined with " · "}
- **Pain points**: {personas[2].pain_points joined with " · "}
```

**Stable heading**: `## Target Personas` — MUST NOT change without a constitution amendment.

---

## Fallback (persona step skipped or failed)

If `persona_generation` output is not present in the run, the `## Target Personas`
section is omitted entirely from the export. The export remains valid without it.
