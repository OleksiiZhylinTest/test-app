#!/usr/bin/env python3
"""Parse a Claude Code session transcript and produce a token-consumption report.

Called automatically by the Stop hook (stdin = hook JSON) or manually:
  python tools/claude_session_stats.py <transcript_path>
  python tools/claude_session_stats.py <transcript_path> --output-dir generated/debug

Outputs:
  generated/debug/claude_session_<session_id_short>.md   (overwritten each turn)

Report structure:
  - Session totals
  - Per-turn sections, each with a per-step table (one row per API call)
  - Hotspots: top steps by cache-write (new context loaded = optimization target)
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ── helpers ──────────────────────────────────────────────────────────────────

def _load_transcript(path: Path) -> list[dict[str, Any]]:
    entries: list[dict[str, Any]] = []
    seen: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(entry, dict):
            continue
        uid = entry.get("uuid")
        if uid:
            if uid in seen:
                continue
            seen.add(uid)
        entries.append(entry)
    return entries


def _is_tool_result(content: Any) -> bool:
    """True when a user entry carries only tool results (not a human prompt)."""
    if not isinstance(content, list) or not content:
        return False
    return all(isinstance(b, dict) and b.get("type") == "tool_result" for b in content)


def _prompt_excerpt(content: Any, max_len: int = 70) -> str:
    if isinstance(content, str):
        text = content
    elif isinstance(content, list):
        parts = [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
        text = " ".join(parts)
    else:
        return ""
    return text.replace("\n", " ").replace("\r", "").strip()[:max_len]


def _op_label(tool: str, inp: dict[str, Any]) -> str:
    """Human-readable one-liner for a single tool call."""
    if tool == "Agent":
        st = inp.get("subagent_type", "")
        desc = inp.get("description", "")[:55]
        return f"**→ {st}**: {desc}" if st else f"**→ Agent**: {desc}"
    if tool == "Read":
        return f"Read({Path(inp.get('file_path', '')).name})"
    if tool in ("Write", "Edit"):
        return f"{tool}({Path(inp.get('file_path', '')).name})"
    if tool == "Bash":
        label = inp.get("description") or str(inp.get("command", ""))
        return f'Bash: "{label[:55]}"'
    if tool == "Glob":
        return f"Glob({inp.get('pattern', '')})"
    if tool == "Grep":
        return f'Grep("{inp.get("pattern", "")}")'
    if tool == "TaskCreate":
        subj = inp.get("subject", "")[:40]
        return f"TaskCreate({subj})" if subj else "TaskCreate"
    if tool == "TaskUpdate":
        return f"TaskUpdate(#{inp.get('taskId', '')})"
    if tool in ("TaskGet", "TaskList"):
        return tool
    return tool


# ── parsing ───────────────────────────────────────────────────────────────────

def _usage_fp(usage: dict[str, Any]) -> tuple[int, ...]:
    """Fingerprint for an API call: all four token fields.

    Consecutive assistant entries (thinking + text + tool_use) from the same
    API call share identical usage values. When the fingerprint changes, a new
    API call has started. cache_read_input_tokens grows each call, so collisions
    between distinct API calls are practically impossible.
    """
    return (
        usage.get("input_tokens", 0),
        usage.get("cache_creation_input_tokens", 0),
        usage.get("cache_read_input_tokens", 0),
        usage.get("output_tokens", 0),
    )


def _parse_turns(entries: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Group transcript entries into turns (one per human prompt), each containing
    a list of steps where one step = one API call.

    Claude Code stores each content block of an API response as a separate JSONL
    entry (thinking / text / tool_use), all carrying identical usage values.
    Grouping by usage fingerprint merges these back into a single step.
    """
    turns: list[dict[str, Any]] = []
    current_turn: dict[str, Any] | None = None
    current_step: dict[str, Any] | None = None
    current_fp: tuple[int, ...] | None = None

    def _flush_step() -> None:
        nonlocal current_step, current_fp
        if current_step is not None and current_turn is not None:
            current_turn["steps"].append(current_step)
        current_step = None
        current_fp = None

    for entry in entries:
        etype = entry.get("type")
        if etype not in ("user", "assistant"):
            continue
        if entry.get("isMeta"):
            continue
        if entry.get("isSidechain"):
            continue

        if etype == "user":
            content = entry.get("message", {}).get("content", "")
            if _is_tool_result(content):
                continue  # transparent tool-result connector between steps
            _flush_step()
            if current_turn is not None:
                turns.append(current_turn)
            current_turn = {
                "timestamp": entry.get("timestamp", ""),
                "prompt": _prompt_excerpt(content),
                "steps": [],
            }

        else:  # assistant
            if current_turn is None:
                continue
            msg = entry.get("message", {})
            usage = msg.get("usage", {})
            fp = _usage_fp(usage)

            if fp != current_fp:
                _flush_step()
                current_fp = fp
                current_step = {
                    "timestamp": entry.get("timestamp", ""),
                    "usage": {
                        k: usage.get(k, 0)
                        for k in ("input_tokens", "cache_creation_input_tokens",
                                  "cache_read_input_tokens", "output_tokens")
                    },
                    "model": msg.get("model"),
                    "stop_reason": msg.get("stop_reason"),
                    "operations": [],
                }

            if current_step is not None:
                for block in msg.get("content", []) if isinstance(msg.get("content"), list) else []:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        current_step["operations"].append({
                            "tool": block.get("name", ""),
                            "input": block.get("input", {}),
                        })
                if msg.get("stop_reason"):
                    current_step["stop_reason"] = msg["stop_reason"]
                if msg.get("model"):
                    current_step["model"] = msg["model"]

    _flush_step()
    if current_turn is not None:
        turns.append(current_turn)
    return turns


def _step_usage_total(step: dict[str, Any]) -> int:
    return sum(step["usage"].values())


def _turn_totals(turn: dict[str, Any]) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for step in turn["steps"]:
        for k, v in step["usage"].items():
            totals[k] += v
    return totals


# ── rendering ─────────────────────────────────────────────────────────────────

def _fmt(n: int) -> str:
    return f"{n:,}"


def _step_op_summary(step: dict[str, Any]) -> str:
    ops = step["operations"]
    if not ops:
        return "_(response)_"
    return ", ".join(_op_label(op["tool"], op["input"]) for op in ops)


def _render_markdown(
    session_id: str,
    turns: list[dict[str, Any]],
    meta: dict[str, str],
) -> str:
    # Session-level totals
    session_totals: dict[str, int] = defaultdict(int)
    for turn in turns:
        for k, v in _turn_totals(turn).items():
            session_totals[k] += v

    total_all = sum(session_totals.values())

    first_ts = turns[0]["timestamp"] if turns else ""
    last_ts = turns[-1]["timestamp"] if turns else ""
    duration_str = ""
    if first_ts and last_ts:
        try:
            t0 = datetime.fromisoformat(first_ts.replace("Z", "+00:00"))
            t1 = datetime.fromisoformat(last_ts.replace("Z", "+00:00"))
            mins = int((t1 - t0).total_seconds() / 60)
            duration_str = f"~{mins} min" if mins > 0 else "<1 min"
        except ValueError:
            pass

    model = next(
        (s["model"] for t in turns for s in t["steps"] if s.get("model")),
        "unknown",
    )
    date_str = first_ts[:10] if first_ts else datetime.now(timezone.utc).strftime("%Y-%m-%d")
    project = meta.get("project", "unknown")
    branch = meta.get("branch", "")

    L: list[str] = []

    # ── header ────────────────────────────────────────────────────────────────
    L += [
        "# Claude Session Token Report",
        "",
        f"**Session:** `{session_id}`  ",
        f"**Project:** {project}" + (f"  **Branch:** `{branch}`" if branch else "") + "  ",
        f"**Date:** {date_str}  **Duration:** {duration_str}  **Model:** {model}",
        "",
    ]

    # ── session totals ────────────────────────────────────────────────────────
    L += [
        "## Session Totals",
        "",
        "| Metric | Tokens | Notes |",
        "|--------|-------:|-------|",
        f"| Input (fresh) | {_fmt(session_totals['input_tokens'])} | uncached tokens sent to model |",
        f"| Cache read | {_fmt(session_totals['cache_read_input_tokens'])} | context served from cache (cheap) |",
        f"| Cache write | {_fmt(session_totals['cache_creation_input_tokens'])} | new context written to cache |",
        f"| Output | {_fmt(session_totals['output_tokens'])} | tokens generated by model |",
        f"| **Total effective** | **{_fmt(total_all)}** | |",
        "",
    ]

    # ── per-turn sections ─────────────────────────────────────────────────────
    L.append("## Turn Details")

    real_turns = [t for t in turns if t["steps"]]
    for turn_num, turn in enumerate(turns, 1):
        ts_full = turn["timestamp"]
        ts_short = ts_full[11:19] if len(ts_full) >= 19 else ts_full
        prompt = turn["prompt"] or "_(system / command)_"
        steps = turn["steps"]

        L += ["", f"---", f"", f"### Turn {turn_num} · {ts_short} UTC"]
        L.append(f'**Prompt:** "{prompt}"')

        if not steps:
            L.append("*(no billable steps)*")
            continue

        t = _turn_totals(turn)
        subtotal_parts = (
            f"in={_fmt(t['input_tokens'])} · "
            f"cache-r={_fmt(t['cache_read_input_tokens'])} · "
            f"cache-w={_fmt(t['cache_creation_input_tokens'])} · "
            f"out={_fmt(t['output_tokens'])}"
        )
        L.append(f"**Subtotal:** {subtotal_parts} ({len(steps)} steps)")
        L.append("")
        L += [
            "| # | Time (UTC) | Operation | In | Cache-W | Cache-R | Out |",
            "|---|------------|-----------|---:|--------:|--------:|----:|",
        ]

        for step_num, step in enumerate(steps, 1):
            sts = step["timestamp"][11:19] if len(step["timestamp"]) >= 19 else step["timestamp"]
            u = step["usage"]
            op = _step_op_summary(step)
            L.append(
                f"| {step_num} | {sts} | {op} "
                f"| {_fmt(u['input_tokens'])} | {_fmt(u['cache_creation_input_tokens'])} "
                f"| {_fmt(u['cache_read_input_tokens'])} | {_fmt(u['output_tokens'])} |"
            )

    # ── hotspots ──────────────────────────────────────────────────────────────
    # Collect all steps across turns, sorted by cache-write (optimization target)
    all_steps: list[tuple[int, int, dict[str, Any]]] = []
    for turn_num, turn in enumerate(turns, 1):
        for step_num, step in enumerate(turn["steps"], 1):
            all_steps.append((turn_num, step_num, step))

    top_cw = sorted(all_steps, key=lambda x: x[2]["usage"]["cache_creation_input_tokens"], reverse=True)[:5]

    if top_cw and top_cw[0][2]["usage"]["cache_creation_input_tokens"] > 0:
        L += [
            "",
            "---",
            "",
            "## Hotspots — Top Cache-Write Steps",
            "",
            "> These steps loaded the most new context into the cache.",
            "> Large cache-write values indicate prompts or files that could be shortened to reduce cost.",
            "",
            "| Turn | Step | Cache-W | Operation |",
            "|------|-----:|--------:|-----------|",
        ]
        for tn, sn, step in top_cw:
            cw = step["usage"]["cache_creation_input_tokens"]
            if cw == 0:
                break
            op = _step_op_summary(step)
            L.append(f"| T{tn} | S{sn} | {_fmt(cw)} | {op} |")

    # ── footer ────────────────────────────────────────────────────────────────
    L += [
        "",
        "---",
        "",
        f"*Generated {datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')} "
        f"by `tools/claude_session_stats.py`*",
    ]
    return "\n".join(L)


# ── entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Claude Code session token report")
    parser.add_argument("transcript", nargs="?", help="Path to session JSONL transcript")
    parser.add_argument("--output-dir", default=None)
    args = parser.parse_args()

    hook_json: dict[str, Any] = {}

    if args.transcript:
        transcript_path = Path(args.transcript)
        cwd = Path.cwd()
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print(
                "No transcript path — pass as argument or pipe Stop hook JSON via stdin",
                file=sys.stderr,
            )
            sys.exit(1)
        try:
            hook_json = json.loads(raw)
        except json.JSONDecodeError as exc:
            print(f"Invalid hook JSON: {exc}", file=sys.stderr)
            sys.exit(1)
        if "transcript_path" not in hook_json:
            print("Hook JSON missing 'transcript_path' field", file=sys.stderr)
            sys.exit(1)
        transcript_path = Path(hook_json["transcript_path"])
        cwd = Path(hook_json.get("cwd", Path.cwd()))

    if not transcript_path.exists():
        print(f"Transcript not found: {transcript_path}", file=sys.stderr)
        sys.exit(1)

    session_id = hook_json.get("session_id") or transcript_path.stem
    entries = _load_transcript(transcript_path)

    meta: dict[str, str] = {"project": hook_json.get("cwd", ""), "branch": ""}
    for e in entries:
        if e.get("gitBranch") and not meta["branch"]:
            meta["branch"] = e["gitBranch"]
        if e.get("cwd") and not meta["project"]:
            meta["project"] = e["cwd"]
    meta["project"] = Path(meta["project"]).name if meta["project"] else "unknown"

    turns = _parse_turns(entries)
    if not turns:
        print("No turns found in transcript", file=sys.stderr)
        sys.exit(0)

    md = _render_markdown(session_id, turns, meta)

    output_dir = Path(args.output_dir) if args.output_dir else cwd / "generated" / "debug"
    output_dir.mkdir(parents=True, exist_ok=True)

    out_file = output_dir / f"claude_session_{session_id[:8]}.md"
    out_file.write_text(md, encoding="utf-8")
    print(f"Token report: {out_file}", file=sys.stderr)


if __name__ == "__main__":
    main()
