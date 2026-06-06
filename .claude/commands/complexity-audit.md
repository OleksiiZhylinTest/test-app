# /complexity-audit

Run a full code-complexity audit and produce a prioritised improvement plan.

## Usage

```bash
/complexity-audit
```

## Step 1 — Route to PSA

Invoke `principal-solution-architect`. All further steps execute under PSA orchestration.

## Step 2 — PSA Delegates to SA

PSA issues the following handoff to `solution-architect`:

```
GOAL: Generate a current complexity report and draft an improvement plan.

KNOWN CONTEXT:
- Test-count source: tests/coverage/test_coverage.md
- Complexity tool: tests/tools/complexity_report.py
- Report output: generated/reports/complexity_<timestamp>.md
- Improvement plan target: docs/development/quality/complexity_improvement_plan.md
- C6 constraint: test_coverage.py MUST run before complexity_report.py

DO NOT:
- Skip python tests/tools/test_coverage.py before running the complexity tool (C6)
- Write files outside docs/development/quality/ and generated/reports/

RETURN: Path of generated report + full draft of complexity_improvement_plan.md
```

## Step 3 — SA Executes

1. `python tests/tools/test_coverage.py` — refresh test count (C6 pre-req)
2. `python tests/tools/complexity_report.py` — generate complexity report
3. Read the report; extract all refactor signals and watch items
4. Write `docs/development/quality/complexity_improvement_plan.md` per the Complexity Audit format in `solution-architect.md`
5. Return output to PSA

## Step 4 — PSA Maker-Checker Review

PSA reviews SA's improvement plan using the standard Review Checklist including item #11 (code complexity).

Key checks:
- All refactor signals from the report are represented in the improvement plan
- Remediations are concrete (specific function/file, action, effort size)
- No scope creep beyond what the report identifies
- C6 sequencing was followed (test_coverage.md regenerated before complexity tool ran)

Cycle limit: 3 (escalate to human after 3 rejections per standard protocol).

## Step 5 — Accept or Reject

- **Approved**: PSA reports `COMPLETE` to PM with path to improvement plan.
- **Rejected after 3 cycles**: PSA escalates to human per Escalation Message Format in `principal-solution-architect.md`.

## After Audit Complete

- `docs/development/quality/complexity_improvement_plan.md` contains prioritised refactor candidates.
- Present findings to the user — do not auto-implement any refactors.
- If the user wants to act on a refactor signal, route through PM → Dev Lead → Developer.
