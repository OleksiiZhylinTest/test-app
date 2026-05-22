"""User data directory: %LOCALAPPDATA%\\AIMetrics on Windows, ~/AIMetrics elsewhere."""

import os
from pathlib import Path

_APP_NAME = "AIMetrics"


def user_data_dir() -> Path:
    base = os.environ.get("LOCALAPPDATA") or os.path.expanduser("~")
    return Path(base) / _APP_NAME


def ensure_user_data_dirs() -> None:
    root = user_data_dir()
    for sub in ("certs", "config", "data/dau", "reports", "logs"):
        (root / sub).mkdir(parents=True, exist_ok=True)
