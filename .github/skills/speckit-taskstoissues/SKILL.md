---
name: speckit-taskstoissues
description: "Convert existing tasks.md items into actionable, dependency-ordered GitHub issues."
argument-hint: "Path to tasks.md or feature name"
user-invocable: true
---

# Spec-Kit: Tasks to Issues

Convert approved `tasks.md` items into dependency-ordered GitHub issues using the GitHub MCP server.

## When to Use

- After `tasks.md` has been reviewed and approved.
- When the team tracks feature implementation work in GitHub Issues.
- Requires: a GitHub remote URL and GitHub MCP server access.

## Procedure

1. **Check extension hooks**: Read `.specify/extensions.yml` for `hooks.before_taskstoissues`. Skip where `enabled: false`. Execute mandatory hooks and wait for results.

2. **Setup**: Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` from repo root. Parse `FEATURE_DIR` and `AVAILABLE_DOCS`. All paths must be absolute. Load `.specify/memory/constitution.md` if it exists. Extract the path to `tasks.md`.

3. **Verify GitHub remote**: Run `git config --get remote.origin.url`. Verify the remote is a GitHub URL.

   > **CAUTION**: Only proceed if the remote is a GitHub URL. Abort if it is not.

4. **Create issues**: For each task in `tasks.md`, use the GitHub MCP server to create a new issue in the repository that matches the Git remote URL. Map task fields: task ID and description → issue title; task labels and phase → issue labels; task dependencies → linked issues or body references.

   > **CAUTION**: Never create issues in repositories that do not match the remote URL.

5. **Post-execution hooks**: Check `.specify/extensions.yml` for `hooks.after_taskstoissues`. Process mandatory and optional hooks.

## Output

- List of created GitHub issue URLs with task ID cross-references.
- Total issues created.
- Any tasks skipped and reason.
