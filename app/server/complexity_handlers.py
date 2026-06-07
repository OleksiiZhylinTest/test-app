"""Handler mixin for GET /api/complexity/audit."""

from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ComplexityHandlerMixin:
    def _handle_complexity_audit(self) -> None:
        from app.core.complexity_audit import build_complexity_report

        root = Path(__file__).resolve().parent.parent.parent
        try:
            report = build_complexity_report(root)
        except Exception as exc:
            logger.error("Complexity audit failed: %s", exc)
            self._send_json(500, {"error": str(exc)})
            return

        recs_by_module: dict[str, list[str]] = {}
        for rec in report["recommendations"]:
            recs_by_module.setdefault(rec["module"], []).append(rec["action"])

        scores = []
        for s in report["scores"]:
            scores.append(
                {
                    "module": s["module"],
                    "loc": s["loc"],
                    "function_count": s["function_count"],
                    "coupling": s["coupling_score"],
                    "cohesion": s["cohesion_score"],
                    "composite_score": s["composite_score"],
                    "classification": s["classification"],
                    "recommendations": recs_by_module.get(s["module"], []),
                }
            )

        self._send_json(
            200,
            {
                "generated_at": report["generated_at"],
                "summary": report["summary"],
                "scores": scores,
            },
        )
