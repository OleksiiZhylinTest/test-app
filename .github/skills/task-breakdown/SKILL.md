---
name: task-breakdown
description: 'Decompose an ambiguous or broad request into typed, assignable sub-tasks. Use when a request spans multiple areas or when the implementation path is unclear. Returns a structured task list with type labels, owner agents, anchor files, and dependency order.'
argument-hint: 'Describe the feature, request, or goal to break down into sub-tasks'
user-invocable: true
---

# Task Breakdown

Use this skill when a request needs to be decomposed before it can be delegated or implemented.

## When to Use

- The request mentions multiple features, modules, or areas without clear boundaries.
- The implementation path is unclear (e.g., "improve performance", "add DAU support", "update the UI").
- The request requires changes across code, tests, docs, and governance simultaneously.
- The user has not specified what kind of output they want (code change, plan, explanation, or all three).

## Task Types

| Type | Label | Owner |
|------|-------|-------|
| Application code change | `[code]` | Default agent (or relevant module owner) |
| Test addition or update | `[test]` | Default agent (narrowest layer via `test-layer-selection` skill) |
| Documentation update | `[docs]` | Default agent |
| Requirements update | `[reqs]` | Default agent (route via `requirements-routing` skill) |
| Copilot environment change | `[copilot-env]` | `GH AI Architect` |
| External research | `[research]` | `GH Web Search` |
| Codebase discovery | `[explore]` | `Explore` |
| Architecture or design decision | `[design]` | `Explore` + default agent synthesis |

## Procedure

1. Read `.github/summaries/project-manager-routing.md` for routing context.
2. Identify the top-level goal from the request (one sentence).
3. List all observable side effects: which modules, surfaces, or docs will change.
4. Assign a type label to each side effect (see table above).
5. Assign a delegate agent to each labeled task.
6. Identify dependencies: which tasks must complete before others can start.
7. Sequence: put independent tasks first (parallelizable), dependent tasks after.
8. Assign an anchor file to each task (the first file the delegate should read).

## Output Format

```
Goal: <one-sentence top-level goal>

Sub-tasks:
1. [explore]  Discover affected modules — delegate: Explore — anchor: AGENTS.md
2. [code]     Implement <X> in <module> — delegate: default agent — anchor: app/<file>
3. [test]     Add unit tests for <X> — delegate: default agent — anchor: tests/unit/
4. [reqs]     Update requirement status for <area> — delegate: default agent — anchor: docs/product/requirements/README.md
5. [docs]     Update architecture.md if modules change — delegate: default agent — anchor: docs/development/architecture.md
6. [copilot-env]  Update PM routing summary — delegate: GH AI Architect — anchor: .github/summaries/project-manager-routing.md

Dependencies:
- Task 2 depends on Task 1 (need discovery results first)
- Tasks 3–6 depend on Task 2 (need implementation complete)
- Tasks 3–6 are independent of each other (parallelizable)
```

## Constraints

- Do not add speculative tasks. Only include tasks the request explicitly or clearly implicitly requires.
- Flag (do not add) tasks that are improvements beyond the stated scope.
- Keep each sub-task atomic: one agent, one anchor, one clear deliverable.
