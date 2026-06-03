# AGENTS.md

Assistant-neutral routing and token-efficiency layer for this repository.
All AI assistants (Claude, Copilot, Cursor, Gemini, etc.) should read this file.
Assistant-specific guidance lives in `CLAUDE.md` for Claude Code and in assistant-owned assets under `.github/` for GitHub Copilot.

## Authoritative References

Go directly to the source of truth — do not rely on summaries in other files:

| Topic | Authoritative file |
|-------|--------------------|
| All config variables (descriptions + defaults) | `.env.example` |
| Module responsibilities, data flow, layer diagram | `docs/development/architecture.md` |
| Sprint / Issue / metrics_dict dict shapes | `docs/development/architecture.md` |
| CI pipeline stages | `docs/development/pipeline.md` |
| Requirements index (which file to update per area) | `docs/product/requirements/README.md` |
| Metric definitions, required Jira fields, calculation logic | `docs/product/metrics/` |
| Test factories and fixtures | `tests/conftest.py` (root), `tests/unit/conftest.py`, `tests/component/conftest.py` |
| Auto-generated test coverage stats | `tests/coverage/test_coverage.md` |

## Module Map

| File | One-line purpose |
|------|-----------------|
| `main.py` | Thin CLI entry-point; delegates to `app.cli` |
| `server.py` | Thin server entry-point; delegates to `app.server` |
| `app/cli.py` | Full report pipeline: config → fetch → metrics → parallel HTML+MD output |
| `app/server/` | Stdlib HTTPServer package; `_base.py` is the handler base; serves `ui/index.html` and all `/api/*` routes |
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
| `tests/conftest.py` | Shared factories: `make_sprint`, `make_issue`, `make_issue_with_changelog`, `make_issue_with_labels` |
| `tests/tools/test_coverage.py` | Regenerates `tests/coverage/test_coverage.md`; run after adding/removing tests |

## Assistant Ownership Model

Use one shared layer plus assistant-owned customization namespaces.

| Surface | Owner | Default behavior |
|---------|-------|------------------|
| `AGENTS.md`, application code, tests, config, and project docs | Shared | All assistants may read and update when the task requires it |
| `CLAUDE.md`, `.claude/**` | Claude Code | Other assistants should not inspect or modify during normal tasks |
| `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, `.github/hooks/**` | GitHub Copilot | Other assistants should not inspect or modify during normal tasks |

Rules:
- Default scope for any assistant is the shared repo surfaces plus its own customization namespace.
- Cross-tool governance, audit, migration, or alignment tasks must be explicitly requested before one assistant reads or edits the other assistant's customization namespace.
- Prefer the owning assistant to author changes in its namespace. Other assistants may review or propose changes when explicitly asked.
- When shared repo conventions change, update `AGENTS.md` first, then refresh assistant-owned files that depend on it.

Assistant-specific operational guidance belongs in assistant-owned files:
- Claude-specific workflow and commands belong in `CLAUDE.md` and `.claude/**`.
- Copilot-specific agents, skills, prompts, and hooks belong in `.github/**`.

Shared governance details live in `docs/development/assistant_customization_governance.md`.

---

## Context Optimization

Use lean context by default.

- Start from the nearest concrete anchor: a file, symbol, failing command, or active requirement.
- Prefer focused local reads over broad repo exploration.
- Prefer summaries, indexes, and owning docs before loading large reference manuals.
- Load large docs such as `docs/development/architecture.md` only when the task directly needs full architectural detail.
- Reuse existing authoritative references instead of duplicating long summaries into assistant-owned files.
- If a task becomes broad, split it into smaller passes instead of front-loading more context than needed.

Copilot-owned low-token context assets should live under `.github/`.
Claude-owned low-token context assets should live under `.claude/`.

---

## Key Conventions

**Testing pyramid** (`tests/`):
- `unit/` — pure functions, no I/O, no mocks of external services
- `component/` — filesystem + HTTP, no inter-module orchestration
- `integration/` — real multi-module interactions (may need Jira credentials)
- `e2e/` — Playwright browser tests (requires Chromium; tests skip if missing)
- Run all stages: `python tests/runners/run_all_checks.py`

**Test tiers** (cross-layer markers — orthogonal to the pyramid):
- `@pytest.mark.smoke` — critical happy paths spanning every layer (~1-2 min). Use after every feature implementation.
- `@pytest.mark.sanity` — broader regression set (~5-10 min). Smoke is included; select with `-m "smoke or sanity"`.
- Run smoke locally: `python tests/runners/run_all_checks.py --smoke`
- Run sanity locally: `python tests/runners/run_all_checks.py --sanity`
- Run full suite: `python tests/runners/run_all_checks.py` (or `--full`)
- CI: `smoke-tests` job runs always; `sanity-tests` job is opt-in via `ENABLE_SANITY` repo var.

**Requirements tracking:**
- Every feature area has a `docs/product/requirements/<topic>_requirements.md` file.
- Status values are exactly `✓ Met`, `✗ Not met`, `⬜ N/T` — no other variants.
- Identify which file(s) to update using `docs/product/requirements/README.md`.
- Do not add rows or create new requirements files.

**Configuration system:**
- All config is read from `.env` (copied from `.env.example` at setup).
- New variables: add to `.env.example` first, then add `os.getenv()` in `app/core/config.py`.
- Config module uses module-level constants loaded at import time; tests must use `importlib.reload(config)` to observe env changes.

**Generated output:**
- `generated/` is gitignored; all runtime artifacts (reports, logs, tmp files) go here.
- Do not create disposable files in the project root or alongside source files.

**File placement conventions:**
- Application source: `app/` (core logic, reporters, utils)
- Persistent config: `config/` (JSON files, source-controlled)
- Test suite: `tests/` (layers: `unit/`, `component/`, `integration/`, `e2e/`)
- Docs: `docs/development/` (architecture, pipeline, API refs) and `docs/product/` (metrics, requirements, features)
- Temporary/generated artifacts: `generated/tmp/`, `generated/debug/`, `generated/reports/`
