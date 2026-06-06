#!/usr/bin/env python3
"""Generate a per-session Copilot token and agent report.

Reads the VS Code Copilot session debug-log directory (all *.jsonl files) and
writes a single Markdown report to generated/debug/.

Outputs:
- generated/debug/copilot_session_<session_id_short>.md
"""

from __future__ import annotations

import argparse
import json
import os
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUTPUT_DIR = ROOT / "generated" / "debug"


def _parse_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            item = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(item, dict):
            events.append(item)
    return events


def _detect_agent(file_name: str, events: list[dict[str, Any]]) -> str:
    if file_name == "main.jsonl":
        return "Main Agent"
    for event in events:
        attrs = event.get("attrs")
        if event.get("type") == "subagent" and isinstance(attrs, dict) and attrs.get("agentName"):
            return f"Subagent: {attrs['agentName']}"
    prefix = "runSubagent-"
    marker = "-call_"
    if file_name.startswith(prefix) and marker in file_name:
        return f"Subagent: {file_name[len(prefix):file_name.index(marker)]}"
    return file_name


def _summarize_run(file_name: str, events: list[dict[str, Any]]) -> dict[str, Any]:
    llm_events = [
        event
        for event in events
        if event.get("type") == "llm_request" and isinstance(event.get("attrs"), dict)
    ]
    input_tokens = 0
    output_tokens = 0
    max_input_tokens = 0
    max_output_tokens = 0
    total_input_message_chars = 0
    max_input_message_chars = 0

    for event in llm_events:
        attrs = event["attrs"]
        event_input_tokens = int(attrs.get("inputTokens") or 0)
        event_output_tokens = int(attrs.get("outputTokens") or 0)
        input_messages = str(attrs.get("inputMessages") or "")
        input_message_chars = len(input_messages)
        input_tokens += event_input_tokens
        output_tokens += event_output_tokens
        total_input_message_chars += input_message_chars
        max_input_tokens = max(max_input_tokens, event_input_tokens)
        max_output_tokens = max(max_output_tokens, event_output_tokens)
        max_input_message_chars = max(max_input_message_chars, input_message_chars)

    return {
        "file": file_name,
        "agent": _detect_agent(file_name, events),
        "llmRequests": len(llm_events),
        "inputTokens": input_tokens,
        "outputTokens": output_tokens,
        "totalTokens": input_tokens + output_tokens,
        "maxInputTokens": max_input_tokens,
        "maxOutputTokens": max_output_tokens,
        "totalInputMessageChars": total_input_message_chars,
        "maxInputMessageChars": max_input_message_chars,
    }


def _aggregate_by_agent(run_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for summary in run_summaries:
        groups[str(summary["agent"])].append(summary)

    aggregated: list[dict[str, Any]] = []
    for agent, items in sorted(groups.items()):
        llm_requests = sum(int(item["llmRequests"]) for item in items)
        input_tokens = sum(int(item["inputTokens"]) for item in items)
        output_tokens = sum(int(item["outputTokens"]) for item in items)
        aggregated.append(
            {
                "agent": agent,
                "runs": len(items),
                "llmRequests": llm_requests,
                "inputTokens": input_tokens,
                "outputTokens": output_tokens,
                "totalTokens": input_tokens + output_tokens,
            }
        )
    return aggregated


def _collect_request_stats(file_name: str, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    agent = _detect_agent(file_name, events)
    request_stats: list[dict[str, Any]] = []
    request_index = 0

    for event in events:
        attrs = event.get("attrs")
        if event.get("type") != "llm_request" or not isinstance(attrs, dict):
            continue

        request_index += 1
        ts_raw = event.get("ts") or event.get("timestamp") or ""
        timestamp = str(ts_raw) if ts_raw else ""
        request_stats.append(
            {
                "agent": agent,
                "requestIndex": request_index,
                "inputTokens": int(attrs.get("inputTokens") or 0),
                "outputTokens": int(attrs.get("outputTokens") or 0),
                "timestamp": timestamp,
            }
        )

    return request_stats


def _top_requests_by_input_tokens(
    request_stats: list[dict[str, Any]],
    limit: int = 10,
) -> list[dict[str, Any]]:
    return sorted(
        request_stats,
        key=lambda item: int(item.get("inputTokens") or 0),
        reverse=True,
    )[:limit]


def _derive_session_id(session_log_dir: Path) -> str:
    dir_name = session_log_dir.name
    return dir_name[-8:] if len(dir_name) >= 8 else dir_name


def build_session_report(session_log_dir: Path) -> dict[str, Any]:
    main_log = session_log_dir / "main.jsonl"
    if not main_log.exists():
        raise SystemExit(f"Session log directory is missing main.jsonl: {session_log_dir}")

    file_names = ["main.jsonl"] + sorted(
        path.name for path in session_log_dir.glob("runSubagent-*.jsonl")
    )

    run_summaries: list[dict[str, Any]] = []
    request_summaries: list[dict[str, Any]] = []

    for file_name in file_names:
        events = _parse_jsonl(session_log_dir / file_name)
        run_summaries.append(_summarize_run(file_name, events))
        request_summaries.extend(_collect_request_stats(file_name, events))

    total_llm_requests = sum(int(r["llmRequests"]) for r in run_summaries)
    total_input_tokens = sum(int(r["inputTokens"]) for r in run_summaries)
    total_output_tokens = sum(int(r["outputTokens"]) for r in run_summaries)

    return {
        "sessionId": _derive_session_id(session_log_dir),
        "sessionLogDir": str(session_log_dir),
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "date": datetime.now(timezone.utc).date().isoformat(),
        "totals": {
            "runs": len(run_summaries),
            "llmRequests": total_llm_requests,
            "inputTokens": total_input_tokens,
            "outputTokens": total_output_tokens,
            "totalTokens": total_input_tokens + total_output_tokens,
        },
        "agentBreakdown": _aggregate_by_agent(run_summaries),
        "hotspots": _top_requests_by_input_tokens(request_summaries),
    }


def _render_markdown(report: dict[str, Any]) -> str:
    totals = report["totals"]
    lines = [
        "# Copilot Session Report",
        "",
        f"**Session:** `{report['sessionId']}`  ",
        f"**Date:** {report['date']}  **Runs:** {totals['runs']}  **LLM Requests:** {totals['llmRequests']}",
        "",
        "## Session Totals",
        "",
        "| Metric | Value |",
        "|--------|------:|",
        f"| LLM Requests | {totals['llmRequests']} |",
        f"| Input Tokens | {totals['inputTokens']} |",
        f"| Output Tokens | {totals['outputTokens']} |",
        f"| Total Tokens | {totals['totalTokens']} |",
        "",
        "## Agent Breakdown",
        "",
        "| Agent | Runs | LLM Requests | Input Tokens | Output Tokens | Total Tokens |",
        "|-------|-----:|-------------:|-------------:|--------------:|-------------:|",
    ]

    for agent in report["agentBreakdown"]:
        lines.append(
            "| {agent} | {runs} | {llmRequests} | {inputTokens} | {outputTokens} | {totalTokens} |".format(
                **agent
            )
        )

    lines.extend(
        [
            "",
            "## Hotspots — Top Input-Token Requests",
            "",
            "> These requests loaded the most tokens into the model.",
            "> Large input values indicate prompts or context that could be shortened to reduce cost.",
            "",
            "| Agent | Request # | Input Tokens | Output Tokens | Timestamp |",
            "|-------|----------:|-------------:|--------------:|-----------|",
        ]
    )

    for req in report["hotspots"]:
        lines.append(
            "| {agent} | {requestIndex} | {inputTokens} | {outputTokens} | {timestamp} |".format(
                **req
            )
        )

    lines.extend(
        [
            "",
            "---",
            "",
            f"*Generated {report['generatedAt']} by `tools/copilot_session_stats.py`*",
        ]
    )

    return "\n".join(lines) + "\n"


def generate_session_report(session_log_dir: Path, output_dir: Path) -> Path:
    report = build_session_report(session_log_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / f"copilot_session_{report['sessionId']}.md"
    out_path.write_text(_render_markdown(report), encoding="utf-8")
    return out_path


def _parse_args() -> argparse.Namespace:
    env_log_dir = os.environ.get("VSCODE_TARGET_SESSION_LOG")
    parser = argparse.ArgumentParser(
        description="Generate a per-session Copilot token and agent report."
    )
    parser.add_argument(
        "--session-log-dir",
        type=Path,
        default=Path(env_log_dir) if env_log_dir else None,
        help=(
            "Path to the VS Code Copilot debug-log session directory. "
            "Defaults to the VSCODE_TARGET_SESSION_LOG environment variable."
        ),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
        help="Directory to write the session report into. Default: generated/debug/",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    if args.session_log_dir is None:
        raise SystemExit(
            "No session log directory provided. "
            "Pass --session-log-dir or set VSCODE_TARGET_SESSION_LOG."
        )
    out_path = generate_session_report(
        session_log_dir=args.session_log_dir,
        output_dir=args.output_dir,
    )
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
