---
name: speckit-specify
description: "Create or update the feature specification from a natural language feature description."
argument-hint: "Describe the feature you want to specify"
user-invocable: true
---

# Spec-Kit: Specify

Create or update the feature specification from a natural language feature description.

## When to Use

- Starting a new feature before any planning or implementation work.
- Updating an existing spec when feature scope changes.
- Run this before `speckit-clarify`, `speckit-plan`, or `speckit-tasks`.

## Procedure

1. **Check extension hooks**: Read `.specify/extensions.yml` if it exists. Look for `hooks.before_specify`. Skip hooks where `enabled: false`. For mandatory hooks, execute and wait for the result. For optional hooks, surface to the user.

2. **Generate feature short name**: Produce a 2–4 word short name from the feature description (action-noun format; preserve technical acronyms).

3. **Resolve feature directory**:
   - Check `.specify/init-options.json` for `branch_numbering` (`sequential` or `timestamp`).
   - Sequential: next 3-digit prefix by scanning `specs/` (e.g., `003-user-auth`).
   - Timestamp: `YYYYMMDD-HHMMSS-<short-name>`.
   - Create `specs/<directory-name>/spec.md` from the resolved spec template.
   - Persist the resolved path to `.specify/feature.json` as `feature_directory`.

4. **Load context**: Load `.specify/memory/constitution.md` if it exists. Load the active spec template to understand required sections.

5. **Generate specification**:
   - Parse the feature description; extract actors, actions, data, constraints.
   - For unclear aspects, add `[NEEDS CLARIFICATION: specific question]` markers — maximum 3.
   - Prioritize clarifications by impact: scope > security/privacy > user experience > technical details.
   - Fill all template sections: User Scenarios, Functional Requirements, Success Criteria, Key Entities, Assumptions.
   - Each Functional Requirement must be testable; Success Criteria must be measurable and technology-agnostic.

6. **Quality validation**: After writing the spec, generate a quality checklist at `specs/<feature-dir>/checklists/requirements.md`. Checklist items validate requirement completeness, clarity, consistency, and measurability — not implementation correctness.

7. **Post-execution hooks**: Check `.specify/extensions.yml` for `hooks.after_specify`. Process mandatory and optional hooks.

## Output

- Path to created `spec.md`.
- List of `[NEEDS CLARIFICATION]` markers inserted (if any).
- Path to generated quality checklist.
- Recommend invoking `speckit-clarify` to resolve open questions before planning.
