---
name: Compact External Brief
description: 'Return a minimal external research brief for the main Copilot agent context.'
agent: Web Research
argument-hint: 'Describe the exact external question, required source priority, and any sensitive local context that must not be sent'
tools: [read, search]
---

Return a compact external research brief.

Requirements:
- Read `.github/summaries/external-research-policy.md` before responding.
- Use external lookup only when the runtime exposes an approved native or MCP capability. If not, fail closed.
- Prefer official sources and primary specifications.
- Do not include long quotations or copied passages.
- Do not exceed 180 words.
- Use exactly these fields in order:
  - `Answer:`
  - `Evidence:`
  - `Sources:`
  - `Confidence:`
  - `Next action:`
- If blocked, replace `Evidence` with `Blocked:` and state the missing approved capability.