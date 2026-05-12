"""
DAU Excel importer.

Parses a Microsoft Forms / Teams Polls weekly export (.xlsx) and writes
individual dau_<username>_<ts>.json records into the filter's
``<dau_path>/original/<week>/`` directory.

Column detection and answer-text mapping are driven by
``config/dau_import_config.json`` so teams with different survey question
wording don't require code changes.

Merge behaviour: if a record for the same (username, week) already exists
with an equal or later timestamp the incoming row is skipped — existing data
wins.  Rows with a newer timestamp overwrite older raw files.
"""

from __future__ import annotations

import base64
import io
import json
import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parent.parent.parent / "config" / "dau_import_config.json"

# Mirrors app.core.metrics._DAU_SCORE_MAP to avoid a circular import.
_SCORE_MAP: dict[str, float] = {
    "Every day (5 days)": 5.0,
    "Most days (3\u20134 days)": 3.5,
    "Rarely (1\u20132 days)": 1.5,
    "Not used": 0.0,
}


def _load_import_config() -> dict:
    try:
        return json.loads(_CONFIG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("DAU importer: could not load import config: %s", exc)
        return {}


def _excel_serial_to_datetime(value: Any) -> datetime | None:
    """Convert an Excel date serial number or datetime/date object to a timezone-aware datetime."""
    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
    if hasattr(value, "timetuple"):
        # date object
        return datetime(value.year, value.month, value.day, tzinfo=timezone.utc)
    if isinstance(value, (int, float)):
        # Excel date serial: days since 1899-12-30
        from datetime import timedelta

        base = datetime(1899, 12, 30, tzinfo=timezone.utc)
        return base + timedelta(days=float(value))
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
            try:
                dt = datetime.strptime(value.strip(), fmt)
                return dt.replace(tzinfo=timezone.utc)
            except ValueError:
                continue
    return None


def _derive_iso_week(dt: datetime) -> str:
    iso_year, iso_week, _ = dt.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _compact_ts(dt: datetime) -> str:
    return dt.strftime("%Y%m%dT%H%M%SZ")


def _find_col(headers: list[str], pattern: str) -> int | None:
    """Return 0-based column index whose header contains *pattern* (case-insensitive)."""
    lp = pattern.lower()
    for i, h in enumerate(headers):
        if lp in str(h).lower():
            return i
    return None


def _existing_ts(week_dir: Path, username: str) -> str | None:
    """Return the latest ISO timestamp string of any existing file for (username, week_dir)."""
    pat = re.compile(rf"^dau_{re.escape(username)}_", re.IGNORECASE)
    best: str | None = None
    for fpath in week_dir.glob("dau_*.json"):
        if not pat.match(fpath.name):
            continue
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            ts = data.get("timestamp", "")
            if ts and (best is None or ts > best):
                best = ts
        except Exception:  # nosec B110
            pass
    return best


def import_dau_excel(xlsx_bytes: bytes, dau_path: str | Path, target_week: str | None = None) -> dict:
    """Parse an xlsx export and write dau JSON records into *dau_path*/original/<week>/.

    Returns ``{"imported": N, "skipped": N, "errors": [...]}``.
    """
    try:
        import openpyxl
    except ImportError:
        return {"imported": 0, "skipped": 0, "errors": ["openpyxl is not installed — run: pip install openpyxl"]}

    cfg = _load_import_config()
    col_cfg = cfg.get("column_detection", {})
    answer_map: dict[str, str] = {k.lower(): v for k, v in cfg.get("answer_mapping", {}).items()}

    email_pat = col_cfg.get("email_header_contains", "email")
    usage_pat = col_cfg.get("usage_header_contains", "how often")
    time_pat = col_cfg.get("start_time_header_contains", "start time")

    try:
        wb = openpyxl.load_workbook(io.BytesIO(xlsx_bytes), data_only=True)
    except Exception as exc:
        return {"imported": 0, "skipped": 0, "errors": [f"Cannot open workbook: {exc}"]}

    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    if not rows:
        wb.close()
        return {"imported": 0, "skipped": 0, "errors": ["Workbook has no rows"]}

    # Detect header row (first non-empty row)
    headers = [str(c) if c is not None else "" for c in rows[0]]
    email_col = _find_col(headers, email_pat)
    usage_col = _find_col(headers, usage_pat)
    time_col = _find_col(headers, time_pat)

    missing = []
    if email_col is None:
        missing.append(f"email column (looking for header containing '{email_pat}')")
    if usage_col is None:
        missing.append(f"usage column (looking for header containing '{usage_pat}')")
    if time_col is None:
        missing.append(f"start-time column (looking for header containing '{time_pat}')")
    if missing:
        wb.close()
        return {"imported": 0, "skipped": 0, "errors": [f"Could not detect columns: {'; '.join(missing)}"]}

    root_path = Path(dau_path).resolve()

    roster: dict[str, str] = {}
    roster_path = root_path / "team_roster.json"
    try:
        if roster_path.is_file():
            data = json.loads(roster_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                roster = data
    except Exception as exc:
        logger.warning("DAU importer: could not load team_roster.json: %s", exc)

    imported = 0
    skipped = 0
    errors: list[str] = []

    for row_idx, row in enumerate(rows[1:], start=2):

        def _cell(col: int) -> Any:
            return row[col] if col < len(row) else None

        raw_email = _cell(email_col)  # type: ignore[arg-type]
        raw_usage = _cell(usage_col)  # type: ignore[arg-type]
        raw_time = _cell(time_col)  # type: ignore[arg-type]

        if not raw_email:
            skipped += 1
            continue

        email_str = str(raw_email).strip()
        username = email_str.split("@")[0] if "@" in email_str else email_str
        if not username:
            errors.append(f"Row {row_idx}: empty username derived from '{email_str}'")
            skipped += 1
            continue

        usage_key = str(raw_usage).strip().lower() if raw_usage else ""
        usage = answer_map.get(usage_key)
        if usage is None:
            errors.append(f"Row {row_idx}: unrecognised answer '{raw_usage}' for user '{username}' — skipped")
            skipped += 1
            continue

        score = _SCORE_MAP.get(usage, 0.0)

        dt = _excel_serial_to_datetime(raw_time)
        if dt is None:
            errors.append(f"Row {row_idx}: cannot parse timestamp '{raw_time}' for user '{username}' — skipped")
            skipped += 1
            continue

        iso_ts = dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        week = target_week if target_week else _derive_iso_week(dt)

        week_dir = root_path / "original" / week
        week_dir.mkdir(parents=True, exist_ok=True)

        existing = _existing_ts(week_dir, username)
        if existing is not None and existing >= iso_ts:
            skipped += 1
            continue

        record: dict = {
            "username": username,
            "role": roster.get(username, ""),
            "usage": usage,
            "score": score,
            "timestamp": iso_ts,
            "week": week,
        }

        filename = f"dau_{username}_{_compact_ts(dt)}.json"
        try:
            (week_dir / filename).write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")
            imported += 1
        except OSError as exc:
            errors.append(f"Row {row_idx}: could not write file for '{username}': {exc}")
            skipped += 1

    wb.close()
    logger.info("DAU import: %d imported, %d skipped, %d errors", imported, skipped, len(errors))
    return {"imported": imported, "skipped": skipped, "errors": errors}


def import_dau_excel_b64(data_b64: str, dau_path: str | Path, target_week: str | None = None) -> dict:
    """Decode a base64-encoded xlsx and delegate to :func:`import_dau_excel`."""
    try:
        xlsx_bytes = base64.b64decode(data_b64)
    except Exception as exc:
        return {"imported": 0, "skipped": 0, "errors": [f"Invalid base64 data: {exc}"]}
    return import_dau_excel(xlsx_bytes, dau_path, target_week=target_week)
