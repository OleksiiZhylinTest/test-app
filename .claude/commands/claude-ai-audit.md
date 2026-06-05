# /claude-ai-audit

Audit the AI Ecosystem for cost efficiency, performance, and quality. Analyzes session token
reports and agent prompt definitions. Produces an inline summary and a full written report.

**Maker-Checker protocol applies:**
- **AI Engineer (Maker)** executes the 5-layer audit, computes metrics, and writes the draft report.
- **AI Architect (Checker)** validates the draft against the rubric and thresholds, then approves
  before returning results to the human.

---

## Usage

```bash
/claude-ai-audit          # full 5-layer audit
```

---

## Routing

1. Delegate execution to `ai-engineer`:
   - Provide: "Run the AI Ecosystem Audit (Maker role). Execute all 5 layers as defined in
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
5. Parse `## Hotspots` section: flag any step with cache-write > 5,000 tokens.
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

Layer 5 — Agent Prompt Quality
  ✓ ai-architect.md   D1✓ D2✓ D3✓ D4✓ D5✓ D6✓
  ⚠ developer.md      D2⚠ — Bash listed but no workflow step uses it

FINDINGS: ✗ 0  ⚠ 3  ✓ N

RECOMMENDATIONS:
  1. [HIGH]   session_8c96e2a4 — cache efficiency 61%; audit system prompt load order;
              ensure CLAUDE.md and agent context are loaded before per-turn tool calls
  2. [MEDIUM] T2S1 hotspot (10,603 tokens) — Explore pair in step 1 writes large cache entry;
              consider merging into a single focused Explore call
  3. [MEDIUM] developer.md D2 — add a workflow step that explicitly invokes Bash, or remove it

Approved by: AI Architect  |  Report: generated/reports/ai-audit-<YYYY-MM-DD>.md
```

---

## After Audit

- Present the approved report inline and confirm the file path.
- For approved fixes affecting agent files → delegate to `ai-engineer`.
- For fixes requiring `settings.json` or `.github/**` changes → escalate to human with a
  proposed change; do not modify those files during the audit.
- Do not auto-apply recommendations. Present findings; let the human decide what to act on.
