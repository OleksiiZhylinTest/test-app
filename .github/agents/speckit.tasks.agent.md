---
description: Generate an actionable, dependency-ordered tasks.md for the feature based on available design artifacts in specs/NNN-feature-name/.
---

# Spec-Kit: Tasks

Generate an actionable, dependency-ordered `tasks.md` from available design artifacts in the feature directory.

## When to Invoke

- After `speckit.plan` has produced `plan.md`.
- Before `speckit.analyze` and `speckit.implement`.

## Key Behavior

### Pre-Execution Hooks

Check `.specify/extensions.yml` for `hooks.before_tasks`. Skip hooks where `enabled: false`. Execute mandatory hooks and wait for results. Surface optional hooks to the user.

### Setup

Run `.specify/scripts/powershell/setup-tasks.ps1 -Json` from repo root. Parse `FEATURE_DIR`, `TASKS_TEMPLATE`, and `AVAILABLE_DOCS` from JSON output. All paths must be absolute.

### Load Design Documents

- **Required**: `plan.md` (tech stack, libraries, structure), `spec.md` (user stories with priorities).
- **Optional**: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`.
- Load `.specify/memory/constitution.md` if it exists.

### Task Generation

1. Extract tech stack, libraries, and project structure from `plan.md`.
2. Extract user stories with priorities (P1, P2, P3) from `spec.md`.
3. Map entities from `data-model.md` (if present) to user stories.
4. Map interface contracts (if present) to user stories.
5. Generate tasks organized by user story using the strict checklist format:
   ```
   - [ ] [TaskID] [P?] [Story?] Description with file path
   ```
6. Generate a dependency graph showing user story completion order.
7. Identify parallel execution opportunities (mark with `[P]`).
8. Validate task completeness: each user story must have all needed tasks and independent test criteria.

### tasks.md Structure

- Phase 1: Setup tasks (project initialization)
- Phase 2: Foundational tasks (blocking prerequisites for all user stories)
- Phase 3+: One phase per user story (priority order from `spec.md`)
- Each phase: story goal, independent test criteria, implementation tasks
- Final Phase: Polish & cross-cutting concerns
- Dependencies section and parallel execution examples
- Implementation strategy section (MVP first, incremental delivery)

**Note**: Test tasks are optional — only include if explicitly requested in the spec or if the user requests TDD approach.

### Post-Execution Hooks

Check `.specify/extensions.yml` for `hooks.after_tasks`. Process mandatory hooks and surface optional hooks.

## Output

- Path to generated `tasks.md`.
- Total task count and count per user story.
- Parallel opportunities identified.
- Independent test criteria per story.
- Suggested MVP scope (typically User Story 1).
- Format validation: confirm all tasks follow the checklist format.
- Recommended next step: Invoke the `speckit.analyze` agent.
