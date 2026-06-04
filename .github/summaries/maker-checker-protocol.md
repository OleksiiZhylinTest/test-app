# Maker-Checker Protocol — GitHub Copilot Agents

> **Note**: This file is the Copilot-side canonical reference. The Claude Code equivalent is `.claude/sdlc-raci.md` § Maker-Checker Protocol. Both must stay in sync when the protocol is updated. The shared, assistant-neutral canonical source for the full 3-tier hierarchy and 21-agent roster is `docs/development/ai/agent-orchestration.md`.

This protocol applies to all **delegating agents** in the Copilot SDLC roster. Leaf agents do not implement this protocol — they are the Makers.

## Delegating Agents (Checkers)

The following 7 agents implement this protocol as Checkers:

1. `gh-project-manager`
2. `gh-ai-architect`
3. `gh-principal-solution-architect`
4. `gh-product-owner`
5. `gh-dev-lead`
6. `gh-test-lead`
7. `gh-devops-lead`

## Loop Mechanics

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

## Cycle Cap

**Maximum cycles: 3.** After 3 rejected cycles, the delegating agent must stop all delegation for this task and surface the escalation message (below) to the user. No further delegation proceeds until the user responds.

## Review Criteria

When reviewing a Maker's output, the Checker evaluates against all of the following:

- **Task specification**: Does the output fulfill the delegated task exactly as described?
- **Scope boundaries**: Does the output stay within the subagent's permitted read/write scope?
- **Repository conventions**: Does the output comply with `AGENTS.md` coding standards and module rules?
- **Security constraints**: Does the output introduce any OWASP Top 10 risks or permission violations?
- **Risk assessment**: Does the output carry unintended side effects on shared contracts (API shapes, test fixtures, metric definitions)?

## Escalation Message Format

When 3 cycles are exhausted without approval, send this message verbatim to the user (fill in the `<>` fields):

```
🚨 ESCALATION REQUIRED — Human Decision Needed

Agent: <delegating-agent-name>
Subagent: <subagent-name>
Task: <one-line task description>
Cycles completed: 3 / 3

Summary of blockers:
- <Cycle 1 rejection reason>
- <Cycle 2 rejection reason>
- <Cycle 3 rejection reason>

Options for human:
A) <option A with tradeoff>
B) <option B with tradeoff>
C) Accept last subagent output as-is

Awaiting human decision. No further delegation will proceed for this task.
```

## Reference in Agent Files

Every delegating agent file includes a `## Review Protocol` section. That section references this document and states the cycle cap and escalation trigger. It does **not** embed the escalation message verbatim — the full format lives here as the single source of truth.

## Knowledge-Gap Escalation

This section governs how all Copilot SDLC agents handle genuinely missing external knowledge during a task. It is distinct from the Maker-Checker cycle and does not consume cycle budget.

### Trigger Condition

A knowledge gap exists only when a fact is **genuinely external** and cannot be resolved from repository files or `.github/summaries/**`. Qualifying examples: unknown vendor API behavior, library version compatibility, external standards specification text (OWASP, WCAG, PEPs), CVE advisory details.

**Do not trigger** for internal repo facts — module owners, config variables, test conventions, metric definitions, server handler maps. Always exhaust local sources before triggering escalation.

### Routing Rule

| Agent has `agent` tool? | Action |
|-------------------------|--------|
| **Yes** | Call `GH Web Search` directly with one narrow, concrete question |
| **No** | Ask the parent agent using the Parent Request Format below |

### Cap

**Maximum 2 knowledge-gap requests per task**, regardless of routing path. After both are used, the agent must either:
1. Proceed using the best available information, or
2. Surface a blocker to its parent with a clear statement of what remains unknown and why the task cannot complete.

### Maker-Checker Exemption

Knowledge-gap requests are **not** counted as a Maker-Checker review cycle. The cycle counter increments only when a Checker rejects a Maker's task output. A knowledge-gap request pauses the task without consuming a cycle.

### Parent Request Format

When an agent without the `agent` tool must ask its parent for external information, the request must include all three of the following elements:

1. **What I need** — the exact external fact required (e.g., "default retry behavior of `requests.Session` on connection errors in requests ≥ 2.28").
2. **Why local search was insufficient** — which local files or summaries were checked and what was missing or contradictory.
3. **What I will do with the answer** — how the answer will be applied to unblock the current task.

### Terminal Point

`GH Web Search` is the terminal knowledge-resolution endpoint in the Copilot hierarchy. It does not escalate knowledge gaps further. If a question is ambiguous, security-sensitive, or sources conflict, it returns a low-confidence brief so the caller can surface a blocker rather than proceeding on uncertain information.
