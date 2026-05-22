"""First-run migration: copy user data from the app folder to user_data_dir."""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path

from app.core.user_data import user_data_dir

logger = logging.getLogger(__name__)

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


def _copy_if_missing(src: Path, dst: Path) -> bool:
    """Copy src to dst only when dst does not yet exist. Returns True if copied."""
    if not src.exists() or dst.exists():
        return False
    try:
        dst.parent.mkdir(parents=True, exist_ok=True)
        if src.is_dir():
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        logger.info("Migrated %s → %s", src, dst)
        return True
    except OSError as exc:
        logger.warning("Could not migrate %s: %s", src, exc)
        return False


def _update_dau_paths(filters_path: Path) -> None:
    """Convert relative DAU_PATH values to absolute paths under user_data_dir."""
    try:
        filters = json.loads(filters_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return
    udd = user_data_dir()
    changed = False
    for f in filters:
        params = f.get("params") or {}
        raw = (params.get("DAU_PATH") or "").strip()
        if raw and not Path(raw).is_absolute():
            params["DAU_PATH"] = str(udd / raw)
            changed = True
    if changed:
        try:
            filters_path.write_text(json.dumps(filters, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            logger.info("Updated DAU_PATH entries in %s to absolute paths", filters_path)
        except OSError as exc:
            logger.warning("Could not update DAU_PATH in %s: %s", filters_path, exc)


def run_first_time_migration() -> None:
    """Copy user-owned data from the app folder to user_data_dir on first run.

    Skipped on subsequent runs via a sentinel file. Non-fatal: failures are logged
    as warnings and the app continues with whatever data is available.
    """
    udd = user_data_dir()
    sentinel = udd / ".migrated"
    if sentinel.is_file():
        return

    root = _PROJECT_ROOT
    _copy_if_missing(root / ".env", udd / ".env")
    _copy_if_missing(root / "certs" / "jira_ca_bundle.pem", udd / "certs" / "jira_ca_bundle.pem")
    _copy_if_missing(root / "config" / "jira_filters.json", udd / "config" / "jira_filters.json")
    _copy_if_missing(root / "config" / "jira_schema.json", udd / "config" / "jira_schema.json")

    _copy_if_missing(root / "generated" / "reports", udd / "reports")
    _copy_if_missing(root / "generated" / "logs", udd / "logs")

    migrated_filters = udd / "config" / "jira_filters.json"
    if migrated_filters.is_file():
        _update_dau_paths(migrated_filters)

    try:
        sentinel.write_text("", encoding="utf-8")
        logger.info("First-run migration complete. User data is now at %s", udd)
    except OSError as exc:
        logger.warning("Could not write migration sentinel: %s", exc)
