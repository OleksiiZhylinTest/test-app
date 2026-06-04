# Assistant Customization Governance

This repository supports two AI assistants with a shared repository layer and separate customization namespaces:

- `AGENTS.md` is the shared, assistant-neutral instruction surface.
- `CLAUDE.md` and `.claude/**` are Claude Code-owned.
- `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, and `.github/hooks/**` are GitHub Copilot-owned.

The goal is to let both assistants work in the same repository without silently reading, editing, or depending on each other's private customization layers.

## Ownership Matrix

| Surface | Owner | Default access |
|---------|-------|----------------|
| `AGENTS.md` | Shared | Both assistants may read and should align to it |
| Project code, tests, config, and normal docs | Shared | Both assistants may read and edit when the task requires it |
| `CLAUDE.md`, `.claude/**` | Claude Code | Claude may read and edit; Copilot should not touch by default |
| `.github/agents/**`, `.github/skills/**`, `.github/prompts/**`, `.github/hooks/**`, `.github/summaries/**` | GitHub Copilot | Copilot may read and edit; Claude should not touch by default |
| `ai-engineer` (Claude variant) write scope | Claude Code | `ai-engineer` may write to `.claude/**` (excl. `settings*.json`), `CLAUDE.md`, and `.vscode/`; it must not write to `.github/**` |
| `gh-ai-engineer` (Copilot variant) write scope | GitHub Copilot | `gh-ai-engineer` may write to `.github/**`, `AGENTS.md`, and `.vscode/`; it must not write to `.claude/**` |

## Source of Truth Hierarchy

1. Shared repository facts, architecture, and conventions live in `AGENTS.md` and referenced project docs.
2. Claude-specific workflow, hooks, commands, and local operating rules live in `CLAUDE.md` and `.claude/**`.
3. Copilot-specific agents, skills, prompts, hooks, and environment rules live in `.github/**`.

If a rule belongs to all assistants, put it in `AGENTS.md`.
If a rule belongs to only one assistant, keep it in that assistant's owned namespace.

## Default Operating Scope

Normal assistant behavior should follow these rules:

- Claude works in shared repo surfaces plus `CLAUDE.md` and `.claude/**`.
- Copilot works in shared repo surfaces plus `.github/**` Copilot customization files.
- Neither assistant should inspect or modify the other assistant's customization namespace during normal feature work or environment work.

This prevents hidden coupling between Claude-only workflows and Copilot-only workflows.

## Cross-Tool Exceptions

Cross-tool behavior is allowed only when the user explicitly requests one of these tasks:

- cross-tool governance
- cross-tool audit
- migration between assistant surfaces
- alignment review between Claude and Copilot customizations

When a cross-tool task is explicitly requested:

- one assistant may inspect the other assistant's customization files to identify risks, overlaps, or drift
- prefer the owning assistant to author the final changes in its namespace
- if one assistant edits the other assistant's namespace by request, it must preserve ownership boundaries and document the reason
- Claude-side edit protection can be intentionally bypassed for a one-off approved task by setting `ALLOW_CROSS_ASSISTANT_CUSTOMIZATION_EDIT=1`.
- Copilot-side workspace hooks should ask for approval before tool access that targets `CLAUDE.md` or `.claude/**`.

## MCP Separation

External systems may be available to both assistants, but MCP configuration remains assistant-scoped.

- Claude MCP configuration belongs in `.claude/**`.
- Copilot MCP configuration belongs in Copilot-supported customization surfaces.
- Do not reuse Claude MCP wrappers or secret injection files directly for Copilot.
- Do not commit secrets, tokens, or credentials into shared repo customization files.

## Review Checklist

Before merging assistant-customization changes, verify the following:

1. `AGENTS.md` stays assistant-neutral.
2. No Claude-only operational guidance leaks into Copilot-owned files.
3. No Copilot-only operational guidance leaks into Claude-owned files.
4. Shared repo rules remain in shared docs rather than being duplicated into both namespaces.
5. Any cross-tool change is explicitly justified in the change description.
6. No assistant-owned customization file embeds secrets.

## Practical Rule

When in doubt:

- shared repo facts go in `AGENTS.md`
- Claude behavior goes in `CLAUDE.md` or `.claude/**`
- Copilot behavior goes in `.github/**`
- cross-tool coordination is explicit, not implicit

## Maker-Checker Cross-Assistant Note

The Maker-Checker review loop protocol is replicated in both assistant namespaces:

- **Copilot side**: `.github/summaries/maker-checker-protocol.md` (canonical Copilot reference)
- **Claude side**: `.claude/sdlc-raci.md` § Maker-Checker Protocol

Both files define the same loop mechanics, 3-cycle cap, and escalation message format. When the protocol is updated, both files must be updated in sync. The Copilot-side reference is the first-contact spec; the Claude-side reference is its mirror. Neither supersedes the other.