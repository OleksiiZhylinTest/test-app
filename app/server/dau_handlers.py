"""DAU data CRUD and Excel import handler mixin — /api/dau/*."""

from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from urllib.parse import unquote as urlunquote

from ._base import _root

logger = logging.getLogger(__name__)

# Mirrors app.core.metrics._DAU_SCORE_MAP to avoid a circular import.
_SCORE_MAP: dict[str, float] = {
    "Every day (5 days)": 5.0,
    "Most days (3\u20134 days)": 3.5,
    "Rarely (1\u20132 days)": 1.5,
    "Not used": 0.0,
}

_VALID_ROLES = {"Developer", "QA / Test Engineer", "Business Analyst", "Delivery Manager / Lead", "Other", ""}
_VALID_USAGES = set(_SCORE_MAP.keys())


class DauHandlerMixin:
    # ── helpers ──────────────────────────────────────────────────────────────

    def _dau_resolve_path(self, filter_slug: str) -> Path | None:
        """Return the absolute dau_path for *filter_slug*, or None if not found."""
        if not filter_slug:
            return None
        filters = self._load_filters()
        for entry in filters:
            if entry.get("slug") == filter_slug:
                dau_path = (entry.get("params") or {}).get("DAU_PATH", "").strip()
                if dau_path:
                    return (_root() / dau_path).resolve()
        return None

    @staticmethod
    def _overrides_path(dau_path: Path) -> Path:
        return dau_path / "manual_overrides.json"

    def _load_overrides(self, dau_path: Path) -> list[dict]:
        path = self._overrides_path(dau_path)
        if not path.is_file():
            return []
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except Exception as exc:
            logger.warning("DAU handler: could not read manual_overrides.json: %s", exc)
            return []

    def _save_overrides(self, dau_path: Path, overrides: list[dict]) -> None:
        path = self._overrides_path(dau_path)
        path.write_text(json.dumps(overrides, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    def _dau_filter_slug(self) -> str:
        qs = parse_qs(urlparse(self.path).query)
        return urlunquote((qs.get("filter") or [""])[0]).strip()

    # ── GET /api/dau/records ─────────────────────────────────────────────────

    def _handle_dau_records_get(self) -> None:
        slug = self._dau_filter_slug()
        dau_path = self._dau_resolve_path(slug)
        if dau_path is None:
            self._send_json(400, {"ok": False, "error": "Unknown or missing filter slug"})
            return

        try:
            from app.core.dau_normalizer import get_dau_records

            records = get_dau_records(dau_path)
        except Exception as exc:
            logger.error("DAU records get failed: %s", exc)
            self._send_json(500, {"ok": False, "error": str(exc)})
            return

        self._send_json(200, {"ok": True, "records": records})

    # ── POST /api/dau/records ────────────────────────────────────────────────

    def _handle_dau_records_post(self) -> None:
        slug = self._dau_filter_slug()
        dau_path = self._dau_resolve_path(slug)
        if dau_path is None:
            self._send_json(400, {"ok": False, "error": "Unknown or missing filter slug"})
            return

        body = self._read_json_body()
        if body is None:
            self._send_json(400, {"ok": False, "error": "Invalid JSON body"})
            return

        username = (body.get("username") or "").strip()
        week = (body.get("week") or "").strip()
        if not username or not week:
            self._send_json(400, {"ok": False, "error": "username and week are required"})
            return

        usage = (body.get("usage") or "").strip()
        if usage and usage not in _VALID_USAGES:
            self._send_json(400, {"ok": False, "error": f"Invalid usage value: {usage!r}"})
            return

        role = (body.get("role") or "").strip()
        if role and role not in _VALID_ROLES:
            self._send_json(400, {"ok": False, "error": f"Invalid role value: {role!r}"})
            return

        score = _SCORE_MAP.get(usage, 0.0) if usage else body.get("score", 0.0)

        orig_username = (body.get("orig_username") or "").strip()
        orig_week = (body.get("orig_week") or "").strip()
        is_move = bool(orig_username and orig_week and (orig_username != username or orig_week != week))

        from datetime import datetime, timezone

        now_ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
        record = {
            "username": username,
            "week": week,
            "role": role,
            "usage": usage,
            "score": score,
            "timestamp": body.get("timestamp") or now_ts,
        }

        overrides = self._load_overrides(dau_path)

        if is_move:
            old_week_dir = dau_path / "original" / orig_week
            if old_week_dir.is_dir():
                pat = re.compile(rf"^dau_{re.escape(orig_username)}_", re.IGNORECASE)
                for f in old_week_dir.glob("dau_*.json"):
                    if pat.match(f.name):
                        f.unlink(missing_ok=True)
            overrides = [
                ov for ov in overrides if not (ov.get("username") == orig_username and ov.get("week") == orig_week)
            ]

        overrides = [ov for ov in overrides if not (ov.get("username") == username and ov.get("week") == week)]
        overrides.append(record)

        try:
            self._save_overrides(dau_path, overrides)
        except OSError as exc:
            self._send_json(500, {"ok": False, "error": f"Could not save override: {exc}"})
            return

        self._send_json(200, {"ok": True, "record": record})

    # ── DELETE /api/dau/records ──────────────────────────────────────────────

    def _handle_dau_records_delete(self) -> None:
        qs = parse_qs(urlparse(self.path).query)
        slug = urlunquote((qs.get("filter") or [""])[0]).strip()
        username = urlunquote((qs.get("username") or [""])[0]).strip()
        week = urlunquote((qs.get("week") or [""])[0]).strip()

        dau_path = self._dau_resolve_path(slug)
        if dau_path is None:
            self._send_json(400, {"ok": False, "error": "Unknown or missing filter slug"})
            return
        if not username or not week:
            self._send_json(400, {"ok": False, "error": "username and week query params are required"})
            return

        week_dir = dau_path / "original" / week
        if week_dir.is_dir():
            pat = re.compile(rf"^dau_{re.escape(username)}_", re.IGNORECASE)
            for f in week_dir.glob("dau_*.json"):
                if pat.match(f.name):
                    f.unlink(missing_ok=True)

        overrides = self._load_overrides(dau_path)
        overrides = [ov for ov in overrides if not (ov.get("username") == username and ov.get("week") == week)]

        try:
            self._save_overrides(dau_path, overrides)
        except OSError as exc:
            self._send_json(500, {"ok": False, "error": f"Could not save override: {exc}"})
            return

        self._send_json(200, {"ok": True})

    # ── POST /api/dau/import ─────────────────────────────────────────────────

    def _handle_dau_import(self) -> None:
        slug = self._dau_filter_slug()
        dau_path = self._dau_resolve_path(slug)
        if dau_path is None:
            self._send_json(400, {"ok": False, "error": "Unknown or missing filter slug"})
            return

        body = self._read_json_body()
        if body is None:
            self._send_json(400, {"ok": False, "error": "Invalid JSON body"})
            return

        data_b64 = (body.get("data_b64") or "").strip()
        if not data_b64:
            self._send_json(400, {"ok": False, "error": "data_b64 field is required"})
            return

        target_week = (body.get("target_week") or "").strip() or None

        try:
            from app.core.dau_importer import import_dau_excel_b64

            result = import_dau_excel_b64(data_b64, dau_path, target_week=target_week)
        except Exception as exc:
            logger.error("DAU import failed: %s", exc)
            self._send_json(500, {"ok": False, "error": str(exc)})
            return

        self._send_json(200, {"ok": True, **result})
