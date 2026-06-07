# Tasks: Design Complexity Audit

**Spec**: `specs/002-design-complexity-audit/spec.md`
**Plan**: `specs/002-design-complexity-audit/plan.md`
**Status**: Ready for implementation
**Created**: 2026-06-07

---

## Phase 1 — Setup

All tasks in this phase are independent and fully parallelisable.

- [ ] T-001 [P1] [P] Pin `radon>=6.0,<7` in `requirements.txt` — promote radon from dev to runtime dependency (Risk 3)
- [ ] T-002 [P1] [P] Annotate radon entry in `requirements-dev.txt` — note radon promoted to `requirements.txt`, keep or remove dev pin
- [ ] T-003 [P1] [P] Add `COMPLEXITY_MEDIUM_THRESHOLD` (default `3.5`) and `COMPLEXITY_HIGH_THRESHOLD` (default `7.0`) env vars to `app/core/config.py`
- [ ] T-004 [P1] [P] Verify `datetime` and `timezone` are imported in `app/cli.py` — add missing imports if absent (Risk 1)
- [ ] T-005 [P1] [P] Confirm `SUCCESS` log level is exported from `app/utils/logging_setup.py` — add export if missing (Risk 2)
- [ ] T-006 [P3] [P] Confirm mixin injection pattern in `app/server/__init__.py` — record base class list order as an inline comment in `app/server/__init__.py` for T-020 (Risk 4)

---

## Phase 2 — Core Engine

Prerequisite for all user story phases. Tasks are sequential within this phase.

- [ ] T-007 [P1] Create `app/core/complexity_audit.py` — skeleton with `discover_modules(root)` excluding `venv/`, `.venv/`, `generated/`
- [ ] T-008 [P1] Add `score_module_source(path, source)` to `app/core/complexity_audit.py` — compute `cc_score`, `loc_score`, `coupling_score`, `cohesion_score` via radon + ast; return `ComplexityScore` dict
- [ ] T-009 [P1] Add classification logic to `app/core/complexity_audit.py` — assign tier (`Low`/`Medium`/`High`) using `COMPLEXITY_MEDIUM_THRESHOLD` and `COMPLEXITY_HIGH_THRESHOLD` from config
- [ ] T-010 [P1] Add `build_complexity_report(root)` to `app/core/complexity_audit.py` — orchestrate discover → read → score → classify → aggregate into `ComplexityReport` dict; no file writes
- [ ] T-011 [P2] Add improvement recommendation generator to `app/core/complexity_audit.py` — produce ≥1 `ImprovementRecommendation` per `High`-tier module; attach `recommendations` list to `ComplexityReport`

---

## Phase 3 — US1: CLI Audit

Depends on Phase 2 (all of T-007 through T-010). T-012 and T-013 are parallelisable; T-014 depends on T-013; T-015 depends on T-012 and T-014.

- [ ] T-012 [P1] [US1] [P] Create `app/reporters/report_complexity_md.py` — `generate_complexity_md(report, output_path)` writing a Markdown score table sorted by `composite_score` descending
- [ ] T-013 [P1] [US1] [P] Create `ui/templates/complexity_audit.html.j2` — Jinja2 template rendering module score table; no business logic in template
- [ ] T-014 [P1] [US1] Create `app/reporters/report_complexity_html.py` — `generate_complexity_html(report, output_path)` rendering `complexity_audit.html.j2` via Jinja2; mirrors `report_html.py` pattern
- [ ] T-015 [P1] [US1] Add `--complexity-audit` argparse flag and early-exit branch to `app/cli.py` — invoke `build_complexity_report()`, call both reporters, write to `generated/reports/<timestamp>/`, exit before `validate_config()`

---

## Phase 4 — US2: Improvement Plan

Depends on Phase 2 (T-011 specifically). Parallelisable with Phase 3 once Phase 2 is complete.

- [ ] T-016 [P2] [US2] [P] Extend `app/reporters/report_complexity_md.py` — append ranked improvement plan section with ≥1 actionable recommendation per `High`-tier module
- [ ] T-017 [P2] [US2] [P] Extend `ui/templates/complexity_audit.html.j2` — add improvement plan section: ranked module table and per-module recommendation list
- [ ] T-018 [P2] [US2] Extend `app/reporters/report_complexity_html.py` — render improvement plan from T-017 template additions

---

## Phase 5 — US3: HTTP API

Depends on Phase 2 (T-007 through T-010). Parallelisable with Phases 3 and 4 once Phase 2 is complete.

- [ ] T-019 [P3] [US3] Create `app/server/complexity_handlers.py` — `ComplexityHandlerMixin` with `_handle_complexity_audit()` calling engine, serialising `ComplexityReport` to JSON response; no reporter imports
- [ ] T-020 [P3] [US3] Register `ComplexityHandlerMixin` in `app/server/__init__.py` — add to base class list; bind route `GET /api/complexity/audit`

---

## Phase 6 — Polish & Cross-cutting

Depends on all prior phases.

- [ ] T-021 [P1] [P] Add unit tests for `discover_modules()` and `score_module_source()` in `tests/unit/test_complexity_audit.py` — in-memory source strings, no tmp files
- [ ] T-022 [P1] [P] Add unit tests for `build_complexity_report()`, classification logic, and recommendation generation in `tests/unit/test_complexity_audit.py` — mock filesystem, assert tier assignments; assert ≥1 recommendation for High modules, ≤1 for Medium, none for Low (SC-2)
- [ ] T-023 [P1] [P] Add unit test for `generate_complexity_md()` in `tests/unit/test_report_complexity_md.py` — assert output string contains expected headers and module rows
- [ ] T-024 [P1] [US1] Add component test for `python main.py --complexity-audit` in `tests/component/test_complexity_cli.py` — assert report files written to `generated/reports/`, no Jira creds needed; assert modules from `tools/`, `tests/tools/`, and root scripts appear in report (full-repo scope); assert wall-clock duration < 30s (SC-3)
- [ ] T-025 [P3] [US3] Add component test for `GET /api/complexity/audit` in `tests/component/test_complexity_api.py` — assert 200 response with `scores` and `recommendations` keys; assert response time < 30s for first call after server start (SC-5)
- [ ] T-026 [P1] Update `docs/development/architecture.md` — add `app/core/complexity_audit.py`, `app/reporters/report_complexity_md.py`, `app/reporters/report_complexity_html.py`, and `app/server/complexity_handlers.py` to module map
- [ ] T-027 [P1] Update `CHANGELOG.md` — add feature entry for design complexity audit (US1 CLI, US2 improvement plan, US3 HTTP API)

---

## Dependency Graph

```
Phase 1 (T-001..T-006) — no dependencies; all parallel
    └─► Phase 2: T-007 → T-008 → T-009 → T-010 → T-011
                                    ├─► Phase 3: T-012[P], T-013[P] → T-014 → T-015
                                    ├─► Phase 4: T-016[P], T-017[P] → T-018
                                    └─► Phase 5: T-019 → T-020
                                                    └─► Phase 6: T-021..T-027
```

---

## Parallel Execution Opportunities

| Window | Parallelisable tasks |
|--------|---------------------|
| Phase 1 | T-001, T-002, T-003, T-004, T-005, T-006 (all 6) |
| Phase 3 start (after Phase 2) | T-012 and T-013 |
| Phase 3 + Phase 4 + Phase 5 (after Phase 2) | T-012, T-013, T-016, T-017, T-019 |
| Phase 6 | T-021, T-022, T-023 (unit tests); T-026, T-027 (docs) |

---

## MVP Scope (US1 only — CLI path)

**Phase 1 + Phase 2 (T-007..T-010) + Phase 3 (T-012..T-015)**

Excludes: T-011 (recommendations engine), Phase 4 (improvement plan), Phase 5 (HTTP API). Phase 6 tests T-021..T-024 and T-026..T-027 are recommended for MVP quality gate.

---

## Total Task Count: 27
