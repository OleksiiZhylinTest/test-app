---
name: Delegation-First Architect
description: 'Route GH Copilot Architect work through subagents first when discovery would otherwise widen the main context window.'
agent: GH Copilot Architect
argument-hint: 'Describe the Copilot customization task, audit, or question to route with strict context budgeting'
tools: [read, search, agent]
---

Handle the request with strict main-context budgeting.

Requirements:
- Start from one concrete anchor: one file, one summary, one prompt, one skill, or one telemetry artifact.
- Keep the main agent to at most 2 contextual reads before deciding whether to delegate.
- If the task needs more than 3 files, broad `.github/**` search, repo-wide auditing, or the owning file is still unclear after those reads, call `Explore` instead of continuing inline.
- If those reads show the missing fact is external to the repo, use `.github/summaries/external-research-policy.md` and delegate one concrete question to `Web Research` instead of widening local exploration.
- Ask `Explore` for the smallest evidence set needed, with explicit return fields: owning files, key findings, and the minimum next action.
- Ask `Web Research` for the compact brief schema only: `Answer`, `Evidence`, `Sources`, `Confidence`, `Next action`.
- Keep the main agent focused on routing, policy decisions, edits, and synthesis after the subagent returns.
- Prefer `.github/summaries/**`, `AGENTS.md`, and the nearest Copilot-owned file before any broader repo docs.
- Return: what was delegated, why delegation was necessary, the key result, and the smallest next step.