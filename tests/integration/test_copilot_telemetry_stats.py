"""Tests for tools/copilot_telemetry_stats.py."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools"))
from copilot_telemetry_stats import generate_stats  # noqa: E402

pytestmark = pytest.mark.integration


def _write_jsonl(path: Path, events: list[dict[str, object]]) -> None:
    path.write_text(
        "\n".join(json.dumps(event) for event in events) + "\n",
        encoding="utf-8",
    )


def test_generate_stats_writes_json_and_markdown(tmp_path):
    session_dir = tmp_path / "session"
    session_dir.mkdir()
    _write_jsonl(
        session_dir / "main.jsonl",
        [
            {
                "type": "llm_request",
                "name": "chat:gpt-5.4",
                "dur": 1000,
                "attrs": {
                    "model": "gpt-5.4",
                    "inputTokens": 120,
                    "outputTokens": 12,
                    "inputMessages": "hello world",
                },
            },
            {"type": "tool_call", "attrs": {}},
            {"type": "user_message", "attrs": {"content": "hi"}},
        ],
    )
    _write_jsonl(
        session_dir / "runSubagent-Explore-call_123.jsonl",
        [
            {
                "type": "subagent",
                "attrs": {"agentName": "Explore"},
            },
            {
                "type": "llm_request",
                "name": "chat:claude-haiku-4.5",
                "dur": 250,
                "attrs": {
                    "model": "claude-haiku-4.5",
                    "inputTokens": 50,
                    "outputTokens": 5,
                    "inputMessages": "subagent prompt",
                },
            },
        ],
    )

    out_json = tmp_path / "generated" / "debug" / "stats.json"
    out_md = tmp_path / "generated" / "debug" / "stats.md"
    otel_file = tmp_path / "generated" / "debug" / "copilot_chat_otel.jsonl"
    otel_file.parent.mkdir(parents=True, exist_ok=True)
    otel_file.write_text('{"kind":"span"}\n', encoding="utf-8")

    stats = generate_stats(session_dir, out_json=out_json, out_md=out_md, otel_file=otel_file)

    assert out_json.exists()
    assert out_md.exists()
    assert stats["totals"]["runs"] == 2
    assert stats["totals"]["inputTokens"] == 170
    assert stats["totals"]["outputTokens"] == 17
    assert any(item["agent"] == "Main Agent" for item in stats["agentTypes"])
    assert any(item["agent"] == "Subagent: Explore" for item in stats["agentTypes"])
    md = out_md.read_text(encoding="utf-8")
    assert "# Copilot Telemetry Stats" in md
    assert "Subagent: Explore" in md


def test_generate_stats_subprocess_smoke(tmp_path):
    session_dir = tmp_path / "session"
    session_dir.mkdir()
    _write_jsonl(
        session_dir / "main.jsonl",
        [
            {
                "type": "llm_request",
                "name": "chat:gpt-5.4",
                "dur": 100,
                "attrs": {
                    "model": "gpt-5.4",
                    "inputTokens": 10,
                    "outputTokens": 2,
                    "inputMessages": "hello",
                },
            }
        ],
    )

    out_json = tmp_path / "stats.json"
    out_md = tmp_path / "stats.md"
    script = Path(__file__).resolve().parent.parent.parent / "tools" / "copilot_telemetry_stats.py"
    result = subprocess.run(
        [
            sys.executable,
            str(script),
            "--session-log-dir",
            str(session_dir),
            "--out-json",
            str(out_json),
            "--out-md",
            str(out_md),
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0
    assert out_json.exists()
    assert out_md.exists()
    assert '"inputTokens": 10' in result.stdout