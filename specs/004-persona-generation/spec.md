# Feature Specification: Persona Generation Workflow Step

**Feature Branch**: `004-persona-generation`
**Created**: 2026-03-22
**Status**: Draft

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Happy Path: Persona Displayed After AI Analysis (Priority: P1)

After confirming products and receiving the AI market analysis, Maya wants to understand
exactly who she is building this product for. A new dedicated workflow step automatically
generates a structured buyer persona profile and displays it as a rich card — giving her
a concrete picture of her target customer before reading the final criteria.

**Why this priority**: The persona is the bridge between abstract market data and actionable
product decisions. It grounds the final go/no-go in a real human being, not just numbers.

**Independent Test**: After the AI Analysis step completes, the workflow automatically
proceeds to a Persona step that displays a fully-populated persona card — without any
additional user input required.

**Acceptance Scenarios**:

1. **Given** the AI Analysis step has completed, **When** the workflow advances to the
   Persona step, **Then** the system displays a progress indicator while generating the
   persona.
2. **Given** persona generation completes, **When** the result is displayed, **Then**
   the user sees a structured profile with at minimum: a persona name, age range,
   occupation, motivations, and pain points.
3. **Given** the persona is displayed, **When** the user reads it, **Then** the content
   is grounded in the confirmed product list and AI analysis data — not generic filler.
4. **Given** the persona step completes, **When** the workflow advances, **Then** the
   Final Criteria step receives the persona data as part of its inputs.

---

### User Story 2 — Persona Visible in Final Report (Priority: P2)

Maya wants to share her full analysis with a co-founder. The persona generated in the
new step appears as a dedicated section in the final report, alongside viability score
and final criteria.

**Why this priority**: Without report inclusion, the persona is a dead-end view — useful
only in-session. Including it in the export extends its value to async collaborators.

**Independent Test**: The exported Markdown report contains a "Target Persona" section
with the same content displayed in the workflow step.

**Acceptance Scenarios**:

1. **Given** the workflow reaches the Report step, **When** the report is generated,
   **Then** the persona data is embedded as a dedicated section with a stable heading
   (e.g., `## Target Persona`).
2. **Given** the Markdown report is exported, **When** an automated script parses it,
   **Then** the "Target Persona" section is present and non-empty.

---

### Edge Cases

- What if the AI Analysis step did not produce a usable output?
  → Persona generation is skipped; the workflow displays a notice and advances to
  Final Criteria without persona data. No blocking error is shown.
- What if persona generation fails?
  → The system displays a scoped error notice with a "Retry" action. The confirmed
  product data and AI analysis results are not lost.
- What if the product list is empty at persona-generation time?
  → Persona generation proceeds using only the AI analysis output. The persona is
  marked as "based on market trends only" in the displayed card.

---

## Requirements *(mandatory)*

### Functional Requirements

**Step 7b — Persona Generation (new step, inserted after AI Analysis)**

- **FR-P01**: The system MUST automatically execute the Persona Generation step
  immediately after the AI Analysis step completes, without requiring user action.
- **FR-P02**: The system MUST generate the persona using only the data already
  confirmed in prior steps: the confirmed product list and the AI Analysis output.
  No new external data sources are queried.
- **FR-P03**: The system MUST generate exactly 3 distinct buyer personas per workflow run.
  Each persona MUST include at minimum the following attributes: a name (archetype label),
  an age range, an occupation or role, key motivations (2–3 items), and key pain points
  (2–3 items). The three personas MUST target meaningfully different buyer profiles
  (e.g., different age segments, use cases, or purchasing motivations).
- **FR-P04**: The system MUST display a progress indicator while persona generation
  is running; the complete persona card is shown once generation completes.
- **FR-P05**: If persona generation fails, the system MUST display a scoped error
  notice and offer a user-initiated "Retry" action; confirmed product and analysis
  data MUST NOT be lost.
- **FR-P06**: If the AI Analysis output is unavailable, the system MUST skip the
  Persona step gracefully and advance to Final Criteria without blocking the user.
- **FR-P07**: The persona data MUST be accessible to the Final Criteria step and the
  Report Generation step via the standard cross-step output access mechanism (FR-026
  from spec 003).

**Frontend Component**

- **FR-P08**: A dedicated Persona component MUST display the 3 generated personas in a
  carousel — one persona visible at a time, with navigation controls to cycle between them.
- **FR-P09**: Each persona card in the carousel MUST show all attributes (name, age range,
  occupation, motivations, pain points) as clearly labelled, scannable fields — not a
  wall of prose.
- **FR-P10**: The persona component MUST follow the same visual design patterns as existing
  step result cards (StepAiAnalysis, StepFinalCriteria).
- **FR-P11a**: Carousel navigation MUST clearly indicate which of the 3 personas is active
  (e.g., "1 / 3" indicator or dot pagination).

**Report Integration**

- **FR-P12**: The Report Generation step MUST include a "Target Personas" section with
  all 3 generated personas when persona generation completed successfully.
- **FR-P13**: The "Target Personas" section heading in the Markdown export MUST be
  stable and predictable (e.g., `## Target Personas`) so that automated tools can
  locate it reliably. Each persona MUST appear as a named sub-section.

### Key Entities

- **Persona**: A structured buyer profile generated from product and market data.
  Attributes: name (archetype label), age range, occupation/role, motivations
  (list of 2–3 strings), pain points (list of 2–3 strings).
- **PersonaSet**: The complete output of the Persona Generation step — exactly 3
  distinct Persona objects.
- **PersonaStep**: A new self-contained workflow step module with declared input
  (confirmed products + AI analysis output) and output (PersonaSet) contracts,
  following the three-layer architecture defined in FR-028/FR-029 of spec 003.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-P01**: The Persona step completes and displays its result within 15 seconds
  of the AI Analysis step finishing, under normal conditions.
- **SC-P02**: The generated persona contains all five mandatory attributes (name,
  age range, occupation, motivations, pain points) in 100% of successful runs.
- **SC-P03**: The persona content references at least one detail from the confirmed
  product list (e.g., a pricing tier, a product feature, or a use case) in 80% of
  runs, as verifiable by manual review of a sample.
- **SC-P04**: The Markdown export includes a non-empty "Target Persona" section in
  100% of runs where the Persona step completed successfully.
- **SC-P05**: A user can read and understand the full persona card in under 60 seconds
  without any additional explanation.

---

## Assumptions

- The Persona step is a system-processing step (no user confirmation gate). Users
  view the result but do not edit or approve it before the workflow advances.
- The Persona step is positioned immediately after the AI Analysis step and before
  the Final Criteria step. Step numbers shift accordingly (old S08 becomes S09,
  old S09 becomes S10).
- Persona generation uses a single LLM call (OpenHosta `emulate_async`) — no external
  API calls, no scraping. The business logic function is a pure async function with
  no workflow state awareness.
- The persona is generated fresh for each workflow run; there is no caching or
  reuse across sessions.
- Partial or degraded persona (e.g., missing one attribute due to sparse input) is
  acceptable and MUST NOT block workflow progression.
- The persona is not editable by the user in this iteration. User editing of persona
  attributes is explicitly out of scope.
- PDF export layout for the new persona section inherits the existing PDF generation
  logic; no new PDF-specific formatting work is in scope.
