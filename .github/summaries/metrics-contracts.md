# Copilot Summary: Metrics Contracts

Use this summary before loading metric documentation or application source metrics modules when the task only needs metric ownership, computation source, or output shape orientation.

## Source of Truth

- Application source metrics module (see `AGENTS.md` or `.claude/summaries/architecture-map.md` for path) — all computation functions
- `docs/product/metrics/README.md` — metric index, data fields reference, config quick reference
- `docs/product/metrics/<metric>.md` — per-metric purpose, calculation, and output shape

## Central Output

`build_metrics_dict()` in the application source metrics module assembles the single dict consumed by both reporters. All metric keys live in this dict.

## Metric → Computation Function Map

| Metric | Function | Output key(s) in metrics_dict |
|--------|----------|-------------------------------|
| [METRIC_KEY] | `compute_[METRIC_KEY]()` | `[METRIC_KEY]` |
| _(add project-specific metrics here)_ | | |

Replace `[METRIC_KEY]` with the actual metric identifiers for your project. See `docs/product/metrics/` for the authoritative list.

## Active Data Source Fields

| Logical key | Default field ID | Used by |
|-------------|-----------------|---------|
| `[METRIC_KEY]` | _(project-specific)_ | _(project-specific metrics)_ |

Field IDs are customisable per data source instance via `config/` schema files.

## Report Coverage

| Metric | HTML report | Markdown report |
|--------|:-----------:|:---------------:|
| [METRIC_KEY] | ✓ | ✓ |

## Design Rules

- The metrics module is pure computation only — no fetch logic, no I/O.
- Reporters format data only — they do not recompute.
- Extend via `build_metrics_dict()`: add a new key, not a new function signature.

## Escalate to Source When

- you need exact output shape (field names, nesting) for a specific metric
- you are adding a new metric (update `build_metrics_dict()` and both reporters)
- you need data source field schema details beyond the active-fields table above
- you need config variable names for classification logic
