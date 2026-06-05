---
name: speckit-implement
description: "Execute the implementation plan by processing all tasks defined in tasks.md."
argument-hint: "Path to the approved tasks.md or feature name"
user-invocable: true
---

# Spec-Kit: Implement

Execute the feature implementation by processing all tasks defined in an approved `tasks.md`. Human approval of `tasks.md` is required before running.

## When to Use

- After `speckit-analyze` has run and the user has reviewed and approved `tasks.md`.
- Do not invoke if `tasks.md` has not been human-reviewed.

## Procedure

1. **Check extension hooks**: Read `.specify/extensions.yml` for `hooks.before_implement`. Skip where `enabled: false`. Execute mandatory hooks and wait for results.

2. **Setup**: Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` from repo root. Parse `FEATURE_DIR` and `AVAILABLE_DOCS`. All paths must be absolute.

3. **Checklist gate**: If `FEATURE_DIR/checklists/` exists, scan all checklist files. Count total, completed (`- [X]`/`- [x]`), and incomplete (`- [ ]`) items per file. Display a status table:
   ```
   | Checklist    | Total | Completed | Incomplete | Status  |
   |--------------|-------|-----------|------------|---------|
   | ux.md        | 12    | 12        | 0          | ✓ PASS  |
   | security.md  | 8     | 5         | 3          | ✗ FAIL  |
   ```
   If any checklist is incomplete: pause and ask "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)". Halt if user says no.

4. **Load implementation context**:
   - **Required**: `tasks.md`, `plan.md`.
   - **Optional (if exists)**: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`, `.specify/memory/constitution.md`.

5. **Project setup verification**: Create or verify ignore files based on detected project setup (`.gitignore`, `.dockerignore`, `.eslintignore`, `.prettierignore`, etc.). Use tech stack from `plan.md` to select appropriate patterns. Append missing critical patterns only if file already exists.

6. **Parse and execute tasks**: Extract phases, dependencies, and task details from `tasks.md`. Execute in dependency order. For `[P]`-marked tasks, identify parallel execution opportunities. Mark each completed task `[x]` in `tasks.md`.

7. **Post-execution hooks**: Check `.specify/extensions.yml` for `hooks.after_implement`. Process mandatory and optional hooks.

## Output

- Implementation progress (tasks completed / total).
- Files created or modified.
- Any blockers or deviations from the plan.
- Updated `tasks.md` with completed items marked.
