"""Tests for app.metrics: pure computation, no Jira connection required."""

from __future__ import annotations

import pytest

from app.core import metrics
from tests.conftest import make_issue, make_issue_with_labels, make_sprint

pytestmark = pytest.mark.unit


# ---------------------------------------------------------------------------
# _is_done
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status,expected",
    [
        ("Done", True),
        ("done", True),
        ("Closed", True),
        ("Resolved", True),
        ("Complete", True),
        ("In Progress", False),
        ("To Do", False),
        ("", False),
        ("Released", False),  # custom status, no resolutiondate
    ],
)
def test_is_done(status, expected):
    issue = make_issue("X-1", status=status)
    assert metrics._is_done(issue) is expected


def test_is_done_missing_fields():
    assert metrics._is_done({}) is False
    assert metrics._is_done({"fields": {}}) is False
    assert metrics._is_done({"fields": {"status": {}}}) is False


def test_is_done_resolutiondate_fallback():
    """Issues with resolutiondate are done regardless of status name (covers KANBAN custom statuses)."""
    issue = make_issue("K-1", status="Released")
    issue["fields"]["resolutiondate"] = "2024-03-01T10:00:00.000+0000"
    assert metrics._is_done(issue) is True


def test_is_done_no_resolutiondate_custom_status():
    """Custom terminal status name without resolutiondate is not considered done."""
    issue = make_issue("K-2", status="Released")
    assert metrics._is_done(issue) is False


def test_compute_velocity_kanban_periods():
    """KANBAN week periods with resolved issues (custom status + resolutiondate) count correctly."""
    period = {
        "id": "week-2024-W14",
        "name": "2024-W14",
        "startDate": "2024-04-01",
        "endDate": "2024-04-07",
    }
    issue = make_issue("K-1", status="Released", points=5.0)
    issue["fields"]["resolutiondate"] = "2024-04-03T10:00:00.000+0000"
    result = metrics.compute_velocity([period], {"week-2024-W14": [issue]})
    assert result[0]["velocity"] == 5.0
    assert result[0]["issue_count"] == 1


# ---------------------------------------------------------------------------
# _get_story_points
# ---------------------------------------------------------------------------


def test_get_story_points_numeric_float():
    issue = make_issue("X-1", points=8.0)
    assert metrics._get_story_points(issue) == 8.0


def test_get_story_points_integer_stored_as_int():
    issue = make_issue("X-1", points=None)
    issue["fields"]["customfield_10016"] = 3
    assert metrics._get_story_points(issue) == 3.0


def test_get_story_points_none():
    issue = make_issue("X-1", points=None)
    assert metrics._get_story_points(issue) == 0.0


def test_get_story_points_non_numeric_string():
    issue = make_issue("X-1", points=None)
    issue["fields"]["customfield_10016"] = "many"
    assert metrics._get_story_points(issue) == 0.0


def test_get_story_points_missing_field():
    issue = {"key": "X-1", "fields": {}}
    assert metrics._get_story_points(issue) == 0.0


def test_get_story_points_custom_field(monkeypatch):
    monkeypatch.setattr("app.core.schema.DEFAULT_STORY_POINTS_FIELD_ID", "customfield_99999")
    issue = {"key": "X-1", "fields": {"customfield_99999": 13.0}}
    assert metrics._get_story_points(issue) == 13.0


def test_get_story_points_nested_value_dict():
    issue = {"key": "X-1", "fields": {"customfield_10016": {"value": 8}}}
    assert metrics._get_story_points(issue) == 8.0


# ---------------------------------------------------------------------------
# compute_velocity
# ---------------------------------------------------------------------------


def test_compute_velocity_all_done():
    sprint = make_sprint(1, "Sprint 1")
    issues = [make_issue("X-1", "Done", 5.0), make_issue("X-2", "Done", 3.0)]
    result = metrics.compute_velocity([sprint], {1: issues})
    assert len(result) == 1
    assert result[0]["velocity"] == 8.0
    assert result[0]["issue_count"] == 2


def test_compute_velocity_mixed_statuses():
    sprint = make_sprint(1)
    issues = [
        make_issue("X-1", "Done", 5.0),
        make_issue("X-2", "In Progress", 3.0),
        make_issue("X-3", "To Do", 2.0),
    ]
    result = metrics.compute_velocity([sprint], {1: issues})
    assert result[0]["velocity"] == 5.0
    assert result[0]["issue_count"] == 1


def test_compute_velocity_no_issues():
    sprint = make_sprint(1)
    result = metrics.compute_velocity([sprint], {1: []})
    assert result[0]["velocity"] == 0.0
    assert result[0]["issue_count"] == 0


def test_compute_velocity_missing_sprint_id():
    sprint = {"name": "Bad Sprint"}  # no "id"
    result = metrics.compute_velocity([sprint], {})
    assert result == []


def test_compute_velocity_sprint_absent_from_issues_dict():
    sprint = make_sprint(42)
    result = metrics.compute_velocity([sprint], {})
    assert result[0]["velocity"] == 0.0


def test_compute_velocity_rounding():
    sprint = make_sprint(1)
    issues = [make_issue("X-1", "Done", 1.05), make_issue("X-2", "Done", 1.05)]
    result = metrics.compute_velocity([sprint], {1: issues})
    assert result[0]["velocity"] == round(2.1, 1)


def test_compute_velocity_preserves_sprint_name():
    sprint = make_sprint(7, "My Sprint")
    result = metrics.compute_velocity([sprint], {7: []})
    assert result[0]["sprint_name"] == "My Sprint"


# ---------------------------------------------------------------------------
# build_metrics_dict
# ---------------------------------------------------------------------------


def test_build_metrics_dict_keys():
    sprint = make_sprint(1)
    issue = make_issue("X-1", "Done", 5.0)
    result = metrics.build_metrics_dict([sprint], {1: [issue]})
    expected_keys = {
        "velocity",
        "generated_at",
        "ai_assistance_trend",
        "ai_usage_details",
        "ai_assisted_label",
        "ai_exclude_labels",
        "dau",
        "schema_name",
        "filter_name",
        "filter_id",
        "filter_jql",
        "project_key",
        "report_name",
        "project_type",
        "estimation_type",
    }
    assert expected_keys.issubset(result.keys())


def test_build_metrics_dict_report_name_defaults_to_none():
    result = metrics.build_metrics_dict([], {})
    assert "report_name" in result
    assert result["report_name"] is None


def test_build_metrics_dict_generated_at_is_iso():
    from datetime import datetime

    result = metrics.build_metrics_dict([], {})
    ts = result["generated_at"]
    # Should parse without error
    parsed = datetime.fromisoformat(ts)
    assert parsed.tzinfo is not None


# ---------------------------------------------------------------------------
# _parse_iso
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "input_val,expected_not_none",
    [
        ("2026-03-01T10:00:00+00:00", True),
        ("2026-03-01T10:00:00Z", True),
        ("", False),
        (None, False),
        ("not-a-date", False),
    ],
)
def test_parse_iso(input_val, expected_not_none):
    result = metrics._parse_iso(input_val)
    if expected_not_none:
        assert result is not None
        assert result.tzinfo is not None
    else:
        assert result is None


# ---------------------------------------------------------------------------
# _get_labels
# ---------------------------------------------------------------------------


def test_get_labels_normal():
    issue = make_issue_with_labels("X-1", labels=["bug", "AI_assistance"])
    assert metrics._get_labels(issue) == ["bug", "AI_assistance"]


def test_get_labels_empty_list():
    issue = make_issue_with_labels("X-1", labels=[])
    assert metrics._get_labels(issue) == []


def test_get_labels_missing_key():
    issue = {"key": "X-1", "fields": {}}
    assert metrics._get_labels(issue) == []


def test_get_labels_missing_fields():
    issue = {"key": "X-1"}
    assert metrics._get_labels(issue) == []


# ---------------------------------------------------------------------------
# compute_ai_assistance_trend
# ---------------------------------------------------------------------------


def test_ai_trend_ai_labeled_done_issues():
    sprint = make_sprint(1, "S1")
    issues = [
        make_issue_with_labels("X-1", "Done", 5.0, ["AI_assistance"]),
        make_issue_with_labels("X-2", "Done", 3.0, []),
    ]
    result = metrics.compute_ai_assistance_trend(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_exclude_labels=[],
    )
    assert len(result) == 1
    assert result[0]["total_sp"] == 8.0
    assert result[0]["ai_sp"] == 5.0
    assert result[0]["ai_pct"] == 62.5


def test_ai_trend_no_done_issues():
    sprint = make_sprint(1)
    issues = [make_issue_with_labels("X-1", "In Progress", 5.0, ["AI_assistance"])]
    result = metrics.compute_ai_assistance_trend(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_exclude_labels=[],
    )
    assert result[0]["total_sp"] == 0.0
    assert result[0]["ai_pct"] == 0.0


def test_ai_trend_exclude_labels():
    sprint = make_sprint(1)
    issues = [
        make_issue_with_labels("X-1", "Done", 5.0, ["AI_assistance"]),
        make_issue_with_labels("X-2", "Done", 3.0, ["exclude_me"]),
    ]
    result = metrics.compute_ai_assistance_trend(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_exclude_labels=["exclude_me"],
    )
    assert result[0]["total_sp"] == 5.0  # X-2 excluded from denominator
    assert result[0]["ai_sp"] == 5.0
    assert result[0]["ai_pct"] == 100.0


def test_ai_trend_multiple_sprints():
    s1, s2 = make_sprint(1, "S1"), make_sprint(2, "S2")
    i1 = [make_issue_with_labels("X-1", "Done", 5.0, ["AI_assistance"])]
    i2 = [make_issue_with_labels("X-2", "Done", 3.0, [])]
    result = metrics.compute_ai_assistance_trend(
        [s1, s2],
        {1: i1, 2: i2},
        ai_assisted_label="AI_assistance",
        ai_exclude_labels=[],
    )
    assert len(result) == 2
    assert result[0]["ai_sp"] == 5.0
    assert result[1]["ai_sp"] == 0.0


def test_ai_trend_no_ai_label():
    sprint = make_sprint(1)
    issues = [make_issue_with_labels("X-1", "Done", 5.0, [])]
    result = metrics.compute_ai_assistance_trend(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_exclude_labels=[],
    )
    assert result[0]["ai_sp"] == 0.0
    assert result[0]["ai_pct"] == 0.0


def test_ai_trend_jira_tickets_mode_counts_issues_not_story_points():
    """When estimation_type=JiraTickets, each done issue counts as 1 regardless of SP."""
    sprint = make_sprint(1, "S1")
    issues = [
        make_issue_with_labels("X-1", "Done", 0.0, ["AI_assistance"]),
        make_issue_with_labels("X-2", "Done", 0.0, []),
        make_issue_with_labels("X-3", "In Progress", 0.0, ["AI_assistance"]),
    ]
    result = metrics.compute_ai_assistance_trend(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_exclude_labels=[],
        estimation_type="JiraTickets",
    )
    assert result[0]["total_sp"] == 2.0, "Should count 2 done issues"
    assert result[0]["ai_sp"] == 1.0, "Should count 1 done AI-labeled issue"
    assert result[0]["ai_pct"] == 50.0


def test_ai_trend_fallback_uses_tool_labels_when_assisted_label_empty():
    sprint = make_sprint(1, "S1")
    issues = [
        make_issue_with_labels("X-1", "Done", 5.0, ["AI_Tool_Copilot"]),
        make_issue_with_labels("X-2", "Done", 3.0, []),
    ]
    result = metrics.compute_ai_assistance_trend(
        [sprint],
        {1: issues},
        ai_assisted_label="",
        ai_exclude_labels=[],
        ai_tool_labels=["AI_Tool_Copilot"],
        ai_action_labels=[],
    )
    assert result[0]["ai_sp"] == 5.0
    assert result[0]["ai_pct"] == 62.5


def test_ai_trend_fallback_uses_action_labels_when_assisted_label_empty():
    sprint = make_sprint(1, "S1")
    issues = [make_issue_with_labels("X-1", "Done", 4.0, ["AI_Case_CodeGen"])]
    result = metrics.compute_ai_assistance_trend(
        [sprint],
        {1: issues},
        ai_assisted_label="",
        ai_exclude_labels=[],
        ai_tool_labels=[],
        ai_action_labels=["AI_Case_CodeGen"],
    )
    assert result[0]["ai_pct"] == 100.0


def test_ai_trend_fallback_no_labels_yields_zero():
    sprint = make_sprint(1, "S1")
    issues = [make_issue_with_labels("X-1", "Done", 5.0, ["AI_Tool_Copilot"])]
    result = metrics.compute_ai_assistance_trend(
        [sprint],
        {1: issues},
        ai_assisted_label="",
        ai_exclude_labels=[],
        ai_tool_labels=[],
        ai_action_labels=[],
    )
    assert result[0]["ai_pct"] == 0.0


def test_ai_trend_explicit_label_overrides_fallback():
    # When ai_assisted_label is set, tool/action labels do NOT promote an issue.
    sprint = make_sprint(1, "S1")
    issues = [make_issue_with_labels("X-1", "Done", 5.0, ["AI_Tool_Copilot"])]
    result = metrics.compute_ai_assistance_trend(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_exclude_labels=[],
        ai_tool_labels=["AI_Tool_Copilot"],
        ai_action_labels=[],
    )
    assert result[0]["ai_pct"] == 0.0


# ---------------------------------------------------------------------------
# compute_ai_usage_details
# ---------------------------------------------------------------------------


def test_ai_usage_tool_breakdown():
    sprint = make_sprint(1)
    issues = [
        make_issue_with_labels("X-1", "Done", 5.0, ["AI_assistance", "AI_Tool_Copilot"]),
        make_issue_with_labels("X-2", "Done", 3.0, ["AI_assistance", "AI_Tool_ChatGPT"]),
    ]
    result = metrics.compute_ai_usage_details(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_tool_labels=["AI_Tool_Copilot", "AI_Tool_ChatGPT"],
        ai_action_labels=[],
    )
    assert result["ai_assisted_issue_count"] == 2
    assert len(result["tool_breakdown"]) == 2
    labels = [r["label"] for r in result["tool_breakdown"]]
    assert "AI_Tool_Copilot" in labels
    assert "AI_Tool_ChatGPT" in labels


def test_ai_usage_action_breakdown():
    sprint = make_sprint(1)
    issues = [
        make_issue_with_labels("X-1", "Done", 5.0, ["AI_assistance", "AI_Case_CodeGen"]),
    ]
    result = metrics.compute_ai_usage_details(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_tool_labels=[],
        ai_action_labels=["AI_Case_CodeGen", "AI_Case_Review"],
    )
    assert len(result["action_breakdown"]) == 1
    assert result["action_breakdown"][0]["label"] == "AI_Case_CodeGen"
    assert result["action_breakdown"][0]["count"] == 1


def test_ai_usage_dedup_across_sprints():
    s1, s2 = make_sprint(1), make_sprint(2)
    issue = make_issue_with_labels("X-1", "Done", 5.0, ["AI_assistance", "AI_Tool_Copilot"])
    result = metrics.compute_ai_usage_details(
        [s1, s2],
        {1: [issue], 2: [issue]},  # same issue in two sprints
        ai_assisted_label="AI_assistance",
        ai_tool_labels=["AI_Tool_Copilot"],
        ai_action_labels=[],
    )
    assert result["ai_assisted_issue_count"] == 1  # deduplicated


def test_ai_usage_no_ai_issues():
    sprint = make_sprint(1)
    issues = [make_issue_with_labels("X-1", "Done", 5.0, [])]
    result = metrics.compute_ai_usage_details(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_tool_labels=["AI_Tool_Copilot"],
        ai_action_labels=[],
    )
    assert result["ai_assisted_issue_count"] == 0
    assert result["tool_breakdown"] == []


def test_ai_usage_empty_labels():
    sprint = make_sprint(1)
    issues = [make_issue_with_labels("X-1", "Done", 5.0, ["AI_assistance"])]
    result = metrics.compute_ai_usage_details(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_tool_labels=[],
        ai_action_labels=[],
    )
    assert result["ai_assisted_issue_count"] == 1
    assert result["tool_breakdown"] == []
    assert result["action_breakdown"] == []


def test_ai_usage_fallback_uses_tool_or_action_labels():
    sprint = make_sprint(1)
    issues = [
        make_issue_with_labels("X-1", "Done", 1.0, ["AI_Tool_Copilot"]),
        make_issue_with_labels("X-2", "Done", 1.0, ["AI_Case_CodeGen"]),
        make_issue_with_labels("X-3", "Done", 1.0, []),
    ]
    result = metrics.compute_ai_usage_details(
        [sprint],
        {1: issues},
        ai_assisted_label="",
        ai_tool_labels=["AI_Tool_Copilot"],
        ai_action_labels=["AI_Case_CodeGen"],
    )
    assert result["ai_assisted_issue_count"] == 2
    tool_labels = [r["label"] for r in result["tool_breakdown"]]
    action_labels = [r["label"] for r in result["action_breakdown"]]
    assert "AI_Tool_Copilot" in tool_labels
    assert "AI_Case_CodeGen" in action_labels


def test_ai_usage_explicit_label_overrides_fallback():
    sprint = make_sprint(1)
    issues = [make_issue_with_labels("X-1", "Done", 1.0, ["AI_Tool_Copilot"])]
    result = metrics.compute_ai_usage_details(
        [sprint],
        {1: issues},
        ai_assisted_label="AI_assistance",
        ai_tool_labels=["AI_Tool_Copilot"],
        ai_action_labels=[],
    )
    assert result["ai_assisted_issue_count"] == 0


# ---------------------------------------------------------------------------
# Schema-driven parameters
# ---------------------------------------------------------------------------


def test_get_story_points_with_custom_field():
    issue = {"key": "X-1", "fields": {"customfield_99": 13.0}}
    assert metrics._get_story_points(issue, story_points_field="customfield_99") == 13.0


def test_get_story_points_custom_field_missing():
    issue = {"key": "X-1", "fields": {"customfield_10016": 5.0}}
    assert metrics._get_story_points(issue, story_points_field="customfield_99") == 0.0


def test_is_done_with_custom_statuses():
    issue = make_issue("X-1", status="Finished")
    assert metrics._is_done(issue) is False
    assert metrics._is_done(issue, done_statuses=frozenset(("finished",))) is True


def test_is_done_custom_statuses_case_insensitive():
    issue = make_issue("X-1", status="SHIPPED")
    assert metrics._is_done(issue, done_statuses=frozenset(("shipped",))) is True


def test_compute_velocity_custom_field_and_statuses():
    sprint = make_sprint(1)
    issues = [
        {"key": "X-1", "fields": {"status": {"name": "Shipped"}, "cf_sp": 8.0}},
        {"key": "X-2", "fields": {"status": {"name": "Done"}, "cf_sp": 3.0}},
    ]
    result = metrics.compute_velocity(
        [sprint],
        {1: issues},
        story_points_field="cf_sp",
        done_statuses=frozenset(("shipped",)),
    )
    assert result[0]["velocity"] == 8.0
    assert result[0]["issue_count"] == 1


def test_build_metrics_dict_with_schema():
    schema = {
        "schema_name": "Test Schema",
        "fields": {"story_points": {"id": "cf_sp"}},
        "status_mapping": {
            "done_statuses": ["Shipped"],
            "in_progress_statuses": ["Active"],
        },
    }
    sprint = make_sprint(1)
    issue = {"key": "X-1", "fields": {"status": {"name": "Shipped"}, "cf_sp": 10.0}}
    result = metrics.build_metrics_dict([sprint], {1: [issue]}, schema=schema)
    assert result["schema_name"] == "Test Schema"
    assert result["velocity"][0]["velocity"] == 10.0
    assert result["velocity"][0]["issue_count"] == 1


def test_build_metrics_dict_without_schema_backward_compat():
    sprint = make_sprint(1)
    issue = make_issue("X-1", "Done", 5.0)
    result = metrics.build_metrics_dict([sprint], {1: [issue]})
    assert result["schema_name"] is None
    assert result["velocity"][0]["velocity"] == 5.0


def test_build_metrics_dict_jira_tickets_velocity_uses_issue_count(monkeypatch):
    monkeypatch.setattr("app.core.config.ESTIMATION_TYPE", "JiraTickets")
    sprint = make_sprint(1, "Sprint 1")
    issues = [
        make_issue("X-1", "Done", 5.0),
        make_issue("X-2", "Done", 3.0),
        make_issue("X-3", "In Progress", 2.0),
    ]
    result = metrics.build_metrics_dict([sprint], {1: issues})
    row = result["velocity"][0]
    assert row["issue_count"] == 2
    assert row["velocity"] == 2, "JiraTickets mode should use issue_count as velocity"


def test_build_metrics_dict_story_points_velocity_unchanged(monkeypatch):
    monkeypatch.setattr("app.core.config.ESTIMATION_TYPE", "StoryPoints")
    sprint = make_sprint(1, "Sprint 1")
    issues = [make_issue("X-1", "Done", 5.0), make_issue("X-2", "Done", 3.0)]
    result = metrics.build_metrics_dict([sprint], {1: issues})
    row = result["velocity"][0]
    assert row["velocity"] == 8.0, "StoryPoints mode should sum story points"
    assert row["issue_count"] == 2


# ---------------------------------------------------------------------------
# deduplicate_sprint_issues
# ---------------------------------------------------------------------------


def test_dedup_basic_issue_kept_in_last_sprint():
    s1, s2 = make_sprint(1), make_sprint(2)
    issue = make_issue("X-1", "Done", 5.0)
    result = metrics.deduplicate_sprint_issues([s1, s2], {1: [issue], 2: [issue]})
    assert result[1] == []
    assert result[2] == [issue]


def test_dedup_three_sprints_kept_in_last():
    s1, s2, s3 = make_sprint(1), make_sprint(2), make_sprint(3)
    issue = make_issue("X-1", "Done", 5.0)
    result = metrics.deduplicate_sprint_issues([s1, s2, s3], {1: [issue], 2: [issue], 3: [issue]})
    assert result[1] == []
    assert result[2] == []
    assert result[3] == [issue]


def test_dedup_no_duplicates_unchanged():
    s1, s2 = make_sprint(1), make_sprint(2)
    i1, i2 = make_issue("X-1", "Done", 5.0), make_issue("X-2", "Done", 3.0)
    result = metrics.deduplicate_sprint_issues([s1, s2], {1: [i1], 2: [i2]})
    assert result[1] == [i1]
    assert result[2] == [i2]


def test_dedup_kanban_string_sprint_ids():
    s1 = {"id": "week-2024-W01", "name": "W01"}
    s2 = {"id": "week-2024-W02", "name": "W02"}
    issue = make_issue("X-1", "Done", 8.0)
    result = metrics.deduplicate_sprint_issues([s1, s2], {"week-2024-W01": [issue], "week-2024-W02": [issue]})
    assert result["week-2024-W01"] == []
    assert result["week-2024-W02"] == [issue]


def test_dedup_kanban_keeps_issues_with_sprint_field():
    """KANBAN issues that carry a Jira sprint custom field must NOT be dropped.

    Real Jira KANBAN boards (especially those built on top of SCRUM-capable projects)
    return issues whose ``customfield_10020`` carries one or more sprint IDs. The
    SCRUM attribution rule "drop if owner sprint not in fetched window" makes the
    entire KANBAN report empty because none of the integer Jira sprint IDs match
    the string period IDs (``week-2026-W17`` etc.) — fall back to placement instead.
    """
    s1 = {"id": "week-2024-W01", "name": "W01"}
    s2 = {"id": "week-2024-W02", "name": "W02"}
    iss_w01 = make_issue("K-1", "Done", 5.0, sprint_ids=[42])  # sprint 42 not in fetched
    iss_w02 = make_issue("K-2", "Done", 8.0, sprint_ids=[99])
    result = metrics.deduplicate_sprint_issues([s1, s2], {"week-2024-W01": [iss_w01], "week-2024-W02": [iss_w02]})
    assert iss_w01 in result["week-2024-W01"]
    assert iss_w02 in result["week-2024-W02"]


def test_dedup_issue_without_key_not_moved():
    s1, s2 = make_sprint(1), make_sprint(2)
    keyless = {"fields": {"status": {"name": "Done"}}}
    result = metrics.deduplicate_sprint_issues([s1, s2], {1: [keyless], 2: []})
    # keyless issue has empty key — not tracked, stays where it was placed
    assert keyless in result[1]
    assert result[2] == []


def test_dedup_mixed_unique_and_duplicate():
    s1, s2 = make_sprint(1), make_sprint(2)
    shared = make_issue("X-1", "Done", 5.0)
    unique_s1 = make_issue("X-2", "Done", 3.0)
    unique_s2 = make_issue("X-3", "Done", 2.0)
    result = metrics.deduplicate_sprint_issues([s1, s2], {1: [shared, unique_s1], 2: [shared, unique_s2]})
    assert shared not in result[1]
    assert unique_s1 in result[1]
    assert shared in result[2]
    assert unique_s2 in result[2]


def test_dedup_newest_first_input_still_keeps_issue_in_most_recent():
    """jira_client returns sprints newest-first; dedup must still attribute to the most recent sprint."""
    s_old = make_sprint(1, start="2026-03-01")
    s_new = make_sprint(2, start="2026-03-15")
    issue = make_issue("X-1", "Done", 5.0)
    # Pass newest-first (as jira_client does)
    result = metrics.deduplicate_sprint_issues([s_new, s_old], {1: [issue], 2: [issue]})
    assert result[1] == [], "Older sprint should be emptied"
    assert result[2] == [issue], "Newer sprint should keep the issue"


def test_dedup_drops_issue_owned_by_active_sprint_outside_fetch():
    """Bug fix: when JIRA_CLOSED_SPRINTS_ONLY=True, the active sprint is not
    fetched. A ticket carried into the active sprint must NOT be attributed
    to the most-recent closed sprint — it should be dropped until the active
    sprint enters the fetch window. Reproduces the user-reported case where
    a ticket in [Sprint 5, Sprint 6, Sprint 7] (Sprint 7 active, not fetched)
    was incorrectly counted in Sprint 6's velocity.
    """
    s5 = make_sprint(5, start="2026-03-23", end="2026-04-05")
    s6 = make_sprint(6, start="2026-04-06", end="2026-04-19")
    issue = make_issue("X-1", "Done", 5.0, sprint_ids=[5, 6, 7])
    # Jira returns the issue under both fetched sprints (its sprint field
    # contains 5 and 6); Sprint 7 is active, not in our sprints list.
    result = metrics.deduplicate_sprint_issues([s5, s6], {5: [issue], 6: [issue]})
    assert result[5] == [], "Sprint 5 must not own a ticket also in a later sprint"
    assert result[6] == [], "Sprint 6 must not own a ticket carried into the active Sprint 7"


def test_dedup_keeps_issue_in_active_sprint_when_fetched():
    """Mirror of the bug fix: when the active sprint IS in the fetch
    (JIRA_CLOSED_SPRINTS_ONLY=False), the ticket lands in the active sprint."""
    s5 = make_sprint(5, start="2026-03-23", end="2026-04-05")
    s6 = make_sprint(6, start="2026-04-06", end="2026-04-19")
    s7 = make_sprint(7, start="2026-04-20", end="2026-05-03")
    issue = make_issue("X-1", "Done", 5.0, sprint_ids=[5, 6, 7])
    result = metrics.deduplicate_sprint_issues(
        [s5, s6, s7],
        {5: [issue], 6: [issue], 7: [issue]},
    )
    assert result[5] == []
    assert result[6] == []
    assert result[7] == [issue]


def test_dedup_attributes_to_latest_sprint_field_id_not_jira_membership():
    """Even if Jira's API returns an issue only under sprint 5, the sprint
    field's max ID is the source of truth. If max ID == 6 and 6 is fetched,
    the issue is attributed to 6."""
    s5 = make_sprint(5, start="2026-03-23", end="2026-04-05")
    s6 = make_sprint(6, start="2026-04-06", end="2026-04-19")
    issue = make_issue("X-1", "Done", 5.0, sprint_ids=[5, 6])
    # Jira returns under sprint 5 only — but the sprint field shows it's also in 6.
    result = metrics.deduplicate_sprint_issues([s5, s6], {5: [issue], 6: []})
    assert result[5] == []
    assert result[6] == [issue]


def test_dedup_falls_back_when_sprint_field_missing():
    """Issues without a sprint field (legacy / unusual data) fall back to
    most-recent-membership attribution."""
    s_old = make_sprint(1, start="2026-03-01")
    s_new = make_sprint(2, start="2026-03-15")
    issue = make_issue("X-1", "Done", 5.0)  # no sprint_ids
    result = metrics.deduplicate_sprint_issues([s_old, s_new], {1: [issue], 2: [issue]})
    assert result[1] == []
    assert result[2] == [issue]


def test_velocity_excludes_ticket_carried_to_unfetched_active_sprint():
    """End-to-end regression for the user-reported bug:

    Sprint 6's velocity should be 18, not 23. The 5-point ticket whose sprint
    field includes Sprint 7 (active, not fetched) must not inflate Sprint 6.
    """
    s5 = make_sprint(5, start="2026-03-23", end="2026-04-05")
    s6 = make_sprint(6, start="2026-04-06", end="2026-04-19")
    # 18 points of work done in Sprint 6 (3 tickets fully owned by sprint 6):
    s6_native = [
        make_issue("S6-1", "Done", 8.0, sprint_ids=[6]),
        make_issue("S6-2", "Done", 5.0, sprint_ids=[6]),
        make_issue("S6-3", "Done", 5.0, sprint_ids=[6]),
    ]
    # The carry-over ticket: 5 points, sprint field = [5, 6, 7]. Belongs to 7.
    carry = make_issue("CARRY-1", "Done", 5.0, sprint_ids=[5, 6, 7])
    sprint_issues_in = {5: [carry], 6: s6_native + [carry]}
    sprint_issues = metrics.deduplicate_sprint_issues([s5, s6], sprint_issues_in)
    velocity = metrics.compute_velocity([s5, s6], sprint_issues)
    by_sid = {row["sprint_id"]: row for row in velocity}
    assert by_sid[6]["velocity"] == 18.0, "Sprint 6 velocity must exclude the carry-over to Sprint 7"
    assert by_sid[5]["velocity"] == 0.0, "Sprint 5 must not retain the carry-over either"
