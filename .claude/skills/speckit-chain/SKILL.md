---
name: "speckit-chain"
description: "Generate specs/NNN/execution-plan.md — the full agentic delegation chain for a feature, covering all agents, parallel groups, read/write scope per agent, and Maker-Checker gates. Requires human approval before /speckit-implement may run."
argument-hint: "Optional: feature folder name or NNN prefix (e.g. 042-metric-latency). Defaults to active feature."
compatibility: "Requires spec-kit project structure with .specify/ directory and approved tasks.md"
metadata:
  author: "claude-code"
  source: ".claude/skills/speckit-chain/SKILL.md"
user-invocable: true
disable-model-invocation: false
---


## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty). If ARGUMENTS names a specific feature folder or NNN prefix, use it. Otherwise derive from the active feature via the setup script.

## Pre-Execution Checks

**Check for extension hooks (before chain generation)**:
- Check if `.specify/extensions.yml` exists in the project root.
- If it exists, read it and look for entries under the `hooks.before_chain` key.
- If the YAML cannot be parsed or is invalid, skip hook checking silently and continue normally.
- Filter out hooks where `enabled` is explicitly `false`. Treat hooks without an `enabled` field as enabled by default.
- For each remaining hook without a `condition` field (or with an empty condition), output based on `optional` flag:
  - **Optional hook**: display command and prompt; do not auto-execute.
  - **Mandatory hook**: emit `EXECUTE_COMMAND: {command}` and wait for result before proceeding.
- If no hooks registered or file does not exist, skip silently.

## Outline

### Step 1 — Locate the feature

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` from repo root. Parse `FEATURE_DIR` (absolute path to the feature folder) and `AVAILABLE_DOCS` list.

**Prerequisite gate:**
- `tasks.md` must exist in FEATURE_DIR. If missing, STOP and tell the user to run `/speckit-tasks` first.
- `plan.md` must exist in FEATURE_DIR. If missing, STOP and tell the user to run `/speckit-plan` first.

### Step 2 — Load design artifacts

Read from FEATURE_DIR:
- **Required**: `tasks.md` (complete task list with IDs, [P] markers, file paths)
- **Required**: `plan.md` (tech stack, architecture, affected modules)
- **If exists**: `spec.md` (user stories, acceptance criteria — for agent context notes)
- **If exists**: `.specify/memory/constitution.md` (governance constraints)

### Step 3 — Determine track coverage

Scan `tasks.md` task descriptions and file paths to determine which tracks are activated:

| Track | Active when any task writes to... |
|-------|----------------------------------|
| Track 0 — AI Ecosystem | `.claude/**`, `CLAUDE.md`, agent definitions, hooks |
| Track 1 — Product Feature | `app/`, `ui/`, `config/`, `main.py`, `server.py` |
| Track 2 — Tests / Coverage | `tests/` (always active if Track 1 is active) |
| Track 3 — CI/CD & Infra | `.github/workflows/`, `Dockerfile`, `requirements*.txt` (major), deployment scripts |

Mark each track as `[x] Active` or `[ ] Inactive` in the output.

### Step 4 — Enumerate subtasks and file scope

For every task in `tasks.md`, extract:
- Task ID (T001, T002, …)
- Description
- File path(s) it writes (from description or [P] marker context)
- Track assignment (0/1/2/3 per Step 3 rules)
- [P] marker presence (candidate for parallel execution)

Produce an internal scope table:

```
T001 → track: 1 | writes: [app/core/metrics.py, tests/unit/test_metrics.py]
T002 → track: 3 | writes: [.github/workflows/ci.yml]
T003 → track: 2 | writes: [tests/integration/test_metrics.py]
```

### Step 5 — Apply Task Dependency Analysis Protocol

For each pair of tasks, classify as **Sequential** if ANY of:
- Data: B requires a file produced by A
- Write conflict: A and B write to the same file
- State: B requires A's side effects (schema before data, migration before query)
- Review gate: B is a Maker-Checker review of A's output

If none apply → the pair is **Independent**.

Group independent tasks into parallel tiers:
- Tier 1 (parallel): tasks with no dependencies
- Tier 2 (parallel, after Tier 1): tasks depending only on Tier 1
- …and so on

**Agent-layer rules:**
- Track 1 tasks → assigned to `Dev Lead → Developer` group
- Track 3 tasks → assigned to `DevOps Lead → DevOps Engineer` group (independent of Track 1 unless write conflict)
- Track 0 tasks → assigned to `AI Architect → AI Engineer` group (run before or in parallel with Track 1 unless output feeds Track 1)
- Track 2 tasks → always assigned to `Test Lead → Test Engineer` group, always **after** Track 1 complete
- Pre-impl tasks (AC lock, arch guard, spec finalization) → assigned to their respective agents, always **before** Track 1

**Standard phase order:**
1. G0 (Pre-impl) — PO + PSA + BA in parallel (if any pre-impl work exists)
2. G1 (Impl) — Developer + DevOps Engineer + AI Engineer in parallel (per tracks active)
3. G2 (Testing) — Test Engineer, after G1-A (Track 1) complete
4. G3 (Post-testing) — BA + Solution Architect in parallel

### Step 6 — Build parallel groups

Produce a parallel groups table:

| Group | Phase | Track | Agent Chain | Task IDs | Can Start When | Parallel With |
|-------|-------|-------|-------------|----------|----------------|---------------|
| G0-A | Pre-impl | — | PM → Product Owner | (pre tasks) | immediately | G0-B, G0-C |
| G0-B | Pre-impl | — | PM → Principal Solution Architect | (pre tasks) | immediately | G0-A, G0-C |
| G0-C | Pre-impl | — | PM → Business Analyst | (pre tasks) | immediately | G0-A, G0-B |
| G1-A | Impl | Track 1 | PM → Dev Lead → Developer | T00N–T00N | G0 complete | G1-B, G1-C |
| G1-B | Impl | Track 3 | PM → DevOps Lead → DevOps Engineer | T00N | G0 complete | G1-A, G1-C |
| G1-C | Impl | Track 0 | PM → AI Architect → AI Engineer | T00N | G0 complete | G1-A, G1-B |
| G2 | Testing | Track 2 | PM → Test Lead → Test Engineer | T00N–T00N | G1-A complete | — |
| G3-A | Post | — | PM → Business Analyst | (post tasks) | G2 complete | G3-B |
| G3-B | Post | — | PM → Solution Architect | (post tasks) | G2 complete | G3-A |

**Omit any row whose track is Inactive** (from Step 3). If G0 has no pre-impl tasks, omit G0 rows entirely.

Mark groups that PM dispatches in a single Agent call with **⚡** — these are groups whose rows share the same "Can Start When" value and have no write conflicts between them.

### Step 7 — Build agent scope table

For each active group, produce a scope entry:

```
### <Group ID> — <Role(s)>

| Dimension | Detail |
|-----------|--------|
| Reads | <files read — be specific, list from tasks.md and plan.md> |
| Writes | <files written — exact paths from tasks.md> |
| Context limit | <one sentence: what this agent must NOT read beyond the listed scope> |
| Maker-Checker | <who reviews before COMPLETE is returned to PM> |
| Output to PM | <what this agent chain returns> |
```

Use these standard context limits:
- Developer: "Target module + one doc file. No broad repo scan."
- Test Engineer: "Spec + source-under-test only. Never reads implementation notes or PR descriptions."
- DevOps Engineer: "CI config only. No app code access."
- AI Engineer: "Claude env files only (.claude/**, CLAUDE.md)."
- Business Analyst: "Spec + requirements files only."
- Principal Solution Architect: "Plan + architecture docs only. No deep source reads."
- Solution Architect: "Architecture docs only."
- Product Owner: "Spec document only."

### Step 8 — Build delegation chain diagram

Produce an ASCII tree showing the full chain:

```
PM (Project Manager — read-only orchestrator)
│
├── ⚡ PRE-IMPLEMENTATION [G0 — THREE-WAY PARALLEL]  ← omit if no G0 tasks
│   ├── [G0-A] Product Owner ──────────────── <task>
│   ├── [G0-B] Principal Solution Architect ─ <task>
│   └── [G0-C] Business Analyst ────────────── <task>
│                                               (all G0 must complete before G1)
│
├── ⚡ IMPLEMENTATION [G1 — <N>-WAY PARALLEL, after G0]
│   ├── [G1-A] Track 1: Dev Lead → Developer          (T00N–T00N)
│   ├── [G1-B] Track 3: DevOps Lead → DevOps Engineer (T00N)      ← if Track 3 active
│   └── [G1-C] Track 0: AI Architect → AI Engineer    (T00N)      ← if Track 0 active
│
├── TESTING [G2 — sequential, after G1-A complete]
│   └── [G2] Track 2: Test Lead → Test Engineer        (T00N–T00N)
│
└── ⚡ POST-TESTING [G3 — TWO-WAY PARALLEL, after G2]  ← omit if no G3 tasks
    ├── [G3-A] Business Analyst ── <task>
    └── [G3-B] Solution Architect ─ <task>              ← conditional: only if ADR flagged
```

### Step 9 — Build execution timeline

Produce an ASCII timeline showing group durations and gates:

```
G0-A ━━━━━┓
G0-B ━━━━━╋━━ GATE ──────────────────────────────────────────────────┐
G0-C ━━━━━┛                                                           │
                                                                      ↓
G1-A ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
G1-B ━━━━━━━━━━━━━━━━━━━━┛                        ┃ GATE ────────────┐
G1-C ━━━━━━━━━━━━━━━━━━┛  (if active)             ┛                  │
                                                                      ↓
G2   ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ GATE ─┐
                                                                       │
G3-A ━━━━━━━━━━━┓                                                      │
G3-B ━━━━━━━━━━━┛  (conditional)                                       ┘
```

Omit any row for an inactive group.

### Step 10 — Write execution-plan.md

Write the file to `<FEATURE_DIR>/execution-plan.md` using this exact structure:

```markdown
# Execution Plan: <feature-folder-name>

Generated: <ISO 8601 date>
Source: specs/<NNN-feature-name>/tasks.md
Approved: [ ] Pending

---

## Track Coverage

| Track | Active | Rationale |
|-------|--------|-----------|
| Track 0 — AI Ecosystem (.claude/**) | [x] / [ ] | <reason or N/A> |
| Track 1 — Product Feature (app/, ui/, config/) | [x] / [ ] | <reason or N/A> |
| Track 2 — Tests / Coverage (tests/) | [x] / [ ] | <reason or N/A> |
| Track 3 — CI/CD & Infra (.github/workflows/) | [x] / [ ] | <reason or N/A> |

---

## Full Delegation Chain

<ASCII tree from Step 8>

---

## Execution Timeline

<ASCII timeline from Step 9>

---

## Parallel Groups

<table from Step 6>

> **⚡ marks groups that PM dispatches in a single Agent call (one message, multiple subagent instances)**

---

## Agent Scope

<scope entries from Step 7, one subsection per active group>

---

## Maker-Checker Gates

| After Group | Checker | Gate Condition |
|-------------|---------|----------------|
| G0 | PM | All sign-offs received before dispatching G1 |
| G1-A | Dev Lead | Reviews Developer output; returns TEST STATE block to PM |
| G1-B | DevOps Lead | Reviews pipeline changes before returning COMPLETE |
| G1-C | AI Architect | Reviews AI Engineer changes before returning COMPLETE |
| G2 | Test Lead | Sign-off gate: broken_tests=0, bug files present, pass rate reported |
| G3 | PM | Reviews BA + SA docs before closing the feature |

(Omit rows for inactive groups)

---

## Human Approval Gate

**PM proceeds with `/speckit-implement` ONLY after this is checked.**

- [ ] Approved
- Approved by: _______________
- Date: _______________

Once approved, this file is the **binding delegation manifest** — agent scope, parallel groups,
and read/write limits are enforced by PM. Any task outside the listed write scope requires
a new execution-plan revision approved by the human before proceeding.
```

### Step 11 — Present for approval

After writing the file, display:

```
EXECUTION PLAN WRITTEN
Path: specs/<NNN-feature-name>/execution-plan.md

Summary:
- Tracks active: <list>
- Parallel groups: <count> (⚡ <N> groups dispatch simultaneously at peak)
- Total agent invocations: <count>
- Critical path: <G0 → G1-A → G2 → G3 | G0 → G1-A → G2 if no G3>

Next step: review and approve the execution-plan.md, then run /speckit-implement.
PM will read this file as its delegation manifest and will not proceed without the approval checkbox.
```

## Mandatory Post-Execution Hooks

**You MUST complete this section before reporting completion to the user.**

Check if `.specify/extensions.yml` exists in the project root.
- If it does not exist, or no hooks are registered under `hooks.after_chain`, skip to the Completion Report.
- If it exists, read it and look for entries under the `hooks.after_chain` key.
- Filter out hooks where `enabled` is explicitly `false`. Skip hooks with non-empty `condition` fields.
- For each remaining hook, output based on `optional` flag:
  - **Mandatory hook**: emit `EXECUTE_COMMAND: {command}`.
  - **Optional hook**: display command and prompt.

## Completion Report

Output:
- Path to generated `execution-plan.md`
- Track coverage summary (active tracks)
- Parallel group count and peak parallelism
- Critical path summary
- Reminder: human approval required before `/speckit-implement`

## Done When

- [ ] `tasks.md` and `plan.md` confirmed present in FEATURE_DIR
- [ ] Track coverage determined for all 4 tracks
- [ ] Task dependency analysis applied (sequential vs independent pairs classified)
- [ ] Parallel groups built with correct "Can Start When" relationships
- [ ] Agent scope table complete for all active groups (reads, writes, context limits)
- [ ] Delegation chain diagram written
- [ ] Execution timeline written
- [ ] `execution-plan.md` written to FEATURE_DIR
- [ ] Summary presented to user with next-step instruction
- [ ] Extension hooks dispatched or skipped
