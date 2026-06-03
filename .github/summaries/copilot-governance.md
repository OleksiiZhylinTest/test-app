# Copilot Summary: Assistant Customization Governance

Use this summary for ownership, boundaries, and cross-tool escalation before loading the full governance doc.

## Source of Truth

- `docs/development/assistant_customization_governance.md`
- `AGENTS.md`

## Agent Hierarchy

| Agent | Role | Delegates to |
|-------|------|-------------|
| `GH Project Manager` | Top-level orchestrator; first-contact for all requests | `GH AI Architect`, `GH Web Search`, `Explore` |
| `GH AI Architect` | Copilot env, governance, MCP, monitoring, security | `GH Web Search`, `Explore` |
| `GH Web Search` | External docs lookup only; read-only | — |

**Entry point**: always start with `GH Project Manager` (via `project-task-intake` prompt) unless the task is explicitly scoped to Copilot environment work.

## Ownership at a Glance

| Surface | Owner | Default access |
|---------|-------|----------------|
| `AGENTS.md`, project code, tests, config, normal docs | Shared | Both assistants may read and edit |
| `CLAUDE.md`, `.claude/**` | Claude Code | Claude edits; GH Copilot must never modify; GH Copilot may read only when user explicitly requests cross-tool governance |
| `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, `.github/hooks/**` | GitHub Copilot | Copilot edits; Claude should not touch by default |

## Key Rules

- Shared repo facts belong in `AGENTS.md`, not duplicated into both namespaces.
- Claude behavior stays in `CLAUDE.md` or `.claude/**`; Copilot behavior stays in `.github/**`.
- MCP configuration is assistant-scoped; do not reuse Claude wrappers for Copilot.
- No secrets in any assistant customization file.
- GH Copilot agents must never modify `.claude/**` — no exceptions.
- GH Copilot agents must not invoke or delegate to Claude agents (`.claude/agents/**`).

## Cross-Tool Access

Cross-tool inspection or editing is allowed only when the user explicitly requests one of:
- cross-tool governance
- cross-tool audit
- migration between assistant surfaces
- alignment review between Claude and Copilot customizations

When cross-tool work is approved, prefer the owning assistant to author final changes in its namespace.

## Hook Enforcement Note

`pre_tool_copilot_boundary.py` is Claude-invoked only. GitHub Copilot boundary enforcement relies on agent instructions, skill procedures, and the agent `tools` list, not a runtime hook. See `.github/hooks/copilot-customization-boundary.json` for details.

## Escalate to Full Governance Doc When

- you need the exact review checklist before merging customization changes
- you are designing a new cross-tool integration pattern
- you are changing the ownership model itself
