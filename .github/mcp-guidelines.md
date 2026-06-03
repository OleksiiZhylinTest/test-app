# Copilot MCP Guidelines

Use this document as the first Copilot-owned reference when designing, reviewing, or expanding MCP usage in this repository.

## Scope

- This document governs GitHub Copilot MCP usage only.
- Claude MCP configuration remains Claude-owned under `.claude/**`.
- Do not reuse Claude wrapper scripts or Claude secret-injection files directly for Copilot.

## Security Rules

- Never commit secrets, tokens, API keys, or personal credentials into `.github/**` files.
- Prefer service accounts over personal accounts for shared external systems.
- Use least-privilege scopes for every MCP server.
- Keep MCP server access restricted to the smallest set of Copilot agents or prompts that need it.
- Use sanitized examples only in MCP-related docs, prompts, skills, and agents.

## Assistant Boundary Rules

- Treat Copilot MCP configuration as Copilot-owned infrastructure.
- Treat Claude MCP configuration as Claude-owned infrastructure.
- Shared external systems such as GitHub or Jira may exist for both assistants, but secret injection, wrappers, and local config remain assistant-scoped.
- Cross-tool governance for MCP is explicit, not implicit.

## Configuration Guidance

- Prefer environment-variable injection over inline credentials.
- Document required environment variable names, not example secrets.
- Prefer local workstation configuration or secure secret stores over repo-shared files for credential material.
- If a server needs special setup steps, document them here or in a Copilot-owned companion doc instead of embedding them in agent instructions.

## Local Configuration Path

- In this repository, treat `.vscode/mcp.json` as the local-only Copilot MCP wiring path.
- `.vscode/mcp.json` is gitignored and should remain uncommitted.
- Keep repo-shared guidance in `.github/**`, but keep executable MCP server registration and secrets in local workstation configuration.
- Do not create committed Copilot MCP config files that duplicate what belongs in `.vscode/mcp.json`.

## External Research Pattern

- For external documentation lookup, prefer one narrowly scoped MCP server exposed only to the `GH Web Search` agent or its companion prompt.
- Do not widen that MCP access to unrelated Copilot agents by default.
- Prefer read-only web or documentation lookup behavior over general remote execution.
- Confirm the actual tool names exposed by the chosen server locally before depending on them in agent instructions.
- Use `.github/mcp-web-research-setup.md` as the companion setup reference for this pattern.

## Review Checklist

Before enabling or changing an MCP server for Copilot, verify:

1. The server is necessary for the workflow and not duplicating a built-in tool.
2. The access scope is minimal.
3. No secrets are stored in `.github/**`.
4. The configuration does not depend on `.claude/**` files.
5. The affected Copilot agents, prompts, or hooks are explicitly named.
6. The change is reviewed for prompt-injection and data-exposure risk.

## Hook Enforcement Note

The boundary hook in `.github/hooks/` uses Claude Code's `PreToolUse` hook schema and is invoked by Claude Code only. GitHub Copilot does not have an equivalent runtime hook system. Copilot boundary enforcement relies on:

- The `tools` list in `.github/agents/gh-ai-architect.agent.md` (least-privilege tool scope)
- Skill procedures that mandate summary-first context loading
- Agent instructions that prohibit Claude-owned surface access during normal work

This means Copilot boundary rules are declarative (instruction-enforced), not runtime-enforced. Keep agent `tools` lists narrow to compensate.



- Does this MCP server reduce real workflow cost or just add more tool surface?
- Can the task be solved with existing repo tools or summaries first?
- Which Copilot-owned asset actually needs the server?
- What is the blast radius if the MCP server is misconfigured or compromised?
