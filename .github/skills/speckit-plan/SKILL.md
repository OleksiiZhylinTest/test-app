---
name: speckit-plan
description: "Execute the implementation planning workflow to generate plan.md and design artifacts."
argument-hint: "Path to the feature spec or feature name to plan"
user-invocable: true
---

# Spec-Kit: Plan

Execute the implementation planning workflow to produce `plan.md` and all required design artifacts.

## When to Use

- After `speckit-specify` (and optionally `speckit-clarify`) have produced a completed `spec.md`.
- Before `speckit-tasks` — tasks depend on the plan's tech stack, architecture, and phase structure.

## Procedure

1. **Check extension hooks**: Read `.specify/extensions.yml` for `hooks.before_plan`. Skip where `enabled: false`. Execute mandatory hooks and wait for results.

2. **Setup**: Run `.specify/scripts/powershell/setup-plan.ps1 -Json` from repo root. Parse `FEATURE_SPEC`, `IMPL_PLAN`, `SPECS_DIR`, and `BRANCH` from JSON output.

3. **Load context**: Read `FEATURE_SPEC` and `.specify/memory/constitution.md` (if exists). Load the plan template (already copied to `IMPL_PLAN`).

4. **Phase 0 — Outline & Research**:
   - Fill the Technical Context section; mark unknowns as `NEEDS CLARIFICATION`.
   - Fill the Constitution Check section from the loaded constitution. Raise ERROR for any unjustified violations before continuing.
   - For each unknown or dependency, generate a research task.
   - Consolidate findings into `research.md` with format: Decision / Rationale / Alternatives Considered.
   - All `NEEDS CLARIFICATION` items must be resolved before Phase 1.

5. **Phase 1 — Design & Contracts**:
   Prerequisites: `research.md` complete.
   - Extract entities from the feature spec → `data-model.md` (name, fields, relationships, validation rules, state transitions).
   - Define interface contracts in `contracts/` if the project exposes external interfaces. Skip if purely internal.
   - Create `quickstart.md` — integration scenarios and validation guide.
   - Run the agent context update script to refresh agent context.
   - Re-evaluate the Constitution Check after design.

6. **Post-execution hooks**: Check `.specify/extensions.yml` for `hooks.after_plan`. Process mandatory hooks (emit execution) and surface optional hooks.

## Output

- `plan.md` with fully resolved Technical Context and Constitution Check.
- `research.md` with all unknowns resolved.
- `data-model.md` (if applicable).
- `contracts/` directory (if applicable).
- `quickstart.md`.
- Recommend invoking `speckit-tasks` next.
