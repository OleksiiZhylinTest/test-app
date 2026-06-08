#!/usr/bin/env python3

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys
from typing import Any


PATH_KEYS = ("file", "path", "uri", "target", "include")
COMMAND_KEYS = ("command",)
HEAVY_DOC_MARKERS = (
    "docs/development/architecture.md",
    "docs/development/ai/assistant_customization_governance.md",
    "docs/product/requirements/",
    "docs/product/metrics/",
)
SUMMARY_MARKERS = (
    ".github/summaries/",
    "agents.md",
)
# Path configurable via NEXUS_DEBUG_DIR env var
_DEBUG_DIR = os.environ.get("NEXUS_DEBUG_DIR", "generated/debug")
TELEMETRY_PATH = Path(_DEBUG_DIR) / "copilot_context_telemetry.jsonl"


def _normalize(value: str) -> str:
    return value.replace("\\", "/").lower()


def _is_claude_owned_path(value: str) -> bool:
    normalized = _normalize(value)
    return "/.claude/" in normalized or normalized.endswith("/claude.md")


def _is_heavy_doc(value: str) -> bool:
    normalized = _normalize(value)
    return any(marker in normalized for marker in HEAVY_DOC_MARKERS)


def _is_summary_doc(value: str) -> bool:
    normalized = _normalize(value)
    return any(marker in normalized for marker in SUMMARY_MARKERS)


def _collect_candidates(node: Any, parent_key: str = "") -> list[str]:
    candidates: list[str] = []

    if isinstance(node, dict):
        for key, value in node.items():
            candidates.extend(_collect_candidates(value, key))
        return candidates

    if isinstance(node, list):
        for item in node:
            candidates.extend(_collect_candidates(item, parent_key))
        return candidates

    if not isinstance(node, str):
        return candidates

    key = parent_key.lower()
    if any(token in key for token in PATH_KEYS):
        candidates.append(node)
        return candidates

    if any(token in key for token in COMMAND_KEYS) and (".claude/" in node or ".claude\\" in node or "CLAUDE.md" in node):
        candidates.append(node)

    return candidates


def _ask_response(reason: str) -> dict[str, Any]:
    return {
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "ask",
            "permissionDecisionReason": reason,
        },
        "systemMessage": reason,
    }


def _continue_response(message: str | None = None) -> dict[str, Any]:
    response: dict[str, Any] = {"continue": True}
    if message:
        response["systemMessage"] = message
    return response


def _write_telemetry(payload: dict[str, Any]) -> None:
    try:
        TELEMETRY_PATH.parent.mkdir(parents=True, exist_ok=True)
        with TELEMETRY_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(payload, ensure_ascii=True) + "\n")
    except OSError:
        return


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        print(json.dumps(_continue_response()))
        return 0

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        print(json.dumps(_continue_response()))
        return 0

    candidates = _collect_candidates(payload)
    heavy_docs = sorted({candidate for candidate in candidates if _is_heavy_doc(candidate)})
    summary_docs = sorted({candidate for candidate in candidates if _is_summary_doc(candidate)})

    telemetry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "candidate_count": len(candidates),
        "heavy_doc_count": len(heavy_docs),
        "summary_doc_count": len(summary_docs),
        "heavy_docs": heavy_docs,
        "summary_docs": summary_docs,
        "claude_boundary_target": False,
        "decision": "allow",
    }

    for candidate in candidates:
        if _is_claude_owned_path(candidate):
            reason = (
                "GitHub Copilot is targeting a Claude-owned customization surface. "
                f"Confirm cross-tool access before proceeding: {candidate}"
            )
            telemetry["claude_boundary_target"] = True
            telemetry["decision"] = "ask"
            _write_telemetry(telemetry)
            print(json.dumps(_ask_response(reason)))
            return 0

    if heavy_docs and not summary_docs:
        message = (
            "High-context warning: this tool input references large repo docs without any summary layer. "
            "Consider starting from `.github/summaries/**` or a focused local file first."
        )
        telemetry["decision"] = "warn"
        _write_telemetry(telemetry)
        print(json.dumps(_continue_response(message)))
        return 0

    _write_telemetry(telemetry)
    print(json.dumps(_continue_response()))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
