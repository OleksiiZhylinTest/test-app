# Copilot Summary: Assistant Customization Governance

Use this summary for ownership, boundaries, and cross-tool escalation before loading the full governance doc.

## Source of Truth

- `docs/development/ai/assistant_customization_governance.md` — ownership model, cross-tool boundaries, review checklist
- `docs/development/ai/agent-orchestration.md` — full 21-agent roster and 3-tier delegation hierarchy
- `docs/development/ai/README.md` — index for the ai/ documentation folder
- `AGENTS.md`

## Agent Hierarchy

| Agent | Role | Delegates to |
|-------|------|-------------|
| `GH Project Manager` | Top-level orchestrator; first-contact for all requests | `GH AI Architect`, `GH Web Search`, `Explore` |
| `GH AI Architect` | Copilot env, governance, MCP, monitoring, security | `GH Web Search`, `Explore` |
| `GH Web Search` | External docs lookup only; read-only | — |

**Entry point**: always start with `GH Project Manager` (via `project-task-intake` prompt) unless the task is explicitly scoped to Copilot environment work.

> **Speckit SDLC agents**: invoked on-demand via `/speckit-*` prompts only. See `.github/agents/speckit.*.agent.md` for definitions.

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

## Agent Runtime Rules

These rules apply to every Copilot agent at runtime. Individual agents must not repeat them inline — reference this section instead.

### `.claude/**` Boundary

1. **No writes.** Agents must never create, modify, or delete any file under `.claude/**` under any circumstances.
2. **No default reads.** Agents must not read `.claude/**` during normal task execution. Reading is permitted only when the user explicitly requests cross-tool governance, audit, migration, or alignment.
3. **No delegation to Claude agents.** Agents must not invoke or delegate to any agent defined under `.claude/agents/**`. Treat those agents as non-existent during normal Copilot operation.

### Generated Artifacts

4. **Artifacts stay in `generated/`.** Any file produced by an agent during task execution (reports, debug output, tmp files, bug reports, audit trails) must be written under `generated/` only. Agents must never write runtime artifacts into the source tree (`app/`, `tests/`, `docs/`, `config/`, `ui/`, `.github/`, etc.).
