---
name: code-review
description: 'Step-by-step structured code review procedure for GH Dev Lead. Use for any PR review across app/, ui/, config/, tests/, or docs/ layers.'
argument-hint: 'Describe the PR: changed files, purpose, and layer(s) affected'
user-invocable: true
---

# Code Review

## When to Use

Use for any PR requiring Dev Lead sign-off, regardless of layer: `app/`, `ui/`, `config/`, `tests/`, or `docs/`.

## Procedure

1. Load `.github/summaries/architecture-module-map.md` for module ownership orientation.
2. If the change touches server handlers, load `.github/summaries/server-handler-map.md`.
3. If the change touches metrics, load `.github/summaries/metrics-contracts.md`.
4. If module boundaries are unclear, invoke the `architecture-lookup` skill.
5. If test coverage is in question, invoke the `test-layer-selection` skill.
6. Apply the full review checklist:
   - [ ] No business logic added to reporters (`report_html.py`, `report_md.py`) — [arch-conventions.md L2]
   - [ ] No fetch logic added to `metrics.py` — [arch-conventions.md L1]
   - [ ] No new cross-module imports violating the layer diagram — [arch-conventions.md L5]
   - [ ] Logging uses `logging.getLogger(__name__)` — no `print()`, no root logger — [dev-conventions.md #1]
   - [ ] No credential values logged or echoed — [dev-conventions.md #3]
   - [ ] New config variables added to `.env.example` first, then `config.py` — [dev-conventions.md #4]
   - [ ] Tests exist for the changed behavior in the narrowest applicable layer — [test-conventions.md Coverage Rules]
   - [ ] All PRs (not just `app/`) have Dev Lead sign-off
   - [ ] No business logic in `.j2` templates — [arch-conventions.md L4]
   - [ ] No `eval()`, `innerHTML` from user-controlled data, or inline `<script>` in UI files — [dev-conventions.md #13, #12]
   - [ ] No fixed-width `px` container values in CSS — [dev-conventions.md #15]
   - [ ] DAU modules follow single-responsibility: importer/normalizer/user_data separate — [arch-conventions.md D1–D4]
   - [ ] Any generated artifacts are in `generated/` not in the source tree — [devops-conventions.md Generated Artifacts Policy]
   - [ ] External API or library behavior is not guessed — must be confirmed or escalated to `GH Web Search`
7. If any checklist item is unclear due to missing external knowledge, escalate to `GH Web Search` before proceeding.
8. Produce output in this format:

   ```
   ## Code Review: [PR/task description]
   **Outcome**: APPROVED | CHANGE REQUEST

   ### Findings
   | Checklist Item | Status | Note |
   |---|---|---|
   ...

   ### Required Changes (if CHANGE REQUEST)
   ...

   ### Open Questions
   ...
   ```

9. Present the review output to the user and wait for confirmation before recording the outcome.

## Output

Structured review report in the format shown in step 8 above.
