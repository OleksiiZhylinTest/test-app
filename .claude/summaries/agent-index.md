---
name: Agent Index
description: One-line index of all 14 Claude agents — name, tier, trigger, owned surface, tools, subagents. Use to scope which agent to invoke without reading individual agent files.
type: reference
---

# Agent Index — 14 Claude Agents

> Anchor before loading individual `.claude/agents/*.md` files.

## Orchestrator

| Agent | Trigger | Owned Surface | Tools | Delegates to |
|-------|---------|---------------|-------|-------------|
| `project-manager` | All intake — features, bugs, questions, env changes | `.claude/agents/`, routing, SDD classification | Read, Glob, Grep, Agent, Atlassian read, GitHub issues | All L1 leads |

## L1 Leads (read-only / checker role)

| Agent | Trigger | Owned Surface | Tools | Delegates to |
|-------|---------|---------------|-------|-------------|
| `ai-architect` | `.claude/**` governance, agent quality, AI ecosystem audit | `.claude/**` review | Read, Glob, Grep, Agent | `ai-engineer` |
| `dev-lead` | Code review, sprint tasks, implementation sign-off | `generated/tmp/` (audit trail only) | Read, Edit\*, Write\*, Bash, Glob, Grep, Agent, Atlassian, GitHub PR | `developer`, `web-search` |
| `devops-lead` | CI/CD strategy, pipeline governance, deployment coordination | Review only | Read, Glob, Grep, Agent, GitHub PR | `devops-engineer` |
| `principal-solution-architect` | Architecture decisions, module boundary review, ADR approval | Review only (write: `generated/tmp/`) | Read, Glob, Grep, Bash, Agent, Atlassian read | `solution-architect`, `web-search` |
| `product-owner` | Backlog, acceptance criteria, story refinement | Jira issues, Confluence pages, `specs/` | Read, Glob, Grep, Agent, Atlassian full | `business-analyst` |
| `test-lead` | Test strategy, coverage gates, quality sign-off | Test strategy review | Read, Edit, Bash, Glob, Grep, Agent, Atlassian, GitHub PR | `test-engineer` |
| `web-search` | External docs, CVEs, framework patterns | External URLs only | WebSearch, WebFetch, Glob, Grep, Read | — |

\* `dev-lead` Edit/Write restricted to `generated/tmp/` only.

## L2 Leaf Agents (scoped write access)

| Agent | Trigger | Write Surface | Tools |
|-------|---------|---------------|-------|
| `ai-engineer` | Track 0 implementation (agent files, hooks, commands) | `.claude/**` (not `settings.json`) | Read, Edit, Write, Bash, Glob, Grep, Agent |
| `business-analyst` | Specs, user stories, docs, README, CHANGELOG, ui/ | `specs/`, `docs/`, `README.md`, `CHANGELOG.md`, `ui/` | Read, Edit, Write, Bash, Glob, Grep, Agent, Atlassian full, Confluence write |
| `developer` | App code, server, reporters, utils, UI templates | `app/`, `config/`, `ui/` | Read, Edit, Write, Bash, Glob, Grep |
| `devops-engineer` | CI workflows, Dockerfile, deploy scripts | `.github/workflows/`, `Dockerfile`, deploy scripts | Read, Edit, Write, Bash, Glob, Grep, GitHub full |
| `solution-architect` | Architecture docs, ADRs, config JSON, quality strategy | `docs/development/`, `config/jira_schema.json`, `config/jira_filters.json`, `generated/tmp/` | Read, Edit, Write, Bash, Glob, Grep |
| `test-engineer` | Tests, test fixtures, coverage regeneration | `tests/` | Read, Edit, Write, Bash, Glob, Grep, Playwright |

## SDD Track Routing

| Track | Scope | Lead + Leaf pair |
|-------|-------|-----------------|
| Track 0 — AI Ecosystem | `.claude/**`, agent defs, hooks | `ai-architect` → `ai-engineer` |
| Track 1 — Product Feature | `app/`, `ui/`, `config/` | spec-kit → `dev-lead` → `developer` |
| Track 2 — Tests/Coverage | `tests/`, coverage thresholds | `test-lead` → `test-engineer` |
| Track 3 — CI/CD & Infra | `.github/workflows/`, Docker | `devops-lead` → `devops-engineer` |
