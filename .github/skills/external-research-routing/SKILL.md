---
name: external-research-routing
description: 'Route GitHub Copilot to external documentation lookup only when local repo context is insufficient and the missing fact is outside the repository.'
argument-hint: 'Describe the unresolved question and the local sources already checked'
user-invocable: true
---

# External Research Routing

Use this skill when GitHub Copilot needs a disciplined fallback from local repo context to external documentation lookup.

## When to Use

- A local summary or owning file has already been checked.
- The unresolved fact concerns vendor docs, standards, external APIs, platform behavior, or current tool support.
- Broadening local exploration would add context cost without likely resolving the question.

## Procedure

1. Read `AGENTS.md`, `.github/summaries/copilot-governance.md`, and `.github/summaries/external-research-policy.md` first.
2. Confirm the problem is external, not repo-internal.
3. If no sanctioned external lookup capability is available in the runtime, stop and return a prerequisite note instead of widening repo search.
4. Delegate one concrete question to `Web Research` rather than an open-ended topic.
5. Require the compact brief schema from the policy summary: `Answer`, `Evidence`, `Sources`, `Confidence`, `Next action`.
6. Validate any resulting repo change locally before editing `.github/**`.

## Output

- Name the local source that was insufficient.
- State why external research was necessary.
- Return the compact brief or the prerequisite note.
- Flag any security-sensitive implications for MCP, secrets, or prompt-injection risk.