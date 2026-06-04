# Copilot Summary: Test Conventions

Lean-context reference for writing and reviewing tests in this repository.
Source of truth: `AGENTS.md`, `tests/conftest.py`, `.github/summaries/test-structure.md`.
Do NOT hand-edit `tests/coverage/test_coverage.md`.

## Factory and Fixture Rules

- Shared factories (call freely from any layer): `make_sprint`, `make_issue`, `make_issue_with_changelog`, `make_issue_with_labels` — all in `tests/conftest.py`.
- Never duplicate fixture logic that already exists in `tests/conftest.py`.
- Unit-layer fixture: `mock_jira` — `tests/unit/conftest.py` only.
- Component-layer fixtures: `minimal_metrics_dict`, `empty_metrics_dict` — `tests/component/conftest.py` only.
- Do not import a layer-specific fixture into a different layer.

## Coverage Rules

- Every changed behavior must have a test in the narrowest applicable layer.
- Layer selection:
  - Pure function, no I/O → `tests/unit/`
  - Handler or reporter slice (filesystem / HTTP, no broad orchestration) → `tests/component/`
  - Real multi-module interaction → `tests/integration/`
  - Browser behavior (requires Chromium) → `tests/e2e/`
- Do not use integration tests for scenarios that unit or component tests can cover.

## Test Tier Rules

- `@pytest.mark.smoke` — critical happy paths spanning every layer; run after every feature.
- `@pytest.mark.sanity` — broader regression set; includes smoke; run before every push.
- Run smoke: `python tests/runners/run_all_checks.py --smoke`
- Run sanity: `python tests/runners/run_all_checks.py --sanity`
- Run full suite: `python tests/runners/run_all_checks.py`
- Proposed marker changes must be presented to the user (GH Test Lead approves).

## Coverage Maintenance

- After adding, removing, or renaming any test function, regenerate the coverage doc:
  `python tests/tools/test_coverage.py`
- Never hand-edit `tests/coverage/test_coverage.md` — the script is the only writer.

## Escalate Beyond This Summary When

- You need exact factory signatures or fixture shapes → read `tests/conftest.py` directly.
- You need current test inventory or coverage stats → read `tests/coverage/test_coverage.md`.
- You are modifying test runner scripts, CI stage definitions, or `pyproject.toml` markers.
- A test pyramid imbalance is detected (unit coverage displaced by integration tests).
