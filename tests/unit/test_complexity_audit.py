"""Unit tests for app.core.complexity_audit and app.reporters.report_complexity_md."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.complexity_audit import (
    build_complexity_report,
    discover_modules,
    score_module_source,
)
from app.reporters.report_complexity_md import generate_complexity_md

pytestmark = pytest.mark.unit

# ---------------------------------------------------------------------------
# In-memory source fixtures
# ---------------------------------------------------------------------------

_SIMPLE_SOURCE = "def greet(name):\n    return f'Hello, {name}'\n"

_COMPLEX_SOURCE = "\n".join(
    [f"import module_{i}" for i in range(10)] + [f"\ndef func_{i}(x):\n    return x + {i}" for i in range(8)]
)

_SYNTAX_ERROR_SOURCE = "def broken(\n    pass\n"


def _make_high_source() -> str:
    """Generate source that reliably scores High (composite >= 7.0)."""
    lines: list[str] = []
    for i in range(200):
        lines.append(f"import unique_mod_{i}")
    for i in range(250):
        params = ", ".join(f"a{j}" for j in range(10))
        lines.append(f"def func_{i}({params}):")
        for j in range(10):
            indent = "    " * (j + 1)
            lines.append(f"{indent}if a{j}:")
        lines.append("    " * 11 + "return True")
        lines.append("    return False")
    return "\n".join(lines)


_HIGH_SOURCE = _make_high_source()


# ---------------------------------------------------------------------------
# discover_modules
# ---------------------------------------------------------------------------


def test_discover_modules_returns_only_py_files(tmp_path):
    (tmp_path / "a.py").write_text("x = 1")
    (tmp_path / "b.txt").write_text("not python")
    result = discover_modules(tmp_path)
    assert len(result) == 1
    assert result[0].name == "a.py"


def test_discover_modules_excludes_excluded_dirs(tmp_path):
    for d in ("venv", ".venv", "generated", "__pycache__", ".git"):
        p = tmp_path / d
        p.mkdir()
        (p / "should_be_excluded.py").write_text("x = 1")
    (tmp_path / "included.py").write_text("y = 2")
    result = discover_modules(tmp_path)
    assert [r.name for r in result] == ["included.py"]


def test_discover_modules_empty_dir_returns_empty(tmp_path):
    assert discover_modules(tmp_path) == []


# ---------------------------------------------------------------------------
# score_module_source
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_score_simple_module_is_low():
    result = score_module_source(Path("simple.py"), _SIMPLE_SOURCE)
    assert result["classification"] == "Low"
    assert result["error"] is None
    for key in (
        "loc",
        "function_count",
        "cc_score",
        "loc_score",
        "coupling_score",
        "cohesion_score",
        "composite_score",
    ):
        assert result[key] is not None, f"Expected {key} to be set, got None"


def test_score_complex_module_has_higher_coupling_and_cohesion():
    simple = score_module_source(Path("simple.py"), _SIMPLE_SOURCE)
    complex_ = score_module_source(Path("complex.py"), _COMPLEX_SOURCE)
    assert complex_["coupling_score"] > simple["coupling_score"]
    assert complex_["cohesion_score"] > simple["cohesion_score"]


def test_score_syntax_error_source_returns_error_classification():
    result = score_module_source(Path("broken.py"), _SYNTAX_ERROR_SOURCE)
    assert result["classification"] == "Error"
    assert result["error"] is not None
    for key in (
        "loc",
        "function_count",
        "cc_score",
        "loc_score",
        "coupling_score",
        "cohesion_score",
        "composite_score",
    ):
        assert result[key] is None, f"Expected {key} to be None for Error module"


# ---------------------------------------------------------------------------
# build_complexity_report
# ---------------------------------------------------------------------------


def test_build_report_module_count_matches_files_created(tmp_path):
    (tmp_path / "a.py").write_text(_SIMPLE_SOURCE)
    (tmp_path / "b.py").write_text(_SIMPLE_SOURCE)
    report = build_complexity_report(tmp_path)
    assert report["module_count"] == 2


def test_build_report_scores_sorted_high_before_low(tmp_path):
    (tmp_path / "low.py").write_text(_SIMPLE_SOURCE)
    (tmp_path / "high.py").write_text(_HIGH_SOURCE)
    report = build_complexity_report(tmp_path)
    _order = {"High": 0, "Medium": 1, "Low": 2, "Error": 3}
    order_values = [_order.get(s["classification"], 4) for s in report["scores"]]
    assert order_values == sorted(order_values), (
        f"Scores not sorted High→Medium→Low→Error: {[s['classification'] for s in report['scores']]}"
    )


def test_build_report_summary_counts_sum_to_module_count(tmp_path):
    for i in range(3):
        (tmp_path / f"mod_{i}.py").write_text(_SIMPLE_SOURCE)
    report = build_complexity_report(tmp_path)
    s = report["summary"]
    total = s["high_count"] + s["medium_count"] + s["low_count"] + s["error_count"]
    assert total == report["module_count"]


# ---------------------------------------------------------------------------
# Recommendation generation
# ---------------------------------------------------------------------------


def test_high_module_generates_at_least_one_recommendation(tmp_path):
    (tmp_path / "high_mod.py").write_text(_HIGH_SOURCE)
    report = build_complexity_report(tmp_path)
    high_scores = [s for s in report["scores"] if s["classification"] == "High"]
    assert high_scores, "Expected _HIGH_SOURCE to produce at least one High module"
    assert len(report["recommendations"]) >= 1


def test_low_module_generates_no_recommendations(tmp_path):
    (tmp_path / "low_mod.py").write_text(_SIMPLE_SOURCE)
    report = build_complexity_report(tmp_path)
    assert report["recommendations"] == []


def test_high_module_classification_and_recommendation_count(tmp_path):
    """SC-2: High module must have classification == 'High' and >= 1 recommendation."""
    (tmp_path / "high_mod.py").write_text(_HIGH_SOURCE)
    report = build_complexity_report(tmp_path)
    high_scores = [s for s in report["scores"] if s["classification"] == "High"]
    assert high_scores, "Expected at least one High module"
    module_name = high_scores[0]["module"]
    recs_for_module = [r for r in report["recommendations"] if r["module"] == module_name]
    assert len(recs_for_module) >= 1


# ---------------------------------------------------------------------------
# Markdown reporter
# ---------------------------------------------------------------------------


def _minimal_report() -> dict:
    return {
        "generated_at": "2026-01-01T00:00:00Z",
        "discovery_root": "/tmp/test",
        "module_count": 1,
        "scores": [
            {
                "module": "sample_mod.py",
                "loc": 10,
                "function_count": 1,
                "cc_score": 0.1,
                "loc_score": 0.03,
                "coupling_score": 0.0,
                "cohesion_score": 0.05,
                "composite_score": 0.05,
                "classification": "Low",
                "mi": None,
                "error": None,
            }
        ],
        "recommendations": [],
        "summary": {"high_count": 0, "medium_count": 0, "low_count": 1, "error_count": 0},
    }


def test_generate_complexity_md_creates_file_with_header(tmp_path):
    out = tmp_path / "out.md"
    generate_complexity_md(_minimal_report(), out)
    assert out.exists()
    assert "# Design Complexity Audit Report" in out.read_text(encoding="utf-8")


def test_generate_complexity_md_contains_improvement_plan_section(tmp_path):
    out = tmp_path / "out.md"
    generate_complexity_md(_minimal_report(), out)
    assert "## Improvement Plan" in out.read_text(encoding="utf-8")


def test_generate_complexity_md_no_recs_shows_empty_message(tmp_path):
    out = tmp_path / "out.md"
    generate_complexity_md(_minimal_report(), out)
    assert "No high-complexity modules found." in out.read_text(encoding="utf-8")
