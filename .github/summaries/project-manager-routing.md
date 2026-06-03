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
| Copilot env / governance / MCP / monitoring | `GH AI Architect` | `.github/summaries/copilot-governance.md` |
| `.claude/` or `.github/` folder content / structure / explanation | `GH AI Architect` | `.github/summaries/copilot-governance.md` |
| `AGENTS.md` or `CLAUDE.md` read / write / explanation | `GH AI Architect` (cross-tool confirmation required for `CLAUDE.md` writes) | `AGENTS.md`, `.github/summaries/copilot-governance.md` |
| Token consumption / AI env audit / AI assistant environment | `GH AI Architect` | `.github/summaries/copilot-governance.md` |
| External research / vendor docs | `GH Web Search` | `.github/summaries/external-research-policy.md` |
| Codebase discovery (>3 files) | `GH Explore` | `AGENTS.md` |
| Requirements update | GH specialist agent + `requirements-routing` skill | `docs/product/requirements/README.md` |
| Test addition / layer selection | GH specialist agent + `test-layer-selection` skill | `tests/conftest.py` |
| Architecture / module design | `GH Explore` + GH specialist agent synthesis | `docs/development/architecture.md` |
| Multi-type (≥2 categories) | Sequence per dependency order | `AGENTS.md` first |

## Subagent Capabilities at a Glance

| Subagent | Tools | Can edit? | Scope |
|----------|-------|-----------|-------|
| `GH AI Architect` | read, agent, edit, search | Yes — `.github/**` only | Copilot env, governance, MCP |
| `GH Web Search` | read, search | No | External docs, vendor references |
| `GH Explore` | read, search | No | Any local codebase discovery (GH Copilot Explore subagent — not the Claude-side Explore agent) |

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
