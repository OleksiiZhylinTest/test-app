---
name: Agent Index
description: One-line index of all enabled Claude agents — name, tier, trigger, owned surface, tools, subagents. Use to scope which agent to invoke without reading individual agent files.
type: reference
---

# Agent Index — 14 Claude Agents

> Anchor before loading individual `.claude/agents/*.md` files.
> Framework: nexus-agentic-sdlc 1.0.0

## Orchestrator

| Agent | Trigger | Owned Surface | Tools | Delegates to |
|-------|---------|---------------|-------|-------------|

## L1 Leads (read-only / checker role)

| Agent | Trigger | Owned Surface | Tools | Delegates to |
|-------|---------|---------------|-------|-------------|

\* `dev-lead` Edit/Write restricted to `generated/tmp/` only.

## L2 Leaf Agents (scoped write access)

| Agent | Trigger | Write Surface | Tools |
|-------|---------|---------------|-------|
| `developer` | App code, server, reporters, utils, UI templates | Application source + config | Read, Edit, Write, Bash, Glob, Grep |

## SDD Track Routing

| Track | Scope | Lead + Leaf pair |
|-------|-------|-----------------|
| Track 0 — AI Ecosystem | `.claude/**`, agent defs, hooks | `ai-architect` → `ai-engineer` |
| Track 1 — Product Feature | Application source, UI, config | spec-kit → `dev-lead` → `developer` |
| Track 2 — Tests/Coverage | `tests/`, coverage thresholds | `test-lead` → `test-engineer` |
| Track 3 — CI/CD & Infra | `.github/workflows/`, Docker | `devops-lead` → `devops-engineer` |
