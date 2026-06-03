---
name: requirements-routing
description: 'Route a task to the correct requirements file with minimal context. Use when behavior changes and you need the right requirement document or status rows before implementation.'
argument-hint: 'Describe the changed behavior or feature area'
user-invocable: true
---

# Requirements Routing

Use this skill to find the correct requirements file before loading multiple requirement documents.

## When to Use

- A task changes behavior and you need the correct requirements file.
- You want the minimum requirements context before implementation.
- You need to know whether multiple requirement areas are affected.

## Procedure

1. Start with `.github/summaries/requirements-routing.md`.
2. Map the task to one or more requirement topic areas.
3. Open `docs/product/requirements/README.md` only if you need exact IDs or acceptance criteria.
4. Open the specific requirement file only after routing is clear.

## Output

- Name the relevant requirement file or files.
- Say whether exact IDs are needed next.
- Keep the response scoped to routing, not full requirement analysis.