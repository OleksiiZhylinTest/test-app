# Claude Code Agent Roster

This file is the authoritative reference for Claude Code SDLC agents and cross-assistant routing. It is referenced from `AGENTS.md`.

## Primary Entry Point

`project-manager` subagent (`.claude/agents/project-manager.md`) handles intake and routing for all requests. Delegates to 7 direct reports (L1 delegates); each L1 delegate applies the Maker-Checker review loop before accepting work from its leaf agents.

> **Cross-assistant routing (X2):** For tasks that span both Claude and Copilot sides, route the Claude-side work to `ai-architect` → `ai-engineer`. Flag the Copilot-side aspects as requiring a separate Copilot invocation. Never route Claude tasks to Copilot agents (`.github/agents/**`) — treat them as non-existent during normal Claude operation.

## Claude Code SDLC Agent Roster

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
| `business-analyst` | L2 Leaf | Requirements elicitation, user stories, gap analysis, documentation maintenance | `docs/`, `README.md`, `CHANGELOG.md`, `ui/`, `specs/[feature-name]/` |
| `developer` | L2 Leaf | Full-stack implementation: Python, API routes, reporters, UI | `app/core/`, `app/server/`, `app/reporters/`, `app/utils/`, `config/`, `ui/templates/`, `ui/index.html`, `ui/css/`, `ui/js/` |
| `test-engineer` | L2 Leaf | Exploratory testing, automation, performance, security review | `tests/`, `generated/tmp/`, `generated/debug/` |
| `devops-engineer` | L2 Leaf | Pipeline implementation, Dockerfile, deploy scripts | `.github/workflows/`, `docs/development/pipeline.md`, `pyproject.toml` |

RACI matrix and Maker-Checker Protocol: `.claude/sdlc-raci.md`.
