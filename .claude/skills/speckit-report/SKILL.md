---
name: "speckit-report"
description: "Generate per-spec SDLC close-out artifacts after full SDLC flow completes: session-telemetry.md (spec-attributed token cost), sdlc-report.md (execution summary), and ai-architect-audit.md (agentic chain assessment)."
argument-hint: "Optional: feature folder name or NNN prefix (e.g. 001-session-token-telemetry). Defaults to active feature."
compatibility: "Requires spec-kit project structure with completed tasks.md"
metadata:
  author: "claude-code"
  source: ".claude/skills/speckit-report/SKILL.md"
user-invocable: true
disable-model-invocation: false
---


## User Input

```text
$ARGUMENTS
```

If ARGUMENTS names a specific feature folder or NNN prefix, use it. Otherwise derive the active feature from the setup script.

## Outline

### Step 1 — Resolve spec folder

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -IncludeTasks` from repo root. Parse `FEATURE_DIR` (absolute path to the feature folder).

If `$ARGUMENTS` is non-empty, match against `specs/` directory entries:
- Exact folder name match first
- NNN prefix match (first 3 digits) if no exact match

**Prerequisite check:**
- `tasks.md` must exist in FEATURE_DIR. If missing → STOP: "Run `/speckit-tasks` first."
- `plan.md` must exist in FEATURE_DIR. If missing → STOP: "Run `/speckit-plan` first."
- `execution-plan.md` must exist in FEATURE_DIR. If missing → WARN: "No execution-plan.md found — agent chain section will be omitted."

### Step 2 — Generate session-telemetry.md

Run:
```bash
python tools/claude_session_stats.py --spec <FEATURE_DIR>
```

This writes `<FEATURE_DIR>/session-telemetry.md`.

- If the script writes a stub (no matching steps found), note this in the report but do not stop.
- If the script fails entirely, write a stub manually:
  ```
  # Spec Session Telemetry
  _Session telemetry unavailable — script error._
  ```
  Then continue to Step 3.

Optionally, if the user can supply a `--projects-dir` path (e.g., `~/.claude/projects/<hash>/`), include it for more accurate JSONL-based attribution:
```bash
python tools/claude_session_stats.py --spec <FEATURE_DIR> --projects-dir <PROJECTS_DIR>
```

### Step 3 — Collect spec artifacts

Read from FEATURE_DIR (stop at first sufficient level):
- **Required**: `tasks.md` — extract total task count and `[X]` completed count
- **Required**: `spec.md` — extract acceptance criteria list and user story count (if present)
- **Required**: `plan.md` — extract affected modules / architecture summary (first 10 lines of plan summary section)
- **If exists**: `execution-plan.md` — extract "## Track Coverage" and "## Full Delegation Chain" sections verbatim
- **If exists**: `checklists/` directory — for each `.md` file: count `[x]` vs `[ ]` items; compute PASS if all checked, FAIL otherwise
- **If exists**: `bugs/` directory — count `.md` files
- **Just written**: `session-telemetry.md` — extract the "## Session Totals" table section

### Step 4 — Write sdlc-report.md

Write `<FEATURE_DIR>/sdlc-report.md` using this structure:

```markdown
# SDLC Close-Out Report: <feature-folder-name>

Generated: <ISO 8601 date>
Source: specs/<NNN-feature-name>/

---

## Feature Overview

- **Acceptance criteria:** <N from spec.md, or "spec.md not found">
- **User stories:** <N, or "N/A">
- **Tasks completed:** <N / total> (<percentage>%)

---

## Track Coverage

<Paste "## Track Coverage" table from execution-plan.md verbatim, or "Not available — no execution-plan.md">

---

## Quality Gates

| Checklist | Total Items | Passed | Status |
|-----------|-------------|--------|--------|
| <checklist filename> | N | N | ✓ PASS / ✗ FAIL |

<"No checklists found." if checklists/ is empty or missing>

---

## Bug Report

- Bug files in `specs/<NNN>/bugs/`: <N>
<List filenames if N > 0>

---

## Session Cost Attribution

<Paste "## Session Totals" table from session-telemetry.md verbatim>
<"Session telemetry unavailable." if stub>

---

## Agent Chain Executed

<Paste "## Full Delegation Chain" section from execution-plan.md verbatim>
<"Not available — no execution-plan.md" if missing>
```

### Step 5 — Delegate to AI Architect for audit

Invoke the AI Architect agent with this handoff:

```
GOAL: Produce a Spec SDLC Audit for specs/<NNN-feature-name>/.
Return the full audit text to this skill as structured markdown text.
DO NOT write any file — the skill will write it.

KNOWN CONTEXT:
- Feature: <feature-folder-name>
- Spec acceptance criteria (from spec.md):
  <inline list of ACs, one per line, or "Not available">
- Plan affected modules (from plan.md):
  <inline 3-5 line summary>
- Execution-plan track coverage:
  <inline track table, or "Not available">
- tasks.md completion: <N / total> tasks completed
- checklists: <summary — e.g., "2/2 PASS" or "1/2 FAIL: deployment.md has 3 open items">
- bugs: <N bug files>
- Session cost (from session-telemetry.md):
  <paste Session Totals table, or "Not available">
- sdlc-report.md: just written to <FEATURE_DIR>/sdlc-report.md

DO NOT:
- Write any files
- Load files beyond what is described in KNOWN CONTEXT
- Perform broad repo exploration

RETURN: Full audit text following the Spec SDLC Audit Protocol format defined in ai-architect.md.
The text must start with "# AI Architect Audit:" and end with the "## Summary" section.
```

### Step 6 — Write ai-architect-audit.md

Write the text returned by AI Architect to `<FEATURE_DIR>/ai-architect-audit.md`.

If AI Architect returns BLOCKED or fails, write a stub:
```markdown
# AI Architect Audit: <feature-name>

_Audit unavailable — AI Architect did not return a complete response._
_Run `/speckit-report` again or invoke the AI Architect agent directly with the spec artifacts._
```

### Step 7 — Completion report

Output:
```
SPECKIT REPORT COMPLETE
Spec: specs/<NNN-feature-name>/

Files written:
  - specs/NNN/session-telemetry.md   (spec-attributed token cost)
  - specs/NNN/sdlc-report.md         (SDLC execution summary)
  - specs/NNN/ai-architect-audit.md  (AI Architect assessment)

SDLC quality: <value from ai-architect-audit.md ## Summary line>
Top recommendation: <first item from ai-architect-audit.md ## Recommendations, or "None">

Next: review ai-architect-audit.md recommendations before merging.
```

## Done When

- [ ] FEATURE_DIR resolved and prerequisites confirmed
- [ ] `session-telemetry.md` written (full data or stub)
- [ ] `sdlc-report.md` written with all 6 sections
- [ ] AI Architect audit text received
- [ ] `ai-architect-audit.md` written (full audit or stub)
- [ ] Completion report shown to user
