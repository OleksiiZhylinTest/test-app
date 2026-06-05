---
name: copilot-agent-monitoring
description: 'Plan, configure, or review GitHub Copilot monitoring in this repository. Use for OpenTelemetry, OTel traces, metrics, events, exporter setup, repo-level telemetry settings, captureContent privacy, or repo-local Copilot telemetry artifacts.'
argument-hint: 'Describe the monitoring task, telemetry question, or OTel setup you need reviewed'
user-invocable: true
---

# Copilot Agent Monitoring

Use this skill for GitHub Copilot monitoring work in this repository.

## When to Use

- Planning or reviewing GitHub Copilot monitoring with OpenTelemetry.
- Configuring repo-level Copilot telemetry in `.vscode/settings.json`.
- Choosing between local trace inspection, file export, or an OTLP backend.
- Interpreting traces, metrics, events, or attribute namespaces for Copilot agents.
- Reviewing privacy, secret-handling, or `captureContent` implications for monitoring.
- Explaining repo-local telemetry artifacts such as `generated/debug/copilot_context_telemetry.jsonl`.

## Procedure

1. Read `AGENTS.md`, `.github/summaries/copilot-governance.md`, and `.github/summaries/monitoring-agents.md` first.
2. Use `.github/summaries/monitoring-agents.md` for OTel defaults, exporter selection, privacy controls, and the preferred low-cost inspection order; configure `.vscode/settings.json` before suggesting any repo-level change.
3. For ongoing analysis, use `tools/copilot_telemetry_stats.py` to summarize the current session debug logs into `generated/debug/copilot_telemetry_stats.json` and `generated/debug/copilot_telemetry_stats.md`. Use the top-run and top-request sections first when the question is about token spikes or context bloat.
4. When the task is repo-local telemetry analysis, inspect `generated/debug/copilot_context_telemetry.jsonl` and `.github/hooks/pre_tool_copilot_boundary.py` together so you can explain both the recorded decision and the condition that triggered it.
5. Treat `generated/debug/copilot_context_telemetry.jsonl` as a local debug artifact, not a clean product-telemetry stream, and distinguish that repo-local hook telemetry from GitHub Copilot runtime behavior.
6. Escalate to `https://code.visualstudio.com/docs/agents/guides/monitoring-agents` only when the task needs detailed attribute tables, exporter semantics, or backend-specific setup guidance.
7. Stay inside shared repo guidance plus Copilot-owned customization files unless the user explicitly requests cross-tool governance.
8. Return the smallest viable monitoring recommendation, and include a lower-cost alternative when one exists.

## Output

- Name the affected Copilot-owned files, settings, or telemetry artifacts.
- Name any repo-level telemetry settings changed in `.vscode/settings.json`.
- Recommend the lowest-cost monitoring or inspection path that satisfies the task.
- Flag privacy, content-capture, header, or secret-handling implications.
- Separate repo-local telemetry findings from upstream VS Code OTel guidance.
- Note whether any shared-layer change in `AGENTS.md` is actually required.