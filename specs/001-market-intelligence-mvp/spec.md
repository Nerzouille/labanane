# Feature Specification: Market Intelligence AI — Hackathon MVP

**Feature Branch**: `001-market-intelligence-mvp`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "create specification based on prd.md"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Live Market Analysis Dashboard (Priority: P1)

Maya is a solopreneur with an e-commerce product idea. She wants to validate
whether a market exists before investing time and money. She enters a keyword
and watches a market intelligence dashboard build itself in real time — without
opening any additional tabs.

**Why this priority**: This is the core product experience. Without it nothing
else has value. It is also the primary hackathon demonstration scenario.

**Independent Test**: A user can type a keyword, submit it, and observe the
dashboard sections appear progressively one after another, ending with a
viability score, a target persona, differentiation angles, and a competitive
overview — all within 60 seconds, without any additional user action.

**Acceptance Scenarios**:

1. **Given** a user opens the application, **When** they enter a keyword or product idea and submit it, **Then** the first marketplace products (title, indicative price, direct link) appear on screen within 5 seconds.
2. **Given** the pipeline is running, **When** each section is ready, **Then** it appears on the dashboard independently of the others — the user does not wait for all sections before seeing any.
3. **Given** a section is still being generated, **When** the user looks at it, **Then** they can visually distinguish it from completed sections (e.g., a loading indicator).
4. **Given** the pipeline is complete, **When** the user reads the dashboard, **Then** they can see: marketplace products, a viability score (0–100) with explanation, a target persona, differentiation angles, and a competitive overview.
5. **Given** a viability score is low (e.g., 28/100), **When** the user reads it, **Then** the dashboard explains why (saturated market, low differentiation potential) with the same clarity as a high score.

---

### User Story 2 — Export & Share the Report (Priority: P2)

Maya wants to share her findings with a business partner or feed the report into
an AI agent workflow. Once the full analysis is complete, she can export it as a
structured Markdown file or a PDF.

**Why this priority**: Export extends the life of the analysis beyond the
session and supports the AI-agent consumer use case (machine-readable MD).

**Independent Test**: After a full analysis completes, the user clicks an export
button and receives a Markdown file and a PDF file, both containing the complete
dashboard content in a readable, shareable format.

**Acceptance Scenarios**:

1. **Given** the full analysis is complete, **When** the user clicks "Export Markdown", **Then** a `.md` file downloads with all dashboard sections structured under predictable headings and the viability score in a machine-parsable format (e.g., `Score: 74/100`).
2. **Given** the full analysis is complete, **When** the user clicks "Export PDF", **Then** a `.pdf` file downloads with the full report in a human-readable layout.
3. **Given** an AI agent submits a keyword and the analysis completes, **When** the agent parses the Markdown export, **Then** all section headings are consistent and the score field is reliably parsable without manual adjustment.
4. **Given** the analysis is still in progress, **When** the user looks for export options, **Then** the export buttons are unavailable until the full report is ready.

---

### User Story 3 — Resilient Analysis under Source Unavailability (Priority: P3)

The analysis pipeline depends on multiple external data sources. If one source
is slow or unavailable, the user should still receive a useful, partial report
rather than a failure message.

**Why this priority**: Reliability is essential for the hackathon demo and for
building user trust. A partial result is always better than a blank screen.

**Independent Test**: With one data source simulated as unavailable, a user who
submits a keyword still receives a dashboard with sections from the working
sources, and the UI explicitly states which source was unavailable.

**Acceptance Scenarios**:

1. **Given** one data source exceeds its response threshold, **When** the pipeline continues with the remaining sources, **Then** the dashboard displays available sections and clearly informs the user that one source is unavailable and results may be partial.
2. **Given** two of three sources are available, **When** the analysis synthesises results, **Then** the viability score and persona are generated from available data — the system does not silently substitute invented data for the missing source.
3. **Given** all sources are available, **When** the pipeline runs, **Then** the user is not shown any unavailability notice.

---

### Edge Cases

- What happens when the keyword is empty or contains only whitespace?
  → The system rejects the input before starting the pipeline and prompts the user to enter a valid keyword.
- What happens when the keyword is extremely generic (e.g., "product")?
  → The pipeline runs as normal for the MVP; keyword-refinement suggestions are a post-MVP feature (FR-32 in prd).
- What happens if all three sources are simultaneously unavailable?
  → The pipeline informs the user that no data could be retrieved and does not generate a report with fabricated content.
- What happens if the user submits a second keyword while an analysis is running?
  → The input field and submit action are disabled during an active analysis; the user must wait for
  completion (or page reload) before starting a new one.
- After a full analysis completes, how does the user start a new analysis?
  → A "New analysis" button appears on the completed dashboard. Clicking it resets the page to the
  input state and clears the current results. The user should export before resetting if they want
  to keep the report.
- What happens if the LLM fails or is interrupted mid-generation within a section?
  → The system displays the partial content already streamed for that section plus a visible error notice
  ("Generation interrupted") on the affected section only. Other completed sections remain intact.

## Requirements *(mandatory)*

### Functional Requirements

**Input & Launch**

- **FR-001**: Users MUST be able to enter a keyword or natural-language product idea description as their analysis input.
- **FR-002**: Users MUST be able to launch the analysis from the input field without any additional configuration step.
- **FR-003**: The system MUST validate that the input contains exploitable content before starting the pipeline; empty or whitespace-only inputs MUST be rejected with a user-friendly message.
- **FR-004**: The system MUST show the user the progress of the ongoing analysis at all times.
- **FR-005**: The dashboard MUST display a skeleton/placeholder state between pipeline launch and the arrival of the first data section.
- **FR-033**: The input field and submit action MUST be disabled while an analysis is in progress; the user cannot trigger a concurrent analysis.
- **FR-034**: Once the full report is complete, a "New analysis" button MUST appear; clicking it resets the application to the input state and clears all current results immediately, with no confirmation prompt.

**Data Collection**

- **FR-006**: The system MUST retrieve existing marketplace products (title, indicative price, direct product URL) and surface them as the first visible section of the dashboard.
- **FR-007**: The system MUST retrieve demand-signal data (trend indicators) associated with the keyword.
- **FR-008**: The system MUST retrieve community sentiment and validation signals associated with the keyword.
- **FR-009**: The system MUST continue the pipeline if any single source exceeds 10 seconds without responding, delivering results from available sources.
- **FR-010**: The system MUST inform the user when a source is unavailable and that results may be partial.
- **FR-011**: The system MUST aggregate and normalise data from all available sources before passing it to the analysis layer.

**Analysis & Scoring**

- **FR-012**: The system MUST generate a viability score (0–100) based on aggregated source data.
- **FR-013**: The system MUST generate a target persona representative of the identified market segment.
- **FR-014**: The system MUST generate actionable differentiation angles for the submitted idea.
- **FR-015**: The system MUST generate an overview of the relevant competitive landscape.
- **FR-016**: The system MUST base all generated insights on real data from available sources — it MUST NOT generate scores or personas without real data input.
- **FR-017**: A low viability score MUST be presented with the same clarity and actionability as a high score (including an explanation of why the score is low).

**Streaming Dashboard**

- **FR-018**: Dashboard sections MUST appear progressively as each becomes available, without waiting for the full pipeline to complete.
- **FR-019**: AI-generated content MUST stream incrementally within each section as it is produced (token by token).
- **FR-020**: Each section MUST appear as soon as it is ready, independently of other sections.
- **FR-021**: Sections still being generated MUST be visually distinguishable from completed sections.
- **FR-032**: If the analysis engine fails or is interrupted mid-generation for a section, the system MUST display the partial content already streamed for that section together with a visible error notice ("Generation interrupted") scoped to that section only; completed sections MUST remain intact and unaffected.

**Dashboard Content**

- **FR-022**: The dashboard MUST display marketplace products with title, indicative price, and a direct link to the product page.
- **FR-023**: Users MUST be able to navigate directly to a competitor product from the dashboard via its link.
- **FR-024**: The dashboard MUST display the viability score with an explanation of the factors that determine it.
- **FR-025**: The dashboard MUST display the target persona with key characteristics.
- **FR-026**: The dashboard MUST display differentiation angles in an actionable format.
- **FR-027**: The dashboard MUST display the competitive overview with identified players.

**Export & Share**

- **FR-028**: Users MUST be able to export the complete report as structured Markdown.
- **FR-029**: The Markdown export MUST follow a stable schema: predictable section headings and a machine-parsable viability score field (e.g., `Score: 74/100`).
- **FR-030**: Users MUST be able to export the complete report as PDF.
- **FR-031**: Export actions MUST only become available once the full report has been generated.

### Key Entities

- **Keyword / Product Idea**: The user's input — a word, phrase, or short natural-language product description. It is the sole input to the analysis pipeline.
- **Analysis Pipeline**: The orchestrated process that collects data from external sources, aggregates it, and produces the structured report sections sequentially.
- **Data Source**: An external information provider (marketplace, trend analytics, social community). Each has a 10-second timeout threshold.
- **Dashboard Section**: An independently-generated and independently-displayed unit of the report. Sections: marketplace products, viability score, target persona, differentiation angles, competitive overview.
- **Viability Score**: A numeric score (0–100) summarising the market opportunity, accompanied by a human-readable explanation of its drivers.
- **Target Persona**: A description of the identified primary customer segment (demographics, motivations, context).
- **Differentiation Angles**: Specific, actionable opportunities for the product to stand out in the identified market.
- **Competitive Overview**: A summary of existing players identified in the relevant market.
- **Report Export**: The final, complete report delivered as a Markdown file or PDF once the pipeline finishes.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The first marketplace products appear on screen within 5 seconds of the user launching the analysis, under normal source availability.
- **SC-002**: The complete analysis report (all five sections) is fully generated within 60 seconds under normal source availability.
- **SC-003**: AI-generated content within a section streams continuously — no visible pause exceeding 3 seconds between content tokens within a single section.
- **SC-004**: When one data source is unavailable, the pipeline still delivers a partial report from the remaining sources within the 60-second target.
- **SC-005**: A non-technical user can understand the full market analysis dashboard — including a low viability score — without opening any additional resource.
- **SC-006**: The Markdown export can be parsed by an automated AI agent without manual adjustment, using stable section headings and score format.
- **SC-007**: The complete hackathon demonstration (from keyword entry to export) can be conveyed in under 3 minutes.

## Clarifications

### Session 2026-03-21

- Q: If the LLM fails or is interrupted mid-generation within a section, what does the user see? → A: Show partial content already streamed + a visible error notice ("Generation interrupted") scoped to that section; other completed sections remain intact.
- Q: After a full analysis completes, how does the user start a new analysis? → A: A "New analysis" button appears on the completed dashboard; clicking it resets the page to the input state and clears current results.
- Q: Should the user receive a warning before resetting if they haven't exported yet? → A: No — reset immediately with no confirmation prompt; the user is responsible for exporting before resetting.

### Assumptions

- The platform targets desktop web browsers; no mobile-optimised experience is required for the MVP.
- No user authentication or account management is in scope; the product is stateless — no analysis results are persisted after the session ends.
- The MVP covers three data sources only (marketplace, trend analytics, social community). Additional sources are explicitly post-MVP.
- Keyword-refinement suggestions for overly generic inputs are post-MVP.
- A "session" ends when the user closes or navigates away from the page.
- All client-server communication is encrypted in transit; no keyword or result data is persisted server-side beyond the active session.
