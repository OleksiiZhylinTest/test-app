"""Integration tests: verify module interaction with mocked external boundaries."""

from __future__ import annotations

import json
import urllib.request
from unittest.mock import MagicMock

import pytest

from tests.conftest import make_issue, make_issue_with_labels, make_sprint

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Full pipeline — success
# ---------------------------------------------------------------------------


@pytest.mark.smoke
def test_main_pipeline_success(monkeypatch, tmp_path):
    """Mock jira_client functions, call main.main(), verify HTML/MD files are created."""
    sprints = [make_sprint(1, "Sprint 1", "2026-01-01", "2026-01-14")]
    issues = [make_issue("T-1", "Done", 5.0)]

    monkeypatch.setattr("app.core.config.JIRA_URL", "https://test.atlassian.net")
    monkeypatch.setattr("app.core.config.JIRA_EMAIL", "u@t.com")
    monkeypatch.setattr("app.core.config.JIRA_API_TOKEN", "tok")
    monkeypatch.setattr("app.core.config.JIRA_BOARD_ID", 42)
    monkeypatch.setattr("app.core.config.JIRA_FILTER_ID", None)

    mock_jira = MagicMock()
    monkeypatch.setattr("app.core.jira_client.create_client", lambda: mock_jira)
    monkeypatch.setattr("app.core.jira_client.fetch_sprint_data", lambda j: (sprints, {1: issues}))

    # Redirect reports to tmp_path
    monkeypatch.setattr("app.cli.REPORTS_DIR", tmp_path / "generated" / "reports")
    monkeypatch.setattr("sys.argv", ["main.py"])

    from main import main

    rc = main()
    assert rc == 0

    reports_dir = tmp_path / "generated" / "reports"
    assert reports_dir.exists()
    subdirs = list(reports_dir.iterdir())
    assert len(subdirs) == 1
    html_files = list(subdirs[0].glob("*.html"))
    md_files = list(subdirs[0].glob("*.md"))
    assert len(html_files) == 1
    assert len(md_files) == 1

    html = html_files[0].read_text(encoding="utf-8")
    assert "Sprint 1" in html
    md = md_files[0].read_text(encoding="utf-8")
    assert "Sprint 1" in md


# ---------------------------------------------------------------------------
# Full pipeline — config failure
# ---------------------------------------------------------------------------


def test_main_pipeline_config_fail(monkeypatch):
    """No credentials → exit 1 with error message."""
    monkeypatch.setattr("app.core.config.JIRA_URL", "")
    monkeypatch.setattr("app.core.config.JIRA_EMAIL", "")
    monkeypatch.setattr("app.core.config.JIRA_API_TOKEN", "")
    monkeypatch.setattr("sys.argv", ["main.py"])

    from main import main

    rc = main()
    assert rc == 1


# ---------------------------------------------------------------------------
# --clean flag
# ---------------------------------------------------------------------------


def test_main_clean_removes_reports(monkeypatch, tmp_path):
    reports_dir = tmp_path / "generated" / "reports"
    reports_dir.mkdir(parents=True)
    (reports_dir / "dummy.txt").write_text("x")

    monkeypatch.setattr("app.cli.REPORTS_DIR", reports_dir)
    monkeypatch.setattr("sys.argv", ["main.py", "--clean"])

    from main import main

    rc = main()
    assert rc == 0
    assert not reports_dir.exists()


# ---------------------------------------------------------------------------
# Filter metadata flow
# ---------------------------------------------------------------------------


def test_filter_metadata_in_html(monkeypatch, tmp_path):
    sprints = [make_sprint(1, "Sprint 1", "2026-01-01", "2026-01-14")]
    issues = [make_issue("T-1", "Done", 5.0)]

    monkeypatch.setattr("app.core.config.JIRA_URL", "https://test.atlassian.net")
    monkeypatch.setattr("app.core.config.JIRA_EMAIL", "u@t.com")
    monkeypatch.setattr("app.core.config.JIRA_API_TOKEN", "tok")
    monkeypatch.setattr("app.core.config.JIRA_BOARD_ID", 7)
    monkeypatch.setattr("app.core.config.JIRA_FILTER_ID", 42)

    mock_jira = MagicMock()
    # Mock the _session.get for filter name
    mock_filter_resp = MagicMock()
    mock_filter_resp.json.return_value = {"name": "My Test Filter"}
    mock_jira._session.get.return_value = mock_filter_resp

    monkeypatch.setattr("app.core.jira_client.create_client", lambda: mock_jira)
    monkeypatch.setattr("app.core.jira_client.fetch_sprint_data", lambda j: (sprints, {1: issues}))
    monkeypatch.setattr("app.core.jira_client.get_filter_jql", lambda j: "project = TEST")

    monkeypatch.setattr("app.cli.REPORTS_DIR", tmp_path / "generated" / "reports")
    monkeypatch.setattr("sys.argv", ["main.py"])

    from main import main

    rc = main()
    assert rc == 0

    subdirs = list((tmp_path / "generated" / "reports").iterdir())
    html_files = list(subdirs[0].glob("*.html"))
    assert len(html_files) == 1
    html = html_files[0].read_text(encoding="utf-8")
    assert "My Test Filter" in html
    assert "42" in html


# ---------------------------------------------------------------------------
# Server test-connection endpoint (real server + mocked urlopen)
# ---------------------------------------------------------------------------


def test_server_test_connection_json_shape(server_url):
    """Verify test-connection returns the expected JSON shape for an error response."""
    body = json.dumps(
        {
            "url": "https://nonexistent-jira-12345.atlassian.net",
            "email": "test@test.com",
            "token": "badtoken",
        }
    ).encode()
    req = urllib.request.Request(
        f"{server_url}/api/test-connection",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    resp = urllib.request.urlopen(req)
    data = json.loads(resp.read())
    assert "ok" in data
    assert isinstance(data["ok"], bool)


# ---------------------------------------------------------------------------
# Server generate endpoint (real server)
# ---------------------------------------------------------------------------


def test_server_generate_sse_format(server_url):
    """Verify generate endpoint returns SSE-formatted response."""
    req = urllib.request.Request(f"{server_url}/api/generate")
    resp = urllib.request.urlopen(req, timeout=30)
    assert "text/event-stream" in resp.headers.get("Content-Type", "")
    body = resp.read().decode()
    # Should contain at least the close event
    assert "event: close" in body


# ---------------------------------------------------------------------------
# Sprint name filter + active sprint + count cap — full pipeline
# ---------------------------------------------------------------------------


def test_main_pipeline_sprint_name_filter_with_active_and_count_cap(monkeypatch, tmp_path):
    """Full pipeline: name filter + active sprint included + count cap — only 2 sprints in report."""
    monkeypatch.setattr("app.core.config.JIRA_URL", "https://test.atlassian.net")
    monkeypatch.setattr("app.core.config.JIRA_EMAIL", "u@t.com")
    monkeypatch.setattr("app.core.config.JIRA_API_TOKEN", "tok")
    monkeypatch.setattr("app.core.config.JIRA_BOARD_ID", 1)
    monkeypatch.setattr("app.core.config.JIRA_FILTER_ID", None)
    monkeypatch.setattr("app.core.config.JIRA_INCLUDE_ACTIVE_SPRINT", True)
    monkeypatch.setattr("app.core.config.JIRA_SPRINT_COUNT", 2)
    monkeypatch.setattr("app.core.config.JIRA_SPRINT_NAME_FILTER", "Test Sprint")

    mock_jira = MagicMock()
    mock_jira.get_all_sprints_from_board.side_effect = [
        {
            "values": [
                {"id": 3, "name": "Test Sprint 3", "startDate": "2025-01-20"},
                {"id": 2, "name": "Test Sprint 2", "startDate": "2025-01-13"},
                {"id": 1, "name": "Test Sprint 1", "startDate": "2025-01-06"},
                {"id": 0, "name": "Test Sprint 0", "startDate": "2024-12-30"},
                {"id": 12, "name": "Alex Sprint 2", "startDate": "2025-01-13"},
                {"id": 11, "name": "Alex Sprint 1", "startDate": "2025-01-06"},
                {"id": 10, "name": "Alex Sprint 0", "startDate": "2024-12-30"},
                {"id": 20, "name": "Test 0", "startDate": "2024-12-23"},
            ]
        },
        {
            "values": [
                {"id": 4, "name": "Test Sprint 4"},
                {"id": 13, "name": "Alex Sprint 3"},
                {"id": 21, "name": "Test 1"},
            ]
        },
    ]
    mock_jira.get_all_issues_for_sprint_in_board.side_effect = [
        {"issues": [make_issue("T-4", "Done", 5.0)], "total": 1},
        {"issues": [make_issue("T-3", "Done", 3.0)], "total": 1},
    ]
    monkeypatch.setattr("app.core.jira_client.create_client", lambda: mock_jira)
    monkeypatch.setattr("app.cli.REPORTS_DIR", tmp_path / "generated" / "reports")
    monkeypatch.setattr("sys.argv", ["main.py"])

    from main import main

    rc = main()
    assert rc == 0

    reports_dir = tmp_path / "generated" / "reports"
    subdirs = list(reports_dir.iterdir())
    html = list(subdirs[0].glob("*.html"))[0].read_text(encoding="utf-8")
    assert "Test Sprint 4" in html
    assert "Test Sprint 3" in html
    assert "Test Sprint 2" not in html
    assert "Alex Sprint" not in html
    assert "Test 1" not in html
    assert "Test 0" not in html


# ---------------------------------------------------------------------------
# Sprint filter + velocity + AI Assisted metric — full pipeline
# ---------------------------------------------------------------------------


def test_main_pipeline_sprint_filter_with_velocity_and_ai_metrics(monkeypatch, tmp_path):
    """Sprint filter + active sprint + count cap: velocity and AI% values appear in the HTML report."""
    monkeypatch.setattr("app.core.config.JIRA_URL", "https://test.atlassian.net")
    monkeypatch.setattr("app.core.config.JIRA_EMAIL", "u@t.com")
    monkeypatch.setattr("app.core.config.JIRA_API_TOKEN", "tok")
    monkeypatch.setattr("app.core.config.JIRA_BOARD_ID", 1)
    monkeypatch.setattr("app.core.config.JIRA_FILTER_ID", None)
    monkeypatch.setattr("app.core.config.JIRA_INCLUDE_ACTIVE_SPRINT", True)
    monkeypatch.setattr("app.core.config.JIRA_SPRINT_COUNT", 2)
    monkeypatch.setattr("app.core.config.JIRA_SPRINT_NAME_FILTER", "Test Sprint")
    monkeypatch.setattr("app.core.config.AI_ASSISTED_LABEL", "AI_assistance")
    monkeypatch.setattr("app.core.config.AI_EXCLUDE_LABELS", [])
    monkeypatch.setattr("app.core.config.AI_TOOL_LABELS", [])
    monkeypatch.setattr("app.core.config.AI_ACTION_LABELS", [])
    monkeypatch.setattr("app.core.config.ESTIMATION_TYPE", "StoryPoints")
    monkeypatch.setattr("app.core.config.METRIC_VELOCITY", True)
    monkeypatch.setattr("app.core.config.METRIC_AI_ASSISTANCE_TREND", True)

    mock_jira = MagicMock()
    mock_jira.get_all_sprints_from_board.side_effect = [
        {
            "values": [
                {"id": 3, "name": "Test Sprint 3", "startDate": "2025-01-20"},
                {"id": 2, "name": "Test Sprint 2", "startDate": "2025-01-13"},
                {"id": 1, "name": "Test Sprint 1", "startDate": "2025-01-06"},
                {"id": 0, "name": "Test Sprint 0", "startDate": "2024-12-30"},
                {"id": 12, "name": "Alex Sprint 2", "startDate": "2025-01-13"},
                {"id": 11, "name": "Alex Sprint 1", "startDate": "2025-01-06"},
                {"id": 10, "name": "Alex Sprint 0", "startDate": "2024-12-30"},
                {"id": 20, "name": "Test 0", "startDate": "2024-12-23"},
            ]
        },
        {
            "values": [
                {"id": 4, "name": "Test Sprint 4"},
                {"id": 13, "name": "Alex Sprint 3"},
                {"id": 21, "name": "Test 1"},
            ]
        },
    ]
    # Test Sprint 4: 5.0 AI + 3.0 non-AI → velocity=8.0, ai_pct=62.5%
    # Test Sprint 3: 3.0 AI              → velocity=3.0, ai_pct=100.0%
    mock_jira.get_all_issues_for_sprint_in_board.side_effect = [
        {
            "issues": [
                make_issue_with_labels("T-4a", "Done", 5.0, ["AI_assistance"]),
                make_issue_with_labels("T-4b", "Done", 3.0, []),
            ],
            "total": 2,
        },
        {
            "issues": [make_issue_with_labels("T-3a", "Done", 3.0, ["AI_assistance"])],
            "total": 1,
        },
    ]
    monkeypatch.setattr("app.core.jira_client.create_client", lambda: mock_jira)
    monkeypatch.setattr("app.cli.REPORTS_DIR", tmp_path / "generated" / "reports")
    monkeypatch.setattr("sys.argv", ["main.py"])

    from main import main

    rc = main()
    assert rc == 0

    reports_dir = tmp_path / "generated" / "reports"
    subdirs = list(reports_dir.iterdir())
    html = list(subdirs[0].glob("*.html"))[0].read_text(encoding="utf-8")

    # Sprint filter correctness
    assert "Test Sprint 4" in html
    assert "Test Sprint 3" in html
    assert "Test Sprint 2" not in html
    assert "Alex Sprint" not in html

    # Velocity values
    assert "8.0" in html  # Test Sprint 4: 5.0 + 3.0

    # AI Assisted metric values
    assert "62.5%" in html  # Test Sprint 4: 5.0 / 8.0 * 100
    assert "100.0%" in html  # Test Sprint 3: 3.0 / 3.0 * 100
