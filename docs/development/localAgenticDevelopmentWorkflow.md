# Local Agentic Development Workflow

Based on your project setup (`CLAUDE.md` + `/subagents` command), here is the end-to-end process.

---

## Step 1 — Start a session with context

Open Claude Code in your project root. Auto mode is already on (`defaultMode: auto`), so no confirmations needed for safe ops.

```bash
claude
```

Optionally orient Claude with a one-liner:
```
What is the current state of the velocity chart feature?
```
Claude will spawn Explore subagents to read the codebase rather than doing it inline.

---

## Step 2 — Clarify requirements before touching code

Run the requirements command to find the relevant acceptance criteria:
```
/requirements
```
This locates the right `docs/product/requirements/<topic>_requirements.md` file and shows the current status column. Tell Claude which rows are affected by your task — it will update them at the end.

---

## Step 3 — Get a plan approved before implementation

For any non-trivial task, trigger plan mode explicitly:
```
Plan how to add <feature> to the velocity chart
```
Claude will:
1. Launch up to 3 Explore agents in parallel to read relevant modules
2. Launch a Plan agent to design the approach
3. Present the plan for your approval before writing any code

You review and approve (or redirect) before a single file is touched.

---

## Step 4 — Delegate implementation with `/implement`

Once the plan is approved:
```
/implement
```
This runs the 7-step checklist from `CLAUDE.md`:
1. Update requirements status
2. Implement the feature
3. Write/update tests
4. Run `python tests/runners/run_all_checks.py`
5. Fix all failures
6. Update test coverage stats
7. Update relevant docs

Claude will spawn subagents for independent sub-tasks (e.g., one agent writes tests while another updates docs) — parallel by default.

---

## Step 5 — Fix failures with `/fix`

If the test run surfaces failures:
```
/fix
```
Claude follows a 7-step bug-fix loop: reads the failure, locates root cause (Explore agent), patches, re-runs checks, and updates requirements. It will NOT mark the task done while tests are red.

---

## Step 6 — Verify alignment with `/sync`

Before committing, run the cross-layer audit:
```
/sync
```
This checks that requirements, code, tests, and docs are all consistent — catches stale requirement rows, missing test coverage, and doc drift.

---

## Step 7 — Commit with `/commit`

```
/commit
```
Produces a correctly formatted commit message (imperative subject, body only when WHY is non-obvious, `Co-Authored-By` trailer). Never amends, never skips hooks.

---

## Delegating specific tasks to subagents manually

When you want to parallelize or isolate work yourself:

| What you want | What to say |
|--------------|-------------|
| Explore the codebase quickly | `"Explore app/core/metrics.py and tell me how velocity is computed"` |
| Research + plan before acting | `"Plan a fix for the dedup asymmetry in compute_dau_metrics"` |
| Run a long task in the background | `"In the background, run the full test suite and report failures"` |
| Isolated experimental change | `"Work in a worktree to refactor the HTML reporter"` |

Reference `/subagents` anytime for the full orchestration guide:
```
/subagents
```

---

## Quick reference — command → phase mapping

```
/requirements   ← before starting
/implement      ← write code
/fix            ← when tests fail
/lint           ← quick check during dev
/coverage       ← after adding/removing tests
/sync           ← before committing
/commit         ← final step
/subagents      ← orchestration patterns
```

---

## Key rules to remember

1. **Plan mode before non-trivial work** — saves more time than it costs
2. **Never start implementing without green requirements** — `/requirements` first
3. **Tests must pass before `/commit`** — the safety hook will block force-push anyway
4. **Subagents run concurrently** — state independent tasks in a single message for parallel execution
5. **`rm` now prompts** — any file deletion will ask for confirmation
