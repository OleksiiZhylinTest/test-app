# Data Model: Solution Architect Design Complexity Audit

**Spec**: `specs/002-design-complexity-audit/spec.md`

All entities are plain Python `dict` types, consistent with the existing codebase convention (see `app/core/metrics.py`). No dataclasses.

---

## ComplexityScore

A record for one Python module.

```python
ComplexityScore = {
    "module": str,          # repo-relative path, e.g. "app/core/metrics.py"
    "loc": int,             # raw lines of code (radon)
    "function_count": int,  # top-level FunctionDef + AsyncFunctionDef + ClassDef count (ast)
    "cc_score": float,      # average cyclomatic complexity normalised 0–10 (radon)
    "loc_score": float,     # LOC normalised 0–10
    "coupling_score": float,# unique imported module names normalised 0–10 (ast)
    "cohesion_score": float,# top-level exported symbol count normalised 0–10 (ast)
    "composite_score": float,  # weighted average: 0.3*cc + 0.3*loc + 0.2*coupling + 0.2*cohesion
    "classification": str,  # "Low" | "Medium" | "High" | "Error"
    "mi": float | None,     # maintainability index 0–100, informational only (radon); None on parse error
    "error": str | None,    # exception message if module could not be parsed; None otherwise
}
```

**Invariants**:
- When `error` is not `None`, all `*_score` fields are `None` and `classification` is `"Error"`.
- `composite_score` is `None` when `error` is not `None`.
- `module` is always a POSIX-style path relative to the discovery root (forward slashes).

---

## ImprovementRecommendation

One actionable suggestion for a specific module and scoring dimension.

```python
ImprovementRecommendation = {
    "module": str,      # matches ComplexityScore.module
    "dimension": str,   # "cc" | "loc" | "coupling" | "cohesion"
    "action": str,      # human-readable, specific, actionable text
    "score": float,     # the dimension score that triggered this recommendation
}
```

---

## ComplexityReport

The aggregate output of one audit run. Returned by `build_complexity_report()`, consumed by reporters and the HTTP handler.

```python
ComplexityReport = {
    "generated_at": str,            # ISO-8601 UTC timestamp, e.g. "2026-06-06T14:23:01Z"
    "discovery_root": str,          # repo-relative root scanned, e.g. "." or "app/"
    "module_count": int,            # total .py files discovered (includes error modules)
    "scores": list[ComplexityScore],              # sorted descending by composite_score (errors last)
    "recommendations": list[ImprovementRecommendation],  # all recommendations, High-module recs first
    "summary": {
        "high_count": int,
        "medium_count": int,
        "low_count": int,
        "error_count": int,
    },
}
```

**Invariants**:
- `len(scores) == module_count`
- `summary.high_count + summary.medium_count + summary.low_count + summary.error_count == module_count`
- `scores` is sorted: `High` modules first (descending `composite_score`), then `Medium`, then `Low`, then `Error`.

---

## HTTP API Response Shape

`GET /api/complexity/audit` returns a **different** (flatter) shape to match spec FR-6 acceptance criteria. The handler in `complexity_handlers.py` performs the explicit mapping:

```python
# HTTP response — recommendations joined per module
{
    "generated_at": str,
    "summary": { "high_count": int, "medium_count": int, "low_count": int, "error_count": int },
    "scores": [
        {
            "module": str,
            "loc": int,
            "function_count": int,
            "coupling": float,      # renamed from coupling_score for API consumers
            "cohesion": float,      # renamed from cohesion_score for API consumers
            "composite_score": float,
            "classification": str,
            "recommendations": list[str],  # action strings joined from ImprovementRecommendation
        },
        ...
    ]
}
```

The internal `ComplexityReport` dict shape is **not** the HTTP response shape. The handler is the single location where this mapping occurs.
