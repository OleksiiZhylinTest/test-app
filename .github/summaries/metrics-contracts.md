# Copilot Summary: Metrics Contracts

Use this summary before loading `docs/product/metrics/` or `app/core/metrics.py` when the task only needs metric ownership, computation source, or output shape orientation.

## Source of Truth

- `app/core/metrics.py` — all computation functions
- `docs/product/metrics/README.md` — metric index, Jira fields reference, config quick reference
- `docs/product/metrics/<metric>.md` — per-metric purpose, calculation, and output shape

## Central Output

`build_metrics_dict()` in `app/core/metrics.py` assembles the single dict consumed by both reporters. All metric keys live in this dict.

## Metric → Computation Function Map

| Metric | Function | Output key(s) in metrics_dict |
|--------|----------|-------------------------------|
| Velocity | `compute_velocity()` | `velocity` |
| Cycle Time | `compute_cycle_time()` | `cycle_time` |
| AI Assistance Trend | `compute_ai_assistance_trend()` | `ai_assistance_trend` |
| AI Usage Details | `compute_ai_usage_details()` | `ai_usage_details` |
| Sprint Issue Details | `compute_sprint_issue_details()` | `sprint_issue_details` |
| DAU Metrics | `compute_dau_metrics()` | `dau` |
| DAU Trend | `compute_dau_trend()` | `dau_trend` |

## Active Jira Fields

| Logical key | Default Jira field ID | Used by |
|-------------|----------------------|---------|
| `story_points` | `customfield_10016` | Velocity, AI Assistance Trend |
| `status` | `status` | Velocity, Cycle Time, AI metrics |
| `labels` | `labels` | AI Assistance Trend, AI Usage Details |
| `sprint` | `customfield_10020` | All metrics (sprint grouping) |
| Changelog histories | _(expand param)_ | Cycle Time |

Field IDs are customisable per Jira instance via `config/jira_schema.json`.

## Report Coverage

| Metric | HTML report | Markdown report |
|--------|:-----------:|:---------------:|
| Velocity | ✓ | ✓ |
| Cycle Time | ✓ | ✓ |
| AI Assistance Trend | ✓ | planned |
| AI Usage Details | ✓ | planned |
| DAU Survey / DAU Trend | ✓ | ✓ |
| Custom Trends | ✓ | ✓ |

## Design Rules

- `metrics.py` is pure computation only — no fetch logic, no I/O.
- Reporters (`report_html.py`, `report_md.py`) format data only — they do not recompute.
- Extend via `build_metrics_dict()`: add a new key, not a new function signature.

## Escalate to Source When

- you need exact output shape (field names, nesting) for a specific metric
- you are adding a new metric (update `build_metrics_dict()` and both reporters)
- you need Jira field schema details beyond the active-fields table above
- you need config variable names for AI label classification
