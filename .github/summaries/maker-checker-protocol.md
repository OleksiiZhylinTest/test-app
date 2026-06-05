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

The loop has three phases per cycle: Checker Pre-Plan → Maker Execution → Checker Review.

### Phase 1 — Checker Verification Plan (isolation required)

Before the Maker is invoked, the Checker produces a **Verification Plan** from the task spec only.

**Isolation rule**: The plan must be derived without access to Maker reasoning, Maker output, or any prior Maker chain-of-thought. The Checker reads only the task specification and relevant repository files needed to understand the domain.

The Verification Plan must enumerate:
1. **Expected artifacts** — which files must be created or modified and what must appear in each
2. **Behavior coverage** — which code paths or behaviors the task spec implies must be handled
3. **Corner cases** — edge inputs, boundary values, failure paths, and concurrent-access risks implied by the task spec (even if not explicitly stated)
4. **Integration surface** — callers, dependents, and integration points that may be affected by the change
5. **Test coverage contract** — for each changed behavior, which test layer must exercise it and at what granularity

This plan is the **review contract** for the cycle. The Checker is bound to follow it during Phase 3.

### Phase 2 — Maker Execution

The Maker receives the task specification only. The Checker's Verification Plan is not shared with the Maker.

### Phase 3 — Checker Review

The Checker reviews the Maker's output against its own Verification Plan.

**Union rule (critical)**: If the Maker has implemented a valid corner case, edge case, or defensive behavior that was NOT in the Checker's plan, that work must be PRESERVED. The Checker cannot remove valid work simply because it was not anticipated in the plan. The Checker updates its plan to acknowledge the addition and marks it as a bonus finding.

The Checker may read the Maker's explanations and chain-of-thought at this phase. However, the Checker is bound to follow its own Verification Plan as the primary review contract — Maker explanations may inform context but do not replace the plan.

### Loop diagram

```
CHECKER reads task spec → produces Verification Plan (isolation — no Maker access)
  └─► MAKER receives task spec only (Checker plan not shared)
       └─► MAKER produces output  ── CYCLE 1
            └─► CHECKER reviews output against Verification Plan (union rule applies)
                ├─ APPROVE → no report; report status up the chain
                └─ REJECT → Structured Checker Report (see §Structured Checker Report) → CYCLE 2
                    └─► MAKER revises
                         └─► CHECKER reviews  ── CYCLE 2
                             ├─ APPROVE → done
                             └─ REJECT → CYCLE 3 (or CYCLE 4/5 for shared contract changes — see §Cycle Cap)
                                 └─► ... up to cycle cap, then ESCALATE
```

## Cycle Cap

The cycle cap depends on the change type:

| Change type | Cycle cap |
|-------------|-----------|
| Simple change | **3 cycles** |
| Shared contract change | **5 cycles** |

**Shared contract change** is defined as any change that touches one or more of:
- Public function signatures in `app/core/`, `app/server/`, `app/reporters/`, or `app/utils/`
- API route shapes (URL, method, request/response body)
- `config/jira_schema.json` or `config/jira_filters.json`
- Test fixtures or factories in `tests/conftest.py`, `tests/unit/conftest.py`, or `tests/component/conftest.py`
- The `metrics_dict` shape produced by `build_metrics_dict()` in `app/core/metrics.py`
- `AGENTS.md` agent roster, ownership rules, or routing table
- Any file under `.github/agents/`, `.github/skills/`, `.github/prompts/`, or `.github/hooks/`

All other changes are **simple changes** with a 3-cycle cap.

After the cycle cap is exhausted without approval, the delegating agent must stop all delegation for this task and surface the escalation message (below) to the user. No further delegation proceeds until the user responds.

## Gap Analysis Tiers

Every Checker review in Phase 3 must evaluate two tiers:

### Tier A — Compliance (required on every cycle)

- **Task specification**: Does the output fulfill the delegated task exactly as described?
- **Scope boundaries**: Does the output stay within the subagent's permitted read/write scope?
- **Repository conventions**: Does the output comply with `AGENTS.md` coding standards and module rules?
- **Security constraints**: Does the output introduce any OWASP Top 10 risks or permission violations?
- **Risk assessment**: Does the output carry unintended side effects on shared contracts (API shapes, test fixtures, metric definitions)?

### Tier B — Gap Analysis (required on every cycle)

- **Implementation completeness**: Are all paths in the task spec handled? Any `TODO`, `pass`, stub, or placeholder left behind?
- **Edge cases**: Are null/empty inputs, boundary values, concurrent access, and failure paths addressed — not just the happy path?
- **Integration surface**: Are all callers of changed functions or APIs updated? Are there other modules that depend on the changed contract?
- **Test coverage gaps**: For every changed code path, does a test exercise it at the narrowest applicable layer?
- **Regression surface**: Does the change risk silently breaking behavior that was previously tested but is not re-tested by the new work?

## Structured Checker Report

A Structured Checker Report is produced **only on REJECT cycles**. On APPROVE, no report is required — the Checker reports status up the chain directly.

### Report format

```
## Checker Review Report — Cycle N / <cap>

### Verification Plan (from task spec — produced before Maker ran)
- Expected artifact 1: <file + what must appear>
- Expected artifact 2: ...
- Corner cases in scope: <list>
- Integration surface: <list>
- Test coverage contract: <list>

### Tier A — Compliance
- Task spec: PASS | FAIL — <note>
- Scope: PASS | FAIL — <note>
- Conventions: PASS | FAIL — <note>
- Security: PASS | FAIL — <note>
- Shared contracts: PASS | FAIL — <note>

### Tier B — Gap Analysis
- Implementation completeness: PASS | GAPS FOUND — <list gaps>
- Edge cases: PASS | GAPS FOUND — <list missing cases>
- Integration surface: PASS | GAPS FOUND — <list>
- Test coverage: PASS | GAPS FOUND — <list>
- Regression surface: PASS | RISKS FOUND — <list>

### Union Rule — Bonus Findings from Maker
- <list any Maker-implemented corner cases or defensive behaviors not in the original plan that are preserved>

### Verdict: REJECT
### Required corrections: <specific, actionable, referencing gap categories above>
```

## Escalation Message Format

When the cycle cap is exhausted without approval, send this message verbatim to the user (fill in the `<>` fields):

```
🚨 ESCALATION REQUIRED — Human Decision Needed

Agent: <delegating-agent-name>
Subagent: <subagent-name>
Task: <one-line task description>
Cycles completed: <N> / <cap>  (<simple|shared contract> change)

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
