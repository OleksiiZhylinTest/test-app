---
description: Identify underspecified areas in the current feature spec by asking up to 5 targeted clarification questions and encoding answers back into the spec.
---

# Spec-Kit: Clarify

Identify underspecified areas in the active feature specification and resolve them interactively before planning begins.

## When to Invoke

- After `speckit.specify` has produced a `spec.md`.
- Before invoking `speckit.plan` — clarification reduces downstream rework risk.
- When the user explicitly wants to resolve `[NEEDS CLARIFICATION]` markers.

## Key Behavior

### Pre-Execution Hooks

Check `.specify/extensions.yml` for `hooks.before_clarify`. Skip hooks where `enabled: false`. Execute mandatory hooks and wait for results. Surface optional hooks to the user.

### Setup

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly` from repo root. Parse `FEATURE_DIR` and `FEATURE_SPEC` from JSON output. If parsing fails, abort and ask the user to re-run `speckit.specify` or verify the feature branch environment.

### Ambiguity Scan

Load `.specify/memory/constitution.md` if it exists. Load the current `spec.md`. Perform a structured scan across these categories (mark each Clear / Partial / Missing):

- Functional Scope & Behavior (goals, out-of-scope declarations, user roles)
- Domain & Data Model (entities, lifecycle, scale assumptions)
- Interaction & UX Flow (user journeys, error/empty states, accessibility)
- Non-Functional Quality Attributes (performance, scalability, security, compliance)
- Integration & External Dependencies (external APIs, protocols, failure modes)
- Edge Cases & Failure Handling (negative scenarios, rate limiting, conflict resolution)
- Constraints & Tradeoffs (technical constraints, rejected alternatives)
- Completion Signals (acceptance criteria testability, Definition of Done indicators)
- Misc / Placeholders (TODO markers, ambiguous adjectives lacking quantification)

### Sequential Questioning

Generate up to 5 targeted clarification questions (internally prioritized by impact × uncertainty). Present exactly one question at a time. For multiple-choice questions, recommend the best option with 1–2 sentence reasoning. For short-answer questions, constrain to ≤5 words. Only include questions whose answers materially affect architecture, data modeling, task decomposition, test design, UX, or compliance.

### Encoding Answers

After each answer, update `spec.md` directly — replace the relevant `[NEEDS CLARIFICATION]` marker or add/refine the appropriate section. Do not accumulate answers and batch-update; encode each answer immediately.

## Output

- Updated `spec.md` with clarifications encoded.
- Summary of resolved questions and sections updated.
- Recommended next step: Invoke the `speckit.plan` agent.
