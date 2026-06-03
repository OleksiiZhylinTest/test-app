"""Tests for Copilot customization hook behavior and summary assets."""

from __future__ import annotations

import importlib.util
import io
import json
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.unit

PROJECT_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = PROJECT_ROOT / ".github" / "hooks" / "pre_tool_copilot_boundary.py"

SUMMARY_SOURCES = {
    ".github/summaries/architecture-module-map.md": [
        "AGENTS.md",
        "docs/development/architecture.md",
    ],
    ".github/summaries/requirements-routing.md": [
        "docs/product/requirements/README.md",
    ],
    ".github/summaries/test-structure.md": [
        "AGENTS.md",
        "pyproject.toml",
        "tests/conftest.py",
        "tests/unit/conftest.py",
        "tests/component/conftest.py",
        "tests/e2e/conftest.py",
    ],
}


def _load_hook_module():
    spec = importlib.util.spec_from_file_location("pre_tool_copilot_boundary", HOOK_PATH)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _run_hook(module, payload: dict, telemetry_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[dict, dict]:
    stdin = io.StringIO(json.dumps(payload))
    stdout = io.StringIO()
    monkeypatch.setattr(sys, "stdin", stdin)
    monkeypatch.setattr(sys, "stdout", stdout)
    monkeypatch.setattr(module, "TELEMETRY_PATH", telemetry_path)

    assert module.main() == 0

    output = stdout.getvalue().strip()
    response = json.loads(output) if output else {}
    telemetry_lines = telemetry_path.read_text(encoding="utf-8").splitlines()
    telemetry = json.loads(telemetry_lines[-1]) if telemetry_lines else {}
    return response, telemetry


def _extract_sources(summary_text: str) -> list[str]:
    lines = summary_text.splitlines()
    start = lines.index("## Source of Truth") + 1
    sources: list[str] = []

    for line in lines[start:]:
        if line.startswith("## "):
            break
        if line.startswith("- `") and line.endswith("`"):
            sources.append(line[3:-1])

    return sources


def test_hook_detects_claude_owned_windows_path(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_hook_module()
    response, telemetry = _run_hook(
        module,
        {"tool_input": {"file_path": r"C:\repo\.claude\settings.json"}},
        tmp_path / "telemetry.jsonl",
        monkeypatch,
    )

    assert response["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert telemetry["decision"] == "ask"
    assert telemetry["claude_boundary_target"] is True


def test_hook_warns_on_heavy_docs_without_summary(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_hook_module()
    response, telemetry = _run_hook(
        module,
        {"tool_input": {"file_path": "docs/development/architecture.md"}},
        tmp_path / "telemetry.jsonl",
        monkeypatch,
    )

    assert response["continue"] is True
    assert "High-context warning" in response["systemMessage"]
    assert telemetry["decision"] == "warn"
    assert telemetry["heavy_doc_count"] == 1
    assert telemetry["summary_doc_count"] == 0


def test_hook_allows_heavy_docs_when_summary_is_present(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    module = _load_hook_module()
    response, telemetry = _run_hook(
        module,
        {
            "tool_input": {
                "file_path": "docs/development/architecture.md",
                "supporting_path": ".github/summaries/architecture-module-map.md",
            }
        },
        tmp_path / "telemetry.jsonl",
        monkeypatch,
    )

    assert response == {"continue": True}
    assert telemetry["decision"] == "allow"
    assert telemetry["heavy_doc_count"] == 1
    assert telemetry["summary_doc_count"] == 1


def test_hook_collects_nested_candidates() -> None:
    module = _load_hook_module()
    candidates = module._collect_candidates(
        {
            "tool_input": {
                "args": {
                    "items": [
                        {"uri": "c:/repo/.claude/hooks/test.sh"},
                        {"path": "docs/development/architecture.md"},
                    ]
                }
            }
        }
    )

    assert "c:/repo/.claude/hooks/test.sh" in candidates
    assert "docs/development/architecture.md" in candidates


@pytest.mark.parametrize("summary_path, expected_sources", SUMMARY_SOURCES.items())
def test_summaries_reference_existing_sources(summary_path: str, expected_sources: list[str]) -> None:
    summary_file = PROJECT_ROOT / summary_path
    summary_text = summary_file.read_text(encoding="utf-8")
    sources = _extract_sources(summary_text)

    assert sources == expected_sources
    for source in sources:
        assert (PROJECT_ROOT / source).exists()


@pytest.mark.parametrize("summary_path, expected_sources", SUMMARY_SOURCES.items())
def test_summaries_stay_smaller_than_sources(summary_path: str, expected_sources: list[str]) -> None:
    summary_file = PROJECT_ROOT / summary_path
    summary_line_count = len(summary_file.read_text(encoding="utf-8").splitlines())
    max_source_line_count = max(
        len((PROJECT_ROOT / source).read_text(encoding="utf-8").splitlines()) for source in expected_sources
    )

    assert summary_line_count < max_source_line_count