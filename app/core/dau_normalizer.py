"""
DAU response normalizer.

Reads raw survey JSON files from a source directory (recursively), enriches each
record with the ISO ``week`` field (derived from ``timestamp`` when absent),
deduplicates to one record per ``(username, week)`` keeping the latest submission,
and writes the clean set to a normalized output directory that mirrors the source
folder structure.

Called automatically by ``app/cli.py`` before metric computation so that both
``compute_dau_metrics`` and ``compute_dau_trend`` always work from consistent data.

Manual overrides are stored in ``<dau_path>/manual_overrides.json`` as a JSON
array.  Each entry is either a deletion marker
``{"deleted": true, "username": "...", "week": "..."}`` or a full record that
replaces/adds the matching ``(username, week)`` pair.  Overrides are applied
after deduplication so manual edits always take precedence over raw imports.
"""

from __future__ import annotations

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

logger = logging.getLogger(__name__)


def _derive_iso_week(iso_ts: str) -> str:
    """Return ISO week string (e.g. ``'2026-W15'``) from an ISO 8601 timestamp."""
    dt = datetime.fromisoformat(iso_ts).astimezone(timezone.utc)
    iso_year, iso_week, _ = dt.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _compact_timestamp(iso_ts: str) -> str:
    """Convert ``'2026-03-30T05:47:29+00:00'`` → ``'20260330T054729Z'`` for filenames."""
    dt = datetime.fromisoformat(iso_ts).astimezone(timezone.utc)
    return dt.strftime("%Y%m%dT%H%M%SZ")


def _load_raw_records(raw_dir: Path) -> list[dict]:
    """Load and enrich all ``dau_*.json`` files from *raw_dir* recursively."""
    records: list[dict] = []
    for fpath in sorted(raw_dir.rglob("dau_*.json")):
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("expected a JSON object")
        except Exception as exc:
            logger.warning("DAU normaliser: skipping malformed file %s — %s", fpath.name, exc)
            continue
        if not data.get("week"):
            try:
                data["week"] = _derive_iso_week(data["timestamp"])
            except Exception as exc:
                logger.warning(
                    "DAU normaliser: cannot derive week for record (username=%s): %s",
                    data.get("username"),
                    exc,
                )
        records.append(data)
    return records


def _dedup(records: list[dict]) -> dict[tuple[str, str], dict]:
    """Return a dict keyed by (username, week) keeping the latest-timestamp record."""
    best: dict[tuple[str, str], dict] = {}
    for rec in records:
        key = (rec.get("username", ""), rec.get("week", ""))
        existing = best.get(key)
        if existing is None or rec.get("timestamp", "") > existing.get("timestamp", ""):
            best[key] = rec
    return best


def _load_overrides(dau_path: Path) -> list[dict]:
    """Load ``<dau_path>/manual_overrides.json``, returning [] if absent or invalid."""
    path = dau_path / "manual_overrides.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return data
    except Exception as exc:
        logger.warning("DAU normaliser: could not load manual_overrides.json: %s", exc)
    return []


def _apply_overrides(best: dict[tuple[str, str], dict], overrides: list[dict]) -> dict[tuple[str, str], dict]:
    """Apply manual override list to the deduplicated record map (in-place, returns same dict)."""
    for ov in overrides:
        username = ov.get("username", "")
        week = ov.get("week", "")
        key = (username, week)
        if not username or not week:
            continue
        if ov.get("deleted"):
            best.pop(key, None)
        else:
            best[key] = ov
    return best


def _normalize_dir(files: list[Path], out_dir: Path) -> tuple[int, int]:
    """Enrich, deduplicate, and write records from *files* into *out_dir*.

    Returns ``(records_written, raw_files_read)``.
    """
    records: list[dict] = []
    for fpath in files:
        try:
            data = json.loads(fpath.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("expected a JSON object")
            records.append(data)
        except Exception as exc:  # nosec B112
            logger.warning("DAU normaliser: skipping malformed file %s — %s", fpath.name, exc)

    for rec in records:
        if not rec.get("week"):
            try:
                rec["week"] = _derive_iso_week(rec["timestamp"])
            except Exception as exc:
                logger.warning(
                    "DAU normaliser: cannot derive week for record (username=%s): %s",
                    rec.get("username"),
                    exc,
                )

    best: dict[tuple[str, str], dict] = {}
    for rec in records:
        key = (rec.get("username", ""), rec.get("week", ""))
        existing = best.get(key)
        if existing is None or rec.get("timestamp", "") > existing.get("timestamp", ""):
            best[key] = rec

    for rec in best.values():
        try:
            filename = f"dau_{rec['username']}_{_compact_timestamp(rec['timestamp'])}.json"
        except Exception:
            filename = f"dau_{rec.get('username', 'unknown')}_{rec.get('week', 'unknown')}.json"
        (out_dir / filename).write_text(
            json.dumps(rec, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    return len(best), len(records)


def normalize_dau_responses(raw_dir: str | Path, normalized_dir: str | Path) -> int:
    """Enrich, deduplicate, and write DAU survey responses to *normalized_dir*.

    Walks *raw_dir* recursively. For each subdirectory that contains ``dau_*.json``
    files, a matching subdirectory is created under *normalized_dir* and the records
    from that directory are processed independently (enriched, deduplicated, written).

    After per-directory normalization, ``manual_overrides.json`` from the parent of
    *raw_dir* is applied: deletion markers remove records, other overrides add or
    replace records in ``normalized/manual/``.

    Steps:
    1. Create *normalized_dir* if it does not exist.
    2. Remove any existing ``dau_*.json`` files from *normalized_dir* recursively (prevent stale data).
    3. Discover all ``dau_*.json`` files under *raw_dir* at any nesting level.
    4. Group files by their parent directory relative to *raw_dir*.
    5. For each group: enrich, deduplicate, and write to the mirrored output subdirectory.
    6. Apply manual_overrides.json from parent of *raw_dir*.

    Returns the total number of records written across all subdirectories.
    """
    raw_path = Path(raw_dir)
    norm_path = Path(normalized_dir)
    dau_path = raw_path.parent

    if norm_path.exists():
        shutil.rmtree(norm_path)
    norm_path.mkdir(parents=True, exist_ok=True)

    by_rel_dir: dict[Path, list[Path]] = {}
    for fpath in sorted(raw_path.rglob("dau_*.json")):
        rel_dir = fpath.parent.relative_to(raw_path)
        by_rel_dir.setdefault(rel_dir, []).append(fpath)

    total_written = 0
    total_raw = 0
    for rel_dir, files in sorted(by_rel_dir.items()):
        out_dir = norm_path / rel_dir
        out_dir.mkdir(parents=True, exist_ok=True)
        written, raw_count = _normalize_dir(files, out_dir)
        total_written += written
        total_raw += raw_count

    # Apply manual overrides: load all current normalized records, apply, rewrite
    overrides = _load_overrides(dau_path)
    if overrides:
        all_norm: list[dict] = []
        for fpath in sorted(norm_path.rglob("dau_*.json")):
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    all_norm.append(data)
            except Exception:  # nosec B110
                pass

        best = _dedup(all_norm)
        before = len(best)
        _apply_overrides(best, overrides)
        after = len(best)

        # Remove all existing normalized files and rewrite from merged best
        for fpath in norm_path.rglob("dau_*.json"):
            fpath.unlink(missing_ok=True)

        for rec in best.values():
            week = rec.get("week", "unknown")
            out_dir = norm_path / week
            out_dir.mkdir(parents=True, exist_ok=True)
            try:
                filename = f"dau_{rec['username']}_{_compact_timestamp(rec['timestamp'])}.json"
            except Exception:
                filename = f"dau_{rec.get('username', 'unknown')}_{rec.get('week', 'unknown')}.json"
            (out_dir / filename).write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")

        total_written = after
        logger.info(
            "DAU overrides applied: %d record(s) before → %d after (%+d from overrides)",
            before,
            after,
            after - before,
        )

    logger.info(
        "DAU normalisation: %d raw file(s) → %d record(s) written to %s",
        total_raw,
        total_written,
        norm_path,
    )
    return total_written


def get_dau_records(dau_path: str | Path) -> list[dict]:
    """Return the current deduplicated DAU records for a filter without writing to disk.

    Reads from ``<dau_path>/original/``, deduplicates globally by (username, week),
    then applies ``<dau_path>/manual_overrides.json`` (deletions and upserts).

    Returns records sorted by (week, username).
    """
    root = Path(dau_path)
    raw_dir = root / "original"

    if not raw_dir.is_dir():
        return []

    records = _load_raw_records(raw_dir)
    best = _dedup(records)
    overrides = _load_overrides(root)
    if overrides:
        _apply_overrides(best, overrides)

    return sorted(best.values(), key=lambda r: (r.get("week", ""), r.get("username", "")))
