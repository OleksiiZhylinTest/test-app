# /sync

Alignment audit — verify requirements, code, tests, and documentation are consistent across all 5 layers.

## Usage

```bash
/sync                      # full audit across all 5 layers
/sync requirements         # audit requirement Status accuracy only
/sync code                 # audit code-to-test alignment
/sync docs                 # audit documentation accuracy
```

---

## Full Audit: 5-Layer Checklist

Run these checks in order. Each layer builds on the previous one.

### Layer 1: Requirements Status

**Goal:** Verify that each requirement Status (`✓ Met`, `✗ Not met`, `⬜ N/T`) accurately reflects implementation.

Delegate to an Explore subagent — do not read requirement files inline:

```
Explore docs/product/requirements/ — requirements cross-check:
1. Read README.md for the file map.
2. For each requirement file: scan all ✓ Met rows and identify the test(s) that verify them
   (check tests/unit/ and tests/component/ for matching test names or requirement IDs).
3. For each ✗ Not met row: check whether corresponding code already exists in the application source.
Return a gap table: requirement ID | file | status | test coverage | gap description.
```

Wait for result. Then also run `/test` — if any test directly tied to a `✓ Met` row fails, add it as an additional gap.

Report all gaps found (do NOT auto-fix — report and wait for direction).

### Layer 2: Code ↔ Tests Alignment

**Goal:** Verify application code matches test expectations (baseline sanity check).

1. Run `/test` — all unit + component tests must pass
2. If any test fails:
   - Read the failure message
   - Identify whether it's a code bug (test is correct, code is wrong) or a test bug (test is wrong)
   - Flag as **gap**: "<test name>: <failure summary>"
3. No code changes yet — just report gaps

### Layer 3: Architecture Documentation

**Goal:** Verify `docs/development/architecture.md` reflects current module structure and patterns.

Delegate to an Explore subagent — do not read architecture.md inline:

```
Explore docs/development/architecture.md vs current code:
1. Read docs/development/architecture.md sections covering Project Layout and Architecture & Module Map.
2. For each directory in the Project Layout tree: verify it still exists (Glob or ls).
3. Compare each module description against the actual file at that path.
4. Check that data dict shapes match the application source.
Return a gap list: section | expected | actual | gap description.
```

Wait for result, then report gaps.

### Layer 4: Feature Documentation

**Goal:** Verify user-facing behavior is documented in `docs/product/features/features.md`.

Delegate to an Explore subagent — do not read UI templates inline:

```
Explore docs/product/features/ vs current UI:
1. Read docs/product/features/features.md (if it exists; if not, report missing).
2. Read ui/index.html and ui/templates/report.html.j2 — list every named UI section,
   tab, control, or report section.
3. Cross-reference: which UI elements appear in features.md? Which are absent?
Return a gap list: UI element | in features.md? | gap description.
```

Wait for result, then report gaps.

### Layer 5: Metric Documentation

**Goal:** Verify `docs/product/metrics/` accurately describes all computed metrics and their output shapes.

Delegate to an Explore subagent — do not read all metric docs inline:

```
Explore docs/product/metrics/ vs application source metrics module:
1. List all .md files in docs/product/metrics/.
2. For each metric doc: extract the metric name, computation description, and output shape.
3. Read the metrics module — list every field added to metrics_dict in build_metrics_dict().
4. Cross-reference: which metrics_dict fields have a doc? Which are undocumented?
Return a gap table: metric name | doc file | documented? | shape matches? | gap description.
```

Wait for result, then report gaps.

---

## Summary Output

After running the audit, provide a report:

```
ALIGNMENT AUDIT SUMMARY
======================

Layer 1 (Requirements):
  ✓ All Met rows have test coverage
  ⚠ GAP: <requirement-id> marked Met but test fails

Layer 2 (Code ↔ Tests):
  ✓ All unit + component tests pass

Layer 3 (Architecture Docs):
  ⚠ GAP: New module not documented

Layer 4 (Feature Docs):
  ⚠ GAP: Feature added but docs/product/features/features.md not updated

Layer 5 (Metric Docs):
  ✓ All metrics documented in docs/product/metrics/

TOTAL GAPS FOUND: <N>
ACTION REQUIRED: See gaps above. User to decide which to address and in what priority.
```

---

## After Audit

Do NOT auto-fix gaps. Instead:

1. Present the gap report to the user
2. Ask which gaps should be fixed (e.g., "Should we update architecture.md to document the new metric?")
3. For each gap user approves: use `/implement`, `/fix`, or direct code changes to address
4. After fixes: re-run `/sync <layer>` to verify the gap is closed
