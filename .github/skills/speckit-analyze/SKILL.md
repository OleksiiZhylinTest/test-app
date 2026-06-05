---
name: speckit-analyze
description: "Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md."
argument-hint: "Path to the feature directory or feature name to analyze"
user-invocable: true
---

# Spec-Kit: Analyze

Perform a non-destructive cross-artifact consistency and quality analysis across the three core spec-kit artifacts. Strictly read-only — makes no file changes.

## When to Use

- After `speckit-tasks` has produced a complete `tasks.md`.
- Before `speckit-implement` — surfaces gaps and constitution violations to resolve first.

## Procedure

1. **Check extension hooks**: Read `.specify/extensions.yml` for `hooks.before_analyze`. Skip where `enabled: false`. Execute mandatory hooks and wait for results.

2. **Initialize analysis context**: Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` from repo root. Parse `FEATURE_DIR` and `AVAILABLE_DOCS`. Derive absolute paths for `spec.md`, `plan.md`, and `tasks.md`. Abort if any required file is missing.

3. **Load artifacts (progressive disclosure)**:
   - **From `spec.md`**: Overview, Functional Requirements, Success Criteria, User Stories, Edge Cases.
   - **From `plan.md`**: Architecture/stack, Data Model references, Phases, Technical constraints.
   - **From `tasks.md`**: Task IDs, descriptions, phase grouping, `[P]` markers, referenced file paths.
   - **From `.specify/memory/constitution.md`**: Principle validation rules.

4. **Build semantic models**:
   - Requirements inventory: FR-### and SC-### keys; include only Success Criteria requiring buildable work.
   - User story/action inventory with acceptance criteria.
   - Task coverage mapping (requirements and stories to tasks).
   - Constitution rule set: MUST/SHOULD normative statements.

5. **Detection passes** (limit 50 total findings):
   - **A. Duplication**: Near-duplicate requirements; lower-quality phrasing candidates.
   - **B. Ambiguity**: Vague adjectives without measurable criteria; unresolved placeholders (TODO, TKTK, `???`, `<placeholder>`).
   - **C. Underspecification**: Requirements missing object or measurable outcome; tasks referencing undefined components.
   - **D. Constitution Alignment**: Any conflict with MUST principles → automatically CRITICAL. Constitution authority is non-negotiable within this analysis scope.
   - **E. Coverage Gaps**: Requirements with zero associated tasks; tasks unmapped to any requirement; SC items requiring buildable work not reflected in tasks.

6. **Output structured report**: Organize findings by detection category. For each finding: severity (CRITICAL / HIGH / MEDIUM / LOW), artifact location, description, suggested remediation. Offer an optional remediation plan — the user must explicitly approve before any follow-up edits occur.

**STRICTLY READ-ONLY**: Do not modify any files.

## Output

- Structured analysis report with findings by category.
- Coverage gap summary.
- Constitution alignment status.
- Optional remediation plan (user must approve before acting).
- Recommend resolving CRITICAL findings, then invoke `speckit-implement`.
