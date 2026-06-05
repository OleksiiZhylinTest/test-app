# Copilot Summary: GH Project Manager Routing

Use this as the first context anchor whenever the GH Project Manager needs to classify and route an incoming request.

## Source of Truth

- `.github/agents/gh-project-manager.agent.md`
- `AGENTS.md` (shared conventions and module map)

## Request Type → Delegate → Anchor

| Request type | Primary delegate | First anchor file |
|-------------|-----------------|-------------------|
| Feature / improvement | `GH Explore` (impact) → GH specialist agent (implement) | `AGENTS.md` |
| Bug fix | `GH Explore` (locate) → GH specialist agent (fix) | `AGENTS.md` |
| Copilot env / governance / MCP / monitoring | `GH AI Architect` → `GH AI Engineer` | `.github/summaries/copilot-governance.md` |
| `.claude/` or `.github/` folder content / structure / explanation | `GH AI Architect` | `.github/summaries/copilot-governance.md` |
| `AGENTS.md` or `CLAUDE.md` read / write / explanation | `GH AI Architect` (cross-tool confirmation required for `CLAUDE.md` writes) | `AGENTS.md`, `.github/summaries/copilot-governance.md` |
| Token consumption / AI env audit / AI assistant environment | `GH AI Architect` | `.github/summaries/copilot-governance.md` |
| External research / vendor docs | `GH Web Search` | `.github/summaries/external-research-policy.md` |
| Codebase discovery (>3 files) | `GH Explore` | `AGENTS.md` |
| Architecture / module design / structural change | `GH Principal Solution Architect` → `GH Solution Architect` | `docs/development/architecture.md` |
| Quality framework / NFR / test layer strategy | `GH Principal Solution Architect` → `GH Solution Architect` | `docs/product/requirements/` |
| Requirements update | `GH Product Owner` → `GH Business Analyst` + `requirements-routing` skill | `docs/product/requirements/README.md` |
| Manual / exploratory testing | `GH Test Lead` → `GH Test Engineer (task_type: manual)` | `docs/product/features/features.md` |
| Test addition / layer selection | `GH Test Lead` → `GH Test Engineer (task_type: automation)` + `test-layer-selection` skill | `tests/conftest.py` |
| Performance testing | `GH Test Lead` → `GH Test Engineer (task_type: performance)` | `tests/` |
| Security review | `GH Test Lead` → `GH Test Engineer (task_type: security)` | `docs/product/requirements/app_non_functional_requirements.md` |
| Code implementation | `GH Dev Lead` → `GH Developer` | `AGENTS.md` |
| UI / UX design | `GH Product Owner` → `GH Business Analyst` | `docs/product/features/features.md` |
| Documentation / technical writing | `GH Product Owner` → `GH Business Analyst` | `docs/` |
| CI/CD pipeline | `GH DevOps Lead` → `GH DevOps` | `docs/development/pipeline.md` |
| Multi-type (≥2 categories) | Sequence per dependency order | `AGENTS.md` first |

## Direct Delegates of GH Project Manager

The GH Project Manager delegates to exactly 7 direct subagents:

| Subagent | Tools | Can edit? | Scope |
|----------|-------|-----------|-------|
| `GH AI Architect` | read, agent, search | No (read-only) — delegates implementation to `GH AI Engineer` | Copilot env, governance, MCP |
| `GH Principal Solution Architect` | read, search, agent | No (read-only) — delegates to `GH Solution Architect` | Architecture strategy, module design |
| `GH Web Search` | read, search | No | External docs, vendor references |
| `GH Product Owner` | read, search | No (read-only) — delegates to `GH Business Analyst` | Requirements, features, priorities |
| `GH Dev Lead` | read, search, agent | No (read-only) — delegates to `GH Developer` | Code review, implementation approval |
| `GH Test Lead` | read, search, agent | No (read-only) — delegates to `GH Test Engineer` | Test strategy, coverage gates |
| `GH DevOps Lead` | read, search, agent | No (read-only) — delegates to `GH DevOps` | CI/CD strategy, pipeline approval |

## Agent Isolation Rules

- GH Project Manager delegates only to GH Copilot agents listed in `.github/agents/`.
- Claude agents (`.claude/agents/**`) must never be invoked by any GH Copilot agent.
- `.claude/**` is off-limits for modification by any GH Copilot agent.
- Reading `.claude/**` is permitted only when the user explicitly requests cross-tool governance, audit, or alignment.

## Plan Confirmation Threshold

Present a plan and confirm with the user before delegating when any of these are true:
- Request requires ≥3 sub-tasks
- Request touches shared contracts (API shapes, metric definitions, test fixtures)
- Request involves cross-tool governance (Copilot ↔ Claude surfaces)
- Security implications are present

## Skills Available to GH Project Manager

| Skill | When to invoke |
|-------|---------------|
| `project-orchestration` | Structuring the delegation sequence for any multi-part request |
| `task-breakdown` | Decomposing ambiguous or broad requests into typed sub-tasks |
| `requirements-routing` | Mapping a feature area to the correct requirements file |
| `test-layer-selection` | Choosing the narrowest test layer for a code change |
| `architecture-lookup` | Locating the owning module without loading the full architecture doc |

## Entry-Point Prompts

| Prompt | Use case |
|--------|---------|
| `project-task-intake` | Default starting point for any new request |
| `feature-planning` | Full sprint/feature planning with impact analysis and sub-task sequencing |

## Escalate to Full Agent Instructions When

- You are changing the PM's delegation model or adding new subagents.
- You are resolving a cross-tool governance conflict.
- The plan involves ≥5 sub-tasks spanning every repo surface.
