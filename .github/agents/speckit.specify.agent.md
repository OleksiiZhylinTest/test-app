---
description: Create or update the feature specification from a natural language feature description. Use when starting a new feature to produce specs/NNN-feature-name/spec.md.
---

# Spec-Kit: Specify

Create or update the feature specification from a natural language feature description.

## When to Invoke

- Starting a new feature that requires a structured specification before planning or implementation.
- Updating an existing spec when feature scope changes.
- Run this before `speckit.clarify`, `speckit.plan`, or `speckit.tasks`.

## Key Behavior

### Pre-Execution Hooks

Check if `.specify/extensions.yml` exists. If it does, look for entries under `hooks.before_specify`. Skip hooks where `enabled: false`. For each executable mandatory hook, execute it and wait for the result before proceeding. For optional hooks, surface them to the user.

### Feature Directory Setup

1. Generate a concise 2–4 word short name for the feature (action-noun format; preserve technical acronyms).
2. Determine the feature directory under `specs/`:
   - Check `.specify/init-options.json` for `branch_numbering` (`sequential` or `timestamp`).
   - Sequential: next 3-digit prefix scanning existing `specs/` directories (e.g., `003-user-auth`).
   - Timestamp: `YYYYMMDD-HHMMSS-<short-name>`.
3. Create `specs/<directory-name>/spec.md` from the resolved spec template.
4. Persist the resolved path to `.specify/feature.json` as `feature_directory`.

### Spec Generation

1. Load `.specify/memory/constitution.md` if it exists.
2. Load the active spec template to understand required sections.
3. Parse the feature description; extract actors, actions, data, constraints.
4. For unclear aspects, add `[NEEDS CLARIFICATION: specific question]` markers — limit to 3 maximum.
5. Fill all template sections: User Scenarios, Functional Requirements, Success Criteria, Key Entities, Assumptions.
6. Each Functional Requirement must be testable; Success Criteria must be measurable.

### Specification Quality Validation

After writing the spec, generate a quality checklist at `specs/<feature-dir>/checklists/requirements.md` validating completeness, clarity, consistency, and measurability of requirements. Do not use checklist items that verify implementation — only verify requirement quality.

### Post-Execution Hooks

Check `.specify/extensions.yml` for `hooks.after_specify`. Process mandatory and optional hooks as above.

## Output

- Path to the created `spec.md`.
- List of any `[NEEDS CLARIFICATION]` markers inserted.
- Path to the generated requirements quality checklist.
- Recommended next step: Invoke the `speckit.clarify` agent to resolve open questions.
