# /implement

Full feature implementation workflow — from requirements to commit-ready code.

## Usage

```bash
/implement <requirement ID or feature description>
```

**Examples:**
- `/implement JDF-SP-001` — implement a specific requirement
- `/implement add support for custom story points field` — describe the feature

---

## Workflow: 7-Step Checklist

Follow these steps in order. Claude will mark each step complete and move to the next.

### Step 0: Spec-Kit Gate (New Features Only)

**Skip this step for bug fixes and refactors.**

If implementing a **new feature**:

1. Check whether `specs/` contains a directory for this feature: `specs/NNN-<feature-name>/`
2. Verify `specs/NNN-<feature-name>/tasks.md` exists and carries a human-approval marker
3. If `tasks.md` does not exist or has not been approved: **stop here**. Run the full spec-kit workflow first:
   `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks` → `/speckit-analyze` → (human approval of `tasks.md`)
4. After human approval, return to this workflow and proceed to Step 1.

> This gate exists because `/implement` operates from approved artifacts. Skipping spec-kit means implementing without agreed scope, acceptance criteria, or task breakdown — the source of most rework.

### Step 1: Read Requirements

1. Look up the feature area using `/requirements` and find the relevant requirement file(s)
2. Read each affected requirement row
3. Note the **current Status** of each row (✓ Met, ✗ Not met, ⬜ N/T)
4. Understand the **Acceptance Criterion** — this is the test you must pass

### Step 2: Implement Code

1. Follow the design principles in CLAUDE.md (Single Responsibility, Open/Closed, DRY, KISS, YAGNI)
2. Use existing patterns and utilities — check `.claude/summaries/architecture-map.md` for module responsibilities; only load `docs/development/architecture.md` if deeper architectural detail is needed
3. For new metrics: see `app/core/metrics.py` and `/extend`
4. For new config vars: see `app/core/config.py` and `/extend`
5. For new server endpoints: see `app/server/_base.py` and `/extend`
6. Keep changes minimal and focused on the requirement

### Step 3: Write or Update Tests

1. Write tests in the **narrowest layer** that proves the behavior (unit > component > integration > e2e)
2. Use test factories from `tests/conftest.py` — see `/test` for reference
3. Each test should assert one aspect of the requirement's acceptance criterion
4. If you updated existing code, update existing tests — don't add redundant tests

### Step 3.5: Delegate to Test Lead

1. Delegate to `test-lead` with:
   - List of changed files (from Step 2 and Step 3)
   - Acceptance criteria from the relevant requirement rows (from Step 1)
   - Spec directory path if a `specs/NNN-feature/` exists
2. **Wait for `test-lead` to return `COMPLETE`** — this implies Phase 1 checklist approval and Phase 2 green smoke run (`python tests/runners/run_all_checks.py --smoke`).
3. **Do not proceed to Step 4 without this sign-off.** If `test-lead` returns `BLOCKED`, resolve the reported issues before continuing.

### Step 4: Run Full Test Suite

1. Run `/test` — all checks must pass (lint, type check, security, unit, component)
2. Fix any failures:
   - **Lint/type errors** — run `/lint --fix` to auto-correct
   - **Test failures** — read the failure, identify root cause, fix code (not the test)
   - **Security warnings** — address in code, not in test config
3. Re-run `/test` after each fix — confirm all pass

### Step 5: Update Test Coverage

1. Run `/coverage` to refresh `tests/coverage/test_coverage.md`
2. Verify the test count increased (if you added tests) or stayed same (if you only changed existing tests)

### Step 6: Update Requirement Status

1. Open the requirement file(s) from Step 1
2. For each row: set Status to `✓ Met` if the acceptance criterion is now satisfied
3. If the criterion is partially met or not yet tested, use `⬜ N/T` instead
4. Save the file

### Step 7: Update Documentation

Update docs **only if behavior changed** (not for internal refactors):

- **Module structure changed** → update `docs/development/architecture.md` (section 3: Project Layout, section 4: Architecture & Module Map)
- **New metric or metric output shape changed** → update `docs/product/metrics/`
- **UI or user-visible behavior changed** → update `docs/product/features/features.md`
- **Setup steps or CLI commands changed** → update `README.md`

---

## After Workflow Complete

1. Run `/test` one final time — all must pass
2. Run `/commit` with type `feat:` (new feature) or `fix:` (if this was a bug fix)
3. Optionally: run `/sync` to verify alignment across all 5 layers (requirements, code, tests, architecture.md, feature docs)

