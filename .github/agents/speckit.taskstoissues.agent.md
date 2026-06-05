---
description: Convert existing tasks in tasks.md into actionable, dependency-ordered GitHub issues. Requires a GitHub remote and MCP GitHub server access.
---

# Spec-Kit: Tasks to Issues

Convert approved `tasks.md` items into dependency-ordered GitHub issues using the GitHub MCP server.

## When to Invoke

- After `tasks.md` has been reviewed and approved.
- When the team uses GitHub Issues to track feature implementation work.
- Requires: a GitHub remote URL and GitHub MCP server access.

## Key Behavior

### Pre-Execution Hooks

Check `.specify/extensions.yml` for `hooks.before_taskstoissues`. Skip hooks where `enabled: false`. Execute mandatory hooks and wait for results. Surface optional hooks to the user.

### Setup

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` from repo root. Parse `FEATURE_DIR` and `AVAILABLE_DOCS`. All paths must be absolute. Load `.specify/memory/constitution.md` if it exists. Extract the path to `tasks.md`.

### GitHub Remote Verification

Run `git config --get remote.origin.url`. Verify the remote is a GitHub URL.

> **CAUTION**: Only proceed if the remote is a GitHub URL. Abort if it is not.

### Issue Creation

For each task in `tasks.md`, use the GitHub MCP server to create a new issue in the repository matching the Git remote URL. Map task fields to issue fields: task ID and description → issue title, task labels and phase → issue labels, task dependencies → linked issues or body references.

> **CAUTION**: Never create issues in repositories that do not match the remote URL.

### Post-Execution Hooks

Check `.specify/extensions.yml` for `hooks.after_taskstoissues`. Process mandatory hooks and surface optional hooks.

## Output

- List of created GitHub issue URLs with task ID cross-references.
- Total issues created.
- Any tasks skipped and reason.
