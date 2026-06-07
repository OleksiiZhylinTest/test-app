"""Component tests for GET /api/complexity/audit HTTP endpoint.

Uses a real server on a random port via the shared `server_url` fixture
from tests/conftest.py.  Each test makes an independent HTTP request.
"""

from __future__ import annotations

import json
import time
import urllib.request

import pytest

pytestmark = pytest.mark.component


@pytest.mark.smoke
def test_complexity_audit_returns_200_json_with_required_top_keys(server_url):
    """SC-5: GET /api/complexity/audit returns 200, application/json, scores+summary, < 60s (CI-adjusted)."""
    start = time.monotonic()
    resp = urllib.request.urlopen(f"{server_url}/api/complexity/audit", timeout=65)
    elapsed = time.monotonic() - start

    assert resp.status == 200
    assert "application/json" in (resp.getheader("Content-Type") or "")
    data = json.loads(resp.read().decode())
    assert "scores" in data, "Response missing 'scores' key"
    assert isinstance(data["scores"], list)
    assert "summary" in data, "Response missing 'summary' key"
    assert isinstance(data["summary"], dict)
    assert elapsed < 60.0, f"Response took {elapsed:.1f}s (limit: 60s under parallel CI load)"


def test_complexity_audit_each_score_has_required_keys(server_url):
    resp = urllib.request.urlopen(f"{server_url}/api/complexity/audit", timeout=65)
    data = json.loads(resp.read().decode())
    required = {
        "module",
        "loc",
        "function_count",
        "coupling",
        "cohesion",
        "composite_score",
        "classification",
        "recommendations",
    }
    for score in data["scores"]:
        missing = required - score.keys()
        assert not missing, f"Score entry missing keys {missing}: {score['module']!r}"


def test_complexity_audit_summary_has_required_keys(server_url):
    resp = urllib.request.urlopen(f"{server_url}/api/complexity/audit", timeout=65)
    data = json.loads(resp.read().decode())
    summary = data["summary"]
    for key in ("high_count", "medium_count", "low_count", "error_count"):
        assert key in summary, f"summary missing key: {key!r}"


def test_complexity_audit_classification_values_are_valid(server_url):
    resp = urllib.request.urlopen(f"{server_url}/api/complexity/audit", timeout=65)
    data = json.loads(resp.read().decode())
    valid = {"Low", "Medium", "High", "Error"}
    for score in data["scores"]:
        assert score["classification"] in valid, (
            f"Invalid classification {score['classification']!r} for {score['module']!r}"
        )
