# SDLC RACI Matrix

R = Responsible (does the work) · A = Accountable (reviews and accepts) · C = Consulted · I = Informed

## Maker-Checker Protocol

All delegating agents apply this protocol when assigning work to subagents. The protocol is the shared source of truth; each delegating agent's `## Review Protocol` section is an instance of it.

### Loop Mechanics

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

**Cycle cap**: Maximum 3 cycles. If `cycle_count > 3` for any reason (off-by-one, interrupted state, re-entry), escalate unconditionally — do not proceed with another cycle.

**Audit trail**: Before sending the escalation message, the Checker must write the full rejection history to `generated/tmp/maker-checker-<timestamp>.md` (plain text, one section per cycle, rejection reason verbatim). This preserves the record across context-compaction events.

### Escalation Message Format

Use verbatim:

```
🚨 ESCALATION REQUIRED — Human Decision Needed
[ESCALATION REQUIRED — fallback for plain-text environments]

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

> **Emoji note**: The `🚨` prefix is a rendering hint. In plain-text terminal or log-file environments, use `[ESCALATION REQUIRED]` prefix instead. The protocol content (cycle count, rejection reasons, human options) is mandatory; the emoji is optional.

---

## INFO REQUEST Protocol

An **INFO REQUEST** is a structured response emitted by any agent mid-task when required information cannot be derived from local files. It is **not** a Maker output — receiving one does **not** start a new Maker-Checker cycle and does **not** increment the cycle counter.

### Scope

- L2 leaf agents emit INFO REQUESTs to their L1 parent agent.
- L1 delegate agents emit INFO REQUESTs to the Project Manager.
- Project Manager resolves INFO REQUESTs from L1 delegates using context or `web-search`; if PM cannot resolve, it emits `BLOCKED` to the human.

### Cap

**2 per task lifetime** — across all Maker-Checker cycles for a given task. A subagent that has already used both requests and emits a third must be treated as `BLOCKED` by the parent (reason: `INFO REQUEST cap exceeded`). The parent tracks remaining requests and includes `[INFO_REQUESTS: N/2]` in every re-issued task handoff.

### INFO REQUEST Format

```
INFO REQUEST [N of 2]
Agent: <agent-name>
Task: <one-line task description — copy from parent handoff>
Already tried: <files read, patterns checked — min 1 entry; never request what a local read would answer>
Gap: <specific question or decision that cannot be derived from local context>
Type: context | web-search | either
```

- `context` — parent answers from its own knowledge or project files
- `web-search` — external lookup required; parent delegates to `web-search` with expanded scope
- `either` — parent's choice: context if possible, otherwise web-search

### Parent Response Pattern

```
INFO RESPONSE
Agent: <parent-agent-name>
To: <requesting-agent-name>
Remaining INFO REQUESTS: <1 | 0>
Answer: <inline answer, or "delegated to web-search — see below">

[web-search RESEARCH RESULT appended verbatim if web-search was delegated]

Re-issued task handoff follows below:
---
[original task spec + KNOWN CONTEXT enriched with answer]
[INFO_REQUESTS: N/2]
```

### Routing Table (for parent agents)

| `Type` field | Action |
|---|---|
| `context` | Answer from own knowledge or project files. If cannot answer: emit `BLOCKED` upward. |
| `web-search` | Delegate to `web-search` with expanded scope. Append RESEARCH RESULT to re-issued handoff. |
| `either` | Answer from context if possible; delegate to `web-search` if not. |

### Web-Search Expanded Scope

When `web-search` is invoked as part of an INFO REQUEST chain (parent indicates `DOMAIN: <domain>` or `INFO_REQUEST_CHAIN: true` in handoff), it operates with **expanded domain scope**: any publicly accessible, non-sensitive domain is permitted (e.g., `docs.python.org`, `developer.atlassian.com`, `developer.mozilla.org`, npm, PyPI). The standard output contract (300-word cap, RESEARCH RESULT format, security rules) remains unchanged. Out-of-scope flagging is suppressed for explicitly named domains.

### What Counts as a Check (clarification)

An INFO REQUEST is not a Maker output and is never subject to a Maker-Checker review pass. The cycle counter does not change when an INFO REQUEST is received or resolved. Only responses that represent a genuine attempt at the delegated task output count as Maker outputs eligible for review.

> **Note**: `solution-architect` and `quality-architect` previously used a `KNOWLEDGE GAP REQUEST` format directed at `principal-solution-architect`. Those are instances of this INFO REQUEST protocol and follow the same rules and cap.

---

## Process RACI

| SDLC Activity | R | A | C | I |
|---|---|---|---|---|
| Vision / roadmap | Product Owner | Project Manager | Business Analyst, Principal Solution Architect | All |
| Requirements elicitation | Business Analyst | Product Owner | Dev Lead | Principal Solution Architect |
| Feature planning & scope | Product Owner | Project Manager | Business Analyst, Dev Lead | All |
| Architecture decision records | Principal Solution Architect | Dev Lead | Solution Architect | Product Owner |
| Technical design / task breakdown | Dev Lead | Principal Solution Architect | Backend / Frontend Dev | Test Lead |
| Backend implementation | Backend Developer | Dev Lead | Principal Solution Architect | Test Lead |
| Frontend implementation | Frontend Developer | Dev Lead | UX Designer | Test Lead |
| UX / interaction design | UX Designer | Dev Lead | Frontend Dev | Product Owner |
| Test strategy & coverage gates | Test Lead | Dev Lead | Automation QA | Project Manager |
| Manual / exploratory testing | Manual QA | Test Lead | Backend Developer | Product Owner |
| Test automation & CI integration | Automation QA | Test Lead | DevOps Engineer | Dev Lead |
| Performance testing | Performance QA | Test Lead | Backend Developer | Dev Lead |
| Security review | Security QA | Test Lead | Dev Lead | Project Manager |
| Architecture documentation | Solution Architect | Principal Solution Architect | Dev Lead | Product Owner |
| Quality framework & coverage docs | Quality Architect | Principal Solution Architect | Test Lead | Dev Lead |
| AI environment implementation | AI Engineer | AI Architect | Project Manager | Dev Lead |
| CI/CD pipeline implementation | DevOps Engineer | DevOps Lead | Dev Lead | Test Lead |
| Deployment & release | DevOps Lead | Project Manager | DevOps Engineer, Dev Lead | All |
| Documentation | Technical Writer | Dev Lead | Business Analyst, Product Owner | All |

---

## Delegation Chain RACI

| Delegating Agent | Direct Delegates (Maker) | Checker Role |
|---|---|---|
| Project Manager | ai-architect, principal-solution-architect, web-search, product-owner, dev-lead, test-lead, devops-lead | Project Manager |
| AI Architect | ai-engineer, web-search | AI Architect |
| Principal Solution Architect | solution-architect, quality-architect, web-search | Principal Solution Architect |
| Product Owner | business-analyst, ux-designer, technical-writer, web-search | Product Owner |
| Dev Lead | frontend-developer, backend-developer, web-search | Dev Lead |
| Test Lead | manual-qa, automation-qa, performance-qa, security-qa, web-search | Test Lead |
| DevOps Lead | devops-engineer, web-search | DevOps Lead |

---

## Agent File Creation RACI

| Artifact | Responsible | Accountable |
|---|---|---|
| `.claude/agents/<role>.md` | AI Engineer | AI Architect |
| `AGENTS.md` routing rows | AI Engineer (with human approval gate) | AI Architect |
| `.claude/sdlc-raci.md` | AI Engineer | AI Architect |
| `.claude/agents/project-manager.md` routing table | AI Engineer | AI Architect |
