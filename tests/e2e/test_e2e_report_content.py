"""E2E tests that verify report HTML content rendered in the browser.

Unlike filter UI tests, these tests generate a real HTML report via the CLI pipeline
(with a mocked Jira client) and open it through the live server, asserting on metric
values visible in the rendered page.
"""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import MagicMock

import allure
import pytest
from playwright.sync_api import Page, expect

from tests.conftest import make_issue_with_labels

pytestmark = pytest.mark.e2e

# ---------------------------------------------------------------------------
# Report-generation fixture
# ---------------------------------------------------------------------------

_REPORT_SUBDIR = Path("generated/reports/_test_sprint_metrics")


@pytest.fixture()
def sprint_metrics_report_url(live_server_url: str, monkeypatch) -> str:
    """Generate a real velocity+AI report via main() and return its browser URL.

    Uses the sprint-filter scenario: JIRA_SPRINT_NAME_FILTER="Test Sprint",
    JIRA_INCLUDE_ACTIVE_SPRINT=True, JIRA_SPRINT_COUNT=2.

    Issues:
      Test Sprint 4: T-4a (5.0 pts, AI) + T-4b (3.0 pts) → velocity=8.0, ai_pct=62.5%
      Test Sprint 3: T-3a (3.0 pts, AI)                  → velocity=3.0, ai_pct=100.0%
    """
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

    _REPORT_SUBDIR.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr("app.cli.REPORTS_DIR", _REPORT_SUBDIR)
    monkeypatch.setattr("sys.argv", ["main.py"])

    from main import main

    main()

    subdirs = sorted(_REPORT_SUBDIR.iterdir())
    html_file = next(iter(subdirs[0].glob("*.html")))

    # Build server URL: the live server serves /generated/reports/** from the project root
    rel = html_file.as_posix()
    url = f"{live_server_url}/{rel}"

    yield url

    shutil.rmtree(_REPORT_SUBDIR, ignore_errors=True)


# ---------------------------------------------------------------------------
# Test
# ---------------------------------------------------------------------------


def test_report_renders_velocity_and_ai_metrics_for_sprint_filter(page: Page, sprint_metrics_report_url: str):
    """The generated report shows only the 2 filtered sprints with correct velocity and AI%."""
    with allure.step("Open the generated report in the browser"):
        page.goto(sprint_metrics_report_url, wait_until="domcontentloaded")

    with allure.step("Correct sprints are present in the report"):
        expect(page.locator("text=Test Sprint 4").first).to_be_visible()
        expect(page.locator("text=Test Sprint 3").first).to_be_visible()

    with allure.step("Velocity metric: Test Sprint 4 = 8.0 points"):
        expect(page.locator("text=8.0").first).to_be_visible()

    with allure.step("AI Assisted metric: 62.5% for Test Sprint 4, 100.0% for Test Sprint 3"):
        expect(page.locator("text=62.5%").first).to_be_visible()
        expect(page.locator("text=100.0%").first).to_be_visible()
