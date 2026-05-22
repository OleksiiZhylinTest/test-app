"""Unit tests for app.core.user_data."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.core.user_data import ensure_user_data_dirs, user_data_dir

pytestmark = pytest.mark.unit


def test_ensure_user_data_dirs_creates_data_dau(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """ensure_user_data_dirs() creates the data/dau subdirectory under the user data root."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    ensure_user_data_dirs()
    assert (tmp_path / "AIMetrics" / "data" / "dau").is_dir()


def test_ensure_user_data_dirs_creates_all_subdirs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """ensure_user_data_dirs() creates all expected subdirectories."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    ensure_user_data_dirs()
    root = tmp_path / "AIMetrics"
    for sub in ("certs", "config", "data/dau", "reports", "logs"):
        assert (root / sub).is_dir(), f"Expected subdirectory '{sub}' was not created"


def test_user_data_dir_uses_localappdata(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """user_data_dir() returns <LOCALAPPDATA>/AIMetrics when LOCALAPPDATA is set."""
    monkeypatch.setenv("LOCALAPPDATA", str(tmp_path))
    assert user_data_dir() == tmp_path / "AIMetrics"
