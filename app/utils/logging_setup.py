"""Centralized logging configuration for the application.

Call setup_logging() once at the top of each entry point (main.py, server.py).
Every run writes a timestamped log file to generated/logs/app-YYYYMMDD-HHMMSS.log
and mirrors output to stdout.

Custom level SUCCESS (25) sits between INFO (20) and WARNING (30).
Usage: logging.getLogger(__name__).success("message")

Root logger level is read from the LOG_LEVEL env var (resolved from
config/defaults.env or .env, see app.core.config for the loading pattern).
Accepted values: DEBUG, INFO, SUCCESS, WARNING, ERROR, CRITICAL.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

from dotenv import dotenv_values as _dotenv_values

from app.core.user_data import user_data_dir as _udd

# ---------------------------------------------------------------------------
# Custom SUCCESS level
# ---------------------------------------------------------------------------

SUCCESS_LEVEL = 25
logging.addLevelName(SUCCESS_LEVEL, "SUCCESS")


def _success(self: logging.Logger, message: str, *args: object, **kwargs: object) -> None:
    if self.isEnabledFor(SUCCESS_LEVEL):
        self._log(SUCCESS_LEVEL, message, args, **kwargs)  # type: ignore[arg-type]


logging.Logger.success = _success  # type: ignore[attr-defined]

# ---------------------------------------------------------------------------
# Env loading (defaults.env then user_data_dir .env; never override values already set)
# ---------------------------------------------------------------------------

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULTS_PATH = _PROJECT_ROOT / "config" / "defaults.env"

# When running under the test profile, default to DEBUG before defaults.env injects INFO.
# An explicit LOG_LEVEL in the caller's environment (e.g. CI) still takes precedence.
if os.environ.get("APP_PROFILE", "").strip().lower() == "test" and "LOG_LEVEL" not in os.environ:
    os.environ["LOG_LEVEL"] = "DEBUG"

for _k, _v in {
    **_dotenv_values(_DEFAULTS_PATH),
    **_dotenv_values(_udd() / ".env"),
}.items():
    if _k not in os.environ and _v is not None:
        os.environ[_k] = _v

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

_LOG_DIR = _udd() / "logs"

_LEVELS: dict[str, int] = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "SUCCESS": SUCCESS_LEVEL,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def _resolve_log_level() -> int:
    name = (os.getenv("LOG_LEVEL", "") or "").strip().upper()
    return _LEVELS.get(name, logging.DEBUG)


def setup_logging() -> tuple[logging.Logger, Path]:
    """Configure the root logger with a file handler and a stream handler.

    Creates generated/logs/ if it does not exist.
    Returns (root_logger, log_file_path).
    """
    _LOG_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    log_file = _LOG_DIR / f"app-{timestamp}.log"

    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(_resolve_log_level())
    root.addHandler(file_handler)
    root.addHandler(stream_handler)

    return root, log_file
