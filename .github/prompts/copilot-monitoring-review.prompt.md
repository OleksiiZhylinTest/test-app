---
name: Copilot Monitoring Review
description: 'Review GitHub Copilot monitoring, OpenTelemetry setup, telemetry privacy, or repo-local Copilot telemetry artifacts.'
agent: GH AI Architect
argument-hint: 'Describe the monitoring task, telemetry artifact, or OTel setup to review'
tools: [read, search]
---

Review the requested Copilot monitoring task in this repository.

Requirements:
- Start from one concrete anchor: one telemetry artifact, one settings file, or one Copilot-owned monitoring file.
- Route through `.github/summaries/monitoring-agents.md` and the `copilot-agent-monitoring` skill before broader references.
- Keep the first pass to at most three reads: the anchor, one summary or skill, and one supporting file if needed.
- If the user asks about token cost or context bloat, inspect `generated/debug/copilot_telemetry_stats.json` or `.md` before any broader repo search.
- Distinguish repo-local telemetry patterns from GitHub Copilot runtime monitoring behavior.
- Prefer the lowest-cost monitoring path that answers the question.
- Flag content-capture, secret-handling, and external collector risks when relevant.
- Return: affected files or settings, the specific finding, key risks, and the smallest safe next step.
- Do not quote large telemetry payloads or restate full guidance files when a short summary will do.

Examples:
- Review the lowest-friction local setup for inspecting GitHub Copilot agent traces during development.
- Explain what `generated/debug/copilot_context_telemetry.jsonl` captures and whether it is GitHub Copilot runtime telemetry.
- Compare file export, DB span export, and a local OTLP backend for a privacy-sensitive monitoring workflow.