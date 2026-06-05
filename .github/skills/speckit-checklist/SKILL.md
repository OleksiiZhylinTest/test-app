---
name: speckit-checklist
description: "Generate a custom quality checklist for the current feature based on user requirements."
argument-hint: "Feature name or path to spec.md"
user-invocable: true
---

# Spec-Kit: Checklist

Generate a custom quality checklist for the current feature. Checklists are **unit tests for requirements** — they validate the quality, clarity, and completeness of requirements, not the implementation.

## When to Use

- After `speckit-specify` to validate requirement quality before planning.
- At any stage to add domain-specific quality gates (security, UX, API, performance, etc.).
- Before `speckit-implement` to establish pre-implementation gates.

## Core Concept

Every checklist item MUST evaluate requirements for:
- **Completeness**: Are all necessary requirements present?
- **Clarity**: Are requirements unambiguous and specific?
- **Consistency**: Do requirements align with each other?
- **Measurability**: Can requirements be objectively verified?

**NOT** for implementation verification (e.g., "Test error handling works"). **FOR** requirement quality (e.g., "Are error state requirements defined for all user-facing operations?").

## Procedure

1. **Check extension hooks**: Read `.specify/extensions.yml` for `hooks.before_checklist`. Skip where `enabled: false`. Execute mandatory hooks and wait for results.

2. **Setup**: Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json` from repo root. Parse `FEATURE_DIR` and `AVAILABLE_DOCS`. Load `.specify/memory/constitution.md` if it exists.

3. **Clarify intent** (up to 5 total questions, present one at a time):
   Extract signals from user input + spec/plan/tasks: feature domain keywords, risk indicators, stakeholder hints, explicit deliverables. Cluster into candidate focus areas (max 4) ranked by relevance. Ask only questions whose answers materially change checklist content. Question archetypes: scope refinement, risk prioritization, depth calibration, audience framing, boundary exclusion, scenario class gap. After initial 3 questions, ask up to 2 more (Q4/Q5) only if ≥2 scenario classes remain unclear.

4. **Load feature context**: Read `spec.md`, `plan.md` (if exists), `tasks.md` (if exists) from `FEATURE_DIR`. Load only portions relevant to active focus areas.

5. **Generate checklist**:
   - Create `FEATURE_DIR/checklists/` if it doesn't exist.
   - Use short descriptive domain-based filename (e.g., `ux.md`, `api.md`, `security.md`).
   - If file does not exist: create with items numbered from CHK001.
   - If file exists: append continuing from the last CHK ID.
   - Never delete or replace existing checklist content — always preserve and append.

6. **Post-execution hooks**: Check `.specify/extensions.yml` for `hooks.after_checklist`. Process mandatory and optional hooks.

## Output

- Path to the generated or updated checklist file.
- Total items added.
- Domain coverage summary.
