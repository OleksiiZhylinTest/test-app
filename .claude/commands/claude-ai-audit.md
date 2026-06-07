# /claude-ai-audit

Audit the AI Ecosystem for cost efficiency, performance, and quality. Analyzes session token
reports and agent prompt definitions. Produces an inline summary and a full written report.

**Maker-Checker protocol applies:**
- **AI Engineer (Maker)** executes the 8-layer audit, computes metrics, and writes the draft report.
- **AI Architect (Checker)** validates the draft against the rubric and thresholds, then approves
  before returning results to the human.

---

## Usage

```bash
/claude-ai-audit          # full 10-layer audit
```

---

## Routing

1. Delegate execution to `ai-engineer`:
   - Provide: "Run the AI Ecosystem Audit (Maker role). Execute all 10 layers as defined in
     `claude-ai-audit.md`. Write the draft report to `generated/reports/ai-audit-<YYYY-MM-DD>.md`
     and return a MAKER REPORT to AI Architect."
2. Receive MAKER REPORT from `ai-engineer`.
3. `ai-architect` performs Checker validation (see `ai-architect.md § AI Ecosystem Audit Protocol`).
4. AI Architect presents the approved inline summary and report file path to the human.
   - If validation fails: issue `REQUEST CHANGES` to AI Engineer (max 3 cycles; escalate at cycle 4).

---

## Audit Layers (executed by AI Engineer)

### Layer 1 — Session Inventory

**Goal:** Establish scope before any metric computation.

1. `Glob generated/debug/claude_session_*.md` — list all session files.
2. For each file: read the header block (Session, Project, Branch, Date, Model fields).
3. Report: session count, date range (oldest → newest), unique model names, unique branch names.

### Layer 2 — Token Cost Analysis

**Goal:** Identify sessions with poor cache efficiency (elevated cost).

1. For each session file: read `## Session Totals` table.
2. Extract: Input (fresh), Cache read, Cache write, Output, Total effective.
3. Compute **cache efficiency** = `cache-read / (cache-read + fresh-input) × 100%`.
4. Thresholds:
   - ≥80% → `✓ GOOD`
   - 50–79% → `⚠ WARN`
   - <50% → `✗ HIGH` (poor caching — active cost burn)
5. Parse `## Hotspots` section: flag any step with cache-write > 5,000 tokens **or** > 20% of session total cache-write.
6. Aggregate: total tokens across all sessions, weighted average cache efficiency.

### Layer 3 — Turn Efficiency

**Goal:** Identify unusually expensive turns or steps.

1. For each session file: parse `## Turn Details` — count total steps and number of turns.
2. Compute average steps/turn across the session.
3. For each step in the Hotspots table: compute that step's share of session total cache-write.
4. Flag any step where a single step accounts for >30% of session total cache-write.

### Layer 4 — Output Token Ratio

**Goal:** Detect verbose or unguided generation.

1. Per session: `output / total-effective × 100%`.
2. Thresholds:
   - ≤15% → `✓ GOOD`
   - >15% → `⚠ WARN` (potentially verbose; review prompts for open-ended instructions)

### Layer 5 — Agent Prompt Quality

**Goal:** Score every agent definition against the D1–D6 rubric.

1. `Glob .claude/agents/*.md` — list all agent files.
2. Read each file.
3. Score each dimension per the rubric in `ai-architect.md § Agent Evaluation Rubric`:

   | Dimension | Pass | Warn | Fail |
   |-----------|------|------|------|
   | D1 Frontmatter | `name`, `description` (trigger phrase + namespace), `tools` all present | description vague | any field missing |
   | D2 Tool minimality | every listed tool has a matching workflow step | one extra tool with plausible latent use | tool clearly unused |
   | D3 Prompt structure | Role/Ownership, Responsibilities, Workflow, Constraints, Output all present | one section thin | a section absent |
   | D4 Namespace compliance | owned surfaces named; off-limits named; bypass mechanism referenced | off-limits implicit | no namespace scope |
   | D5 Context discipline | canonical sources ordered cheapest-first; "stop when sufficient" instruction present | loading order present but not prioritized | no loading guidance |
   | D6 Security posture | no credentials; least-privilege tools; bypass env var flagged | extra tools present | hardcoded secret or missing bypass flag |

4. For each WARN or FAIL: include the specific observation (e.g., "D2⚠ — Bash listed in tools
   but no workflow step calls it").

### Layer 6 — Runtime Context Management

**Goal:** Verify that every agent enforces a context ceiling during runtime to prevent context overflow in multi-agent sessions.

For each agent file in `.claude/agents/*.md`, check:

1. Does the file contain a `## Context Optimization` section (or equivalent context discipline section)?
2. Does it name a concrete file-read ceiling (e.g., "read ≤ 3 files before delegating", "no more than N inline reads")?
3. Is "stop when sufficient" present (or an equivalent directive such as "stop at the first level that answers the question")?
4. Is there a specified trigger for Explore subagent delegation (e.g., task scope threshold, file count limit)?

Scoring per agent:
- `✓ PASS` — all four criteria met
- `⚠ WARN` — 1–2 criteria missing
- `✗ FAIL` — no context discipline section at all, or L2 leaf agent with no ceiling defined

Aggregate metric: percentage of agents scoring PASS → GOOD ≥80%, WARN 50–79%, FAIL <50%.

### Layer 7 — Loop & Recursion Safety

**Goal:** Detect unbounded delegation chains, missing cycle caps, and scheduled/iterative workflows without termination guarantees.

1. **Maker-Checker cycle caps** — for each L1 agent file (ai-architect, dev-lead, test-lead, devops-lead, product-owner, principal-solution-architect): grep for `max.*cycle` or `cycle_count`. Flag any L1 agent missing an explicit cap → `⚠ WARN`.
2. **Leaf agent depth bound** — for each L2 agent file (ai-engineer, solution-architect, business-analyst, developer, test-engineer, devops-engineer): grep its frontmatter `tools:` list for `Agent`. If `Agent` is listed → `✗ FAIL` (L2 leaf must not spawn sub-agents — creates unbounded delegation depth).
3. **Scheduled loop termination** — grep `.claude/commands/*.md` and `.claude/skills/**/*.md` for `ScheduleWakeup`, `CronCreate`, `/loop`. For each match, check for an adjacent termination condition (`recurring: false`, explicit iteration count, or named break clause). Missing termination condition → `⚠ WARN`.
4. **INFO REQUEST cap enforcement** — verify that each L1 agent file references the 2-per-task-lifetime INFO REQUEST cap (grep for `INFO REQUEST` or `2 per task`). Missing reference → `⚠ WARN`.

Report format: table `Agent/File | Cycle Cap | Leaf Depth Safe | Loop Termination | INFO Cap | Notes`.

### Layer 8 — Hanging Request Protection

**Goal:** Identify agents and hooks that can block indefinitely without a timeout or escalation path.

1. **Hook timeout coverage** — read `.claude/settings.json`. For each hook entry:
   - Sync hooks (no `"async": true`): verify `"timeout"` is present and ≤ 30s. Missing or >30s → `⚠ WARN`.
   - Async hooks: note fire-and-forget (no timeout possible); flag if the corresponding hook script file contains a blocking call without a process timeout (e.g., `curl` without `--max-time`).

2. **Agent blocking pattern audit** — for each agent file, check whether the Workflow or Constraints section contains:
   - Guidance for Monitor tool usage including `timeout_ms` → absence → `⚠ WARN`
   - Guidance for long-running Bash calls to use `run_in_background` or `timeout` → absence → `⚠ WARN`
   - Any iterative retry loop with a "escalate if N attempts fail" clause → absence → `⚠ WARN`

3. **Agent escalation completeness** — for each agent file, verify at least one explicit "if blocked / if no response / if N retries exceeded → escalate to human" clause exists. Missing → `⚠ WARN`.

Report format: table `Agent/Hook | Has Timeout | Has BLOCKED Escalation | Blocking Pattern Notes`.

Aggregate metrics:
- Agents with explicit BLOCKED escalation path → GOOD ≥90%, WARN 70–89%, FAIL <70%
- Sync hooks with `"timeout"` ≤ 30s → GOOD 100%, WARN any sync hook without timeout

### Layer 9 — Prompt Injection & Credential Safety

**Goal:** Detect injection-prone patterns and credential leakage across agent definitions and generated artifacts.

1. **Bash injection scan** — for each agent file: grep for patterns where a dynamic or external value is concatenated into a Bash command string without quoting (e.g., `f"cmd {var}"`, `"cmd " + input`, unquoted `$ARGUMENTS` in a shell call). Flag any match → `✗ FAIL`.
2. **Subagent input forwarding** — for each agent file: check whether the Workflow or Handoff section passes raw user-supplied text (e.g., `$ARGUMENTS`) directly into a subagent prompt without an explicit sanitization or quoting acknowledgment. Flag absence → `⚠ WARN`.
3. **Inline credential scan** — grep all files in `.claude/agents/*.md` and `.claude/commands/*.md` for credential-shaped strings: bearer token patterns (`Bearer [A-Za-z0-9+/]{20,}`), key assignments (`api_key\s*=\s*\S+`, `password\s*=\s*\S+`), and PAT formats. Any match → `✗ FAIL`.
4. **MCP wrapper credential isolation** — for each MCP server entry in `.claude/settings.local.json`: verify credentials use `$ENV_VAR` substitution, not hardcoded values. If file is absent or has no `mcpServers`, record "N/A". Any hardcoded credential → `✗ FAIL`.
5. **Generated artifact leakage** — grep the 5 most-recently-modified files in `generated/debug/` and `generated/reports/` for the same credential-shaped patterns from step 3. Any match → `✗ FAIL`.

Scoring per file:
- `✗ FAIL` — any match in steps 1, 3, 4, or 5; flag as CRITICAL in RECOMMENDATIONS before all other entries
- `⚠ WARN` — match in step 2 only
- `✓ PASS` — no matches

Report format: table `File | Bash Injection | Input Forwarding | Inline Creds | MCP Isolation | Artifact Leak | Notes`

### Layer 10 — Model Currency & Prompt Deduplication

**Goal:** Verify all agents reference a supported model ID and identify guidance blocks duplicated across ≥ 3 agents that should be centralised.

**Supported model IDs** (canonical source: `CLAUDE.md`): `claude-sonnet-4-6`, `claude-opus-4-7`, `claude-haiku-4-5-20251001`.

1. **Model currency check** — for each agent file in `.claude/agents/*.md`:
   - Read the frontmatter `model:` field.
   - Value matches a supported ID → `✓ PASS`.
   - Field absent → `⚠ WARN` (inherits parent model; not explicitly controlled).
   - Value present but not in the supported list → `✗ FAIL` (deprecated or retired model ID).
   Aggregate: count PASS / WARN / FAIL. GOOD = all PASS; WARN = any missing; FAIL = any deprecated ID present.
2. **Prompt deduplication scan** — identify guidance blocks appearing verbatim or near-verbatim in ≥ 3 agent files:
   - Target patterns: INFO REQUEST format block, output expectations boilerplate, logging convention text, coding standards paragraph.
   - Each duplicated block > 150 tokens appearing in ≥ 3 files → `⚠ WARN` (deduplication candidate — centralise in `AGENTS.md` or `CLAUDE.md`).
   - Record: block description, number of files, estimated token size.

Report format: table `Agent | Model Field | Currency Status | Notes` followed by deduplication candidates list.

Aggregate metrics:
- Model currency: GOOD = 100% agents PASS; WARN = any absent field; FAIL = any deprecated ID
- Deduplication: GOOD = no candidates; WARN = ≥1 candidate identified

---

## Report Format

```
AI ECOSYSTEM AUDIT REPORT
==========================
Date: <today>   Sessions: N   Range: YYYY-MM-DD – YYYY-MM-DD   Model(s): ...

Layer 1 — Session Inventory
  ✓ N sessions  |  Branches: feature/x, develop  |  Models: claude-sonnet-4-6

Layer 2 — Token Cost (cache efficiency)
  ✓ session_01c13369   97.8%  GOOD
  ⚠ session_8c96e2a4   61.2%  WARN — fresh input elevated
  Aggregate efficiency: XX%
  Hotspots (cache-write > 5k):
    session_01c13369 · T2S1 · 10,603 tokens · Explore subagent pair

Layer 3 — Turn Efficiency
  ✓ Avg steps/turn: 13.5 (all sessions)
  ⚠ session_01c13369 · T2S1 = 22% of session cache-write

Layer 4 — Output Ratio
  ✓ session_01c13369   1.04%  GOOD

Layer 5 — Agent Prompt Quality (D1–D7)
  ✓ ai-architect.md   D1✓ D2✓ D3✓ D4✓ D5✓ D6✓ D7✓
  ⚠ developer.md      D2⚠ — Bash listed but no workflow step uses it; D7⚠ — no BLOCKED escalation path

Layer 6 — Runtime Context Management
  Agent context ceiling coverage: N/14 agents PASS  (XX%)  GOOD|WARN|FAIL
  ⚠ <agent>.md — missing concrete file-read ceiling
  ✗ <agent>.md — no context discipline section

Layer 7 — Loop & Recursion Safety
  Agent        | Cycle Cap | Leaf Depth Safe | Loop Termination | INFO Cap | Notes
  ai-architect | ✓ 3       | N/A (L1)        | N/A              | ✓        |
  ai-engineer  | N/A (L2)  | ✓ no Agent tool | N/A              | ✓        |
  ⚠ <command>.md — ScheduleWakeup used without explicit termination condition

Layer 8 — Hanging Request Protection
  Agent/Hook                      | Has Timeout | Has BLOCKED Escalation | Notes
  pre_edit_customization_boundary | ✓ 10s       | N/A (hook)             |
  pre_bash_safety                 | ✓ 10s       | N/A (hook)             |
  post_edit_lint (async)          | N/A async   | N/A (hook)             |
  ⚠ <agent>.md — no BLOCKED escalation path found
  Agents with BLOCKED escalation: N/14 (XX%)  GOOD|WARN|FAIL

Layer 9 — Prompt Injection & Credential Safety
  File                              | Bash Inj | Input Fwd | Inline Creds | MCP Iso | Artifact Leak
  .claude/agents/developer.md       | ✓ PASS   | ⚠ $ARGS   | ✓ PASS       | N/A     | ✓ PASS
  .claude/agents/ai-architect.md    | ✓ PASS   | ✓ PASS    | ✓ PASS       | N/A     | ✓ PASS
  Findings: ✗ N  ⚠ N  ✓ N

Layer 10 — Model Currency & Prompt Deduplication
  Agent              | Model Field              | Currency
  ai-architect.md    | claude-sonnet-4-6        | ✓ PASS
  developer.md       | claude-sonnet-4-6        | ✓ PASS
  Aggregate currency: N/14 PASS  GOOD|WARN|FAIL
  Deduplication candidates:
    INFO REQUEST format block — found in N agents (~XXX tokens) → ⚠ WARN

FINDINGS: ✗ N  ⚠ N  ✓ N

RECOMMENDATIONS:
  1. [HIGH]   session_8c96e2a4 — cache efficiency 61%; audit system prompt load order;
              ensure CLAUDE.md and agent context are loaded before per-turn tool calls
  2. [MEDIUM] T2S1 hotspot (10,603 tokens) — Explore pair in step 1 writes large cache entry;
              consider merging into a single focused Explore call
  3. [MEDIUM] developer.md D2 — add a workflow step that explicitly invokes Bash, or remove it
  4. [MEDIUM] <agent>.md D7 — add explicit context ceiling and BLOCKED escalation path

## Best Practices Gap Analysis
  BP-1 Every agent has a context ceiling (file count / "stop when sufficient")         ✓ MET | ⚠ PARTIAL | ✗ GAP
  BP-2 L2 leaf agents have no Agent tool (no unbounded delegation depth)               ✓ MET | ✗ GAP
  BP-3 All L1 checker agents name their Maker-Checker cycle cap explicitly             ✓ MET | ⚠ PARTIAL | ✗ GAP
  BP-4 Every scheduled/iterative workflow has a documented termination condition       ✓ MET | ⚠ PARTIAL | ✗ GAP
  BP-5 Every agent has a BLOCKED escalation path                                       ✓ MET | ⚠ PARTIAL | ✗ GAP
  BP-6 All sync hooks carry "timeout" ≤ 30s                                            ✓ MET | ✗ GAP
  BP-7 Long-running Bash/Monitor calls include timeout_ms or run_in_background guide   ✓ MET | ⚠ PARTIAL | ✗ GAP
  BP-8  INFO REQUEST cap (2/task) referenced in every L1 agent                         ✓ MET | ⚠ PARTIAL | ✗ GAP
  BP-9  No agent constructs Bash commands from un-quoted external input                ✓ MET | ✗ GAP
  BP-10 All MCP credentials injected via env vars; no hardcoded values in config       ✓ MET | ✗ GAP
  BP-11 All agent frontmatter specifies a current, supported model ID                  ✓ MET | ⚠ PARTIAL | ✗ GAP
  BP-12 Shared guidance (≥3 agents, >150 tokens) centralised in AGENTS.md not duped   ✓ MET | ⚠ PARTIAL | ✗ GAP

Approved by: AI Architect  |  Report: generated/reports/ai-audit-<YYYY-MM-DD>.md
```

---

## After Audit

- Present the approved report inline and confirm the file path.
- For approved fixes affecting agent files → delegate to `ai-engineer`.
- For fixes requiring `settings.json` or `.github/**` changes → escalate to human with a
  proposed change; do not modify those files during the audit.
- Do not auto-apply recommendations. Present findings; let the human decide what to act on.
