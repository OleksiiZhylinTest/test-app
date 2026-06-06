# Agent Orchestration

This document describes the Claude Code multi-agent orchestration system for this repository.

For the authoritative operational specs see:
- **SDLC RACI + Maker-Checker Protocol**: `.claude/sdlc-raci.md`
- **Agent routing table**: `AGENTS.md`
- **Per-agent definitions**: `.claude/agents/<agent-name>.md`

---

## Delegation Hierarchy

Three tiers: one Orchestrator routes all requests to 7 read-only L1 Delegates, each of which supervises a set of write-capable L2 Leaf Agents via the Maker-Checker review loop.

```
project-manager  (Orchestrator)
│
├── ai-architect               ──► ai-engineer
│
├── principal-solution-architect ──► solution-architect
│                                    quality-architect
│
├── product-owner              ──► business-analyst
│                                    ux-designer
│                                    technical-writer
│
├── dev-lead                   ──► backend-developer
│                                    frontend-developer
│
├── test-lead                  ──► manual-qa
│                                    automation-qa
│                                    performance-qa
│                                    security-qa
│
├── devops-lead                ──► devops-engineer
│
└── web-search  (leaf, external-only — no subagents)
```

All L1 Delegates are **read-only** (no Edit/Write/Bash tools). All L2 Leaf Agents carry **scoped write access** to their own workspace only.

---

## Agent Roster

| Tier | Agent | Role | Write access | Agent file |
|------|-------|------|--------------|------------|
| Orchestrator | `project-manager` | Intake, routing, plan-mode | None (read-only) | `.claude/agents/project-manager.md` |
| L1 Delegate | `ai-architect` | Claude env governance, agent definitions, hooks audit | None (read-only) | `.claude/agents/ai-architect.md` |
| L1 Delegate | `principal-solution-architect` | Strategic architecture oversight and approval | None (read-only) | `.claude/agents/principal-solution-architect.md` |
| L1 Delegate | `product-owner` | Backlog, acceptance criteria, prioritisation | None (read-only) | `.claude/agents/product-owner.md` |
| L1 Delegate | `dev-lead` | Technical oversight, code review, sprint breakdown | None (read-only) | `.claude/agents/dev-lead.md` |
| L1 Delegate | `test-lead` | Test strategy, coverage gates, quality sign-off | None (read-only) | `.claude/agents/test-lead.md` |
| L1 Delegate | `devops-lead` | CI/CD strategy, deployment approval, incident review | None (read-only) | `.claude/agents/devops-lead.md` |
| L1 Delegate | `web-search` | External documentation lookups | None (external-only) | `.claude/agents/web-search.md` |
| L2 Leaf | `ai-engineer` | Claude AI environment implementation | `.claude/**` (excl. `settings*.json`), `CLAUDE.md`, `.vscode/` | `.claude/agents/ai-engineer.md` |
| L2 Leaf | `solution-architect` | Architecture implementation: module structure, API contracts, schema | `docs/development/`, `config/jira_schema.json`, `config/jira_filters.json` | `.claude/agents/solution-architect.md` |
| L2 Leaf | `quality-architect` | Quality framework, test layers, coverage gates, NFR definitions | `docs/product/requirements/`, `docs/development/` | `.claude/agents/quality-architect.md` |
| L2 Leaf | `business-analyst` | Requirements elicitation, user stories, gap analysis | None (read-only) | `.claude/agents/business-analyst.md` |
| L2 Leaf | `backend-developer` | Server-side Python, API routes, reporters, config | `app/core/`, `app/server/`, `app/reporters/`, `app/utils/`, `config/` | `.claude/agents/backend-developer.md` |
| L2 Leaf | `frontend-developer` | UI templates, HTML/CSS, accessibility | `ui/templates/`, `ui/index.html`, `ui/css/`, `ui/js/` | `.claude/agents/frontend-developer.md` |
| L2 Leaf | `manual-qa` | Exploratory testing, regression checklists, bug reports | None (read-only) | `.claude/agents/manual-qa.md` |
| L2 Leaf | `automation-qa` | Automated tests, CI integration, flaky test triage | `tests/unit/`, `tests/component/`, `tests/integration/`, `tests/e2e/` | `.claude/agents/automation-qa.md` |
| L2 Leaf | `performance-qa` | Performance test suites, latency baselines, throughput benchmarks | `tests/component/`, `tests/integration/`, `generated/reports/`, `generated/tmp/` | `.claude/agents/performance-qa.md` |
| L2 Leaf | `security-qa` | OWASP review, TLS validation, secrets audit, CVE triage | Security NFR Status column only | `.claude/agents/security-qa.md` |
| L2 Leaf | `ux-designer` | Interaction specs, accessibility, design contracts | `docs/product/features/`, `ui/templates/`, `ui/css/`, `ui/js/` | `.claude/agents/ux-designer.md` |
| L2 Leaf | `technical-writer` | README, architecture docs, changelogs, API docs | `docs/`, `README.md`, `CHANGELOG.md` | `.claude/agents/technical-writer.md` |
| L2 Leaf | `devops-engineer` | Pipeline implementation, Dockerfile, deploy scripts | `.github/workflows/`, `docs/development/pipeline.md`, `pyproject.toml` | `.claude/agents/devops-engineer.md` |

---

## GitHub Copilot Agent Roster

Copilot agent definitions live under `.github/agents/`. The GH Copilot hierarchy mirrors the Claude Code 3-tier structure.

```
GH Project Manager  (Orchestrator)
│
├── GH AI Architect            ──► GH AI Engineer
│
├── GH Principal Solution Architect ──► GH Solution Architect
│
├── GH Product Owner           ──► GH Business Analyst
│
├── GH Dev Lead                ──► GH Developer
│
├── GH Test Lead               ──► GH Test Engineer
│
├── GH DevOps Lead             ──► GH DevOps
│
└── GH Web Search  (leaf, external-only — no subagents)
```

| Tier | Agent file | Role | Write access |
|------|-----------|------|--------------|
| Orchestrator | `gh-project-manager.agent.md` | Intake, routing, plan-mode | None (read-only) |
| L1 Delegate | `gh-ai-architect.agent.md` | Copilot env governance, agent/skill/hook oversight | None (read-only) |
| L1 Delegate | `gh-principal-solution-architect.agent.md` | Strategic architecture oversight and approval | None (read-only) |
| L1 Delegate | `gh-product-owner.agent.md` | Requirements acceptance, feature acceptance, priority | None (read-only) |
| L1 Delegate | `gh-dev-lead.agent.md` | Code review, coding standards enforcement | None (read-only) |
| L1 Delegate | `gh-test-lead.agent.md` | Test strategy, coverage gates, quality sign-off | None (read-only) |
| L1 Delegate | `gh-devops-lead.agent.md` | CI/CD strategy, pipeline approval | None (read-only) |
| L1 Delegate | `gh-web-search.agent.md` | External documentation research | None (external-only) |
| L2 Leaf | `gh-ai-engineer.agent.md` | Copilot AI environment implementation | `.github/**`, `AGENTS.md`, `.vscode/` |
| L2 Leaf | `gh-solution-architect.agent.md` | Architecture implementation and quality framework ownership: module-boundary changes, API/schema design, test layer assignments, coverage gates, NFR definitions | `docs/development/`, `config/jira_schema.json`, `config/jira_filters.json`, `docs/product/requirements/`, `tests/coverage/` |
| L2 Leaf | `gh-business-analyst.agent.md` | Requirements elicitation, acceptance criteria, UX/interaction design, documentation | `docs/`, `ui/templates/`, `ui/index.html`, `ui/css/`, `ui/js/`, `README.md`, `CHANGELOG.md` |
| L2 Leaf | `gh-developer.agent.md` | Full-stack implementation: backend Python and frontend UI | `app/core/`, `app/server/`, `app/reporters/`, `app/utils/`, `config/`, `ui/` |
| L2 Leaf | `gh-test-engineer.agent.md` | Unified QA: manual, automation, performance, security. Two-phase execution (checklist → implementation). Stateless per invocation. | Domain-scoped per task_type |
| L2 Leaf | `gh-devops.agent.md` | Pipeline implementation, workflow YAML, CI configuration | `.github/workflows/`, `docs/development/pipeline.md`, `pyproject.toml` |

> **SDD workflow**: Spec-Driven Development (specify → clarify → plan → tasks → analyze → implement) and git integration are invoked as skills (`/speckit-*`) from `.github/skills/`, not as agents. See `.github/summaries/maker-checker-protocol.md` for the Maker-Checker loop specification.

---

## Maker-Checker Review Loop

Every L1 Delegate (Checker) applies this loop when assigning work to an L2 Leaf Agent (Maker):

```
DELEGATING AGENT (Checker) assigns task to SUBAGENT (Maker)
  └─► SUBAGENT produces plan or output  ── CYCLE 1
       └─► CHECKER reviews against: task spec, scope, conventions, risks
           ├─ APPROVE → accept output, report back up the chain
           └─ REJECT → specific, actionable feedback → CYCLE 2
               └─► SUBAGENT revises
                   └─► CHECKER reviews  ── CYCLE 2
                       ├─ APPROVE → done
                       └─ REJECT → CYCLE 3
                           └─► SUBAGENT revises (final cycle)
                               └─► CHECKER reviews  ── CYCLE 3
                                   ├─ APPROVE → done
                                   └─ REJECT → ESCALATE TO HUMAN (stop all delegation)
```

**Cycle cap**: Maximum 3 cycles. If `cycle_count > 3` for any reason, escalate unconditionally.

Full protocol spec (escalation message format, audit trail rules): `.claude/sdlc-raci.md`

---

## Cross-Assistant Note

Claude agents are defined in `.claude/agents/` and delegate only within that namespace. GitHub Copilot has a parallel agent hierarchy in `.github/agents/` — the two systems are independent and must never cross-invoke each other during normal operation.

Full ownership rules and cross-tool exception handling: [`assistant-customization-governance.md`](assistant-customization-governance.md)
