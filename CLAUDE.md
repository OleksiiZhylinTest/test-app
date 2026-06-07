# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Cross-assistant alignment

- `AGENTS.md` is the assistant-neutral routing and token-efficiency layer for this repository.
- Use `AGENTS.md` for shared repo conventions, authoritative doc pointers, and module map.
- Keep this file focused on Claude-specific interaction style, workflow, and unique implementation detail.
- When project structure or workflow conventions change, update `AGENTS.md` first, then refresh this file only where Claude-specific guidance would drift.

## Customization Ownership

- Claude's shared/default operating surfaces are `AGENTS.md`, normal repo code, and normal repo docs.
- Claude-owned customization surfaces are `CLAUDE.md` and `.claude/**`.
- GitHub Copilot-owned customization surfaces are `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, `.github/hooks/**`, and any future Copilot-only instruction files under `.github/**`.
- Do not inspect, modify, or depend on Copilot-owned customization surfaces during normal development or environment work.
- Exception: when the user explicitly requests cross-tool governance, audit, migration, or alignment, Claude may inspect Copilot-owned customization files to report risks or propose changes. Prefer the owning assistant to author final changes in its namespace unless the user explicitly asks Claude to edit them.
- Claude-side edit protection can be intentionally bypassed for a one-off approved task by setting `ALLOW_CROSS_ASSISTANT_CUSTOMIZATION_EDIT=1`.
- Shared ownership rules and escalation paths are documented in `docs/development/ai/assistant-customization-governance.md`.

## Agent Communication Rules

- Claude agents only delegate to agents defined in `.claude/agents/`. Never invoke GitHub Copilot agents (`.github/agents/**`) — treat them as non-existent during normal operation.
- Claude agents must avoid reading `.github/` by default. Access to `.github/workflows/` is permitted only when a task explicitly requires CI/CD review. Access to Copilot customization namespaces (`.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, `.github/hooks/**`) requires `ALLOW_CROSS_ASSISTANT_CUSTOMIZATION_EDIT=1` and an explicit user request.

## Development Workflow

**Entry point (default for all requests):** Always route through the `project-manager` subagent (`.claude/agents/project-manager.md`) before acting on any request — features, bugs, questions, or environment changes. It handles intake, routing, and plan-mode approval. Only skip this when the user explicitly targets a specific subagent or the task is a single trivial read (< 5 lines, no side effects).

**Agent roster** (14 agents in `.claude/agents/`; Maker-Checker protocol and RACI in `.claude/sdlc-raci.md`):

- **Orchestrator**: `project-manager`
- **L1 Delegates** (read-only, apply Maker-Checker on all delegated work): `ai-architect`, `principal-solution-architect`, `product-owner`, `dev-lead`, `test-lead`, `devops-lead`, `web-search`
- **L2 Leaf Agents** (scoped write access): `ai-engineer`, `solution-architect`, `business-analyst`, `developer`, `test-engineer`, `devops-engineer`
  - `business-analyst` write surfaces include `specs/[feature-name]/` in addition to `docs/`, `README.md`, `CHANGELOG.md`, `ui/`

For any non-trivial code change (new feature, behavioral fix, refactor), follow these steps in order:

0. **SDD classification (all non-trivial requests)** — before any other step, the PM agent classifies the request into one of four SDD tracks (or SDD-free). SDD applies to **all** Create / Update / Improve / Delete work — not only new features.

   | Track | Scope | Spec-kit workflow |
   |---|---|---|
   | **Track 0 — AI Ecosystem** | `.claude/**`, agent definitions, hooks | No spec-kit; AI Architect → AI Engineer Maker-Checker loop |
   | **Track 1 — Product Feature** | `app/`, `ui/`, `config/`, user-visible behavior | Full spec-kit: `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` |
   | **Track 2 — Tests / Coverage** | `tests/`, coverage thresholds | No spec-kit; Test Lead → Test Engineer Maker-Checker loop |
   | **Track 3 — CI/CD & Infra** | `.github/workflows/`, Dockerfile, deployment scripts | No spec-kit; DevOps Lead → DevOps Engineer Maker-Checker loop |

   For Track 1: artifacts land in `specs/NNN-feature-name/` (authored by `business-analyst`, approved by `product-owner`). Human approval of `specs/NNN-feature-name/tasks.md` is required before proceeding to step 1.

   SDD-free requests (explain, audit, code review, execute tests, read docs) skip this step entirely — see `.claude/agents/project-manager.md § SDD Decision Framework`.

1. **Maintain requirements** — identify the relevant file(s) using `docs/product/requirements/README.md` (lists all files and their ID prefixes); update the `Status` column (`✓ Met`, `✗ Not met`, `⬜ N/T`) for rows whose acceptance criterion is affected. Do not add rows or create new files.
2. **Maintain application functionality** — implement the feature, fix, or refactor.
3. **Maintain tests** — write or update tests in the narrowest layer that proves the changed behavior.
4. **Complete testing and verification** — run `python tests/runners/run_all_checks.py`; fix all failures before proceeding.
5. **Maintain test coverage** — run `python tests/tools/test_coverage.py` after adding, removing, or renaming test functions.
6. **Maintain project documentation** — update relevant docs when behavior changes:
   - `docs/product/metrics/` — when metric behavior or output shape changes
   - `docs/development/architecture.md` — when modules are added or restructured
   - `README.md` — when setup steps, commands, or project purpose changes
   - `docs/product/features/features.md` — when UI or user-visible behavior changes

## Interaction Style

**Provide recommendations proactively:** before implementing, propose design alternatives with trade-off explanations; after finishing, suggest logical follow-up tasks (e.g. "the metric doc may also need updating").

**Ask clarifying questions before acting when:**
- A change touches multiple areas (core + reporters + tests + docs) — ask about priorities or constraints.
- A change might break existing metrics contracts, API shapes, or test expectations.

## Coding Standards

### Design Principles (Python code)

| Principle | Project-specific application |
|-----------|------------------------------|
| **Single Responsibility** | Each module has one job: `metrics.py` computes only, reporters render only, `config.py` reads env only. Never add fetch logic to a reporter. |
| **Open/Closed** | Extend via the Extension Patterns below (new metric, new schema field, new server handler) — don't modify existing function signatures. |
| **DRY** | Shared test data → `conftest.py` factories. Shared field definitions → `config/jira_schema.json`. Never duplicate a computation across reporters. |
| **KISS** | Prefer stdlib and plain `dict` over frameworks and custom classes. `HTTPServer` not Flask; `dict` contracts not dataclasses unless type safety is critical. |
| **YAGNI** | Implement what the task requires; flag (don't build) future needs. No speculative parameters or generalization. |

### Logging Conventions

Extends global `CLAUDE.md` logging rules. Project adds `SUCCESS` (level 25, between INFO and WARNING) for user-visible positive outcomes (report written, server ready). Log at the call site; never log credential values.

### UI Design Conventions (for `ui/templates/report.html.j2` and `ui/index.html`)

- **No logic in templates**: `.j2` files receive pre-computed data only; all conditionals and loops that involve business logic belong in `report_html.py`.
- **Semantic HTML**: use `<section>`, `<table>`, `<figure>`, `<nav>` — not bare `<div>` wrappers.
- **Responsive layout**: avoid fixed-width `px` values for containers; prefer `%`, `rem`, or CSS Grid/Flexbox.
- **Accessibility**: include `aria-label` on interactive controls; maintain WCAG AA color contrast (4.5:1 for normal text).

## Generated and Temporary Files

Extends global `CLAUDE.md` file placement rules. Subdirectory convention: `generated/tmp/` for scratch, `generated/debug/` for diagnostics, `generated/reports/` for report artifacts. Never move source files into `generated/`.

## Spec-Driven Development Skills (spec-kit)

Invoked as slash commands in Claude Code. Skills live in `.claude/skills/speckit-*/SKILL.md`.

| Skill | Purpose |
|-------|---------|
| `/speckit-specify <description>` | Create `specs/NNN-feature/spec.md` from feature description |
| `/speckit-clarify` | Resolve `[NEEDS CLARIFICATION]` markers in the active spec |
| `/speckit-plan` | Produce `specs/NNN-feature/plan.md` (technical approach) |
| `/speckit-tasks` | Produce `specs/NNN-feature/tasks.md` (ordered task breakdown) |
| `/speckit-analyze` | Cross-check spec/plan/tasks for coverage gaps |
| `/speckit-chain` | Generate `specs/NNN-feature/execution-plan.md` — full agent delegation chain with parallel groups, agent read/write scope, and Maker-Checker gates; **requires human approval before `/speckit-implement`** |
| `/speckit-implement` | Drive implementation from approved `tasks.md` + `execution-plan.md` |
| `/speckit-checklist` | Generate/update quality checklists |
| `/speckit-taskstoissues` | Convert `tasks.md` items to GitHub Issues |
| `/speckit-constitution` | Update `.specify/memory/constitution.md` |
| `/speckit-report [NNN-feature]` | Generate `specs/NNN/session-telemetry.md`, `specs/NNN/sdlc-report.md`, and `specs/NNN/ai-architect-audit.md` after SDLC completion |

Run the full workflow in order: specify → clarify → plan → tasks → analyze → **(human approval of tasks.md)** → chain → **(human approval of execution-plan.md)** → implement → **(test-lead COMPLETE)** → **report** (auto-triggered by PM).

### Slash Command Placement Rule

| Use `.claude/commands/<name>.md` | Use `.claude/skills/<name>/SKILL.md` |
|----------------------------------|--------------------------------------|
| Prose workflow checklist — ordered steps, no arguments | Parameterized command — accepts `$ARGUMENTS` |
| Multi-step orchestration guide Claude follows | Needs frontmatter metadata (`argument-hint`, `compatibility`, `user-invocable`) |
| No special dispatch required | Requires skill-dispatch features (`disable-model-invocation`, etc.) |

When in doubt: if your command takes no input and is just "do these steps", use `.claude/commands/`. If it takes a description or identifier as input, use `.claude/skills/`.

## Commands

```bash
# Setup
pip install -r requirements.txt        # install into .venv
pip install -r requirements-dev.txt    # install + pytest for testing

# Generate reports (requires .env with Jira credentials)
python main.py                    # delegates to app/cli.py; outputs to generated/reports/<timestamp>/
python main.py --clean            # delete all generated/reports/ and exit
python main.py --clean-logs       # delete all generated/logs/ and exit

# Dev server (serves UI + proxies Jira API to avoid CORS)
python server.py                  # http://localhost:8080
python server.py 9000             # custom port

# Run all CI checks in parallel (lint + unit + component + windows + integration + e2e + security)
python tests/runners/run_all_checks.py                    # full suite (default)
python tests/runners/run_all_checks.py --smoke            # cross-layer smoke (~1-2 min) — run after every feature
python tests/runners/run_all_checks.py --sanity           # cross-layer smoke + sanity (~5-10 min) — run before push
python tests/runners/run_all_checks.py --full             # explicit full suite
python tests/runners/run_all_checks.py --skip-integration # full suite minus integration
python tests/runners/run_all_checks.py --skip-e2e         # full suite minus e2e

# Run a specific pytest subset directly
pytest tests/ -v

# Update tests/coverage/test_coverage.md after adding/removing tests (never hand-edit it)
python tests/tools/test_coverage.py
python tests/tools/test_coverage.py --dry-run   # preview only

# Documentation audit — scan docs/ for structure/content/format/link/gap issues
python tools/docs_audit.py docs/ --output generated/reports/docs-audit.md   # docs/ only (recommended)
python tools/docs_audit.py .    --output generated/reports/docs-audit.md   # full repo
python tools/docs_audit.py docs/ --output generated/reports/docs-audit.md --json  # + machine-readable findings
```

## Key Files Quick Reference

See `AGENTS.md § Module Map` — the authoritative, always-current source for module responsibilities and data-flow.
