---
description: Create or update the project constitution from interactive or provided principle inputs, ensuring all dependent spec-kit templates stay in sync.
---

# Spec-Kit: Constitution

Create or update the project constitution at `.specify/memory/constitution.md` and propagate principle changes to all dependent spec-kit templates.

## When to Invoke

- During initial project setup to establish governance principles.
- When project principles, constraints, or governance rules change.
- When dependent templates need to be realigned with updated principles.

## Key Behavior

### Pre-Execution Hooks

Check `.specify/extensions.yml` for `hooks.before_constitution`. Skip hooks where `enabled: false`. Execute mandatory hooks and wait for results. Surface optional hooks to the user.

### Load Constitution

Load `.specify/memory/constitution.md`. If missing, copy from `.specify/templates/constitution-template.md` first. Identify every placeholder token of the form `[ALL_CAPS_IDENTIFIER]`.

### Collect & Draft

1. Collect values for all placeholders from user input, conversation context, or repo context (README, docs).
2. For governance dates: `RATIFICATION_DATE` is the original adoption date; `LAST_AMENDED_DATE` is today if changes are made.
3. Increment `CONSTITUTION_VERSION` using semantic versioning:
   - MAJOR: Backward-incompatible principle removals or redefinitions.
   - MINOR: New principle or section added.
   - PATCH: Clarifications, wording, typo fixes.
4. Replace every placeholder with concrete text. Justify any intentionally retained placeholders.
5. Ensure each Principle section has: succinct name, non-negotiable rules, explicit rationale.
6. Ensure Governance section covers: amendment procedure, versioning policy, compliance review.

### Consistency Propagation

After updating the constitution, verify and update dependent artifacts:
- `.specify/templates/plan-template.md` — align "Constitution Check" rules with updated principles.
- `.specify/templates/spec-template.md` — update mandatory sections or constraints.
- `.specify/templates/tasks-template.md` — update principle-driven task types.
- `.specify/templates/commands/*.md` — remove outdated agent-specific references when generic guidance is required.
- `README.md` and relevant docs — update principle references.

### Sync Impact Report

Prepend a Sync Impact Report as an HTML comment at the top of the updated constitution file:
- Version change (old → new)
- Modified principles
- Added/removed sections
- Templates updated (✅ updated / ⚠ pending) with file paths
- Deferred TODOs with justification

### Validation

Before writing: no unexplained bracket tokens; version matches report; dates in ISO format (YYYY-MM-DD); principles are declarative and free of vague language.

### Post-Execution Hooks

Check `.specify/extensions.yml` for `hooks.after_constitution`. Process mandatory hooks and surface optional hooks.

## Output

- Updated `.specify/memory/constitution.md`.
- New version and bump rationale.
- Files updated or flagged for manual follow-up.
- Suggested commit message.
