# /test

Run the full CI test suite (all stages) in parallel.

## Usage

```bash
/test                        # run ALL stages in parallel (default)
/test --skip-integration     # skip integration tests (no external service needed)
/test --skip-e2e             # skip E2E tests (no browser needed)
/test --skip-integration --skip-e2e   # lint + unit + component + windows + security only
```

## Implementation

Delegates to `python tests/runners/run_all_checks.py` with optional skip flags. This runner:
- Launches all active stages concurrently via threads
- Lint stage: ruff check, ruff format, mypy, bandit — sequential within the stage
- Test stages: pytest with appropriate markers per stage
- Security stage: pip-audit against requirements.txt
- Returns unified exit code; prints failed stage output only

## Test Conventions

**Test factories** in `tests/conftest.py` are plain functions — call directly in test body (do not inject as fixtures):
- `make_sprint(id, name="", start=None, end=None)` — omit state; metrics don't filter on it
- `make_issue(key, status="Done", points=5.0, story_points_field="customfield_10016")`
- `make_issue_with_changelog(key, in_progress_ts=None, done_ts=None)` — timestamps must be ISO-8601 with timezone offset; naive datetimes cause cycle time to return `None`
- `make_issue_with_labels(key, status="Done", points=5.0, labels=None, story_points_field="customfield_10016")` — use for all AI metrics tests

**Pytest fixtures** (inject via function arg, not call):
- `minimal_metrics_dict` — metrics dict with sample data
- `empty_metrics_dict` — metrics dict with no velocity/cycle-time data

**Config tests** use `importlib.reload(config)` with `monkeypatch.setenv()` / `delenv()` to re-parse module-level constants.

**Coverage stats** in `tests/coverage/test_coverage.md` are auto-generated — never hand-edit. Run `/coverage` to refresh.
