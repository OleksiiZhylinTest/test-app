---
name: copilot-env-governance
description: 'Govern GitHub Copilot customization files safely and with minimal context. Use for Copilot agents, skills, prompts, hooks, guardrails, summaries, MCP guidance, or context-cost reduction work.'
argument-hint: 'Describe the Copilot environment change or governance task'
user-invocable: true
---

# Copilot Environment Governance

Use this skill for GitHub Copilot environment work in this repository.

## When to Use

- Creating or refining Copilot agents, skills, prompts, hooks, or summaries.
- Auditing Copilot customization drift.
- Reviewing Copilot context cost or security posture.

## Procedure

1. Read `AGENTS.md` and `.github/summaries/copilot-governance.md` first.
2. Prefer existing `.github/summaries/**` and local `.github/**` assets before broader repo docs, and escalate to `docs/development/ai/assistant_customization_governance.md` only when you need the full review checklist or are changing the ownership model itself.
3. Stay inside `.github/**` unless the user explicitly requests cross-tool governance.
4. Call out security-sensitive implications whenever the change touches hooks, MCP, telemetry, or external-system access.
5. Return the smallest viable change, any shared-layer impact in `AGENTS.md`, and a lower-cost alternative when one exists.

## Output

- Name the affected Copilot-owned files.
- Note any shared-layer changes needed in `AGENTS.md`.
- Flag context-cost and security implications.