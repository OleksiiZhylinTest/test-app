---
name: Deep Architecture Review
description: 'Run a deliberate higher-context architecture review when minimal context is not enough. Use for cross-layer design analysis, refactoring strategy, or repo-wide design questions.'
agent: GH Copilot Architect
argument-hint: 'Describe the architecture question or review target'
tools: [read, search, agent]
---

Perform a deep architecture review for the requested area.

Requirements:
- Start from `AGENTS.md` and relevant `.github/summaries/**` first.
- Escalate to larger docs only after stating why lower-cost sources are insufficient.
- Focus on boundaries, ownership, tradeoffs, and affected files.
- Return: findings, risks, recommended approach, and the minimum additional context still needed.