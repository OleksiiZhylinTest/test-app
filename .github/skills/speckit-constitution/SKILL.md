---
name: speckit-constitution
description: "Create or update the project constitution and ensure all dependent spec-kit templates stay in sync."
argument-hint: "Describe the principle or change to encode in the constitution"
user-invocable: true
---

# Spec-Kit: Constitution

Create or update the project constitution at `.specify/memory/constitution.md` and propagate all principle changes to dependent spec-kit templates.

## When to Use

- During initial project setup to establish governance principles.
- When project principles, constraints, or governance rules need to change.
- When templates need realignment after principle updates.

## Procedure

1. **Check extension hooks**: Read `.specify/extensions.yml` for `hooks.before_constitution`. Skip where `enabled: false`. Execute mandatory hooks and wait for results.

2. **Load constitution**: Load `.specify/memory/constitution.md`. If missing, copy from `.specify/templates/constitution-template.md` first. Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.

3. **Collect and draft**:
   - Collect values for all placeholders from user input, conversation context, or repo context (README, docs).
   - Governance dates: `RATIFICATION_DATE` = original adoption date; `LAST_AMENDED_DATE` = today if changes are made.
   - Increment `CONSTITUTION_VERSION` (semantic versioning):
     - MAJOR: Backward-incompatible principle removals or redefinitions.
     - MINOR: New principle or section added or materially expanded.
     - PATCH: Clarifications, wording, typo fixes.
   - Replace every placeholder with concrete text. Justify any intentionally retained placeholders.
   - Ensure each Principle section has: succinct name, non-negotiable rules, explicit rationale.
   - Ensure Governance section covers: amendment procedure, versioning policy, compliance review.
   - Principles must be declarative and free of vague language ("should" → MUST/SHOULD with rationale).

4. **Consistency propagation**: After updating, verify and update dependent artifacts:
   - `.specify/templates/plan-template.md` — align "Constitution Check" rules.
   - `.specify/templates/spec-template.md` — update mandatory sections or constraints.
   - `.specify/templates/tasks-template.md` — update principle-driven task types.
   - `.specify/templates/commands/*.md` — remove outdated agent-specific references.
   - `README.md` and relevant docs — update principle references.

5. **Sync Impact Report**: Prepend as HTML comment at top of updated constitution:
   - Version change (old → new), modified principles, added/removed sections.
   - Templates updated (✅ / ⚠ pending) with file paths.
   - Deferred TODOs with justification.

6. **Validate before writing**: No unexplained bracket tokens; version matches report; dates ISO format (YYYY-MM-DD); principles declarative and non-vague.

7. **Write** completed constitution back to `.specify/memory/constitution.md` (overwrite).

8. **Post-execution hooks**: Check `.specify/extensions.yml` for `hooks.after_constitution`. Process mandatory and optional hooks.

## Output

- Updated `.specify/memory/constitution.md`.
- New version and bump rationale.
- Files updated or flagged for manual follow-up.
- Suggested commit message (e.g., `docs: amend constitution to vX.Y.Z`).
