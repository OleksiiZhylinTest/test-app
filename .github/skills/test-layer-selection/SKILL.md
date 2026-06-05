---
name: test-layer-selection
description: 'Choose the narrowest useful test layer for a change. Use for deciding between unit, component, integration, and e2e coverage without loading broad test docs by default.'
argument-hint: 'Describe the changed code path or user-visible behavior'
user-invocable: true
---

# Test Layer Selection

Use this skill to choose the cheapest effective test layer before exploring the full test suite.

## When to Use

- You changed logic and need to know where to add tests.
- You want to avoid over-testing a small slice.
- You need a quick route to the right fixtures or runner.

## Procedure

1. Start with `.github/summaries/test-structure.md`.
2. Identify whether the change is pure logic, handler/reporter slice, cross-module flow, or browser behavior.
3. Select the narrowest layer that proves the behavior.
4. Escalate to `tests/conftest.py` or a layer-specific conftest only when fixture detail is required.

## Output

- Name the recommended primary test layer.
- Note any secondary layer only if necessary.
- Identify the next fixture or test file to inspect.