---
name: Claude Governance Summary
description: Claude namespace ownership rules, bypass mechanisms, and cross-tool governance anchor. Use before loading docs/development/ai/assistant_customization_governance.md.
type: reference
---

# Claude Governance Summary

> Lightweight anchor. Load before `docs/development/ai/assistant_customization_governance.md`.

## Namespace Ownership

| Owner | Surfaces |
|-------|---------|
| Claude | `CLAUDE.md`, `.claude/**` (agents, commands, skills, hooks, settings) |
| Copilot | `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, `.github/hooks/**` |
| Shared | `AGENTS.md`, all `app/`, `tests/`, `docs/`, `config/`, `ui/` |

## Cross-Tool Access Rules

- Claude agents must **not** read `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, or `.github/hooks/**` during normal operation.
- Claude agents may read `.github/workflows/` **only** when a task explicitly requires CI/CD review.
- Claude agents must **not** modify any Copilot-owned file without `ALLOW_CROSS_ASSISTANT_CUSTOMIZATION_EDIT=1` set **and** an explicit user request.
- Prefer the owning assistant to author final changes in its namespace.

## Bypass Mechanism

```
ALLOW_CROSS_ASSISTANT_CUSTOMIZATION_EDIT=1
```

Set in the environment to permit Claude to edit Copilot-owned surfaces for a single approved task.
Must be accompanied by explicit user authorization naming the target file(s).

## Claude Edit Protection

`pre_edit_customization_boundary.sh` (PreToolUse: Edit|Write) blocks edits to Claude-owned surfaces without explicit approval — prevents accidental self-modification.

## Agent Routing Constraint

Claude agents delegate only to agents defined in `.claude/agents/`. Never invoke Copilot agents (`.github/agents/**`) — treat as non-existent during normal operation.

## Authority Chain

```
docs/development/ai/assistant_customization_governance.md  ← authoritative full doc
CLAUDE.md § Customization Ownership                        ← Claude-specific rules
AGENTS.md § Assistant Ownership Model                      ← shared assistant-neutral layer
this file                                                  ← cheap read anchor
```

## Drift Check Checklist

When auditing governance compliance, verify:

1. `CLAUDE.md` Customization Ownership section matches ownership table above
2. `AGENTS.md` Assistant Ownership Model table reflects current namespace split
3. No Claude-specific guidance leaked into `AGENTS.md` (shared layer stays neutral)
4. `pre_edit_customization_boundary.sh` is registered in `.claude/settings.json`
5. No `.github/agents/**` or `.github/skills/**` path appears in any `.claude/agents/*.md` workflow step
