# Contract Delta: WebSocket Messages — Persona Generation Step

**Feature**: 004-persona-generation
**Base contract**: 003-market-analysis-platform/contracts/ws-messages.md
**Date**: 2026-03-22

This document describes ONLY the changes to the WS message contract introduced by
this feature. All other message types and the connection lifecycle are unchanged.

---

## Changes to `workflow_started`

`total_steps` increases from 9 to **10**.
`step_ids` array gains `"persona_generation"` between `"ai_analysis"` and `"final_criteria"`.

```json
{
  "type": "workflow_started",
  "total_steps": 10,
  "step_ids": [
    "product_description",
    "keyword_refinement",
    "keyword_confirmation",
    "product_research",
    "product_validation",
    "market_research",
    "ai_analysis",
    "persona_generation",
    "final_criteria",
    "report_generation"
  ]
}
```

---

## New `step_result` shape: persona_generation

When `PersonaGenerationStep` completes, the server emits:

```json
{
  "type": "step_result",
  "step_id": "persona_generation",
  "component_type": "persona_generation",
  "data": {
    "personas": [
      {
        "name": "The Weekend Creator",
        "age_range": "25–35",
        "occupation": "Freelance graphic designer",
        "motivations": [
          "Wants a professional-looking workspace at low cost",
          "Values aesthetic tools that inspire creativity"
        ],
        "pain_points": [
          "Existing desk mats look cheap or wear out quickly",
          "Hard to find sizes that fit a dual-monitor setup"
        ]
      },
      {
        "name": "The Remote Professional",
        "age_range": "30–45",
        "occupation": "Software engineer working from home",
        "motivations": [
          "Needs a large, ergonomic surface for keyboard and mouse",
          "Prefers minimal, distraction-free design"
        ],
        "pain_points": [
          "Mouse skips on bare wooden desks",
          "Cables slide around without a mat anchor"
        ]
      },
      {
        "name": "The Student Hustler",
        "age_range": "18–24",
        "occupation": "University student / part-time streamer",
        "motivations": [
          "Wants a gaming-aesthetic setup on a tight budget",
          "LED-lit accessories are a status signal in their community"
        ],
        "pain_points": [
          "Most premium mats are too expensive for a student budget",
          "Parents' house desk is too small for XL mats"
        ]
      }
    ]
  }
}
```

**Field constraints**:
- `personas`: always an array of exactly 3 objects
- `name`: non-empty string, archetype label
- `age_range`: non-empty string (e.g. "25–35")
- `occupation`: non-empty string
- `motivations`: array of 2–3 non-empty strings
- `pain_points`: array of 2–3 non-empty strings

---

## No changes to other message types

`step_processing`, `step_error`, `confirmation_request`, `workflow_complete` are
unchanged for this step. `PersonaGenerationStep` is a `system_processing` type step
and does not emit a `confirmation_request`.
