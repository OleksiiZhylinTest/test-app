# /review — Pull Request Review

Reviews the current branch against `master` for correctness, test coverage, requirements alignment, and project standards.

## Usage

```
/review
/review --quick     # diff + test impact only (skip docs/requirements check)
```

## Procedure

### Step 1 — Scope the diff
```bash
git diff master...HEAD --stat
git log master..HEAD --oneline
```
Identify all changed modules. Stop if the branch has no commits ahead of master.

### Step 2 — Requirements alignment
For each changed module, look up its requirement ID prefix using the table in `.claude/commands/requirements.md`. For each affected requirement row:
- Check `Status` column in the relevant `docs/product/requirements/*.md` file.
- Flag any requirement whose acceptance criterion is affected but whose `Status` is still `⬜ N/T` or `✗ Not met`.

### Step 3 — Test coverage impact
```bash
git diff master...HEAD -- tests/
```
- Confirm new behavior has a test in the narrowest applicable layer (unit > component > integration > e2e).
- Flag if a changed function in application source module has no corresponding test change.
- Flag if a new `/api/*` route handler has no component test.

### Step 4 — Code standards check
Review changed Python files against CLAUDE.md coding standards:
- Single Responsibility: application source modules each have one job (metrics computes only, reporters render only, config reads env only).
- No logic in `.j2` templates.
- No bare `print()` — use `logger.*`.
- No docstrings on self-explanatory functions.
- No error handling for impossible scenarios.
- No credentials in committed files.

### Step 5 — Security scan (for non-`--quick` runs)
```bash
git diff master...HEAD -- '*.py' | grep -E "(subprocess|eval|exec|os\.system|shell=True)"
```
Flag any new use of `shell=True`, `eval`, `exec`, or `os.system`. Confirm no `.env` values are logged.

### Step 6 — Docs check (for non-`--quick` runs)
If the diff touches:
- The metrics module in application source → check `docs/product/metrics/` for outdated metric descriptions
- Server handlers in application source → check route table in `.claude/summaries/architecture-map.md §Dev Server API Routes`
- `README.md` or `main.py` → no further check needed (these are the docs)

### Step 7 — Summary
Return a review report with these sections:
1. **Diff summary** — files changed, lines +/-
2. **Requirements** — IDs affected, status (met / not met / untested)
3. **Test coverage** — gaps found or confirmed covered
4. **Code standards** — violations or clean
5. **Security** — issues or clean
6. **Docs** — outdated or in sync
7. **Verdict** — `APPROVE`, `REQUEST CHANGES`, or `NEEDS DISCUSSION` with one-line rationale

## Notes
- Load `.claude/summaries/architecture-map.md` for module map and ownership; do not load `docs/development/architecture.md` unless a specific section is needed.
- Do not implement fixes. Flag issues with file:line references for the developer to address.
- If the diff is >500 lines, delegate the code-standards scan to an Explore subagent scoped to the changed files only.
