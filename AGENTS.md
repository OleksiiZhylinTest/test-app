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

**Claude Code primary entry point:** `project-manager` subagent (`.claude/agents/project-manager.md`) handles intake and routing for all requests. Delegates to 7 direct reports (L1 delegates); each L1 delegate applies the Maker-Checker review loop before accepting work from its leaf agents.

> **Cross-assistant routing (X2):** For tasks that span both Claude and Copilot sides, route the Claude-side work to `ai-architect` → `ai-engineer`. Flag the Copilot-side aspects as requiring a separate Copilot invocation. Never route Claude tasks to Copilot agents (`.github/agents/**`) — treat them as non-existent during normal Claude operation.

**Claude Code SDLC agent roster** (`.claude/agents/`):

| Agent | Tier | Role | Primary workspace |
|-------|------|------|-------------------|
| `project-manager` | Orchestrator | Intake, routing, plan-mode orchestration | All surfaces (read-only) |
| `ai-architect` | L1 Delegate | Claude env governance, agent definitions, hooks, CLAUDE.md audit | `.claude/**` (read); `CLAUDE.md` (read); `.github/**` (read-only) |
| `principal-solution-architect` | L1 Delegate | Strategic architecture oversight and approval | `docs/`, `app/`, `config/`, `tests/` (read-only) |
| `product-owner` | L1 Delegate | Backlog, acceptance criteria, prioritisation | `docs/product/` (read-only) |
| `dev-lead` | L1 Delegate | Technical oversight, code review, sprint breakdown | `app/`, `tests/`, `docs/development/` (read-only) |
| `test-lead` | L1 Delegate | Test strategy, coverage gates, quality sign-off; owns all Code Review / Test Review / Coverage Review | `tests/` (read); `generated/tmp/` (audit trails write) |
| `devops-lead` | L1 Delegate | CI/CD strategy, deployment approval, incident review | `.github/workflows/` (read-only) |
| `web-search` | L1 Delegate | External documentation lookups | Web only (read-only) |
| `ai-engineer` | L2 Leaf | Claude AI environment implementation (`.claude/**`, `CLAUDE.md`, `.vscode/`) | `.claude/**` (excl. `settings*.json`), `CLAUDE.md`, `.vscode/` |
| `solution-architect` | L2 Leaf | Architecture implementation: module structure, API contracts, schema, ADRs | `docs/development/` (excl. `docs/development/quality/`), `config/jira_schema.json`, `config/jira_filters.json` |
| `quality-architect` | L2 Leaf | Quality framework, test layers, coverage gates, NFR definitions | `docs/product/requirements/`, `docs/development/quality/` |
| `business-analyst` | L2 Leaf | Requirements elicitation, user stories, gap analysis | `docs/product/requirements/` (read-only) |
| `backend-developer` | L2 Leaf | Server-side Python, API routes, reporters, config | `app/core/`, `app/server/`, `app/reporters/`, `app/utils/`, `config/` |
| `frontend-developer` | L2 Leaf | UI templates, HTML/CSS, accessibility | `ui/templates/`, `ui/index.html`, `ui/css/`, `ui/js/` |
| `manual-qa` | L2 Leaf | Exploratory testing, regression checklists, bug reports | `tests/` (read), `docs/product/requirements/`; `generated/tmp/` (bug reports write) |
| `automation-qa` | L2 Leaf | Automated tests, CI integration, flaky test triage | `tests/unit/`, `tests/component/`, `tests/integration/`, `tests/e2e/` |
| `performance-qa` | L2 Leaf | Performance test suites, latency baselines, throughput benchmarks | `tests/component/`, `tests/integration/`, `generated/reports/`, `generated/tmp/` |
| `security-qa` | L2 Leaf | OWASP review, TLS validation, secrets audit, CVE triage | All surfaces (read); security NFR Status column; `generated/tmp/` and `generated/debug/` (findings write) |
| `ux-designer` | L2 Leaf | Interaction specs, accessibility, design contracts | `docs/product/features/`, `ui/templates/`, `ui/css/`, `ui/js/` |
| `technical-writer` | L2 Leaf | README, architecture docs, changelogs, API docs | `docs/`, `README.md`, `CHANGELOG.md` |
| `devops-engineer` | L2 Leaf | Pipeline implementation, Dockerfile, deploy scripts | `.github/workflows/`, `docs/development/pipeline.md`, `pyproject.toml` |

RACI matrix and Maker-Checker Protocol: `.claude/sdlc-raci.md`.

**GitHub Copilot primary entry point:** `GH Project Manager` agent (`.github/agents/gh-project-manager.agent.md`) handles intake and routing for all requests. Delegates Claude environment work to `GH AI Architect` → `GH AI Engineer`, and external lookups to `GH Web Search`.

## GitHub Copilot SDLC Agents

Copilot agent definitions live under `.github/agents/`. Maker-Checker review loop specification: `.github/summaries/maker-checker-protocol.md`.

| Agent file | Role | Permission level | Subagents |
|-----------|------|-----------------|-----------|
| `gh-project-manager.agent.md` | First-contact orchestrator, intake and routing | Orchestrate-only (no write) | gh-ai-architect, gh-principal-solution-architect, gh-web-search, gh-product-owner, gh-dev-lead, gh-test-lead, gh-devops-lead |
| `gh-ai-architect.agent.md` | Copilot env governance, agent/skill/prompt/hook oversight | Read-only | gh-ai-engineer, gh-web-search |
| `gh-ai-engineer.agent.md` | Copilot AI environment implementation (`.github/**`, `AGENTS.md`, `.vscode/`) | Write (`.github/**`, `AGENTS.md`, `.vscode/`) | None (leaf) |
| `gh-principal-solution-architect.agent.md` | Strategic architecture oversight and approval | Read-only | gh-solution-architect, gh-quality-architect, gh-web-search |
| `gh-solution-architect.agent.md` | Concrete architecture implementation (renamed from `gh-architect`) | Write (`docs/development/` excl. `docs/development/quality/`, `config/jira_schema.json`, `config/jira_filters.json`) | None (leaf) |
| `gh-quality-architect.agent.md` | Quality framework, test layers, coverage gates, NFR docs | Write (`docs/product/requirements/`, `tests/coverage/`, `docs/development/quality/`) | None (leaf) |
| `gh-web-search.agent.md` | External documentation research | External-only (no repo write) | None (leaf) |
| `gh-product-owner.agent.md` | Requirements acceptance, feature acceptance, priority | Read-only | gh-business-analyst, gh-ux-designer, gh-technical-writer, gh-web-search |
| `gh-business-analyst.agent.md` | Requirements elicitation, acceptance criteria, gap analysis | Read-only | None (leaf) |
| `gh-ux-designer.agent.md` | Interaction design, accessibility specs, frontend design contracts | Write (`docs/product/features/`, `ui/templates/`, `ui/index.html`, `ui/css/`, `ui/js/`) | None (leaf) |
| `gh-technical-writer.agent.md` | Docs maintenance: README, architecture, pipeline, features, metrics | Write (`docs/`, `README.md`, `CHANGELOG.md`, `generated/tmp/`) | gh-web-search |
| `gh-dev-lead.agent.md` | Code review, coding standards enforcement, implementation approval | Read-only | gh-frontend-developer, gh-backend-developer, gh-web-search |
| `gh-frontend-developer.agent.md` | UI templates, HTML/CSS/JS implementation | Write (`ui/templates/`, `ui/index.html`, `ui/css/`, `ui/js/`, `ui/dau_survey.html`) | None (leaf) |
| `gh-backend-developer.agent.md` | Server-side Python, API routes, reporters, config | Write (`app/core/`, `app/server/`, `app/reporters/`, `app/utils/`, `app/cli.py`, `config/`) | None (leaf) |
| `gh-test-lead.agent.md` | Test strategy, coverage gates, quality sign-off | Read-only | gh-manual-qa, gh-automation-qa, gh-performance-qa, gh-security-qa, gh-web-search |
| `gh-manual-qa.agent.md` | Exploratory testing, regression checklists, bug reports | Read-only | None (leaf) |
| `gh-automation-qa.agent.md` | Automated tests, CI integration, flaky test triage | Write (`tests/unit/`, `tests/component/`, `tests/integration/`, `tests/e2e/`, `tests/coverage/`) | None (leaf) |
| `gh-performance-qa.agent.md` | Performance test suites, latency baselines, throughput benchmarks | Write (`tests/component/`, `tests/integration/`, `generated/reports/`, `generated/tmp/`, `docs/development/`) | None (leaf) |
| `gh-security-qa.agent.md` | OWASP scanning, TLS validation, secrets audit, CVE review (renamed from `gh-security-reviewer`) | Read all + limited write (security NFR Status column) | None (leaf) |
| `gh-devops-lead.agent.md` | CI/CD strategy, pipeline approval, infra governance | Read-only | gh-devops, gh-web-search |
| `gh-devops.agent.md` | Pipeline implementation, workflow YAML, CI configuration | Write (`.github/workflows/`, `docs/development/pipeline.md`, `pyproject.toml`) | None (leaf) |

Rules:
- Default scope for any assistant is the shared repo surfaces plus its own customization namespace.
- Cross-tool governance, audit, migration, or alignment tasks must be explicitly requested before one assistant reads or edits the other assistant's customization namespace.
- Prefer the owning assistant to author changes in its namespace. Other assistants may review or propose changes when explicitly asked.
- When shared repo conventions change, update `AGENTS.md` first, then refresh assistant-owned files that depend on it.

Assistant-specific operational guidance belongs in assistant-owned files:
- Claude-specific workflow and commands belong in `CLAUDE.md` and `.claude/**`.
- Copilot-specific agents, skills, prompts, and hooks belong in `.github/**`.

Shared governance details live in `docs/development/ai/assistant_customization_governance.md`.

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
