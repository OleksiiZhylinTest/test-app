# Implementation Plan: Solution Architect Design Complexity Audit

**Spec**: `specs/002-design-complexity-audit/spec.md`
**Status**: Approved
**Created**: 2026-06-06

---

## Technical Context

- **Language**: Python 3.12+
- **New runtime dependency**: `radon` — promoted from `requirements-dev.txt` to `requirements.txt`
- **Analysis libraries**: `radon.complexity` (CC), `radon.metrics` (MI), `ast` (imports, symbols)
- **No new frameworks**: extend existing stdlib HTTPServer + Jinja2 patterns only

---

## Architecture Decision — Module Boundaries

Each new module has exactly one responsibility, consistent with the Single Responsibility rule in `AGENTS.md`.

| Module | Responsibility | I/O |
|--------|---------------|-----|
| `app/core/complexity_audit.py` | Scoring engine and recommendation derivation — discovers modules, scores them, generates improvement recommendations, and builds `ComplexityReport`. **No file writes.** File reads are the minimum necessary I/O for analysis; scoring functions accept `source: str` and are pure. | Read-only filesystem (discovery + source reading) |
| `app/reporters/report_complexity_md.py` | Write Markdown report. Mirrors `report_md.py` pattern: `generate_complexity_md(report, output_path)`. | Write |
| `app/reporters/report_complexity_html.py` | Render Jinja2 template + write HTML report. Mirrors `report_html.py` pattern: `generate_complexity_html(report, output_path)`. | Write |
| `app/server/complexity_handlers.py` | Handle `GET /api/complexity/audit`. Calls engine, maps result to API shape, returns JSON. | None (delegates to engine) |
| `ui/templates/complexity_audit.html.j2` | Jinja2 template for HTML report. No logic beyond iteration and conditional display. | None |

**Constraint**: `app/core/complexity_audit.py` MUST NOT write any files. All write operations belong in reporters. The HTTP handler MUST NOT import reporters.

---

## Scoring Engine Design (`app/core/complexity_audit.py`)

### Public API

```python
def discover_modules(root: Path) -> list[Path]:
    """Return all .py files under root, excluding venv/, .venv/, generated/."""

def score_module_source(path: Path, source: str) -> ComplexityScore:
    """Pure scoring function — takes pre-read source string, returns ComplexityScore dict.
    No filesystem access. Testable without disk."""

def build_complexity_report(root: Path) -> ComplexityReport:
    """Orchestrator: discover → read source → score → aggregate → recommend.
    Performs the minimal required filesystem reads (source files only).
    All scoring is delegated to score_module_source()."""
```

**Rationale for the split**: `score_module_source()` accepts `source: str` so unit tests can call it with in-memory strings — no tmp files required. `build_complexity_report()` is the only function that touches the filesystem.

### Dimension Scoring

All dimensions normalised 0–10. Normalisation is a linear clamp: `min(raw / scale_factor, 10.0)`.

| Dimension | Key | Raw metric | Scale factor | API |
|-----------|-----|-----------|-------------|-----|
| Cyclomatic complexity | `cc_score` | Average CC over all functions/methods | 10 → score 10 | `radon.complexity.cc_visit(source)` |
| LOC | `loc_score` | Raw LOC | 300 → score 10 | `radon.metrics.mi_parameters(source).loc` |
| Coupling | `coupling_score` | Unique imported module names | 20 → score 10 | `ast.Import` + `ast.ImportFrom` walk |
| Cohesion | `cohesion_score` | Top-level `def` + `class` count | 20 → score 10 | `ast.FunctionDef` + `ast.AsyncFunctionDef` + `ast.ClassDef` walk at module body level only |

**Composite score** (weighted average):
```
composite_score = 0.3*cc_score + 0.3*loc_score + 0.2*coupling_score + 0.2*cohesion_score
```

**Classification thresholds** (overridable via env vars):
```
Low:    composite_score < COMPLEXITY_MEDIUM_THRESHOLD  (default 3.5)
Medium: composite_score < COMPLEXITY_HIGH_THRESHOLD    (default 7.0)
High:   composite_score >= COMPLEXITY_HIGH_THRESHOLD
```

### Extension Point

```python
_DIMENSION_WEIGHTS: dict[str, float] = {
    "cc_score": 0.3,
    "loc_score": 0.3,
    "coupling_score": 0.2,
    "cohesion_score": 0.2,
}
```

To add a new dimension: implement a scorer, add its key + weight to `_DIMENSION_WEIGHTS`, normalise the weight sum to 1.0.

### Error Handling

If `ast.parse()` or radon raises for a module: populate `ComplexityScore.error` with the exception message, set all numeric scores to `None`, set `classification` to `"Error"`. Continue to next module.

### Maintainability Index

`radon.metrics.mi_visit(source, multi=True)` is computed and stored in `ComplexityScore.mi` for informational display only. It is **not** included in the composite score (keeps scoring structural and independent of MI's opaque formula).

---

## Recommendation Generation

Recommendations are generated inside `build_complexity_report()` after all scores are computed.

Rules:
- `High` modules: generate one recommendation per dimension whose normalised score ≥ 5.0 (i.e., ≥ 50% of the maximum possible score). If no individual dimension reaches 5.0, generate one recommendation for the highest-scoring dimension.
- `Medium` modules: generate at most one recommendation for the highest-scoring dimension
- `Low` modules: no recommendations

Recommendation `action` text is generated from a lookup table keyed by `dimension`:

| Dimension | Action template |
|-----------|----------------|
| `cc` | `"Reduce cyclomatic complexity in {module}: extract conditional branches into named functions"` |
| `loc` | `"Split {module} ({loc} LOC): separate concerns into two or more focused modules"` |
| `coupling` | `"Reduce import coupling in {module}: inject {top_import} as a parameter rather than importing directly"` — `{top_import}` is selected as the most frequently referenced imported module name in the file; falls back to alphabetical first if all are referenced once. |
| `cohesion` | `"Reduce scope of {module}: it defines {function_count} top-level symbols — extract unrelated groups into dedicated modules"` |

---

## CLI Integration

### `app/cli.py` — add `--complexity-audit` flag

In `_parse_args()`, add:
```python
p.add_argument("--complexity-audit", action="store_true",
               help="Run structural complexity audit (no Jira credentials required)")
```

In `main()`, add early-exit branch **before** `config.validate_config()`:
```python
if args.complexity_audit:
    from app.core.complexity_audit import build_complexity_report
    from app.reporters.report_complexity_md import generate_complexity_md
    from app.reporters.report_complexity_html import generate_complexity_html
    report = build_complexity_report(_PROJECT_APP_ROOT)
    ts = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
    out_dir = REPORTS_DIR / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    generate_complexity_md(report, out_dir / "complexity_report.md")
    generate_complexity_html(report, out_dir / "complexity_report.html")
    logger.log(SUCCESS, "Complexity audit written to %s", out_dir)
    return 0
```

### `app/core/config.py` — add threshold env vars

Add after existing metric env vars:
```python
_complexity_med = os.getenv("COMPLEXITY_MEDIUM_THRESHOLD", "3.5").strip()
COMPLEXITY_MEDIUM_THRESHOLD: float = float(_complexity_med) if _complexity_med else 3.5

_complexity_high = os.getenv("COMPLEXITY_HIGH_THRESHOLD", "7.0").strip()
COMPLEXITY_HIGH_THRESHOLD: float = float(_complexity_high) if _complexity_high else 7.0
```

`validate_config()` is **not modified** — the new env vars have defaults and are never required.

---

## HTTP Integration

### `app/server/complexity_handlers.py`

```python
class ComplexityHandlerMixin:
    def _handle_complexity_audit(self) -> None:
        from app.core.complexity_audit import build_complexity_report
        root = Path(__file__).resolve().parent.parent.parent
        report = build_complexity_report(root)
        recs_by_module: dict[str, list[str]] = {}
        for rec in report["recommendations"]:
            recs_by_module.setdefault(rec["module"], []).append(rec["action"])
        scores = []
        for s in report["scores"]:
            scores.append({
                "module": s["module"],
                "loc": s["loc"],
                "function_count": s["function_count"],
                "coupling": s["coupling_score"],
                "cohesion": s["cohesion_score"],
                "composite_score": s["composite_score"],
                "classification": s["classification"],
                "recommendations": recs_by_module.get(s["module"], []),
            })
        self._json({"generated_at": report["generated_at"], "scores": scores,
                    "summary": report["summary"]})
```

**Note**: The API shape uses `coupling` and `cohesion` (without `_score` suffix) to match the spec FR-6 acceptance criteria. The internal data model retains `coupling_score` / `cohesion_score` for clarity.

### `app/server/__init__.py` — register handler

Import and mix in `ComplexityHandlerMixin` following the existing pattern for other handler modules.

Route: `GET /api/complexity/audit` → `_handle_complexity_audit()`

---

## Data Flow Diagrams

### CLI path
```
main.py --complexity-audit
  → app/cli.py: early-exit branch (bypasses validate_config)
  → app/core/complexity_audit.py
      discover_modules(ROOT) → list[Path]
      for each path: _read_source(path) → str
                     score_module_source(path, source) → ComplexityScore
      aggregate → ComplexityReport
  → app/reporters/report_complexity_md.py → generated/reports/<ts>/complexity_report.md
  → app/reporters/report_complexity_html.py → generated/reports/<ts>/complexity_report.html
```

### HTTP path
```
GET /api/complexity/audit
  → app/server/complexity_handlers.py: ComplexityHandlerMixin._handle_complexity_audit()
  → app/core/complexity_audit.py: build_complexity_report(ROOT)
  → map ComplexityReport → API shape (recs joined per module)
  → self._json(response)
```

---

## Security

- `discover_modules()` uses `pathlib.Path.rglob("*.py")` on the repo root — no user input enters the path.
- Exclusion patterns (`venv/`, `.venv/`, `generated/`) are a hardcoded allowlist, not a user-supplied filter.
- `ast.parse()` receives only files discovered by `discover_modules()` — no user-controlled input.
- HTTP endpoint exposes only computed numeric scores and module names relative to repo root. No absolute filesystem paths are returned.
- No credentials or env var values are included in any report output.

---

## Files to Create

```
app/core/complexity_audit.py
app/reporters/report_complexity_md.py
app/reporters/report_complexity_html.py
app/server/complexity_handlers.py
ui/templates/complexity_audit.html.j2
```

## Files to Modify

```
app/cli.py                  — add --complexity-audit flag + early-exit branch
app/core/config.py          — add COMPLEXITY_MEDIUM_THRESHOLD, COMPLEXITY_HIGH_THRESHOLD
app/server/__init__.py      — register ComplexityHandlerMixin
requirements.txt            — add radon
requirements-dev.txt        — add comment noting radon promoted to runtime dep
```

---

## Constitution Compliance

| Principle | Compliance |
|-----------|-----------|
| Single Responsibility | Each new module has exactly one job ✓ |
| Open/Closed | New dimensions extend `_DIMENSION_WEIGHTS` dict; no existing functions modified ✓ |
| DRY | `discover_modules()` is the single discovery implementation ✓ |
| KISS | stdlib + radon only; no new frameworks ✓ |
| YAGNI | No speculative parameters or generalisations beyond spec FRs ✓ |
