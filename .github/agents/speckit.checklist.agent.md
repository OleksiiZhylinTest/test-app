---
description: Generate a custom quality checklist for the current feature based on user requirements, written to specs/NNN-feature-name/checklists/.
---

# Spec-Kit: Checklist

Generate a custom quality checklist for the current feature. Checklists are "unit tests for requirements" — they validate the quality, clarity, and completeness of requirements, not the implementation.

## When to Invoke

- After `speckit.specify` to validate requirement quality before planning.
- At any point during the SDLC to add domain-specific quality gates (security, UX, API, etc.).
- Before `speckit.implement` to establish pre-implementation gates.

## Key Behavior

### Core Concept: Unit Tests for Requirements

Every checklist item MUST evaluate requirements for:
- **Completeness**: Are all necessary requirements present?
- **Clarity**: Are requirements unambiguous and specific?
- **Consistency**: Do requirements align with each other?
- **Measurability**: Can requirements be objectively verified?

Do NOT write checklist items that verify implementation correctness (e.g., "Verify the button clicks correctly"). Write items that test requirement quality (e.g., "Are hover state requirements defined for all interactive elements?").

### Pre-Execution Hooks

Check `.specify/extensions.yml` for `hooks.before_checklist`. Skip hooks where `enabled: false`. Execute mandatory hooks and wait for results. Surface optional hooks to the user.

### Setup

Run `.specify/scripts/powershell/check-prerequisites.ps1 -Json` from repo root. Parse `FEATURE_DIR` and `AVAILABLE_DOCS`. Load `.specify/memory/constitution.md` if it exists.

### Clarify Intent (Dynamic)

Derive up to 3 targeted clarifying questions from user input + spec/plan/tasks signals. Questions must be generated from extracted signals (feature domain keywords, risk indicators, stakeholder hints). Only ask questions whose answers materially change checklist content. Present as Q1/Q2/Q3; may ask up to 2 more follow-ups (Q4/Q5) if ≥2 scenario classes remain unclear, with one-line justification each. Do not exceed 5 total questions.

Question archetypes: scope refinement, risk prioritization, depth calibration, audience framing, boundary exclusion, scenario class gap.

### Load Feature Context

Read from `FEATURE_DIR`: `spec.md` (requirements and scope), `plan.md` if exists (technical details, dependencies), `tasks.md` if exists (implementation tasks). Load only portions relevant to active focus areas.

### Generate Checklist

- Create `FEATURE_DIR/checklists/` directory if it doesn't exist.
- Use short descriptive filename based on domain (e.g., `ux.md`, `api.md`, `security.md`).
- If file does not exist: create with items numbered from CHK001.
- If file exists: append new items continuing from the last CHK ID.
- Never delete or replace existing checklist content — always preserve and append.

## Output

- Path to generated or updated checklist file.
- Total items added.
- Domain coverage summary.
