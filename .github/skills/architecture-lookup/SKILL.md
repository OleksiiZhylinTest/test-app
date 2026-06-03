---
name: architecture-lookup
description: 'Look up repository architecture ownership and module boundaries with minimal context. Use for locating the right module, understanding layer responsibilities, or deciding whether a task needs the full architecture doc.'
argument-hint: 'Describe the feature area, file, or module you need to orient on'
user-invocable: true
---

# Architecture Lookup

Use this skill when you need architecture orientation without loading the full architecture manual first.

## When to Use

- You need to locate the right module for a change.
- You need to understand whether logic belongs in `app/core/`, `app/server/`, reporters, tests, or docs.
- You need a quick ownership map before deeper exploration.

## Procedure

1. Start with `AGENTS.md` for the shared module map.
2. If that is not enough, read `.github/summaries/architecture-module-map.md`.
3. Read only the nearest relevant source file after the summary points you to the right layer.
4. Escalate to `docs/development/architecture.md` only when you need full data-flow or cross-layer design detail.

## Output

- Name the likely owning module or layer.
- State whether the summary was sufficient or the full architecture doc is needed.
- Suggest the cheapest next file to read.