# Project Constitution

## Project Identity

**Name:** Jira Sprint Metrics Reporter  
**Purpose:** A local Python tool that fetches sprint data from Jira and generates HTML/Markdown reports containing velocity, cycle time, AI assistance trend, and DAU metrics. Designed for engineering teams to review sprint health.

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Runtime | Python 3.x |
| HTTP server | `http.server` (stdlib) — no Flask, no FastAPI |
| Templating | Jinja2 (`ui/templates/report.html.j2`) |
| Config | python-dotenv; all vars in `.env` (copied from `.env.example`) |
| Testing | pytest; four layers: `unit/`, `component/`, `integration/`, `e2e/` |
| Jira client | Custom REST wrapper (`app/core/jira_client.py`) |
| Frontend | Vanilla HTML/CSS/JS in `ui/`; no build toolchain |

## Design Principles

Apply these in order of precedence when making trade-offs:

1. **KISS** — Prefer stdlib and plain `dict` over third-party frameworks and custom classes. `HTTPServer`, not Flask. `dict` contracts, not dataclasses unless type safety is critical.
2. **Single Responsibility** — Each module has exactly one job. `metrics.py` computes; reporters render; `config.py` reads env. Never add fetch logic to a reporter.
3. **YAGNI** — Implement what the task requires. Flag (do not build) future needs. No speculative parameters or generalization.
4. **DRY** — Shared test data → `conftest.py` factories. Shared field definitions → `config/jira_schema.json`. Never duplicate a computation across reporters.
5. **Open/Closed** — Extend via extension patterns (new metric, new schema field, new server handler) — do not modify existing function signatures.

## Coding Standards

- No comments unless the WHY is non-obvious (hidden constraint, subtle invariant, workaround).
- No docstrings on functions whose name and signature are self-explanatory.
- Validate at system boundaries only (user input, external APIs); trust internal contracts.
- No error handling for scenarios that cannot happen.
- Logging: `logger = logging.getLogger(__name__)` per module. `SUCCESS` (level 25) for user-visible outcomes. Never log credential values.

## File Placement Rules

| Content type | Location |
|---|---|
| Application source | `app/` (core logic, reporters, utils) |
| Persistent config | `config/` (JSON, source-controlled) |
| Test suite | `tests/unit/`, `tests/component/`, `tests/integration/`, `tests/e2e/` |
| Documentation | `docs/development/` (architecture, pipeline) or `docs/product/` (metrics, requirements, features) |
| **Spec artifacts** | `specs/[feature-name]/` (spec-kit SDD output; source-controlled) |
| Temporary/generated | `generated/tmp/`, `generated/debug/`, `generated/reports/` (gitignored) |
| UI | `ui/templates/`, `ui/index.html`, `ui/css/`, `ui/js/` |

## Agent Ownership

| Agent | Write surfaces |
|---|---|
| `business-analyst` | `specs/`, `docs/`, `README.md`, `CHANGELOG.md`, `ui/templates/`, `ui/css/`, `ui/js/` |
| `developer` | `app/core/`, `app/server/`, `app/reporters/`, `app/utils/`, `config/`, `ui/` |
| `test-engineer` | `tests/` |
| `devops-engineer` | `.github/workflows/`, `pyproject.toml` |
| `ai-engineer` | `.claude/**`, `CLAUDE.md` |
| `solution-architect` | `docs/development/`, `config/jira_schema.json`, `config/jira_filters.json` |

## Spec-to-Requirements Traceability

- `specs/[feature-name]/spec.md` is the upstream planning artifact — it does **not** replace requirements tables.
- After a spec is approved, `business-analyst` maps acceptance criteria to `docs/product/requirements/<topic>_requirements.md` status columns.
- Status values are exactly `✓ Met`, `✗ Not met`, `⬜ N/T` — no other variants.
- Never add new rows or new requirements files without explicit Product Owner approval.
- Requirements index: `docs/product/requirements/README.md` maps topic areas to file names and ID prefixes.

## UI Design Constraints

- No logic in Jinja2 templates — `.j2` files receive pre-computed data only.
- Semantic HTML: use `<section>`, `<table>`, `<figure>`, `<nav>` — not bare `<div>` wrappers.
- Responsive layout: `%`, `rem`, CSS Grid/Flexbox — no fixed-width `px` containers.
- WCAG AA colour contrast (4.5:1 for normal text) is a hard requirement.
- `aria-label` on all interactive controls.

## Security Non-Negotiables

- No command injection, XSS, SQLi, or other OWASP Top 10 vulnerabilities.
- No credentials or secrets in source; `.env` files are gitignored.
- TLS validation via `app/utils/cert_utils.py` — never skip certificate verification.

## What NOT to Build

- No web framework (no Flask, FastAPI, Django).
- No database (Jira is the data source; reports are generated files).
- No authentication layer (tool is local/internal use only).
- No speculative features, flags, or backwards-compatibility shims.
