---
name: speckit-tasks
description: "Generate an actionable, dependency-ordered tasks.md from available design artifacts."
argument-hint: "Path to the feature spec or feature name"
user-invocable: true
---

# Spec-Kit: Tasks

Generate an actionable, dependency-ordered `tasks.md` from available design artifacts in the feature directory.

## When to Use

- After `speckit-plan` has produced `plan.md`.
- Before `speckit-analyze` and `speckit-implement`.

## Procedure

1. **Check extension hooks**: Read `.specify/extensions.yml` for `hooks.before_tasks`. Skip where `enabled: false`. Execute mandatory hooks and wait for results.

2. **Setup**: Run `.specify/scripts/powershell/setup-tasks.ps1 -Json` from repo root. Parse `FEATURE_DIR`, `TASKS_TEMPLATE`, and `AVAILABLE_DOCS` from JSON. All paths must be absolute.

3. **Load design documents**:
   - **Required**: `plan.md` (tech stack, libraries, structure), `spec.md` (user stories with priorities).
   - **Optional**: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`.
   - Load `.specify/memory/constitution.md` if it exists.

4. **Execute task generation**:
   - Extract tech stack, libraries, and project structure from `plan.md`.
   - Extract user stories with priorities (P1, P2, P3) from `spec.md`.
   - Map entities from `data-model.md` to user stories (if present).
   - Map interface contracts to user stories (if present).
   - Generate tasks organized by user story. Every task MUST follow this format:
     ```
     - [ ] [TaskID] [P?] [Story?] Description with file path
     ```
   - Generate a dependency graph showing user story completion order.
   - Identify parallel execution opportunities (mark `[P]`).
   - Validate completeness: each user story has all needed tasks and independent test criteria.

5. **Generate `tasks.md`** using `TASKS_TEMPLATE` (fall back to `.specify/templates/tasks-template.md`):
   - Phase 1: Setup tasks
   - Phase 2: Foundational tasks (blocking prerequisites)
   - Phase 3+: One phase per user story (priority order)
   - Final Phase: Polish & cross-cutting concerns
   - Dependencies section and parallel execution examples
   - Implementation strategy (MVP first)

   **Test tasks are optional** — include only if explicitly requested in the spec or user requests TDD.

6. **Post-execution hooks**: Check `.specify/extensions.yml` for `hooks.after_tasks`. Process mandatory and optional hooks.

## Output

- Path to generated `tasks.md`.
- Total task count and count per user story.
- Parallel opportunities identified.
- Independent test criteria per story.
- Suggested MVP scope (typically User Story 1).
- Recommend invoking `speckit-analyze` next.
