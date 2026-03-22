# Feature Specification: Labanane — Guided Market Analysis Platform

**Feature Branch**: `003-market-analysis-platform`
**Created**: 2026-03-21
**Status**: Draft
**Input**: Unified rewrite of 001-market-intelligence-mvp + 002-guided-analysis-workflow.
Inspired by both archived specs. Reddit removed from scope; no new features added.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Happy Path: Full Analysis from Idea to Report (Priority: P1)

Maya has a product idea. She enters a description, confirms the suggested keywords,
confirms the found products, and watches the market analysis stream in real time
step by step — ending with a structured report she can export.

**Why this priority**: This is the core end-to-end value delivery. Every other
story branches from this happy path.

**Independent Test**: A user can enter a product description, pass both confirmation
gates without looping, and receive a final exportable report — all in one
uninterrupted session under 5 minutes of active interaction.

**Acceptance Scenarios**:

1. **Given** a user is on the start screen, **When** they submit a product
   description, **Then** the system displays a progress indicator and then
   shows the complete set of 3–5 refined keyword suggestions.
2. **Given** keywords are displayed, **When** the user confirms them, **Then**
   product research begins automatically and results appear progressively on screen.
3. **Given** found products are displayed, **When** the user confirms them,
   **Then** market research and AI analysis run sequentially, each showing a
   progress indicator and displaying its full result on completion.
4. **Given** AI analysis completes, **When** the result is displayed, **Then**
   the user can read viability score, target persona, differentiation angles,
   and competitive overview in a single fully-rendered view.
5. **Given** the workflow reaches step 9, **When** the report is generated,
   **Then** the user can view it inline and download it as Markdown or PDF.

---

### User Story 2 — Keyword Refinement Loop (Priority: P2)

Maya's first description produces keyword suggestions that don't match her vision.
She rejects them and refines her description to generate a better set.

**Why this priority**: Poor keywords produce poor downstream research. This loop
is the first quality gate and directly protects the value of the full analysis.

**Independent Test**: A user can reject keyword suggestions, edit their description,
and see a new set of keyword suggestions generated — without losing their place
in the workflow.

**Acceptance Scenarios**:

1. **Given** keyword suggestions are displayed, **When** the user selects "No,
   refine", **Then** the system returns to the product description step with the
   current description pre-filled for editing.
2. **Given** the user submits a revised description, **When** new keywords are
   generated, **Then** the previous suggestions are replaced by the new ones.
3. **Given** the user confirms keywords on a subsequent attempt, **Then** the
   workflow continues to product research using the confirmed set.

---

### User Story 3 — Product Validation Loop (Priority: P3)

Product research returns results, but some are off-topic or irrelevant. Maya
rejects the batch and triggers a fresh product research pass.

**Why this priority**: Irrelevant products distort market research and AI analysis.
This gate ensures only valid products feed into the downstream steps.

**Independent Test**: A user can reject a batch of found products and trigger a
fresh product research pass — the previous results are discarded and a new set
is presented for validation.

**Acceptance Scenarios**:

1. **Given** found products are displayed, **When** the user selects "No, redo
   research", **Then** the system re-runs product research with the same confirmed
   keywords and streams fresh results.
2. **Given** new products are returned, **When** the user reviews them, **Then**
   they can confirm or reject the new batch.
3. **Given** the user confirms products, **When** market research begins, **Then**
   only the confirmed products are used as input.

---

### User Story 4 — Export the Report (Priority: P4)

Maya wants to share her findings with a business partner or feed them into another
AI workflow. She exports the completed report as Markdown or PDF.

**Why this priority**: Export extends the value of the analysis beyond the session
and supports both human sharing and automated agent consumption.

**Independent Test**: After a full workflow completes, the user can download a
Markdown file and a PDF file, both containing the complete analysis content.

**Acceptance Scenarios**:

1. **Given** the full analysis is complete, **When** the user clicks "Export
   Markdown", **Then** a `.md` file downloads with all sections under predictable
   headings and the viability score in a consistent format (e.g., `Score: 74/100`).
2. **Given** the full analysis is complete, **When** the user clicks "Export
   PDF", **Then** a `.pdf` file downloads with the complete report in a
   human-readable layout.
3. **Given** the report is not yet complete, **When** the user looks for export
   actions, **Then** both export buttons are unavailable.

---

### Edge Cases

- What if the user abandons the workflow or refreshes the page mid-way?
  → The server-side run state is tied to the WebSocket connection. On disconnect
  or page refresh the run is discarded and the user starts a new workflow from step 1.
- What if product research returns zero results?
  → The system informs the user and returns automatically to the keyword
  confirmation step, prompting them to refine their keywords.
- What if a system-processing step fails with an error?
  → The system displays a scoped error notice on the active step and offers a
  "Retry" action. No confirmed data from prior steps is lost.
- What if the user loops through keyword refinement many times?
  → No hard loop limit. After 3 rejections the system may surface a hint to
  try a broader or more specific description.
- What if a data source (Amazon, Google Trends) is unavailable?
  → The pipeline continues without that source. The affected step displays a
  visible partial-results notice. The AI analysis proceeds on available data
  and MUST NOT substitute invented data for the missing source.

---

## Requirements *(mandatory)*

### Functional Requirements

**Workflow Execution**

- **FR-001**: The system MUST execute workflow steps sequentially in the defined order.
- **FR-002**: The system MUST pass the confirmed output of each step as the input to the next step.
- **FR-003**: The system MUST display the current step number and total step count at all times during a run.
- **FR-004**: The server MUST maintain the active WorkflowRun state in memory for the lifetime of the WebSocket connection, so that the engine can resume execution across asynchronous steps without recomputing prior results. This state is not recoverable after disconnection — a page refresh starts a new run.
- **FR-005**: The user MUST be able to see a summary of confirmed data from previous steps at any point during the workflow.

**Step 1 — Product Description**

- **FR-006**: Users MUST be able to enter a free-text product description to initiate the workflow.
- **FR-007**: The system MUST reject empty or whitespace-only descriptions before proceeding.

**Step 2 — Keyword Refinement**

- **FR-008**: The system MUST generate 3–5 refined keyword suggestions derived from the product description.
- **FR-009**: The system MUST display a progress indicator while keyword suggestions are being generated; the complete set is shown once the step finishes.

**Step 3 — Keyword Confirmation**

- **FR-010**: Users MUST be able to confirm the keyword suggestions to advance to product research.
- **FR-011**: Users MUST be able to reject the keyword suggestions to return to step 1 (product description), with their current description pre-filled.

**Step 4 — Product Research**

- **FR-012**: The system MUST search for existing marketplace products using the confirmed keywords. The data source is Amazon; Google Shopping is an optional fallback.
- **FR-012b**: The system MUST display a progress indicator while product research is running. All found products are shown at once when the step completes.
- **FR-012c**: While product research is running, the rest of the interface MUST remain accessible and non-blocking.
- **FR-012d**: If product research is rate-limited by the data source, the system MUST automatically retry at least once silently before surfacing an error to the user. If all automatic retries are exhausted, the system MUST display a scoped error notice and offer a user-initiated "Retry" action; confirmed keywords MUST NOT be lost.
- **FR-013**: The system MUST display found products (title, indicative price, direct product link) before asking for validation.

**Step 5 — Product Validation**

- **FR-014**: Users MUST be able to confirm the found products to advance to market research.
- **FR-015**: Users MUST be able to reject the found products to re-run product research (step 4) with the same confirmed keywords.

**Step 6 — Market Research**

- **FR-016**: The system MUST retrieve market trend data for the confirmed products. The data source is Google Trends. Reddit is explicitly out of scope for this iteration.
- **FR-016b**: The system MUST display a progress indicator while market research is running. Trend data is shown in full once the step completes.
- **FR-016c**: If the data source is unavailable, the system MUST continue the workflow and display a visible partial-results notice; it MUST NOT substitute invented data.
- **FR-016d**: If market research fails, the system MUST display a scoped error notice and offer a "Retry" action; confirmed products MUST NOT be lost.

**Step 7 — AI Analysis**

- **FR-017**: The system MUST generate a viability score (0–100), a target persona, differentiation angles, and a competitive overview from the aggregated market data.
- **FR-017b**: The system MUST display a progress indicator while AI analysis is running. The full analysis result is shown at once when the step completes; no token-by-token streaming.
- **FR-018**: A low viability score MUST be presented with the same clarity and actionability as a high score, including an explanation of contributing factors.
- **FR-018b**: If AI analysis fails, the system MUST display a scoped error notice and offer a "Retry" action; market research data MUST NOT be lost.
- **FR-018c**: The system MUST NOT generate scores or analysis without real data from at least one available source.

**Step 8 — Final Criteria**

- **FR-019**: The system MUST derive and display final go/no-go criteria from the AI analysis output.

**Step 9 — Report Generation**

- **FR-020**: The system MUST generate a structured report from all confirmed step outputs and final criteria.
- **FR-021**: Users MUST be able to view the full report inline within the workflow interface.
- **FR-022**: Users MUST be able to export the report as Markdown. The schema MUST use predictable section headings and a consistent viability score format (e.g., `Score: 74/100`) so the file can be reliably parsed by automated tools.
- **FR-023**: Users MUST be able to export the report as PDF.
- **FR-024**: Export actions MUST only become available once the full report has been generated.

**Workflow Extensibility**

- **FR-025**: Each workflow step MUST be implemented as a self-contained module with a declared input contract and output contract, so that steps can be inserted or reordered by composing modules in code without modifying the core execution engine.

**Cross-Step Data Access**

- **FR-026**: Any step MUST be able to retrieve the confirmed output of any previously completed step by its identifier, without traversing internal engine state directly. A dedicated access method on the run context MUST be the sole sanctioned way for steps to read prior outputs.
- **FR-027**: The cross-step access method MUST return an empty result (not raise an error) when the requested step has no confirmed output, so that steps can safely query optional upstream data without defensive boilerplate.

**Architecture Separation**

- **FR-028**: The codebase MUST maintain a strict three-layer separation:
  - **Engine layer**: orchestration only — step sequencing, loop-back handling, error recovery, WebSocket message dispatch. No business logic.
  - **Step layer**: step definition and wiring only — declares step identity, type, and input/output contracts; delegates all computation to the business logic layer. No scraping, LLM calls, or data transformation inline.
  - **Business logic layer**: pure functions for all domain operations — scraping, LLM calls, data parsing, scoring, report formatting. No awareness of workflow state or WebSocket messages.
- **FR-029**: A change to a business logic function (e.g., switching the scraping strategy or swapping the LLM prompt) MUST require no modifications to the engine layer or step wiring.

### Key Entities

- **Workflow**: An ordered sequence of step modules composed in code; no runtime editing UI.
- **Step**: A self-contained module with a type (user-input, system-processing, confirmation, derivation), a declared input contract, and a declared output contract.
- **WorkflowRun**: A single execution instance for a user session. Tracks current step index, confirmed outputs per step, and overall status.
- **ProductDescription**: The user's free-text input that initiates the run.
- **KeywordSet**: The set of 3–5 refined keywords confirmed by the user.
- **ProductBatch**: The set of marketplace products found and confirmed by the user. Each product carries a title, indicative price, and direct URL.
- **MarketData**: Aggregated trend data retrieved for the confirmed products (Google Trends only; no Reddit).
- **AnalysisResult**: AI-generated insights: viability score, target persona, differentiation angles, competitive overview.
- **FinalCriteria**: Structured go/no-go conclusions derived from the analysis.
- **Report**: The final artefact containing all step outputs and criteria, exportable as Markdown and PDF.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can complete the full 9-step workflow (no loops) and reach the exported report in under 5 minutes of active interaction time.
- **SC-002**: Keyword suggestions are fully displayed within 5 seconds of the user submitting their product description.
- **SC-003**: Product research completes and displays all results within 15 seconds under normal source availability.
- **SC-004**: The AI analysis step completes and displays its full result within 30 seconds under normal conditions.
- **SC-005**: When one data source is unavailable, the workflow still delivers a partial analysis from the remaining source within the normal time budget.
- **SC-006**: A user unfamiliar with the product can complete a full workflow run guided solely by the step-by-step interface, without external help.
- **SC-007**: The Markdown export can be parsed by an automated script using stable section headings and the `Score: NN/100` field, without manual adjustment.

---

## Assumptions

- Multiple users may run analyses simultaneously; each browser session is fully isolated with its own independent WorkflowRun. No shared state between sessions.
- Workflow steps are defined and ordered in code; adding or reordering steps requires a code change and redeployment. No configuration file or runtime UI for step editing.
- No workflow history — only the current active run is tracked within the session.
- Data sources: Amazon (product scraping) and Google Trends (market data). Reddit is explicitly excluded from this iteration.
- Confirmation gates (steps 3 and 5) present a binary Yes/No choice. Partial confirmation (e.g., approving only some keywords) is out of scope.
- No user authentication and no server-side persistence beyond the active session.
- The platform targets desktop web browsers; mobile-optimised layout is out of scope.
- All client-server communication is encrypted in transit.

## Clarifications

### Session 2026-03-21

- Q: Can multiple users run analyses simultaneously, or is the server single-tenant? → A: Multiple users, fully isolated — each browser session gets its own independent run; no shared state between sessions.
- Q: How is workflow progress preserved across a page refresh? → A: It is not — page refresh discards the run and starts over. The server holds run state in memory only for the duration of the active WebSocket connection.
- Q: How should the scraper handle Amazon rate-limiting specifically? → A: Automatic silent retry at least once before surfacing an error to the user; user-initiated retry available if automatic retries fail.
- Q: Should AI-generated content stream token by token within steps? → A: No streaming within steps. Each step runs fully and displays its complete result at once. Workflow progresses node by node, each with a progress indicator while running.
