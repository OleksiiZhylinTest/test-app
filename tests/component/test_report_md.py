"""Tests for app.report_md: Markdown output correctness."""

from __future__ import annotations

import pytest

from app.reporters.report_md import _md_table, generate_md

pytestmark = pytest.mark.component


@pytest.mark.smoke
def test_file_created(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    assert out.exists()


def test_title_present(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "# AI Adoption Metrics Report" in content


def test_date_present(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "2026-03-25" in content


def test_sprint_name_present(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "Sprint Alpha" in content


@pytest.mark.sanity
def test_velocity_value_present(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "20.0" in content


def test_no_velocity_data_message(tmp_path, empty_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(empty_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "No velocity data" in content


def test_bar_chart_present_when_velocity_nonzero(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "█" in content


# ---------------------------------------------------------------------------
# _md_table
# ---------------------------------------------------------------------------


def test_md_table_header_row():
    table = _md_table(["A", "B"], [])
    lines = table.splitlines()
    assert lines[0] == "| A | B |"


def test_md_table_separator_row():
    table = _md_table(["A", "B"], [])
    lines = table.splitlines()
    assert lines[1] == "| --- | --- |"


def test_md_table_data_row():
    table = _md_table(["X", "Y"], [["foo", "bar"]])
    lines = table.splitlines()
    assert lines[2] == "| foo | bar |"


# ---------------------------------------------------------------------------
# AI Assistance Trend section
# ---------------------------------------------------------------------------


def test_md_report_ai_assistance_section_present(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "## AI Assistance Trend" in content


def test_md_report_ai_assistance_shows_pct(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "50.0%" in content


def test_md_report_ai_assistance_table_headers(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "AI %" in content


def test_md_report_ai_assistance_shows_label(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "AI_assistance" in content


def test_md_report_ai_assistance_empty_data(tmp_path, empty_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(empty_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "## AI Assistance Trend" in content
    assert "No AI assistance data" in content


def test_md_report_ai_assistance_hidden_when_toggled_off(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out, section_visibility={"ai_assistance_trend": False})
    content = out.read_text(encoding="utf-8")
    assert "## AI Assistance Trend" not in content


# ---------------------------------------------------------------------------
# AI Usage Details section
# ---------------------------------------------------------------------------


def test_md_report_ai_usage_section_present(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "## AI Usage Details" in content


def test_md_report_ai_usage_shows_count(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "2" in content
    assert "AI-assisted" in content


def test_md_report_ai_usage_tool_breakdown(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "AI_Tool_Copilot" in content


def test_md_report_ai_usage_action_breakdown(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "AI_Case_CodeGen" in content


def test_md_report_ai_usage_hidden_when_toggled_off(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out, section_visibility={"ai_usage_details": False})
    content = out.read_text(encoding="utf-8")
    assert "## AI Usage Details" not in content


# ---------------------------------------------------------------------------
# Sprint Issues section
# ---------------------------------------------------------------------------


def test_md_report_sprint_issues_section_present(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "## Sprint Issues" in content


def test_md_report_sprint_issues_shows_issue_keys(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "PROJ-1" in content
    assert "PROJ-2" in content


def test_md_report_sprint_issues_shows_ai_flag(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "✓" in content


def test_md_report_sprint_issues_absent_when_no_data(tmp_path, empty_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(empty_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "## Sprint Issues" not in content


def test_md_report_sprint_issues_hidden_when_toggled_off(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out, section_visibility={"sprint_issues": False})
    content = out.read_text(encoding="utf-8")
    assert "## Sprint Issues" not in content


# ---------------------------------------------------------------------------
# Diagnostics section
# ---------------------------------------------------------------------------


def test_md_report_diagnostics_section_present(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "## Diagnostics" in content


def test_md_report_diagnostics_cycle_time_stats(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "Cycle Time" in content
    assert "3.5" in content  # mean_days


def test_md_report_diagnostics_no_cycle_time_message(tmp_path, empty_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(empty_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "No cycle time data" in content


def test_md_report_diagnostics_jira_config(tmp_path, minimal_metrics_dict):
    minimal_metrics_dict["schema_name"] = "Default_Jira_Cloud"
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "Default_Jira_Cloud" in content


def test_md_report_diagnostics_hidden_when_toggled_off(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out, section_visibility={"diagnostics": False})
    content = out.read_text(encoding="utf-8")
    assert "## Diagnostics" not in content


# ---------------------------------------------------------------------------
# Project type, estimation type, and velocity label in report header
# (RG-PT-005, RG-ET-005, RG-ET-007)
# ---------------------------------------------------------------------------


def test_project_type_shown_in_md_header(tmp_path, minimal_metrics_dict):
    minimal_metrics_dict["project_type"] = "SCRUM"
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "Project Type:" in content
    assert "SCRUM" in content


def test_estimation_type_shown_in_md_header(tmp_path, minimal_metrics_dict):
    minimal_metrics_dict["estimation_type"] = "StoryPoints"
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "Estimation:" in content
    assert "StoryPoints" in content


def test_velocity_header_label_story_points(tmp_path, minimal_metrics_dict):
    minimal_metrics_dict["estimation_type"] = "StoryPoints"
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "Velocity (points)" in content


def test_velocity_header_label_jira_tickets(tmp_path, minimal_metrics_dict):
    minimal_metrics_dict["estimation_type"] = "JiraTickets"
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out)
    content = out.read_text(encoding="utf-8")
    assert "Velocity (tickets)" in content


# ---------------------------------------------------------------------------
# section_visibility — MD sections hidden when toggled off
# ---------------------------------------------------------------------------

_ALL_HIDDEN = {
    "velocity_trend": False,
    "ai_assistance_trend": False,
    "ai_usage_details": False,
    "dau": False,
}


def test_velocity_section_hidden_when_section_visibility_false(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out, section_visibility=_ALL_HIDDEN)
    content = out.read_text(encoding="utf-8")
    assert "## Velocity trend" not in content


def test_dau_section_hidden_when_section_visibility_false(tmp_path, minimal_metrics_dict):
    out = tmp_path / "report.md"
    generate_md(minimal_metrics_dict, out, section_visibility=_ALL_HIDDEN)
    content = out.read_text(encoding="utf-8")
    assert "## Daily Active Usage" not in content
