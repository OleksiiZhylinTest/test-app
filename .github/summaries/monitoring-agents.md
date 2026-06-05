# Copilot Summary: Monitoring Agents

Use this summary for monitoring choices, privacy defaults, and repo-local telemetry context before loading the full VS Code guide.

## Source of Truth

- `https://code.visualstudio.com/docs/agents/guides/monitoring-agents`
- `.github/hooks/pre_tool_copilot_boundary.py`
- `.github/summaries/copilot-governance.md`

## OTel at a Glance

- Copilot Chat emits traces, metrics, and events for agent interactions.
- Prefer `github.copilot.*` attributes for new dashboards and analysis. Treat `copilot_chat.*` as legacy compatibility keys.
- Monitoring is off by default, and prompt or tool content is off by default.
- Lowest-cost inspection order: local SQLite export, repo-local session debug log rollups, then file export or a local OTLP backend such as Aspire Dashboard or Jaeger when raw span browsing matters.

## Key Monitoring Controls

- Enable monitoring with `github.copilot.chat.otel.enabled`, `github.copilot.chat.otel.dbSpanExporter.enabled`, `COPILOT_OTEL_ENABLED=true`, or an OTLP endpoint.
- Use `github.copilot.chat.otel.otlpEndpoint` or `OTEL_EXPORTER_OTLP_ENDPOINT` to point at a collector.
- Use `github.copilot.chat.otel.exporterType` to choose `otlp-http`, `otlp-grpc`, `console`, or `file`.
- Current repo-local setup: `.vscode/settings.json` attempts file export to `generated/debug/copilot_chat_otel.jsonl` with `github.copilot.chat.otel.captureContent: false`, but treat the JSONL export as unverified until the file is observed locally.
- Preferred low-cost workflow in this repository today: use session debug log rollups from `tools/copilot_telemetry_stats.py` first, enable SQLite export when you need local span persistence, and use file export only after confirming the JSONL file is actually being written in the current VS Code build.
- Treat `github.copilot.chat.otel.captureContent`, `COPILOT_OTEL_CAPTURE_CONTENT=true`, and `OTEL_EXPORTER_OTLP_HEADERS` as security-sensitive because they can capture prompt/tool content or carry secrets.

## Repo-Level Stats Workflow

- Use `tools/copilot_telemetry_stats.py` to summarize the current Copilot session debug logs.
- The script writes rollups to `generated/debug/copilot_telemetry_stats.json` and `generated/debug/copilot_telemetry_stats.md`, including per-agent totals plus top costly runs and individual requests by input tokens.
- The raw file-export OTel output and the generated stats are complementary when the JSONL export is present: the OTel file is raw export data, while the stats files are repo-local rollups for quick inspection.
- Use `tools/copilot_session_stats.py` for **per-session analysis**: it reads the current session debug-log directory and writes `generated/debug/copilot_session_<id>.md` with session totals, per-agent breakdown, and input-token hotspots. Use this report as the primary input when `GH AI Architect` produces a session-specific improvement plan. Use `tools/copilot_telemetry_stats.py` for **cross-session aggregate trends**.
- Artifact pattern: `generated/debug/copilot_session_<id>.md` — per-session report, ephemeral, gitignored.

## Repo-Local Telemetry Pattern

- `.github/hooks/pre_tool_copilot_boundary.py` writes local debug JSONL records to `generated/debug/copilot_context_telemetry.jsonl`.
- The hook records candidate counts, heavy-doc usage, summary-doc usage, Claude-boundary targets, and decisions such as `allow`, `warn`, or `ask`.
- The file is useful for explaining repo-specific boundary and context-cost decisions, but it can include file paths or truncated content-derived strings from tool inputs.
- This is a repo-local Claude pattern, not GitHub Copilot runtime enforcement. For GitHub Copilot, rely on agent descriptions, skill procedures, prompts, and tool restrictions.

## Escalate When

- you need the full span attribute tables, exporter details, or backend-specific setup steps
- you need to compare foreground Copilot, CLI, and Claude trace structures in detail
- you need a monitoring recommendation that depends on a specific observability backend