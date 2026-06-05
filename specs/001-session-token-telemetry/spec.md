# Feature Specification: Agentic SDLC Token Consumption Telemetry

**Feature Branch**: `001-session-token-telemetry`

**Created**: 2026-06-05

**Status**: Draft

**Input**: User description: "Agentic SDLC Token Consumption Telemetry — a framework-level observability feature that automatically generates a human-readable Markdown report of token consumption per step after each Claude Code agentic session."

## Clarifications

### Session 2026-06-05

- Q: How many steps should the Hotspots section show? → A: Top 5 steps (matches current implementation, standard convention for diagnostic top-N lists).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - View Session Token Report After Agentic Run (Priority: P1)

As a developer or team lead running AI-assisted SDLC tasks, I want to automatically receive a token consumption report after each agentic session so that I can understand where tokens are being spent and identify opportunities to reduce cost.

**Why this priority**: Token cost is a direct operational expense. Without visibility into per-step consumption, teams cannot optimize their agent workflows. This is the core value of the feature.

**Independent Test**: After completing any agentic session, a Markdown report file should appear in `generated/debug/` with session totals and per-turn breakdown — verifiable without any additional setup.

**Acceptance Scenarios**:

1. **Given** an agentic session has ended, **When** the session stop event fires, **Then** a Markdown report file is automatically generated at a known location without manual intervention.
2. **Given** a generated report exists, **When** the developer opens it, **Then** they see session-level totals for all four token categories (fresh input, cache reads, cache writes, output).
3. **Given** a session with multiple user prompts, **When** the report is viewed, **Then** each user prompt is shown as a separate turn section with its own subtotal line.

---

### User Story 2 - Identify Expensive Steps Within a Turn (Priority: P2)

As a developer reviewing a session report, I want to see which individual operations consumed the most tokens within each turn so that I can pinpoint the specific actions that drive cost.

**Why this priority**: Session totals alone are insufficient for optimization — developers need step-level granularity to know whether cost comes from file reads, agent delegations, or long assistant responses.

**Independent Test**: A session report for a multi-step turn should list each step as a table row with its timestamp, operation description, and per-category token counts — readable and actionable without additional tooling.

**Acceptance Scenarios**:

1. **Given** a turn with multiple tool calls, **When** the report section for that turn is viewed, **Then** each distinct tool invocation appears as a separate row in a per-step table.
2. **Given** a step that delegated to a subagent, **When** that step row is read, **Then** the operation label identifies the subagent type and the delegation description.
3. **Given** a step with no tool calls (pure assistant response), **When** that row is read, **Then** it is labelled clearly as a response step rather than an operation.

---

### User Story 3 - Find Optimization Targets via Hotspots (Priority: P3)

As a developer or architect optimizing agent workflow costs, I want to see a ranked list of the steps that loaded the most new context into the session so that I can prioritize which prompts, files, or delegations to shorten or restructure.

**Why this priority**: Cache-write tokens represent new context being priced at full rate. Surfacing the top contributors enables targeted optimization without requiring the developer to manually scan the full report.

**Independent Test**: A session with varied context-loading steps should produce a Hotspots section at the end of the report that lists the top steps by cache-write volume with a cross-reference back to their turn and step numbers.

**Acceptance Scenarios**:

1. **Given** a session where different steps loaded different amounts of new context, **When** the Hotspots section is read, **Then** steps are listed in descending order of new-context volume.
2. **Given** a session where no step loaded any new context, **When** the report is generated, **Then** no Hotspots section appears (no empty placeholder section).
3. **Given** a hotspot entry, **When** reading it, **Then** the turn number, step number, cache-write count, and operation label are all visible on a single row.

---

### Edge Cases

- What happens when a session produces no user prompts (e.g., only system messages)? → Report should exit gracefully with a diagnostic message; no partial file written.
- How does the system handle a session transcript that cannot be located or read? → Report generation is skipped with a logged warning; the stop notification still fires.
- What happens when a session transcript contains duplicate entries (e.g., from reconnection)? → Duplicate entries are de-duplicated before processing; the report reflects each API call exactly once.
- What happens when two distinct API calls happen to share identical token counts? → The system treats consecutive same-fingerprint entries as one call; non-consecutive same-fingerprint entries from different calls are treated as separate steps.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The system MUST automatically generate a token consumption report at the end of every agentic session without requiring any manual developer action.
- **FR-002**: The report MUST display session-level totals for all four token categories: fresh input tokens, cache-read tokens, cache-write tokens, and output tokens.
- **FR-003**: The report MUST group API calls into turns, where each turn corresponds to a single user prompt.
- **FR-004**: Each turn section MUST include a per-step table showing, at minimum, the step sequence number, timestamp, operation description, and per-category token counts.
- **FR-005**: Agent delegation steps MUST be labelled with the subagent type and a description of the delegation task so that delegated work is distinguishable from direct tool calls.
- **FR-006**: The report MUST include a Hotspots section listing the **top 5 steps** by new-context volume (cache-write tokens), with each entry cross-referenced to its turn and step.
- **FR-007**: The Hotspots section MUST be omitted entirely when no step in the session loaded any new context.
- **FR-008**: The report file MUST be written to the project's designated debug output directory and MUST be overwritten (not appended) on subsequent sessions with the same session identifier.
- **FR-009**: The system MUST handle malformed or unreadable transcript data gracefully — skipping generation and emitting a diagnostic — without interrupting the developer's session notification.
- **FR-010**: The system MUST support manual invocation with an explicit transcript file path so that developers can regenerate or inspect reports outside of an active session.

### Key Entities

- **Session**: A single Claude Code interaction from start to stop; identified by a unique session ID; maps to one report file.
- **Turn**: A segment of a session corresponding to one user prompt and all subsequent assistant steps until the next user prompt.
- **Step**: A single API call within a turn; one step may involve multiple tool invocations if they were issued in the same API call.
- **Token Report**: The generated Markdown artifact containing session totals, per-turn tables, and hotspots.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A token report is available within 5 seconds of any agentic session ending, requiring zero developer action.
- **SC-002**: The report correctly attributes 100% of the session's billable API calls to named turns and steps — no orphaned or missing entries.
- **SC-003**: Developers can identify the single most expensive step in a session in under 30 seconds by reading the Hotspots section alone.
- **SC-004**: The report is human-readable without any additional tooling — plain Markdown renderable in any editor or viewer.
- **SC-005**: Manual regeneration of a report from a transcript file completes without error for any valid session transcript.

## Assumptions

- The Claude Code runtime exposes the session transcript file path to stop hooks via standard input — this is the data source for the report.
- Report generation is a developer/framework-internal tool; it does not need to be accessible to end users of the product.
- The designated debug output directory (`generated/debug/`) is gitignored and does not need to be committed.
- Sessions that end abnormally (crash, force-quit) may not trigger the stop hook; reports for such sessions are not guaranteed.
- Subagent internal transcripts (from delegated agents) are separate files; this feature covers only the main session transcript. Subagent token costs are visible as a single delegation step, not as individual subagent steps.
- The feature is scoped to Claude Code sessions only; other AI assistant sessions are out of scope.
