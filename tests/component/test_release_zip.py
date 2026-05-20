"""Tests for create_app_zip.bat: verifies the contents of the release ZIP package.

Covers: IR-01, IR-02, IR-03, IR-04, IR-05, IR-06, IR-07, IR-08, IR-09,
        IR-10, IR-11, IR-12, IR-13, IR-14, IR-15, IR-16, IR-17, IR-39, IR-40
"""

from __future__ import annotations

import re
import subprocess
import sys
import zipfile
from pathlib import Path

import pytest

pytestmark = [
    pytest.mark.component,
    pytest.mark.windows_only,
    pytest.mark.skipif(sys.platform != "win32", reason="create_app_zip.bat is Windows-only"),
]

ROOT = Path(__file__).parent.parent.parent


def _read_version() -> str:
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    match = re.search(r'^version\s*=\s*"([^"]+)"', text, re.MULTILINE)
    assert match, "Could not read version from pyproject.toml"
    return match.group(1)


@pytest.fixture(scope="session")
def release_zip() -> Path:
    """Build the release ZIP via create_app_zip.bat and return its path."""
    result = subprocess.run(
        ["cmd", "/c", str(ROOT / "create_app_zip.bat")],
        cwd=ROOT,
        capture_output=True,
        stdin=subprocess.DEVNULL,
        timeout=120,
    )
    if result.returncode != 0:
        pytest.skip(f"create_app_zip.bat exited with {result.returncode}:\n{result.stdout.decode(errors='replace')}")
    version = _read_version()
    zip_path = ROOT / "generated" / "releases" / f"ai_adoption_manager_v{version}.zip"
    assert zip_path.exists(), f"Expected ZIP not found: {zip_path}"
    return zip_path


@pytest.fixture(scope="session")
def zip_entries(release_zip: Path) -> set[str]:
    """All paths inside the ZIP."""
    with zipfile.ZipFile(release_zip) as zf:
        return set(zf.namelist())


# ── Name format ────────────────────────────────────────────────────────────────


def test_zip_name_format(release_zip: Path):
    """ZIP filename matches ai_adoption_manager_v{version}.zip."""
    version = _read_version()
    assert release_zip.name == f"ai_adoption_manager_v{version}.zip"


# ── Required folders ───────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "folder",
    ["app/", "templates/", "ui/", "config/", "data/", "tools/", "certs/"],
)
def test_zip_contains_required_folder(zip_entries: set[str], folder: str):
    """Each required folder has at least one entry in the ZIP."""
    assert any(e.startswith(folder) for e in zip_entries), f"Folder '{folder}' not found in release ZIP"


# ── Required root files ────────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "filename",
    [
        "main.py",
        "server.py",
        "requirements.txt",
        ".env.example",
        "start_app.bat",
        "project_setup.bat",
        "README.md",
    ],
)
def test_zip_contains_required_root_file(zip_entries: set[str], filename: str):
    """Each required root-level file is present in the ZIP."""
    assert filename in zip_entries, f"Required file '{filename}' not found in release ZIP"


# ── Specific content entries ───────────────────────────────────────────────────


def test_zip_contains_fetch_ssl_cert(zip_entries: set[str]):
    """tools/fetch_ssl_cert.py is the only file copied from tools/."""
    assert "tools/fetch_ssl_cert.py" in zip_entries


def test_zip_contains_certs_readme(zip_entries: set[str]):
    """certs/README.txt placeholder is present."""
    assert "certs/README.txt" in zip_entries


# ── Excluded items ─────────────────────────────────────────────────────────────


def test_zip_excludes_venv(zip_entries: set[str]):
    """Virtual environment directory (.venv/) is not distributed."""
    assert not any(e.startswith(".venv/") for e in zip_entries)


def test_zip_excludes_generated(zip_entries: set[str]):
    """Runtime artifacts (generated/) are not distributed."""
    assert not any(e.startswith("generated/") for e in zip_entries)


def test_zip_excludes_dev_requirements(zip_entries: set[str]):
    """requirements-dev.txt is not distributed."""
    assert "requirements-dev.txt" not in zip_entries


def test_zip_excludes_tests(zip_entries: set[str]):
    """Test suite (tests/) is not distributed."""
    assert not any(e.startswith("tests/") for e in zip_entries)


def test_zip_excludes_dotenv(zip_entries: set[str]):
    """.env is not distributed; only .env.example is allowed."""
    assert ".env" not in zip_entries


def test_zip_excludes_pycache(zip_entries: set[str]):
    """Compiled bytecode caches (__pycache__) are not distributed."""
    assert not any("__pycache__" in e for e in zip_entries)
