"""Unit tests: app.__version__ resolution."""

from __future__ import annotations

import re
import sys
from importlib.metadata import PackageNotFoundError
from pathlib import Path
from unittest.mock import patch

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.smoke]

_SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+")


def test_version_is_not_unknown():
    import app

    assert app.__version__ != "0.0.0+unknown", (
        "app.__version__ resolved to '0.0.0+unknown' — "
        "pyproject.toml is missing or unreadable in the current environment"
    )


def test_version_matches_semver():
    import app

    assert _SEMVER_RE.match(app.__version__), f"app.__version__ '{app.__version__}' does not match semver (X.Y.Z)"


def test_version_matches_pyproject_toml():
    toml_path = Path(__file__).parent.parent.parent / "pyproject.toml"
    match = re.search(r'^version\s*=\s*"([^"]+)"', toml_path.read_text(encoding="utf-8"), re.MULTILINE)
    assert match, "Could not find version in pyproject.toml"
    import app

    assert app.__version__ == match.group(1)


def test_pyproject_toml_fallback_uses_file_relative_path():
    """Fallback reads pyproject.toml via __file__-relative path, not CWD."""
    # Remove cached module so __init__ re-runs
    sys.modules.pop("app", None)

    with patch("importlib.metadata.version", side_effect=PackageNotFoundError):
        import app as fresh_app

        assert _SEMVER_RE.match(fresh_app.__version__), (
            f"pyproject.toml fallback produced '{fresh_app.__version__}' — path resolution may still be CWD-relative"
        )

    # Restore cached module for subsequent tests
    sys.modules.pop("app", None)
    import app  # noqa: F401 — re-prime cache
