"""E2E tests for NFR-U-006: release version badge in UI headers.

Verifies that both index.html and dau_survey.html display a version badge
populated dynamically from GET /api/version.

Run:
    pytest tests/e2e/test_e2e_version.py -v
    pytest tests/e2e/test_e2e_version.py -v --headed   # visual debug
"""

from __future__ import annotations

import re

import allure
import pytest
from playwright.sync_api import Page, expect

import app as _app
from tests.e2e.conftest import _goto

pytestmark = pytest.mark.e2e

_EXPECTED_VERSION = f"App version {_app.__version__}"
_VERSION_RE = re.compile(r"^App version \d+\.\d+\.\d+")


# ---------------------------------------------------------------------------
# index.html
# ---------------------------------------------------------------------------


@pytest.mark.sanity
def test_index_header_shows_version_badge(page: Page, live_server_url: str):
    """Version badge in index.html header is populated after page load (NFR-U-006)."""
    with allure.step("Navigate to index.html"):
        _goto(page, live_server_url)

    with allure.step("Wait for version badge to populate via /api/version"):
        badge = page.locator("#app-version")
        expect(badge).to_have_text(_EXPECTED_VERSION, timeout=3000)

    with allure.step("Version badge is visible in the header"):
        expect(badge).to_be_visible()


def test_index_version_badge_text_matches_semver(page: Page, live_server_url: str):
    """Version badge text matches semver format vX.Y.Z on index.html."""
    _goto(page, live_server_url)
    expect(page.locator("#app-version")).to_have_text(_VERSION_RE, timeout=3000)


# ---------------------------------------------------------------------------
# dau_survey.html (served via HTTP so /api/version fetch succeeds)
# ---------------------------------------------------------------------------


@pytest.mark.sanity
def test_dau_survey_header_shows_version_badge(page: Page, live_server_url: str):
    """Version badge in dau_survey.html header is populated when served via HTTP (NFR-U-006)."""
    survey_url = f"{live_server_url}/ui/dau_survey.html"

    with allure.step("Navigate to dau_survey.html via HTTP"):
        page.goto(survey_url, wait_until="domcontentloaded", timeout=5000)

    with allure.step("Wait for version badge to populate via /api/version"):
        badge = page.locator("#app-version")
        expect(badge).to_have_text(_EXPECTED_VERSION, timeout=3000)

    with allure.step("Version badge is visible in the header"):
        expect(badge).to_be_visible()


def test_dau_survey_version_badge_text_matches_semver(page: Page, live_server_url: str):
    """Version badge text matches semver format vX.Y.Z on dau_survey.html."""
    page.goto(f"{live_server_url}/ui/dau_survey.html", wait_until="domcontentloaded", timeout=5000)
    expect(page.locator("#app-version")).to_have_text(_VERSION_RE, timeout=3000)
