---
description: Execute the implementation planning workflow using the plan template to generate specs/NNN-feature-name/plan.md and related design artifacts.
---

# Spec-Kit: Plan

Execute the implementation planning workflow to produce `plan.md` and all required design artifacts for the feature.

## When to Invoke

- After `speckit.specify` (and optionally `speckit.clarify`) have produced a completed `spec.md`.
- Before `speckit.tasks` — tasks depend on the plan's tech stack, architecture, and phase structure.

## Key Behavior

### Pre-Execution Hooks

Check `.specify/extensions.yml` for `hooks.before_plan`. Skip hooks where `enabled: false`. Execute mandatory hooks and wait for results. Surface optional hooks to the user.

### Setup

Run `.specify/scripts/powershell/setup-plan.ps1 -Json` from repo root. Parse `FEATURE_SPEC`, `IMPL_PLAN`, `SPECS_DIR`, and `BRANCH` from JSON output.

### Phase 0: Outline & Research

1. Load `spec.md` and `.specify/memory/constitution.md` (if exists). Load the plan template (already copied to `IMPL_PLAN`).
2. Fill the Technical Context section; mark unknowns as `NEEDS CLARIFICATION`.
3. Fill the Constitution Check section; flag any violations as ERROR before proceeding.
4. For each unknown or dependency, generate a research task.
5. Consolidate findings into `research.md` using format: Decision / Rationale / Alternatives Considered.

### Phase 1: Design & Contracts

Prerequisites: `research.md` complete.

1. Extract entities from the feature spec → `data-model.md` (entity name, fields, relationships, validation rules, state transitions).
2. Define interface contracts in `contracts/` if the project exposes external interfaces (APIs, CLI commands, UI contracts). Skip if purely internal.
3. Create `quickstart.md` — integration scenarios and validation guide.
4. Run the agent context update script to refresh agent context.
5. Re-evaluate the Constitution Check after design.

### Post-Execution Hooks

Check `.specify/extensions.yml` for `hooks.after_plan`. Process mandatory hooks (emit execution) and surface optional hooks.

## Output

- `plan.md` with fully resolved Technical Context and Constitution Check.
- `research.md` with all `NEEDS CLARIFICATION` items resolved.
- `data-model.md` (if applicable).
- `contracts/` directory (if applicable).
- `quickstart.md`.
- Recommended next step: Invoke the `speckit.tasks` agent.
