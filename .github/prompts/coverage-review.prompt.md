---
name: coverage-review
description: 'Structured coverage review for GH Test Lead. Run after any test addition, removal, or rename to validate coverage doc accuracy and pyramid balance.'
model: 'Claude Sonnet 4.6 (copilot)'
---

# Coverage Review

## Purpose
Validate that `tests/coverage/test_coverage.md` is accurate, up-to-date, and reflects a healthy test pyramid.

## Steps

1. Read `tests/coverage/test_coverage.md` — note current counts per layer (unit/component/integration/e2e).
2. Read `.github/summaries/test-structure.md` — confirm layer definitions.
3. Check pyramid balance:
   - Unit count should be the largest tier.
   - Integration count should be smaller than component count.
   - Flag if integration > component (pyramid inversion risk).
4. Verify the coverage doc was regenerated (not hand-edited) — check that the header contains the auto-generation timestamp comment if present.
5. Identify any test files added or removed since last review by comparing against known test inventory.
6. Report findings: pyramid balance status, any missing coverage areas, and recommended actions.

## Output
Produce a concise coverage review report. Flag any pyramid imbalance or coverage gap with severity: HIGH / MEDIUM / LOW.
