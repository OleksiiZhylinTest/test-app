---
name: project-orchestration
description: 'Orchestrate an incoming request end-to-end: classify the request type, identify the correct delegate agents, sequence sub-tasks, and synthesize results into one coherent response. Use when the GH Project Manager needs a structured procedure for routing a multi-part or ambiguous request.'
argument-hint: 'Describe the incoming request to orchestrate'
user-invocable: true
---

# Project Orchestration

Use this skill when the GH Project Manager receives a request that needs structured classification, delegation, and synthesis.

## When to Use

- Any new feature, improvement, bug, or task that is not immediately self-contained.
- Requests that could touch more than one module, agent, or repo surface.
- Requests where the correct specialist agent is not immediately obvious.

## Procedure

1. **Load the routing anchor**: read `.github/summaries/project-manager-routing.md` first.
2. **Load shared conventions**: read `AGENTS.md` if not already in context.
3. **Classify the request** using the type table in the routing anchor (feature, governance, research, discovery, requirements, multi-type).
4. **Check for ambiguity**: if the request spans ≥2 categories or the output shape is unclear, ask one focused clarifying question before proceeding.
5. **Build the sub-task list**: map each classified part to its delegate agent and anchor file.
6. **Present the plan** to the user if ≥3 sub-tasks or if shared contracts are affected; otherwise proceed.
7. **Delegate sequentially or in parallel**:
   - Independent sub-tasks (no shared state): invoke delegates in parallel.
   - Dependent sub-tasks (output of one feeds the next): invoke sequentially.
8. **Collect results**: wait for all delegations to complete before synthesizing.
9. **Synthesize**: produce one coherent response. Do not echo raw subagent output verbatim.
10. **Flag residuals**: list any unresolved items, follow-up tasks, or security findings at the end.

## Escalation Conditions

- If a subagent returns a security concern → stop the plan, surface the finding, and wait for user guidance.
- If classification requires >2 inline reads → delegate discovery to `Explore` before routing.
- If the request is ambiguous after one clarifying exchange → default to the broadest safe classification and note the assumption.

## Output

- Classification label (one line).
- Ordered sub-task list with delegate agent and anchor per step.
- Synthesized result after all delegates complete.
- Residual flags section (may be empty).
