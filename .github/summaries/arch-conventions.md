# arch-conventions.md — Lean-Context Architecture Conventions Summary

Source of truth: `docs/development/architecture.md`
This file is a standing-rules extract. Do NOT duplicate or override the full doc.

## Layer Rules

| Rule | Constraint |
|------|-----------|
| L1 | `metrics.py` computes only — no fetch logic, no rendering, no I/O |
| L2 | `reporters/report_html.py` and `reporters/report_md.py` render only — no business logic, no metric computation |
| L3 | `config.py` reads env only — no computation, no I/O beyond `os.getenv()` / `python-dotenv` load |
| L4 | `ui/templates/report.html.j2` contains no business logic — all conditionals and loops belong in `report_html.py` |
| L5 | No new cross-module imports that violate the layer diagram in `docs/development/architecture.md` |

## DAU Pipeline Rules

| Rule | Module | Responsibility |
|------|--------|---------------|
| D1 | `dau_importer.py` | Import raw DAU data only — no normalisation, no state management |
| D2 | `dau_normalizer.py` | Normalise DAU records only — no import I/O, no user state |
| D3 | `user_data.py` | Manage user state only — no import or normalisation logic |
| D4 | `migration.py` | Handle schema migration only — no business logic from other DAU modules |

## Shared Module Rules

| Rule | Constraint |
|------|-----------|
| S1 | `app/exceptions.py` is the sole registry for project-wide exception types — add a new type here only when it must be raised or caught across module boundaries; do not add module-local exceptions here |

## Escalate to Full Architecture Doc When

- Adding or removing a module from `app/`
- Altering the `build_metrics_dict()` output shape
- Adding a new `/api/*` server route
- Introducing a new third-party dependency
- Any change that crosses two or more layers simultaneously
