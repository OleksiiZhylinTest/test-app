# Architecture Map — AI Adoption Metrics Report

> Lightweight anchor for `implement`, `fix`, `sync`, `extend`. Use this before loading `docs/development/architecture.md`.

## Entry Points
| File | Delegates to |
|------|-------------|
| `main.py` | `app/cli.py` — full report pipeline |
| `server.py` | `app/server/` — stdlib HTTPServer package |

## Layer Map
```
app/core/config.py        ← env loading, validate_config(), all JIRA_*/AI_* constants
app/core/jira_client.py   ← fetch_sprint_data() / fetch_kanban_data() → (sprints, sprint_issues)
app/core/metrics.py       ← build_metrics_dict() → metrics_dict (pure, no I/O)
app/core/schema.py        ← load/query config/jira_schema.json
app/core/dau_importer.py  ← .xlsx import → dau_*.json files
app/core/dau_normalizer.py← normalize(src, dst) — dedup, called before metrics
app/reporters/report_html.py ← Jinja2 render of ui/templates/report.html.j2
app/reporters/report_md.py   ← build Markdown string, write to disk
app/server/_base.py       ← Handler base class + do_GET/do_POST/do_DELETE routing
app/server/*_handlers.py  ← one file per /api/* route group
app/utils/cert_utils.py   ← validate_cert(Path) → {valid, expires_at, days_remaining, subject}
app/utils/logging_setup.py← setup_logging() → (root_logger, log_file_path); SUCCESS_LEVEL=25
```

## Key Data Contracts
- `metrics_dict` — assembled by `build_metrics_dict()`; consumed by both reporters. Shape in `extend.md` or `docs/development/architecture.md §4`.
- Sprint dict: `{"id": int, "name": str, "startDate": str|None, "endDate": str|None}`
- Issue dict: `{"key": str, "fields": {"status": {"name": str}, "customfield_10016": float|None, ...}}`

## Config Files
| File | Tracked | Purpose |
|------|---------|---------|
| `config/defaults.env` | Yes | Non-sensitive defaults (sprint count, metric toggles, AI labels) |
| `.env` | No | Credentials: `JIRA_URL`, `JIRA_EMAIL`, `JIRA_API_TOKEN` |
| `config/jira_schema.json` | Yes | Jira field schema registry per instance |
| `config/jira_filters.json` | Yes | Named JQL filter registry |

## Test Pyramid
```
tests/unit/        ← pure functions, no I/O       (372 tests)
tests/component/   ← filesystem + HTTP, no mocks  (182 tests)
tests/integration/ ← multi-module                 ( 19 tests)
tests/e2e/         ← Playwright browser           (119 tests)
```
Run: `python tests/runners/run_all_checks.py`

## Extension Patterns (quick ref)
- **New metric**: add `compute_<name>()` in `metrics.py` → call in `build_metrics_dict()` → render in reporters → add unit test
- **New config var**: add to `defaults.env` (non-sensitive) or `.env.example` (credential) → `os.getenv()` in `config.py` → test in `test_config.py`
- **New server route**: add `_handle_<name>()` in `app/server/_base.py` → route from `do_GET`/`do_POST` → test in `tests/component/test_server.py`

## Module Ownership (single responsibility)
- `metrics.py` computes only — no fetch, no render
- reporters render only — no fetch, no compute
- `config.py` reads env only — no logic
- `app/server/*_handlers.py` — each file owns one /api/* route group
