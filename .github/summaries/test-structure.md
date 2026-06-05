# Copilot Summary: Test Structure

Use this summary before loading multiple test files. Its job is to route changes to the narrowest useful test layer.

## Source of Truth

- `AGENTS.md`
- `pyproject.toml`
- `tests/conftest.py`
- `tests/unit/conftest.py`
- `tests/component/conftest.py`
- `tests/e2e/conftest.py`

## Test Pyramid

- `tests/unit/` -> pure functions, no I/O
- `tests/component/` -> filesystem and HTTP slices, no broad orchestration
- `tests/integration/` -> real multi-module interactions
- `tests/e2e/` -> Playwright browser flows

## Shared Factories And Fixtures

- `tests/conftest.py` provides shared factories such as `make_sprint`, `make_issue`, `make_issue_with_changelog`, and `make_issue_with_labels`.
- `tests/unit/conftest.py` provides `mock_jira`.
- `tests/component/conftest.py` provides `minimal_metrics_dict` and `empty_metrics_dict`.
- `tests/e2e/conftest.py` provides the live server setup for browser tests.

## Runner Shortcuts

- Full checks -> `python tests/runners/run_all_checks.py`
- Smoke -> `python tests/runners/run_all_checks.py --smoke`
- Sanity -> `python tests/runners/run_all_checks.py --sanity`

## Selection Guidance

- Change in `app/core/*.py` pure logic -> start with unit tests.
- Change in reporter rendering or server handler slice -> start with component tests.
- Change spanning fetch, compute, render, or CLI/server orchestration -> add integration coverage.
- Change in browser UI behavior -> add or update e2e coverage.

## Escalate Beyond This Summary When

- you need exact fixture shapes or factory signatures
- you need current coverage/test inventory details
- you are changing test runners, markers, or CI stage definitions