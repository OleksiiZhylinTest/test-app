# AI Development Reference

This folder contains documentation for the AI assistant environment in this repository.

| Document | What it covers |
|----------|----------------|
| [Agent Orchestration](agent-orchestration.md) | Delegation hierarchy, agent roster by tier, Maker-Checker loop diagram |
| [Local Agentic Development Workflow](local-agentic-development-workflow.md) | Step-by-step guide: plan mode, slash commands, subagent invocation |
| [Assistant Customization Governance](assistant-customization-governance.md) | Claude vs Copilot ownership model, cross-tool rules, Maker-Checker sync |

Operational specs (not user-facing reference docs):
- Agent definitions: `.claude/agents/*.md` (Claude), `.github/agents/*.md` (Copilot)
- SDLC RACI + Maker-Checker Protocol: `.claude/sdlc-raci.md`
- Agent routing table: `AGENTS.md`
