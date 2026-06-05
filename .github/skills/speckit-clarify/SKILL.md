---
name: speckit-clarify
description: "Identify underspecified areas in the current feature spec and resolve them interactively."
argument-hint: "Path to the spec.md file or feature name to clarify"
user-invocable: true
---

# Spec-Kit: Clarify

Identify underspecified areas in the active feature specification and resolve them interactively, then encode answers back into the spec before planning begins.

## When to Use

- After `speckit-specify` has produced a `spec.md`.
- Before invoking `speckit-plan` to reduce downstream rework risk.
- To resolve `[NEEDS CLARIFICATION]` markers in the active spec.

## Procedure

1. **Check extension hooks**: Read `.specify/extensions.yml` for `hooks.before_clarify`. Skip where `enabled: false`. Execute mandatory hooks first.

2. **Setup**: Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -PathsOnly` from repo root. Parse `FEATURE_DIR` and `FEATURE_SPEC` from JSON. If parsing fails, abort and ask the user to re-run `speckit-specify`.

3. **Load context**: Load `.specify/memory/constitution.md` if it exists. Load the current `spec.md`.

4. **Ambiguity scan**: Perform a structured scan across these categories (mark each Clear / Partial / Missing):
   - Functional Scope & Behavior (goals, out-of-scope declarations, user roles)
   - Domain & Data Model (entities, lifecycle, scale assumptions)
   - Interaction & UX Flow (user journeys, error/empty states, accessibility)
   - Non-Functional Quality Attributes (performance, scalability, security, compliance)
   - Integration & External Dependencies (external APIs, protocols, failure modes)
   - Edge Cases & Failure Handling (negative scenarios, rate limiting, conflict resolution)
   - Constraints & Tradeoffs (technical constraints, rejected alternatives)
   - Completion Signals (acceptance criteria testability, Definition of Done indicators)
   - Misc / Placeholders (TODO markers, ambiguous adjectives lacking quantification)

5. **Generate questions**: Produce a prioritized queue of up to 5 clarification questions (internally, by impact × uncertainty). Present exactly one question at a time. For multiple-choice questions, recommend the best option with 1–2 sentence reasoning and present all options with a Why It Matters column. For short-answer questions, constrain to ≤5 words. Only include questions whose answers materially affect architecture, data modeling, task decomposition, test design, UX, or compliance.

6. **Encode answers**: After each answer, immediately update the relevant section in `spec.md`. Do not batch-update; encode each answer as it arrives.

7. **Complete**: After all questions are answered (up to 5), confirm the spec has no remaining unresolved clarification markers.

## Output

- Updated `spec.md` with clarifications encoded.
- Summary of resolved questions and sections updated.
- Recommend invoking `speckit-plan` next.
