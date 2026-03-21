# Feature Specification: Guided Analysis Workflow

**Feature Branch**: `002-guided-analysis-workflow`
**Created**: 2026-03-21
**Status**: Draft
**Input**: User description: "strict workflow mindset — 9-step guided analysis pipeline with confirmation loops and extensible steps"

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Happy Path: Full Analysis from Description to Report (Priority: P1)

Maya has a product idea. She goes through the full 9-step workflow in one sitting
without needing to loop back at any confirmation point. She ends up with a
structured market intelligence report ready to act on.

**Why this priority**: This is the core end-to-end value delivery. Every other
story builds on or branches from this flow.

**Independent Test**: A user can enter a product description, confirm the refined
keywords, confirm the validated products, and receive a final report — all in a
single uninterrupted session.

**Acceptance Scenarios**:

1. **Given** a user is on the start screen, **When** they submit a product description, **Then** the system presents 3–5 refined keyword suggestions based on the description.
2. **Given** keywords are displayed, **When** the user confirms they are correct, **Then** product research begins automatically using those keywords.
3. **Given** product research is complete, **When** the user confirms the found products are valid, **Then** market research begins on those products.
4. **Given** market research is complete, **When** AI analysis finishes, **Then** the system presents the final criteria and a downloadable report.
5. **Given** the workflow reaches the final step, **When** the report is generated, **Then** the user can view it inline and export it.

---

### User Story 2 — Keyword Refinement Loop (Priority: P2)

Maya describes her product idea but the suggested keywords don't quite match her
vision. She rejects them and re-enters a more precise description to generate
better keywords.

**Why this priority**: The refinement loop is the first quality gate. Poor
keywords produce poor research — allowing the user to course-correct here avoids
wasted downstream steps.

**Independent Test**: A user can reject keyword suggestions, provide a revised
description, and see new keyword suggestions generated — without losing their
place in the workflow.

**Acceptance Scenarios**:

1. **Given** keyword suggestions are displayed, **When** the user selects "No, refine", **Then** the system returns to the product description step with the current description pre-filled for editing.
2. **Given** the user submits a revised description, **When** new keywords are generated, **Then** the previous rejected keywords are no longer shown.
3. **Given** the user has looped back multiple times, **When** they finally confirm keywords, **Then** the workflow continues to product research using the confirmed set.

---

### User Story 3 — Product Validation Loop (Priority: P3)

Product research returns results, but some are off-topic or irrelevant. The user
rejects the batch and triggers a new product research pass to get better results.

**Why this priority**: The second quality gate ensures only relevant products
feed into market research and AI analysis. Irrelevant products distort the
final report.

**Independent Test**: A user can reject a batch of found products and trigger
a fresh product research pass — the previous results are discarded and new
ones are presented for validation.

**Acceptance Scenarios**:

1. **Given** found products are displayed, **When** the user selects "No, redo research", **Then** the system re-runs product research with the same confirmed keywords.
2. **Given** new products are returned, **When** the user reviews them, **Then** they can confirm or reject this new batch.
3. **Given** the user confirms products, **When** market research begins, **Then** only the confirmed products are used as input.

---

### User Story 4 — Workflow Step Insertion (Priority: P4)

A power user wants to add a custom step between two existing steps (e.g., a
"filter by price range" step between product research and product validation).
The workflow registry allows this without breaking the existing flow.

**Why this priority**: Extensibility is a stated design goal. This story ensures
the workflow is not hardcoded and can grow over time.

**Independent Test**: A new step can be inserted between any two existing steps
and the workflow executes correctly in the new order, with the inserted step
receiving the output of the preceding step as its input.

**Acceptance Scenarios**:

1. **Given** a workflow definition exists with steps 1–9, **When** a new step is inserted at position 5 (between existing steps 4 and 5), **Then** the workflow executes steps 1→4→new→5→…→9 in that order.
2. **Given** the inserted step completes, **When** its output is passed to the next step, **Then** the next step receives the inserted step's output (not the previous step's).
3. **Given** a step is inserted, **When** the user runs the workflow, **Then** the step counter and progress indicator reflect the new total step count.

---

### Edge Cases

- What happens if the user abandons the workflow mid-way?
  → The current progress is preserved in the session; the user can resume from the last confirmed step. If the session expires, the workflow restarts from step 1.
- What if product research returns zero results?
  → The system informs the user that no products were found for the given keywords and returns to the keyword refinement step automatically.
- What if the user loops through keyword refinement more than 5 times?
  → No hard limit is enforced; the user may loop indefinitely. The system may optionally surface a suggestion to try broader keywords after 3 failed loops.
- What if any system-processing step (product research, market research, AI analysis) fails with an error?
  → All system-processing steps share the same recovery pattern: the system displays an error notice scoped to that step and offers a "Retry" action. No prior confirmed data (from earlier steps) is lost. The user retries from the failed step only.
- What if a newly inserted step produces no output?
  → The workflow treats an empty output the same as a skipped step and passes the preceding step's output to the next step unchanged, with a visible notice to the user.

---

## Requirements *(mandatory)*

### Functional Requirements

**Workflow Execution**

- **FR-001**: The system MUST execute workflow steps sequentially in the defined order.
- **FR-002**: The system MUST pass the output of each step as the input to the next step.
- **FR-003**: The system MUST display the current step number and total step count at all times during a workflow run.
- **FR-004**: The system MUST preserve workflow progress within a session; a page refresh MUST NOT lose the user's confirmed data.
- **FR-005**: The system MUST allow the user to see a summary of all confirmed data from previous steps at any point during the workflow.

**Step 1 — Product Description**

- **FR-006**: Users MUST be able to enter a free-text product description to initiate the workflow.
- **FR-007**: The system MUST reject empty or whitespace-only descriptions before proceeding.

**Step 2 — Keyword Refinement**

- **FR-008**: The system MUST generate 3–5 refined keyword suggestions from the product description.
- **FR-009**: The system MUST display the suggested keywords clearly before asking for confirmation.

**Step 3 — Keyword Confirmation**

- **FR-010**: Users MUST be able to confirm the keyword suggestions to advance to product research.
- **FR-011**: Users MUST be able to reject the keyword suggestions to return to step 1 (product description), with the current description pre-filled.

**Step 4 — Product Research**

- **FR-012**: The system MUST conduct product research using the confirmed keywords.
- **FR-012b**: While product research is running, the system MUST display an inline progress indicator on the active step; the rest of the interface MUST remain accessible (non-blocking).
- **FR-012c**: If product research fails with an error, the system MUST display a scoped error notice and offer a retry action without losing the confirmed keywords.
- **FR-013**: The system MUST display the found products to the user before asking for validation.

**Step 5 — Product Validation**

- **FR-014**: Users MUST be able to confirm the found products to advance to market research.
- **FR-015**: Users MUST be able to reject the found products to re-run product research (step 4) with the same keywords.

**Step 6 — Market Research**

- **FR-016**: The system MUST conduct market research on the confirmed products.
- **FR-016b**: If market research fails with an error, the system MUST display a scoped error notice and offer a retry action without losing the confirmed products.
- **FR-016c**: While market research is running, the system MUST display an inline progress indicator on the active step; the rest of the interface MUST remain accessible (non-blocking).

**Step 7 — AI Analysis**

- **FR-017**: The system MUST run AI analysis on the market research data.
- **FR-017b**: While AI analysis is running, the system MUST display an inline progress indicator on the active step; the rest of the interface MUST remain accessible (non-blocking).
- **FR-018**: If AI analysis fails, the system MUST display a scoped error notice and offer a retry action without discarding the market research data.

**Step 8 — Final Criteria**

- **FR-019**: The system MUST derive and display final criteria from the AI analysis output.

**Step 9 — Report Generation**

- **FR-020**: The system MUST generate a structured report from the final criteria.
- **FR-021**: Users MUST be able to view the report inline within the workflow interface.
- **FR-022**: Users MUST be able to export the report (at minimum as Markdown and PDF).

**Workflow Extensibility**

- **FR-023**: Each workflow step MUST be implemented as an independent, self-contained code module with a defined input contract and output contract, so that steps can be inserted, appended, or reordered by composing modules in code without modifying the core execution engine.
- **FR-024**: A new step module inserted between two existing steps MUST receive the preceding step's output as its input and pass its own output to the following step, enforced by the shared step interface.
- **FR-025**: The step counter and progress indicator MUST automatically reflect the correct total derived from the assembled step sequence at runtime.

### Key Entities

- **Workflow**: An ordered sequence of steps. Carries a version or definition identifier. Steps can be inserted or appended.
- **Step**: A self-contained code module implementing a shared step interface. Has a type (user-input, system-processing, confirmation), a declared input contract, and a declared output contract. Position is determined by the order in which steps are composed in code.
- **WorkflowRun**: A single execution instance of a Workflow for a given user session. Tracks current step, confirmed outputs per step, and overall status.
- **ProductDescription**: The user's free-text input that initiates the run.
- **KeywordSet**: The set of 3–5 refined keywords generated from the product description and confirmed by the user.
- **ProductBatch**: The set of products returned by product research, subject to user validation.
- **MarketData**: The aggregated market research output for the validated products.
- **AnalysisResult**: The AI-generated insights derived from market data.
- **FinalCriteria**: The structured set of conclusions derived from the analysis.
- **Report**: The final artefact, containing all criteria and supporting data, exportable as Markdown and PDF.

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A user can complete the full 9-step workflow (no loops) and receive a final report in under 5 minutes of active interaction time.
- **SC-002**: At each confirmation step, the decision (confirm / reject) is registered and acted upon within 1 second.
- **SC-003**: A user who rejects keywords and re-enters a description can reach the product research step within 2 additional interactions.
- **SC-004**: A new workflow step can be inserted at any position and the workflow executes correctly in the new order on the next run, without any changes to existing steps.
- **SC-005**: Workflow progress is recoverable within the same session after a page refresh — the user does not lose any confirmed data.
- **SC-006**: A user unfamiliar with the product can complete a full workflow run without external help, guided solely by the step-by-step interface.

## Clarifications

### Session 2026-03-21

- Q: If system-processing steps (product research, market research, AI analysis) fail with an error, do all share the same retry pattern as AI analysis? → A: Yes — all system-processing steps show a scoped error notice + retry, no prior confirmed data lost.
- Q: When does a step insertion take effect — config file, runtime UI, or code? → A: Steps are defined directly in code as modular units; the workflow is assembled programmatically. No config file, no runtime UI for step editing.
- Q: What does the user see while a system-processing step is running? → A: A step-level progress indicator shown inline on the active step; the interface is non-blocking — the user can scroll and review prior confirmed steps.

### Assumptions

- One workflow run corresponds to one user session; no multi-user or team collaboration is in scope.
- The workflow is assembled in code from modular step units; there is no configuration file and no runtime UI for step editing. Adding or reordering steps requires a code change and redeployment.
- Workflow history (past runs) is not required for this feature; only the current active run is tracked.
- The confirmation UI at steps 3 and 5 presents a simple Yes / No choice; partial confirmation (e.g., confirming only some keywords) is out of scope.
- While a system-processing step runs, the UI shows a step-level inline progress indicator and remains non-blocking — the user can scroll and review all prior confirmed steps. The interface is never fully locked.
