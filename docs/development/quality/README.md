# Quality Framework Documentation

This directory contains quality strategy documents maintained by the `quality-architect` agent.

## Scope

| Topic | Document |
|-------|----------|
| Performance baselines | [performance-baselines.md](performance-baselines.md) |
| Test layer pyramid strategy | (add as `test-layer-strategy.md`) |
| Coverage gate thresholds | (add as `coverage-gates.md`) |
| Smoke / sanity tier assignment rules | (add as `test-tier-strategy.md`) |
| NFR quality framework decisions | (add as `nfr-framework.md`) |

For NFR acceptance criteria and status tracking, see `docs/product/requirements/app_non_functional_requirements.md`.
For NFR gap analysis, see `docs/product/requirements/app_nfr_gap_analysis.md`.

## Ownership

- **Writes**: `quality-architect`
- **Approves**: `principal-solution-architect` (Maker-Checker)
- **Consulted**: `test-lead`

Do not write to this directory from `solution-architect` — architecture docs live in `docs/development/` (excluding this subdirectory).
