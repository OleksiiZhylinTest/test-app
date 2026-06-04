# Metrics Knowledge Base — Quick Reference

Use this summary before loading full metric definition files.
Source of truth: `docs/product/metrics/`

## Metric Index

| Metric | Category | Computed in | Key output fields | Definition file |
|--------|----------|-------------|------------------|-----------------|
| Velocity | Sprint performance | `app/core/metrics.py` — `compute_velocity()` | `sprint_id`, `sprint_name`, `start_date`, `end_date`, `velocity`, `issue_count` | velocity.md |
| AI Assistance Trend | AI adoption | `app/core/metrics.py` — `compute_ai_trend()` | `sprint_id`, `sprint_name`, `ai_sp`, `total_sp`, `ai_pct` | ai_assistance_trend.md |
| AI Usage Details | AI adoption | `app/core/metrics.py` — `compute_ai_usage_details()` | `ai_assisted_issue_count`, `tools` (list: `label`, `count`, `pct`), `actions` (list: `label`, `count`, `pct`) | ai_usage_details.md |
| Cycle Time | Delivery speed | `app/core/metrics.py` — `compute_cycle_time()` | `sample_size`, `mean_days`, `median_days`, `min_days`, `max_days` | cycle_time.md |
| DAU (Daily Active Usage) | Tool adoption | `app/core/metrics.py` — `compute_dau_metrics()` | `response_count`, `team_avg`, `team_avg_pct`, `by_role` (list), `breakdown` (list) | dau_metric.md |
| Custom Trends | Extensible / custom | `app/core/metrics.py` — `compute_custom_trends()` (placeholder) | `sprint_id`, `sprint_name`, `<custom_keys>` | custom_trends.md |

## Value Types at a Glance

| Metric field | Type | Range | Notes |
|---|---|---|---|
| `velocity` | Absolute (story points or issue count) | ≥ 0.0 | Switches to issue count when `ESTIMATION_TYPE=JiraTickets` |
| `ai_sp`, `total_sp` | Absolute (story points) | ≥ 0.0 | Raw sums, never normalised |
| `ai_pct` | Percentage | 0.0 – 100.0 | `(ai_sp / total_sp) × 100`, 1 dp |
| `pct` (AI Usage Details) | Percentage (can exceed 100%) | ≥ 0.0 | Issues can carry multiple labels simultaneously |
| `mean_days`, `median_days`, `min_days`, `max_days` | Absolute (calendar days) | ≥ 0.0 | Never expressed as percentages |
| `team_avg` | Absolute (avg days/week) | 0.0 – 5.0 | DAU snapshot |
| `team_avg_pct` | Percentage | 0.0 – 100.0 | `(team_avg / 5) × 100`, 1 dp |

## When to Load the Full Metric Doc

Load a full metrics file only when:
- An acceptance criterion directly references calculation logic for that metric.
- A requirement gap involves a specific metric's expected output shape.

## Routing

- Metric behavior questions → `docs/product/metrics/<metric>.md`
- Metric output shape (dict keys) → `docs/development/architecture.md` (metrics_dict section)
- Metric computation code → `app/core/metrics.py` → `build_metrics_dict()`
