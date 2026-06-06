# Task Dependency Analysis Protocol

Apply this protocol before delegating two or more subtasks to subagents.

## Step 1 — Enumerate subtasks
List every subtask that will be delegated in this work item.

## Step 2 — Classify each pair
For each pair (A, B), mark **Sequential (A → B)** if **any** of the following hold:

| Dependency type | Condition |
|---|---|
| Data | B requires a file, value, schema, or artifact produced by A |
| Write conflict | A and B write to the same file or resource |
| State | B requires A's side effects to be in place (e.g., migration before query, schema before data) |
| Review gate | B is a Maker-Checker review or verification of A's output |

If none of the above apply → the pair is **Independent**.

## Step 3 — Build execution tiers
Group mutually independent tasks into the same tier:

```
Tier 1 (parallel): [task-a, task-b, task-c]
Tier 2 (parallel, after Tier 1): [task-d, task-e]
Tier 3 (sequential, after Tier 2): [task-f — Maker-Checker review]
```

## Step 4 — Execute per tier
- **Same tier → single Agent call**: issue all subtask prompts in one message
- **Between tiers → wait**: do not start Tier N+1 until all Tier N results are received
- **Uncertainty rule**: when unsure whether two tasks are independent, treat as sequential
