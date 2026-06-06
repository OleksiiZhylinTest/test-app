# Repo Quick Reference

Lean orientation anchor for Copilot agents. For full conventions see `AGENTS.md`.

## Module Map

| File | One-line purpose |
|------|-----------------|
| `main.py` | Thin CLI entry-point; delegates to `app.cli` |
| `server.py` | Thin server entry-point; delegates to `app.server` |
| `app/cli.py` | Full report pipeline: config → fetch → metrics → parallel HTML+MD output |
| `app/server/` | Stdlib HTTPServer package; `_base.py` handler base; serves `ui/index.html` and all `/api/*` routes |
| `app/core/config.py` | Loads `.env`, exposes all constants, `validate_config()` |
| `app/core/jira_client.py` | Jira REST wrapper; `fetch_sprint_data()` → `(sprints, sprint_issues)` |
| `app/core/metrics.py` | Pure metric functions; `build_metrics_dict()` → dict consumed by reporters |
| `app/core/schema.py` | Jira field schema registry backed by `config/jira_schema.json` |
| `app/reporters/report_html.py` | Renders `ui/templates/report.html.j2` via Jinja2 |
| `app/reporters/report_md.py` | Builds Markdown report string and writes to disk |
| `app/utils/logging_setup.py` | `setup_logging()` → `(root_logger, log_file_path)`; custom SUCCESS level |
| `app/utils/cert_utils.py` | PEM certificate validation via `cryptography` library |
| `config/jira_schema.json` | Jira field/status definitions per instance (source-controlled) |
| `config/jira_filters.json` | Named JQL filter presets (source-controlled) |
| `ui/templates/report.html.j2` | Jinja2 HTML report template |

## Test Runner Shortcuts

```bash
python tests/runners/run_all_checks.py          # full suite
python tests/runners/run_all_checks.py --smoke  # cross-layer smoke (~1-2 min)
python tests/runners/run_all_checks.py --sanity # smoke + sanity (~5-10 min)
python tests/tools/test_coverage.py            # regenerate tests/coverage/test_coverage.md
```

## Key Conventions

- **Config**: all config from `.env`; new vars → `.env.example` first, then `app/core/config.py`
- **Generated output**: all runtime artifacts go to `generated/` (gitignored); never write to source tree
- **Requirements status**: exactly `✓ Met`, `✗ Not met`, `⬜ N/T` — no variants
- **Logging**: `logger = logging.getLogger(__name__)` per module; never root logger or `print()`
- **Test layers**: `unit/` pure functions · `component/` filesystem+HTTP · `integration/` multi-module · `e2e/` browser

## Authoritative References

| Topic | File |
|-------|------|
| Module responsibilities, data flow | `docs/development/architecture.md` |
| CI pipeline stages | `docs/development/pipeline.md` |
| Requirements index | `docs/product/requirements/README.md` |
| Test factories and fixtures | `tests/conftest.py` |
| Full conventions | `AGENTS.md` |
