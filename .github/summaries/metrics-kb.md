# Metrics Knowledge Base — Quick Reference

Use this summary before loading full metric definition files.
Source of truth: `docs/product/metrics/`

## Metric Index

| Metric | Category | Computed in | Key output fields | Definition file |
|--------|----------|-------------|------------------|-----------------|
| [METRIC_KEY] | [category] | Application source metrics module — `compute_[METRIC_KEY]()` | _(project-specific field names)_ | [METRIC_KEY].md |
| _(add project-specific metrics here)_ | | | | |

Replace `[METRIC_KEY]` and `[category]` with the actual metric identifiers and categories for your project. See `docs/product/metrics/` for the authoritative list.

## Value Types at a Glance

| Metric field | Type | Range | Notes |
|---|---|---|---|
| [METRIC_KEY] | _(absolute / percentage / count)_ | _(project-specific)_ | _(project-specific notes)_ |

## When to Load the Full Metric Doc

Load a full metrics file only when:
- An acceptance criterion directly references calculation logic for that metric.
- A requirement gap involves a specific metric's expected output shape.

## Routing

- Metric behavior questions → `docs/product/metrics/<metric>.md`
- Metric output shape (dict keys) → `docs/development/architecture.md` (metrics_dict section)
- Metric computation code → application source metrics module → `build_metrics_dict()`
