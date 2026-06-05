# Dev Conventions

Source of truth: `AGENTS.md` (Key Conventions) and `CLAUDE.md` (Design Principles)

## Python Conventions

| # | Rule |
|---|------|
| 1 | `logger = logging.getLogger(__name__)` per module — never `print()`, never root logger |
| 2 | Log levels: DEBUG = internal state · INFO = flow milestones · WARNING = recoverable problems · ERROR = failures · SUCCESS (25) = positive outcomes |
| 3 | Never log credential values |
| 4 | New config variables: add to `.env.example` first, then `app/core/config.py` via `os.getenv()` |
| 5 | No error handling for scenarios that cannot happen |
| 6 | YAGNI: no features, refactors, or abstractions beyond what the task requires |
| 7 | Validate only at system boundaries (user input, external APIs) — trust internal contracts |
| 8 | Single Responsibility: each module has one job; never add fetch logic to reporters or business logic to config |
| 9 | DRY: shared test data → `conftest.py`; shared field definitions → `config/jira_schema.json` |
| 10 | KISS: prefer stdlib and plain `dict` over frameworks and custom classes |

## JavaScript Conventions

| # | Rule |
|---|------|
| 11 | Vanilla JS only — no bundler, no framework imports |
| 12 | No inline `<script>` blocks — all JS lives in `ui/js/` files |
| 13 | No `eval()`, no `innerHTML` from user-controlled data, no `document.write()` |
| 14 | Use `addEventListener` for event binding — no `onclick` attributes |

## CSS/Layout Conventions

| # | Rule |
|---|------|
| 15 | No fixed-width `px` containers — use `%`, `rem`, CSS Grid, or Flexbox |
| 16 | No inline styles for layout — use CSS classes |

## Workflow Rules

| # | Rule |
|---|------|
| 17 | Never bypass CI hooks (`--no-verify`) without explicit user instruction |

## Escalate to Source When

- Convention nuance or full context needed → read `CLAUDE.md` (Design Principles, Logging Conventions)
- Module boundaries, test pyramid, CI stages → read `AGENTS.md` (Key Conventions, Module Map)
- UI design contracts, accessibility, Jinja2 template rules → read `CLAUDE.md` (UI Design Conventions)
