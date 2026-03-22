# Feature Specification: Workflow UX Improvements

**Feature Branch**: `004-workflow-ux-improvements`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "specification for better ux, when things appear on the page, it should scroll down just like a chat. The product research should not have skeleton, only loader like it is, for waiting. each step of the workflow should never disappear, even the keyword validation. The confirmation step when refused should just reset the analyse. it should transition into a validated state when confirmed."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Auto-Scroll on New Content (Priority: P1)

As a user progressing through the workflow, when new content appears (a new step, results, or messages), the page automatically scrolls down to reveal it — mimicking a chat-like experience. The user never has to manually scroll to see what just appeared.

**Why this priority**: This is the foundational UX expectation. Every other improvement builds on the user being able to see new content without effort.

**Independent Test**: Can be fully tested by triggering any workflow step and verifying the page scrolls to the newly visible content automatically.

**Acceptance Scenarios**:

1. **Given** the user is on the workflow page and new content is added (new step, result, or message), **When** the content appears, **Then** the page smoothly scrolls to bring the new content into view.
2. **Given** the user has manually scrolled up to read previous steps, **When** new content appears, **Then** the page does NOT auto-scroll — the user's reading position is preserved.
3. **Given** content appears rapidly in succession, **When** multiple items appear, **Then** the scroll follows each new item without jarring jumps.

---

### User Story 2 - Persistent Workflow Steps (Priority: P1)

Each step of the workflow — including keyword validation — remains visible on the page as the user progresses. No step is removed or collapsed once it has appeared. The page grows like a conversation history.

**Why this priority**: Disappearing steps create confusion and prevent users from reviewing past decisions. Combined with auto-scroll, persistent steps make the workflow feel like a trustworthy record.

**Independent Test**: Can be fully tested by completing two or more workflow steps and verifying all previous steps remain visible on screen.

**Acceptance Scenarios**:

1. **Given** the keyword validation step has completed, **When** the next step begins, **Then** the keyword validation step is still visible above.
2. **Given** any workflow step has been shown, **When** the user progresses to a later step, **Then** all earlier steps remain displayed in order.
3. **Given** the entire workflow is complete, **When** the user looks at the page, **Then** all steps from start to finish are visible.

---

### User Story 3 - Spinner-Only Loading State Across All Steps (Priority: P2)

At every point in the workflow where the system is waiting for data or processing — including product research, any intermediate steps, and after the workflow ends or no confirmation is needed — the interface shows only a spinner. No skeleton placeholders are used anywhere in the workflow. The spinner persists until the next piece of content is ready to appear.

**Why this priority**: Skeletons imply known content shapes and can feel deceptive. A consistent spinner across all waiting states is honest, simple, and predictable — users always know the system is working.

**Independent Test**: Can be tested by observing every loading state in the workflow (each step transition, product research, end-of-workflow) and confirming zero skeleton elements appear anywhere.

**Acceptance Scenarios**:

1. **Given** any workflow step is loading or waiting for data, **When** the user views the page, **Then** a spinner is shown — no skeleton placeholder elements appear at any point.
2. **Given** the product research step has started, **When** the data is loading, **Then** a spinner is shown and no skeleton rows or cards appear.
3. **Given** the workflow has ended (all steps done, no confirmation required), **When** the system is idle, **Then** the spinner disappears and no terminal indicator is shown.
4. **Given** a step produces no confirmation prompt (auto-confirmed or skipped), **When** the workflow moves forward, **Then** a spinner is shown in place of the confirmation UI while the next step loads.
5. **Given** any loading phase completes, **When** real content is ready, **Then** the spinner disappears and the content appears in its place.

---

### User Story 4 - Confirmation Refusal Resets the Analysis (Priority: P2)

When the user reaches the confirmation step and chooses to refuse/reject, the workflow resets the analysis from the beginning — clearing results and starting fresh — without navigating the user away from the page.

**Why this priority**: A clean reset gives users a fast path to try again without confusion about what state the system is in.

**Independent Test**: Can be tested by reaching the confirmation step, refusing, and verifying the page resets to the initial analysis state.

**Acceptance Scenarios**:

1. **Given** the user is at the confirmation step, **When** they refuse/reject the results, **Then** the workflow resets to the start of the analysis.
2. **Given** the workflow has reset after a refusal, **When** the user views the page, **Then** all steps, results, and the original input field are cleared — the page is fully blank.
3. **Given** the user has refused once, **When** they start a new analysis, **Then** the full workflow runs again from scratch.

---

### User Story 5 - Confirmation Approval Transitions to Validated State (Priority: P2)

When the user confirms the results at the confirmation step, the confirmation UI transitions into a clear "validated" state — indicating the analysis has been accepted — rather than disappearing or navigating away.

**Why this priority**: A visual validated state provides closure and confidence. Users know the confirmation was registered and can see the validated outcome inline.

**Independent Test**: Can be tested by reaching the confirmation step and confirming, then verifying the confirmation UI shows a validated/accepted state.

**Acceptance Scenarios**:

1. **Given** the user is at the confirmation step, **When** they confirm/accept the results, **Then** the confirmation step transitions to a "validated" visual state (e.g., checkmark, "Validated" label, or success indicator).
2. **Given** the confirmation is validated, **When** the user views the step, **Then** the validation state is clearly distinguishable from the pending confirmation state.
3. **Given** the workflow has been validated, **When** the user scrolls through all steps, **Then** the validated confirmation step is visible among all other persistent steps.

---

### Edge Cases

- What happens when the user scrolls up while a new step is loading — does the auto-scroll interrupt reading or only trigger after content settles?
- If product research or any step fails, the spinner is replaced by an inline error message within that step — the step remains visible and is not removed.
- If the user resets via confirmation refusal while another async operation is pending, is the pending operation cleanly cancelled?
- What is shown in the "validated" state if the confirmation step has additional metadata (e.g., timestamp, summary)?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The page MUST automatically scroll to newly appeared content whenever a new step, result, or message is added — but ONLY if the user is already near the bottom of the page. If the user has scrolled up, their reading position MUST be preserved and auto-scroll MUST NOT fire.
- **FR-002**: All workflow steps, once displayed, MUST remain visible and in order for the duration of the session — no step may be removed, hidden, or collapsed after it has appeared.
- **FR-003**: The keyword validation step MUST remain visible after it completes, alongside all subsequent steps.
- **FR-004**: Skeleton placeholder elements MUST NOT be rendered anywhere in the workflow at any point — every waiting or loading state MUST use a spinner exclusively.
- **FR-004b**: When the workflow ends with no confirmation required, the spinner MUST disappear — no terminal indicator is shown.
- **FR-005**: When the user refuses/rejects at the confirmation step, the workflow MUST reset to its initial state — clearing all steps, results, and the original input field.
- **FR-006**: When the user confirms/accepts at the confirmation step, the confirmation UI MUST transition into a visible "validated" state without disappearing.
- **FR-007**: The validated state MUST be visually distinct from the pending confirmation state so the user can clearly identify that confirmation was accepted.
- **FR-008**: After a reset triggered by confirmation refusal, the user MUST be able to start a fresh analysis from the same page without navigating away.
- **FR-009**: When a workflow step fails, the error MUST be displayed inline within that step, replacing the spinner. The failed step MUST remain visible (not removed) in the persistent step list.

### Key Entities

- **Workflow Step**: A discrete unit of the analysis workflow (e.g., keyword validation, product research, confirmation). Steps are append-only in the view.
- **Confirmation State**: The state of the confirmation step — one of: pending, validated, or reset.
- **Analysis Session**: The current run of the workflow from start to confirmation or reset.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: When the user is near the bottom of the page, 100% of newly added content triggers an automatic scroll. When the user has scrolled up, their position is never interrupted by auto-scroll.
- **SC-002**: 100% of workflow steps remain visible on screen after they appear — zero steps disappear or are hidden during normal progression.
- **SC-003**: Zero skeleton elements appear anywhere in the workflow at any time — every loading or waiting state shows only a spinner.
- **SC-003b**: When the workflow ends with no confirmation required, the spinner disappears cleanly — no lingering indicator remains.
- **SC-004**: Users who refuse at the confirmation step see a fully blank page — zero residual steps, results, or input values from the previous run remain visible.
- **SC-005**: Users who confirm at the confirmation step see a validated state within the same view — zero navigations or disappearances of the confirmation UI.
- **SC-006**: Users can complete a reset-and-restart cycle without leaving the page.

## Clarifications

### Session 2026-03-22

- Q: What happens to the spinner when the workflow ends with no confirmation needed? → A: Spinner disappears entirely — no terminal indicator shown.
- Q: Does auto-scroll fire even when the user has manually scrolled up? → A: Only auto-scroll if user is near the bottom; do not interrupt if they've scrolled up.
- Q: How are step errors displayed? → A: Error shown inline within the failed step, replacing the spinner.
- Q: What does "reset" clear on confirmation refusal? → A: Everything — all steps and the original input field.

## Assumptions

- The workflow is presented as a vertically growing list of steps, making an append-and-scroll model natural.
- "Reset" on confirmation refusal means clearing all steps, results, and the original input field — returning to a fully blank state without refreshing the page.
- The "validated" state is a UI state change on the existing confirmation step card (e.g., color change, icon, label) — no new page or modal is introduced.
- Auto-scroll fires only when the user is near the bottom of the page. If the user has scrolled up, auto-scroll is suppressed entirely — no nudge or indicator is shown.
- The spinner shown across all loading states is the existing spinner/loader already in use — no new loading component is required.
- "Workflow ended with no confirmation needed" means the spinner disappears cleanly — nothing is shown after the last step's content renders.
