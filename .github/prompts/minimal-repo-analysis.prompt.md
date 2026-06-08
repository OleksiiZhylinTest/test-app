---
name: Minimal Repo Analysis
description: 'Analyze a repository task with minimal context cost. Use for low-cost orientation or quick scoping before deeper work.'
agent: GH AI Architect
argument-hint: 'Describe the task or file to analyze with minimal context'
tools: [read, search]
---

Analyze the request using the smallest relevant context in this repository.

Requirements:
- Start from the nearest concrete anchor.
- Prefer `.github/summaries/**`, `AGENTS.md`, and nearby source files before larger docs.
- Keep the first pass to one anchor plus at most two supporting reads.
- If more than three files appear necessary, stop and name the next most discriminating read instead of continuing broad exploration inline.
- For repo-wide cost or telemetry questions, prefer `generated/debug/copilot_telemetry_stats.json` or `.md` before searching across `.github/**`.
- Do not load `docs/development/architecture.md` unless the task cannot be answered from lower-cost sources.
- Return: likely owning files, the cheapest next read, whether a deeper pass is warranted, and what was intentionally skipped to keep context cost low.
