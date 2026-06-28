"""Component tests for `python main.py --complexity-audit` CLI path.

Uses subprocess to exercise the CLI as a user would.  Reports are written
to user_data_dir() / "reports" / <timestamp>/.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import pytest

from app.core.user_data import user_data_dir

pytestmark = pytest.mark.component

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _run_complexity_audit() -> tuple[subprocess.CompletedProcess, Path]:
    """Run `python main.py --complexity-audit` and return (result, new_report_dir)."""
    reports_dir = user_data_dir() / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    before = {p for p in reports_dir.iterdir() if p.is_dir()}

    result = subprocess.run(
        [sys.executable, "main.py", "--complexity-audit"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )

    after = {p for p in reports_dir.iterdir() if p.is_dir()}
    new_dirs = after - before
    assert new_dirs, f"No new report directory created. stderr: {result.stderr}"
    report_dir = max(new_dirs, key=lambda p: p.stat().st_mtime)
    return result, report_dir


@pytest.mark.smoke
def test_complexity_audit_cli_exits_zero_creates_md_within_60s():
    """SC-3: --complexity-audit returns exit code 0 and writes complexity_report.md in < 60s (CI-adjusted)."""
    reports_dir = user_data_dir() / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    before = {p for p in reports_dir.iterdir() if p.is_dir()}

    start = time.monotonic()
    result = subprocess.run(
        [sys.executable, "main.py", "--complexity-audit"],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    elapsed = time.monotonic() - start

    assert result.returncode == 0, f"main.py --complexity-audit exited {result.returncode}:\n{result.stderr}"
    assert elapsed < 60.0, f"Audit took {elapsed:.1f}s (limit: 60s under parallel CI load)"

    after = {p for p in reports_dir.iterdir() if p.is_dir()}
    new_dirs = after - before
    assert new_dirs, "No new report directory was created"
    report_dir = max(new_dirs, key=lambda p: p.stat().st_mtime)
    md_files = list(report_dir.glob("complexity_report.md"))
    assert md_files, f"No complexity_report.md found in {report_dir}"


def test_complexity_audit_cli_creates_html_alongside_md():
    """--complexity-audit produces complexity_report.html in the same report dir."""
    result, report_dir = _run_complexity_audit()
    assert result.returncode == 0, f"CLI failed:\n{result.stderr}"
    html_files = list(report_dir.glob("complexity_report.html"))
    assert html_files, f"No complexity_report.html found in {report_dir}"


def test_complexity_audit_md_contains_expected_sections():
    """complexity_report.md must contain '## Module Scores' and '## Improvement Plan'."""
    result, report_dir = _run_complexity_audit()
    assert result.returncode == 0, f"CLI failed:\n{result.stderr}"
    md_file = next(report_dir.glob("complexity_report.md"))
    content = md_file.read_text(encoding="utf-8")
    assert "## Module Scores" in content
    assert "## Improvement Plan" in content


def test_complexity_audit_md_includes_non_app_modules():
    """Full-repo scope: report must include modules from tools/ or tests/."""
    result, report_dir = _run_complexity_audit()
    assert result.returncode == 0, f"CLI failed:\n{result.stderr}"
    md_file = next(report_dir.glob("complexity_report.md"))
    content = md_file.read_text(encoding="utf-8")
    assert "tools/" in content or "tests/" in content, (
        "Expected modules from tools/ or tests/ in the report (full-repo scope)"
    )
