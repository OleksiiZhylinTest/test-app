---
description: Execute the implementation plan by processing and executing all tasks defined in specs/NNN-feature-name/tasks.md. Requires human-approved tasks.md before running.
---

# Spec-Kit: Implement

Execute the feature implementation by processing all tasks defined in an approved `tasks.md`.

## When to Invoke

- After `speckit.analyze` has run and the user has reviewed and approved `tasks.md`.
- Human approval of `tasks.md` is required before this agent runs.
- Do not invoke if `tasks.md` has not been reviewed.

## Key Behavior

### Pre-Execution Hooks

Check `.specify/extensions.yml` for `hooks.before_implement`. Skip hooks where `enabled: false`. Execute mandatory hooks and wait for results. Surface optional hooks to the user.

### Setup

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` from repo root. Parse `FEATURE_DIR` and `AVAILABLE_DOCS`. All paths must be absolute.

### Checklist Gate

If `FEATURE_DIR/checklists/` exists, scan all checklist files. Count total, completed (`- [X]`/`- [x]`), and incomplete (`- [ ]`) items per checklist. Display a status table. If any checklist is incomplete, pause and ask: "Some checklists are incomplete. Do you want to proceed with implementation anyway? (yes/no)". Do not continue unless user confirms.

### Load Implementation Context

- **Required**: `tasks.md` (complete task list and execution plan), `plan.md` (tech stack, architecture, file structure).
- **Optional (if exists)**: `data-model.md`, `contracts/`, `research.md`, `quickstart.md`, `.specify/memory/constitution.md`.

### Project Setup Verification

Create or verify ignore files based on detected project setup:
- Git repo → `.gitignore` (patterns for detected language from `plan.md`)
- Docker → `.dockerignore`
- ESLint → `.eslintignore`
- Prettier → `.prettierignore`

If the ignore file already exists, verify it contains essential patterns and append only missing critical patterns. If missing, create with full pattern set.

### Task Execution

Parse `tasks.md` for phases, dependencies, and task details. Execute tasks in dependency order. For tasks marked `[P]`, identify parallel execution opportunities. After completing each task, mark it `[x]` in `tasks.md`.

### Post-Execution Hooks

Check `.specify/extensions.yml` for `hooks.after_implement`. Process mandatory hooks and surface optional hooks.

## Output

- Implementation progress (tasks completed / total).
- Files created or modified.
- Any blockers or deviations from the plan.
- Updated `tasks.md` with completed items marked.
