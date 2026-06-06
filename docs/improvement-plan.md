# Documentation Improvement Plan

Generated from `python tools/docs_audit.py docs/` on 2026-06-05.
Audit report: `generated/reports/docs-audit.md`.

**Scope:** 48 files, 85 findings → 10 Critical, 1 Warning, 74 Info.
**Genuine actionable issues after false-positive triage:** 15 work items across 4 groups.

---

## Group 1 — Fix Broken Links (P0, ~30 min total)

Root cause: `docs/development/` files use `../` to reference repo-root files, but `../`
from `docs/development/` resolves to `docs/`, not the repo root. Correct to `../../`.

| File | Current | Fix |
|------|---------|-----|
| `development/architecture.md:668` | `../README.md` | `../../README.md` |
| `development/architecture.md:669` | `../CLAUDE.md` | `../../CLAUDE.md` |
| `development/architecture.md:673` | `../tests/coverage/test_coverage.md` | `../../tests/coverage/test_coverage.md` |
| `development/architecture.md:674` | `../tests/coverage/requirements/` | `../../tests/coverage/requirements/` |
| `development/architecture.md:675` | `../.env.example` | `../../.env.example` |

**`development/pipeline.md`** — 3 cross-boundary links to `.github/` and `tests/`. Since
these reference files outside `docs/`, convert to descriptive text rather than live links;
the `.github` files are readable in the GitHub web UI directly.

| Line | Action |
|------|--------|
| :5 | Replace `[.github/workflows/ci.yml](../.github/workflows/ci.yml)` → plain text reference |
| :341 | Replace `[.github/dependabot.yml](../.github/dependabot.yml)` → plain text reference |
| :442 | Replace `[tests/component/test_server.py](../tests/component/test_server.py)` → `../../tests/component/test_server.py` |

**`product/metrics/custom_trends.md:65,151`** — 2 links to `.cursor/rules/extension-patterns.mdc`
which no longer exists. Replace both with a link to `../../docs/development/jira/extension-guide.md`.

---

## Group 2 — Remove Duplicate File (P0, 2 min)

`docs/development/assistant_customization_governance.md` is an exact duplicate of
`docs/development/ai/assistant_customization_governance.md`.

**Action:** Delete `docs/development/assistant_customization_governance.md`. The canonical
copy lives under `docs/development/ai/`.

---

## Group 3 — Add Missing Index Files (P1, ~1 hr total)

`docs/development/` and `docs/product/features/` have no README. This leaves 7 documents
as orphans with no navigation path from any other doc. Creating two index files closes all
7 orphan findings.

### `docs/development/README.md` (new)

Should link to:
- `architecture.md` — module map, data flow, technology stack
- `pipeline.md` — CI/CD operations guide
- `adr/` — Architecture Decision Records
- `ai/` — agent orchestration, customization governance
- `confluence/` — Confluence API reference and extension guides
- `jira/` — Jira API reference and extension guides
- `quality/` — test strategy, performance baselines

### `docs/product/features/README.md` (new)

Should link to:
- `features.md` — UI and user-visible feature inventory
- `confluence_kb.md` — Confluence knowledge base feature

---

## Group 4 — Defer / Skip

The following Info findings are noise for this codebase:

| Finding | Why deferred |
|---------|-------------|
| Underscore filenames in `product/requirements/` (20 files) | Intentional — filenames match requirement ID prefix convention tracked in `requirements/README.md` |
| Thin sections in code-heavy reference docs (`confluence/`, `jira/`) | Code blocks are the content; prose is intentionally minimal in API reference docs |
| `development/adr/adr-template.md` orphan | Expected — ADR templates are not linked from other docs; accessed via `adr/README.md` |
| `development/quality/performance-baselines.md` orphan | Link from `quality/README.md` to resolve if desired, but low urgency |

---

## Execution Order

| # | Action | File(s) | Effort |
|---|--------|---------|--------|
| 1 | Fix `architecture.md` relative paths | `development/architecture.md` | 5 min |
| 2 | Fix `pipeline.md` cross-boundary links | `development/pipeline.md` | 10 min |
| 3 | Fix `.cursor` links in `custom_trends.md` | `product/metrics/custom_trends.md` | 5 min |
| 4 | Delete duplicate governance file | `development/assistant_customization_governance.md` | 1 min |
| 5 | Create `docs/development/README.md` | new | 20 min |
| 6 | Create `docs/product/features/README.md` | new | 15 min |

All six items are BA-owned. PO approval needed before executing 5–6 (new docs).
Re-run `python tools/docs_audit.py docs/` after to verify Critical count reaches 0.
