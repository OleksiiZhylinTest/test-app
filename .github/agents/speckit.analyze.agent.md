---
description: Perform a non-destructive cross-artifact consistency and quality analysis across spec.md, plan.md, and tasks.md. Read-only — makes no file changes.
---

# Spec-Kit: Analyze

Perform a non-destructive cross-artifact consistency and quality analysis across the three core spec-kit artifacts before implementation begins.

## When to Invoke

- After `speckit.tasks` has produced a complete `tasks.md`.
- Before `speckit.implement` — analysis surfaces gaps that should be resolved first.
- Run as a read-only quality gate; never modifies any file.

## Key Behavior

### Pre-Execution Hooks

Check `.specify/extensions.yml` for `hooks.before_analyze`. Skip hooks where `enabled: false`. Execute mandatory hooks and wait for results. Surface optional hooks to the user.

### Initialize Analysis Context

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json -RequireTasks -IncludeTasks` from repo root. Parse `FEATURE_DIR` and `AVAILABLE_DOCS`. Derive absolute paths for `spec.md`, `plan.md`, and `tasks.md`. Abort if any required file is missing.

### Load Artifacts (Progressive Disclosure)

- **From `spec.md`**: Overview, Functional Requirements, Success Criteria, User Stories, Edge Cases.
- **From `plan.md`**: Architecture/stack choices, Data Model references, Phases, Technical constraints.
- **From `tasks.md`**: Task IDs, descriptions, phase grouping, parallel markers `[P]`, referenced file paths.
- **From constitution**: Load `.specify/memory/constitution.md` for principle validation.

### Build Semantic Models

- Requirements inventory: record FR-### and SC-### keys; include only Success Criteria requiring buildable work.
- User story/action inventory with acceptance criteria.
- Task coverage mapping: map each task to requirements/stories.
- Constitution rule set: MUST/SHOULD normative statements.

### Detection Passes (Limit 50 findings)

**A. Duplication Detection** — near-duplicate requirements; lower-quality phrasing candidates.

**B. Ambiguity Detection** — vague adjectives without measurable criteria; unresolved placeholders (TODO, TKTK, `???`, `<placeholder>`).

**C. Underspecification** — requirements missing object or measurable outcome; user stories missing acceptance criteria; tasks referencing undefined files or components.

**D. Constitution Alignment** — requirements or plan elements conflicting with MUST principles; missing mandated sections. Constitution conflicts are automatically CRITICAL.

**E. Coverage Gaps** — requirements with zero associated tasks; tasks with no mapped requirement/story; Success Criteria requiring buildable work not reflected in tasks.

### Output Format

Produce a structured analysis report organized by detection category. For each finding: severity (CRITICAL / HIGH / MEDIUM / LOW), artifact location, description, suggested remediation. Offer an optional remediation plan — the user must explicitly approve before any follow-up edits occur.

**STRICTLY READ-ONLY**: Do not modify any files.

## Output

- Structured analysis report with findings by category.
- Coverage gap summary.
- Constitution alignment status.
- Optional remediation plan (user must approve before acting).
- Recommended next step: resolve CRITICAL findings, then invoke the `speckit.implement` agent.
