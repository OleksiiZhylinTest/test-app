#!/usr/bin/env python3
"""Summarize Copilot session telemetry into generated/debug artifacts.

By default the script reads the current VS Code session debug-log directory from
the `VSCODE_TARGET_SESSION_LOG` environment variable when available. You can also
pass `--session-log-dir` explicitly.

Outputs:
- generated/debug/copilot_telemetry_stats.json
- generated/debug/copilot_telemetry_stats.md
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_JSON_PATH = ROOT / "generated" / "debug" / "copilot_telemetry_stats.json"
DEFAULT_MD_PATH = ROOT / "generated" / "debug" / "copilot_telemetry_stats.md"
DEFAULT_OTEL_PATH = ROOT / "generated" / "debug" / "copilot_chat_otel.jsonl"


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
    total_input_message_chars = 0
    max_input_tokens = 0
    max_output_tokens = 0
    max_input_message_chars = 0
    total_llm_duration_ms = 0
    models: set[str] = set()

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
        total_llm_duration_ms += int(event.get("dur") or 0)
        model = attrs.get("model") or event.get("name")
        if model:
            models.add(str(model))

    llm_request_count = len(llm_events)
    return {
        "file": file_name,
        "agent": _detect_agent(file_name, events),
        "llmRequests": llm_request_count,
        "userMessages": sum(1 for event in events if event.get("type") == "user_message"),
        "subagentCount": sum(1 for event in events if event.get("type") == "subagent"),
        "toolCalls": sum(1 for event in events if event.get("type") == "tool_call"),
        "inputTokens": input_tokens,
        "outputTokens": output_tokens,
        "totalTokens": input_tokens + output_tokens,
        "maxInputTokens": max_input_tokens,
        "avgInputTokens": round(input_tokens / llm_request_count) if llm_request_count else 0,
        "maxOutputTokens": max_output_tokens,
        "avgOutputTokens": round(output_tokens / llm_request_count) if llm_request_count else 0,
        "totalLlmDurationMs": total_llm_duration_ms,
        "totalInputMessageChars": total_input_message_chars,
        "maxInputMessageChars": max_input_message_chars,
        "models": sorted(models),
    }


def _collect_request_stats(file_name: str, events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    agent = _detect_agent(file_name, events)
    request_stats: list[dict[str, Any]] = []
    request_index = 0

    for event in events:
        attrs = event.get("attrs")
        if event.get("type") != "llm_request" or not isinstance(attrs, dict):
            continue

        request_index += 1
        input_messages = str(attrs.get("inputMessages") or "")
        request_stats.append(
            {
                "file": file_name,
                "agent": agent,
                "requestIndex": request_index,
                "inputTokens": int(attrs.get("inputTokens") or 0),
                "outputTokens": int(attrs.get("outputTokens") or 0),
                "totalTokens": int(attrs.get("inputTokens") or 0) + int(attrs.get("outputTokens") or 0),
                "inputMessageChars": len(input_messages),
                "durationMs": int(event.get("dur") or 0),
                "model": str(attrs.get("model") or event.get("name") or ""),
            }
        )

    return request_stats


def _top_items(
    items: list[dict[str, Any]],
    *keys: str,
    limit: int = 10,
) -> list[dict[str, Any]]:
    return sorted(
        items,
        key=lambda item: tuple(int(item.get(key) or 0) for key in keys),
        reverse=True,
    )[:limit]


def _aggregate_by_agent(run_summaries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for summary in run_summaries:
        groups[str(summary["agent"])].append(summary)

    aggregated: list[dict[str, Any]] = []
    for agent, items in sorted(groups.items()):
        llm_requests = sum(int(item["llmRequests"]) for item in items)
        input_tokens = sum(int(item["inputTokens"]) for item in items)
        output_tokens = sum(int(item["outputTokens"]) for item in items)
        total_input_message_chars = sum(int(item["totalInputMessageChars"]) for item in items)
        aggregated.append(
            {
                "agent": agent,
                "runs": len(items),
                "llmRequests": llm_requests,
                "inputTokens": input_tokens,
                "outputTokens": output_tokens,
                "totalTokens": input_tokens + output_tokens,
                "peakInputTokens": max(int(item["maxInputTokens"]) for item in items),
                "avgInputTokensPerRequest": round(input_tokens / llm_requests) if llm_requests else 0,
                "totalInputMessageChars": total_input_message_chars,
                "peakInputMessageChars": max(int(item["maxInputMessageChars"]) for item in items),
            }
        )
    return aggregated


def _summarize_otel_file(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"path": str(path), "exists": False, "lineCount": 0, "parsedJsonLines": 0}
    lines = path.read_text(encoding="utf-8").splitlines()
    parsed = 0
    for line in lines:
        if not line.strip():
            continue
        try:
            json.loads(line)
        except json.JSONDecodeError:
            continue
        parsed += 1
    return {
        "path": str(path),
        "exists": True,
        "lineCount": len(lines),
        "parsedJsonLines": parsed,
    }


def build_stats(session_log_dir: Path | None, otel_file: Path) -> dict[str, Any]:
    run_summaries: list[dict[str, Any]] = []
    request_summaries: list[dict[str, Any]] = []
    source: dict[str, Any] = {"sessionLogDir": None}

    if session_log_dir is not None:
        main_log = session_log_dir / "main.jsonl"
        if not main_log.exists():
            raise SystemExit(f"Session log directory is missing main.jsonl: {session_log_dir}")
        source["sessionLogDir"] = str(session_log_dir)
        file_names = ["main.jsonl"] + sorted(
            path.name for path in session_log_dir.glob("runSubagent-*.jsonl")
        )
        for file_name in file_names:
            events = _parse_jsonl(session_log_dir / file_name)
            run_summaries.append(_summarize_run(file_name, events))
            request_summaries.extend(_collect_request_stats(file_name, events))

    totals = {
        "runs": len(run_summaries),
        "llmRequests": sum(int(item["llmRequests"]) for item in run_summaries),
        "inputTokens": sum(int(item["inputTokens"]) for item in run_summaries),
        "outputTokens": sum(int(item["outputTokens"]) for item in run_summaries),
    }
    totals["totalTokens"] = totals["inputTokens"] + totals["outputTokens"]

    return {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "source": source,
        "otelFile": _summarize_otel_file(otel_file),
        "totals": totals,
        "agentTypes": _aggregate_by_agent(run_summaries),
        "topRunsByInputTokens": _top_items(
            run_summaries,
            "inputTokens",
            "maxInputTokens",
            limit=10,
        ),
        "topRequestsByInputTokens": _top_items(
            request_summaries,
            "inputTokens",
            "inputMessageChars",
            "durationMs",
            limit=10,
        ),
        "agentRuns": run_summaries,
    }


def _render_markdown(stats: dict[str, Any]) -> str:
    lines = [
        "# Copilot Telemetry Stats",
        "",
        f"Generated: {stats['generatedAt']}",
        "",
        "## Totals",
        "",
        f"- Runs: {stats['totals']['runs']}",
        f"- LLM requests: {stats['totals']['llmRequests']}",
        f"- Input tokens: {stats['totals']['inputTokens']}",
        f"- Output tokens: {stats['totals']['outputTokens']}",
        f"- Total tokens: {stats['totals']['totalTokens']}",
        "",
        "## By Agent Type",
        "",
        "| Agent | Runs | LLM Requests | Input Tokens | Output Tokens | Total Tokens | Peak Input Tokens | Avg Input Tokens / Request |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for agent in stats["agentTypes"]:
        lines.append(
            "| {agent} | {runs} | {llmRequests} | {inputTokens} | {outputTokens} | {totalTokens} | {peakInputTokens} | {avgInputTokensPerRequest} |".format(
                **agent
            )
        )

    lines.extend(
        [
            "",
            "## Top Runs By Input Tokens",
            "",
            "| Agent | File | Input Tokens | Peak Request Input Tokens | LLM Requests | Tool Calls |",
            "|---|---|---:|---:|---:|---:|",
        ]
    )
    for run in stats["topRunsByInputTokens"]:
        lines.append(
            "| {agent} | {file} | {inputTokens} | {maxInputTokens} | {llmRequests} | {toolCalls} |".format(
                **run
            )
        )

    lines.extend(
        [
            "",
            "## Top Requests By Input Tokens",
            "",
            "| Agent | File | Request # | Input Tokens | Input Chars | Duration ms | Model |",
            "|---|---|---:|---:|---:|---:|---|",
        ]
    )
    for request in stats["topRequestsByInputTokens"]:
        lines.append(
            "| {agent} | {file} | {requestIndex} | {inputTokens} | {inputMessageChars} | {durationMs} | {model} |".format(
                **request
            )
        )

    lines.extend(
        [
            "",
            "## OTel File Export",
            "",
            f"- Path: {stats['otelFile']['path']}",
            f"- Exists: {stats['otelFile']['exists']}",
            f"- Lines: {stats['otelFile']['lineCount']}",
            f"- Parsed JSON lines: {stats['otelFile']['parsedJsonLines']}",
        ]
    )
    return "\n".join(lines) + "\n"


def generate_stats(
    session_log_dir: Path | None,
    out_json: Path = DEFAULT_JSON_PATH,
    out_md: Path = DEFAULT_MD_PATH,
    otel_file: Path = DEFAULT_OTEL_PATH,
) -> dict[str, Any]:
    if session_log_dir is None and not otel_file.exists():
        raise SystemExit(
            "No telemetry source found. Pass --session-log-dir or generate the OTel file export first."
        )

    stats = build_stats(session_log_dir=session_log_dir, otel_file=otel_file)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(stats, indent=2), encoding="utf-8")
    out_md.write_text(_render_markdown(stats), encoding="utf-8")
    return stats


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Summarize Copilot telemetry into generated/debug.")
    parser.add_argument(
        "--session-log-dir",
        type=Path,
        default=Path(os.environ["VSCODE_TARGET_SESSION_LOG"]) if os.environ.get("VSCODE_TARGET_SESSION_LOG") else None,
        help="Path to the VS Code Copilot debug-log session directory.",
    )
    parser.add_argument(
        "--otel-file",
        type=Path,
        default=DEFAULT_OTEL_PATH,
        help="Path to the repo-local Copilot OTel JSONL export file.",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=DEFAULT_JSON_PATH,
        help="Path to the JSON stats artifact.",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=DEFAULT_MD_PATH,
        help="Path to the Markdown stats artifact.",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()
    stats = generate_stats(
        session_log_dir=args.session_log_dir,
        out_json=args.out_json,
        out_md=args.out_md,
        otel_file=args.otel_file,
    )
    print(f"Wrote {args.out_json}")
    print(f"Wrote {args.out_md}")
    print(json.dumps(stats["totals"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())