"""Cross-section chart label tests.

Verifies that Chart.js globally-promoted plugins (usagePieLabels, aiPointLabels)
and globally-registered plugins (avgVelocityLabels, avgDauLabels) do not corrupt
each other's label format when multiple report sections are rendered together.

Requirements covered: MC-FMT-101, MC-FMT-103, MC-FMT-105, MC-FMT-107, MC-FMT-108, MC-FMT-109
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.reporters.report_html import generate_html

pytestmark = pytest.mark.component


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _sv(
    velocity: bool = False,
    ai_trend: bool = False,
    ai_usage: bool = False,
    dau: bool = False,
    dau_trend: bool = False,
) -> dict:
    return {
        "velocity_trend": velocity,
        "ai_assistance_trend": ai_trend,
        "ai_usage_details": ai_usage,
        "dau": dau,
        "dau_trend": dau_trend,
    }


def _velocity_js(content: str) -> str:
    """Isolate the velocity chart JS initialisation block."""
    start = content.find("getElementById('velocityChart')")
    if start == -1:
        return ""
    end = content.find("})();", start) + len("})();")
    return content[start:end]


# ---------------------------------------------------------------------------
# Group 1 — Isolation: each section alone
# ---------------------------------------------------------------------------


def test_t01_velocity_alone_no_pct(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-01: velocity rendered alone — avg-line labels must be plain numbers, no %."""
    out = tmp_path / "report.html"
    generate_html(minimal_metrics_dict, out, section_visibility=_sv(velocity=True))
    content = out.read_text(encoding="utf-8")
    assert "getElementById('velocityChart')" in content
    assert "aiAssistanceChart" not in content
    assert "dauTrendChart" not in content
    velocity_js = _velocity_js(content)
    assert "+ '%'" not in velocity_js


def test_t02_ai_usage_alone_pie_pct(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-02: AI usage rendered alone — pie slice labels must include %."""
    out = tmp_path / "report.html"
    generate_html(minimal_metrics_dict, out, section_visibility=_sv(ai_usage=True))
    content = out.read_text(encoding="utf-8")
    assert "aiUsageToolsChart" in content
    assert "velocityChart" not in content
    assert "toFixed(1) + '%'" in content


def test_t03_ai_trend_alone_pct(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-03: AI assistance trend rendered alone — ai_pct must be displayed with %."""
    out = tmp_path / "report.html"
    generate_html(minimal_metrics_dict, out, section_visibility=_sv(ai_trend=True))
    content = out.read_text(encoding="utf-8")
    assert "aiAssistanceChart" in content
    assert "velocityChart" not in content
    assert "50.0%" in content


def test_t04_dau_trend_alone_pct(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-04: DAU trend rendered alone — avg-line labels must include %."""
    out = tmp_path / "report.html"
    generate_html(minimal_metrics_dict, out, section_visibility=_sv(dau_trend=True))
    content = out.read_text(encoding="utf-8")
    assert "dauTrendChart" in content
    assert "70.0%" in content
    assert "velocityChart" not in content


# ---------------------------------------------------------------------------
# Group 2 — Pairings: cross-plugin interference candidates
# ---------------------------------------------------------------------------


def test_t05_ai_usage_plus_velocity(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-05: usagePieLabels (from AI usage) must not corrupt velocity avg-line labels."""
    out = tmp_path / "report.html"
    generate_html(minimal_metrics_dict, out, section_visibility=_sv(velocity=True, ai_usage=True))
    content = out.read_text(encoding="utf-8")
    # Pie labels still work
    assert "toFixed(1) + '%'" in content
    # Velocity avg-line labels remain plain numbers
    assert "+ '%'" not in _velocity_js(content)


def test_t06_ai_trend_plus_velocity(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-06: aiPointLabels (from AI trend) must not corrupt velocity avg-line labels."""
    out = tmp_path / "report.html"
    generate_html(minimal_metrics_dict, out, section_visibility=_sv(velocity=True, ai_trend=True))
    content = out.read_text(encoding="utf-8")
    # AI trend labels still show %
    assert "50.0%" in content
    # Velocity avg-line labels remain plain numbers
    assert "+ '%'" not in _velocity_js(content)


def test_t07_dau_trend_plus_velocity(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-07 + T-10: avgDauLabels must not corrupt velocity AND avgVelocityLabels must not
    corrupt DAU trend when both sections are present simultaneously. This is the
    original bug scenario."""
    out = tmp_path / "report.html"
    generate_html(minimal_metrics_dict, out, section_visibility=_sv(velocity=True, dau_trend=True))
    content = out.read_text(encoding="utf-8")
    # DAU trend still shows % labels
    assert "dauTrendChart" in content
    assert "70.0%" in content
    # Velocity avg-line labels remain plain numbers (the bug: they were showing %)
    assert "+ '%'" not in _velocity_js(content)


def test_t08_ai_usage_plus_dau_trend(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-08: usagePieLabels must not corrupt DAU trend, and DAU trend must not corrupt pies."""
    out = tmp_path / "report.html"
    generate_html(minimal_metrics_dict, out, section_visibility=_sv(ai_usage=True, dau_trend=True))
    content = out.read_text(encoding="utf-8")
    # Pie labels still work
    assert "toFixed(1) + '%'" in content
    # DAU trend % labels still present
    assert "dauTrendChart" in content
    assert "70.0%" in content


def test_t09_ai_trend_plus_dau_trend(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-09: aiPointLabels must not corrupt DAU trend labels."""
    out = tmp_path / "report.html"
    generate_html(minimal_metrics_dict, out, section_visibility=_sv(ai_trend=True, dau_trend=True))
    content = out.read_text(encoding="utf-8")
    # AI trend labels correct
    assert "50.0%" in content
    # DAU trend labels correct
    assert "dauTrendChart" in content
    assert "70.0%" in content


# ---------------------------------------------------------------------------
# Group 3 — Triples: compounding interference
# ---------------------------------------------------------------------------


def test_t11_ai_usage_plus_velocity_plus_dau_trend(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-11: all three globally-promoted/registered plugins active simultaneously.
    The original combination that exposed the bug."""
    out = tmp_path / "report.html"
    generate_html(
        minimal_metrics_dict,
        out,
        section_visibility=_sv(velocity=True, ai_usage=True, dau_trend=True),
    )
    content = out.read_text(encoding="utf-8")
    # Velocity avg-line labels remain plain
    assert "+ '%'" not in _velocity_js(content)
    # Pie % labels present
    assert "toFixed(1) + '%'" in content
    # DAU trend % labels present
    assert "70.0%" in content


def test_t12_ai_trend_plus_velocity_plus_dau_trend(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-12: aiPointLabels + avgVelocityLabels + avgDauLabels all active."""
    out = tmp_path / "report.html"
    generate_html(
        minimal_metrics_dict,
        out,
        section_visibility=_sv(velocity=True, ai_trend=True, dau_trend=True),
    )
    content = out.read_text(encoding="utf-8")
    # Velocity avg-line labels remain plain
    assert "+ '%'" not in _velocity_js(content)
    # AI trend % labels present
    assert "50.0%" in content
    # DAU trend % labels present
    assert "70.0%" in content


def test_t13_ai_usage_plus_ai_trend_plus_dau_trend(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-13: three sections with % labels; no velocity chart present as a cross-contamination target."""
    out = tmp_path / "report.html"
    generate_html(
        minimal_metrics_dict,
        out,
        section_visibility=_sv(ai_usage=True, ai_trend=True, dau_trend=True),
    )
    content = out.read_text(encoding="utf-8")
    # No velocity chart
    assert "velocityChart" not in content
    # All three % label sources intact
    assert "toFixed(1) + '%'" in content  # pie labels
    assert "50.0%" in content  # AI trend ai_pct
    assert "70.0%" in content  # DAU trend team_avg_pct


# ---------------------------------------------------------------------------
# Group 4 — Full: all sections simultaneously
# ---------------------------------------------------------------------------


def test_t14_all_sections_correct_pct_labels(minimal_metrics_dict: dict, tmp_path: Path) -> None:
    """T-14: all sections ON — velocity plain, AI trend %, pie %, DAU trend %."""
    out = tmp_path / "report.html"
    generate_html(minimal_metrics_dict, out)  # default: all sections ON
    content = out.read_text(encoding="utf-8")
    # Velocity avg-line labels remain plain (the regression guard)
    assert "+ '%'" not in _velocity_js(content)
    # AI assistance % label present in table
    assert "50.0%" in content
    # Pie chart % callback present
    assert "toFixed(1) + '%'" in content
    # DAU trend % present
    assert "70.0%" in content
