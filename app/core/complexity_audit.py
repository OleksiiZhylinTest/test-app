"""Scoring engine and recommendation derivation for structural complexity audit."""

from __future__ import annotations

import ast
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_EXCLUDED_DIRS = {"venv", ".venv", "generated", "__pycache__", ".git"}

_DIMENSION_WEIGHTS: dict[str, float] = {
    "cc_score": 0.3,
    "loc_score": 0.3,
    "coupling_score": 0.2,
    "cohesion_score": 0.2,
}


def discover_modules(root: Path) -> list[Path]:
    """Return all .py files under root, excluding _EXCLUDED_DIRS path components."""
    result = []
    for path in sorted(root.rglob("*.py")):
        if not any(part in _EXCLUDED_DIRS for part in path.parts):
            result.append(path)
    return result


def score_module_source(path: Path, source: str) -> dict[str, Any]:
    """Pure scoring function — accepts pre-read source string. No filesystem access."""
    from app.core import config as _cfg

    try:
        from radon.complexity import cc_visit
        from radon.metrics import mi_visit
        from radon.raw import analyze

        cc_results = cc_visit(source)
        if cc_results:
            avg_cc = sum(r.complexity for r in cc_results) / len(cc_results)
        else:
            avg_cc = 1.0
        cc_score = min(avg_cc / 10.0, 10.0)

        loc = analyze(source).loc
        loc_score = min(loc / 300.0, 10.0)

        try:
            mi = mi_visit(source, multi=True)
        except Exception:
            mi = None

        tree = ast.parse(source)
        imported_modules: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imported_modules.add(alias.name.split(".")[0])
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imported_modules.add(node.module.split(".")[0])
        coupling_score = min(len(imported_modules) / 20.0, 10.0)

        top_level_symbols: list[str] = []
        for node in tree.body:
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                top_level_symbols.append(node.name)
        function_count = len(top_level_symbols)
        cohesion_score = min(function_count / 20.0, 10.0)

        composite_score = (
            _DIMENSION_WEIGHTS["cc_score"] * cc_score
            + _DIMENSION_WEIGHTS["loc_score"] * loc_score
            + _DIMENSION_WEIGHTS["coupling_score"] * coupling_score
            + _DIMENSION_WEIGHTS["cohesion_score"] * cohesion_score
        )

        if composite_score >= _cfg.COMPLEXITY_HIGH_THRESHOLD:
            classification = "High"
        elif composite_score >= _cfg.COMPLEXITY_MEDIUM_THRESHOLD:
            classification = "Medium"
        else:
            classification = "Low"

        return {
            "module": path.as_posix(),
            "loc": loc,
            "function_count": function_count,
            "cc_score": round(cc_score, 2),
            "loc_score": round(loc_score, 2),
            "coupling_score": round(coupling_score, 2),
            "cohesion_score": round(cohesion_score, 2),
            "composite_score": round(composite_score, 2),
            "classification": classification,
            "mi": round(mi, 1) if mi is not None else None,
            "error": None,
            "_imported_modules": sorted(imported_modules),
        }

    except Exception as exc:
        logger.warning("Could not score %s: %s", path, exc)
        return {
            "module": path.as_posix(),
            "loc": None,
            "function_count": None,
            "cc_score": None,
            "loc_score": None,
            "coupling_score": None,
            "cohesion_score": None,
            "composite_score": None,
            "classification": "Error",
            "mi": None,
            "error": str(exc),
            "_imported_modules": [],
        }


_ACTION_TEMPLATES: dict[str, str] = {
    "cc": "Reduce cyclomatic complexity in {module}: extract conditional branches into named functions",
    "loc": "Split {module} ({loc} LOC): separate concerns into two or more focused modules",
    "coupling": "Reduce import coupling in {module}: inject {top_import} as a parameter rather than importing directly",
    "cohesion": (
        "Reduce scope of {module}: it defines {function_count} top-level symbols"
        " — extract unrelated groups into dedicated modules"
    ),
}


def _make_recommendation(score: dict[str, Any], dimension: str) -> dict[str, Any]:
    template = _ACTION_TEMPLATES[dimension]
    top_import = (score["_imported_modules"] or ["(unknown)"])[0]
    action = template.format(
        module=score["module"],
        loc=score["loc"],
        function_count=score["function_count"],
        top_import=top_import,
    )
    dim_key = "cc_score" if dimension == "cc" else f"{dimension}_score"
    return {
        "module": score["module"],
        "dimension": dimension,
        "action": action,
        "score": score[dim_key],
    }


def _generate_recommendations(score: dict[str, Any]) -> list[dict[str, Any]]:
    if score["classification"] == "Error":
        return []
    recs = []
    dim_map = {"cc": "cc_score", "loc": "loc_score", "coupling": "coupling_score", "cohesion": "cohesion_score"}
    if score["classification"] == "High":
        triggered = [d for d, k in dim_map.items() if (score[k] or 0) >= 5.0]
        if not triggered:
            triggered = [max(dim_map, key=lambda d: score[dim_map[d]] or 0)]
        for dim in triggered:
            recs.append(_make_recommendation(score, dim))
    elif score["classification"] == "Medium":
        best_dim = max(dim_map, key=lambda d: score[dim_map[d]] or 0)
        recs.append(_make_recommendation(score, best_dim))
    return recs


def build_complexity_report(root: Path) -> dict[str, Any]:
    """Discover all modules under root, score them, and return a ComplexityReport dict."""
    paths = discover_modules(root)
    scores: list[dict[str, Any]] = []
    for path in paths:
        try:
            source = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            scores.append(
                {
                    "module": path.as_posix(),
                    "loc": None,
                    "function_count": None,
                    "cc_score": None,
                    "loc_score": None,
                    "coupling_score": None,
                    "cohesion_score": None,
                    "composite_score": None,
                    "classification": "Error",
                    "mi": None,
                    "error": str(exc),
                    "_imported_modules": [],
                }
            )
            continue
        scores.append(score_module_source(path, source))

    root_posix = root.resolve().as_posix()
    for s in scores:
        mod = s["module"]
        if mod.startswith(root_posix + "/"):
            s["module"] = mod[len(root_posix) + 1 :]

    _order = {"High": 0, "Medium": 1, "Low": 2, "Error": 3}
    scores.sort(key=lambda s: (_order.get(s["classification"], 4), -(s["composite_score"] or 0)))

    recommendations: list[dict[str, Any]] = []
    for s in scores:
        recommendations.extend(_generate_recommendations(s))

    for s in scores:
        s.pop("_imported_modules", None)

    summary = {
        "high_count": sum(1 for s in scores if s["classification"] == "High"),
        "medium_count": sum(1 for s in scores if s["classification"] == "Medium"),
        "low_count": sum(1 for s in scores if s["classification"] == "Low"),
        "error_count": sum(1 for s in scores if s["classification"] == "Error"),
    }

    return {
        "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "discovery_root": root.resolve().as_posix(),
        "module_count": len(scores),
        "scores": scores,
        "recommendations": recommendations,
        "summary": summary,
    }
