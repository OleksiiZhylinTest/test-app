# Metric Computation Requirements — AI Adoption Metrics Report

This document defines requirements for the pure metric computation logic implemented in
`app/core/metrics.py`. It covers done-status resolution, story points extraction, sprint
attribution and deduplication, velocity aggregation, estimation-type switching, and the
canonical value type (absolute vs. percentage) for every metric field and its chart
display format.

---

## Table of Contents

1. [Done Status Resolution](#1-done-status-resolution)
2. [Story Points Extraction](#2-story-points-extraction)
3. [Sprint Attribution and Deduplication](#3-sprint-attribution-and-deduplication)
4. [Velocity Aggregation](#4-velocity-aggregation)
5. [Estimation Type Mode](#5-estimation-type-mode)
6. [Output Shape](#6-output-shape)
7. [Metric Value Types and Percentage Display](#7-metric-value-types-and-percentage-display)
8. [Future Enhancements](#8-future-enhancements)

---

## 1. Done Status Resolution

Controls which issues `_is_done()` considers complete. Applies to velocity and AI assistance trend.

| ID | Requirement | Acceptance Criterion | Status | Tests |
|----|-------------|----------------------|--------|-------|
| MC-V-DS-001 | Default done statuses cover standard Jira terminal values | `_is_done()` returns `True` for status names `Done`, `Closed`, `Resolved`, `Complete`; returns `False` for `In Progress`, `To Do`, and an empty string | ✓ Met | `test_is_done` |
| MC-V-DS-002 | Status matching is case-insensitive | `_is_done()` returns `True` for `"done"` (lowercase) and `"DONE"` (uppercase) without any schema changes | ✓ Met | `test_is_done`, `test_is_done_custom_statuses_case_insensitive` |
| MC-V-DS-003 | `resolutiondate` fallback marks an issue done regardless of its status name | An issue with a non-empty `resolutiondate` field and a non-default status (e.g. `"Released"`) is treated as done; this supports Kanban boards with custom terminal status names | ✓ Met | `test_is_done_resolutiondate_fallback` |
| MC-V-DS-004 | A custom terminal status without `resolutiondate` is not done | An issue with status `"Released"` and no `resolutiondate` returns `False`; `resolutiondate` is required to trigger the fallback | ✓ Met | `test_is_done_no_resolutiondate_custom_status` |
| MC-V-DS-005 | Schema-configured done statuses override built-in defaults | When a `done_statuses` frozenset is passed explicitly, only those statuses (and the `resolutiondate` fallback) determine completeness | ✓ Met | `test_is_done_with_custom_statuses` |
| MC-V-DS-006 | Issues with missing or malformed status fields are not done | `_is_done({})`, `_is_done({"fields": {}})`, and `_is_done({"fields": {"status": {}}})` all return `False` without raising an exception | ✓ Met | `test_is_done_missing_fields` |

### 1b. Excluded Statuses

Issues whose status matches an entry in `excluded_statuses` (schema `status_mapping.excluded_statuses`) are silently dropped from **all** metric calculations before any done-status check.

| ID | Requirement | Acceptance Criterion | Status | Tests |
|----|-------------|----------------------|--------|-------|
| MC-V-ES-001 | User-configured `excluded_statuses` in schema removes issues from all metric calculations | A `Cancelled` issue with story points does not contribute to velocity, AI trend numerator, or AI trend denominator when `excluded_statuses=["Cancelled"]` | ✓ Met | `test_compute_velocity_excluded_statuses`, `test_ai_trend_excluded_statuses` |
| MC-V-ES-002 | Excluded check has priority over `resolutiondate` fallback | A `Cancelled` issue that also has a `resolutiondate` is still excluded (`_is_excluded` returns `True` and the issue is skipped before `_is_done` is evaluated) | ✓ Met | `test_is_excluded_resolutiondate_does_not_override`, `test_compute_velocity_excluded_statuses`, `test_ai_trend_excluded_statuses` |
| MC-V-ES-003 | Excluded status matching is case-insensitive | `_is_excluded` returns `True` for `"cancelled"`, `"CANCELLED"`, and `"Cancelled"` when the excluded set contains `"cancelled"` | ✓ Met | `test_is_excluded` |
| MC-V-ES-004 | Empty or absent `excluded_statuses` is backward-compatible | When `excluded_statuses` is `None`, `frozenset()`, or absent from the schema, no issues are excluded and velocity results are identical to pre-feature behaviour | ✓ Met | `test_is_excluded`, `test_compute_velocity_no_excluded_statuses_backward_compat`, `test_post_schema_accepts_absent_excluded_statuses` |

---

## 2. Story Points Extraction

Controls how `_get_story_points()` converts raw Jira field values into a numeric float.

| ID | Requirement | Acceptance Criterion | Status | Tests |
|----|-------------|----------------------|--------|-------|
| MC-V-SP-001 | A numeric float value is returned as-is | An issue with `customfield_10016 = 8.0` yields `8.0` | ✓ Met | `test_get_story_points_numeric_float` |
| MC-V-SP-002 | An integer value is coerced to float | An issue with `customfield_10016 = 3` (int) yields `3.0` | ✓ Met | `test_get_story_points_integer_stored_as_int` |
| MC-V-SP-003 | A `None` value yields `0.0` | An issue with `customfield_10016 = None` yields `0.0` | ✓ Met | `test_get_story_points_none` |
| MC-V-SP-004 | A non-numeric string value yields `0.0` | An issue with `customfield_10016 = "many"` yields `0.0` without raising an exception | ✓ Met | `test_get_story_points_non_numeric_string` |
| MC-V-SP-005 | A missing story-points field yields `0.0` | An issue whose `fields` dict has no story-points key at all yields `0.0` | ✓ Met | `test_get_story_points_missing_field` |
| MC-V-SP-006 | A nested `{"value": N}` dict is unwrapped | An issue with `customfield_10016 = {"value": 8}` yields `8.0` | ✓ Met | `test_get_story_points_nested_value_dict` |
| MC-V-SP-007 | An explicit `story_points_field` parameter targets a custom field ID | When `story_points_field="customfield_99"` is passed, the value is read from that field rather than the default `customfield_10016` | ✓ Met | `test_get_story_points_with_custom_field`, `test_get_story_points_custom_field` |
| MC-V-SP-008 | A custom field ID with no matching field in the issue yields `0.0` | When `story_points_field="customfield_99"` but the issue only has `customfield_10016`, the result is `0.0` | ✓ Met | `test_get_story_points_custom_field_missing` |

---

## 3. Sprint Attribution and Deduplication

Controls how `deduplicate_sprint_issues()` assigns each ticket to exactly one sprint before velocity is computed.

| ID | Requirement | Acceptance Criterion | Status | Tests |
|----|-------------|----------------------|--------|-------|
| MC-V-SA-001 | A ticket appearing in multiple fetched sprints is placed in the sprint with the highest sprint ID in its sprint custom field | Given sprints 1 and 2 both containing ticket X-1, and X-1's sprint field containing `[1, 2]`, the ticket is attributed to sprint 2 and removed from sprint 1 | ✓ Met | `test_dedup_basic_issue_kept_in_last_sprint`, `test_dedup_three_sprints_kept_in_last` |
| MC-V-SA-002 | The sprint field's max ID is the source of truth, not the sprint(s) where Jira returned the ticket | If Jira returns ticket X-1 only under sprint 5, but its sprint field contains `[5, 6]` and sprint 6 is fetched, the ticket is moved to sprint 6 | ✓ Met | `test_dedup_attributes_to_latest_sprint_field_id_not_jira_membership` |
| MC-V-SA-003 | A ticket whose owner sprint is outside the fetch window is dropped entirely | If a ticket's sprint field max ID is sprint 7 and sprint 7 is not in the fetched list, the ticket is removed from all fetched sprints and contributes 0 to velocity | ✓ Met | `test_dedup_drops_issue_owned_by_active_sprint_outside_fetch`, `test_velocity_excludes_ticket_carried_to_unfetched_active_sprint` |
| MC-V-SA-004 | A ticket whose owner sprint is in the fetch window is placed in that sprint | If sprint 7 is fetched and a ticket's sprint field max is 7, the ticket lands in sprint 7 regardless of which other sprints it was returned under | ✓ Met | `test_dedup_keeps_issue_in_active_sprint_when_fetched` |
| MC-V-SA-005 | Fallback to most-recent membership when the sprint field is absent or unparseable | A ticket with no sprint custom field is attributed to the latest sprint (by `startDate`) in which Jira returned it | ✓ Met | `test_dedup_falls_back_when_sprint_field_missing` |
| MC-V-SA-006 | Kanban week-period string IDs use membership-based fallback (sprint field integers never match string IDs) | Issues on Kanban boards whose sprint field contains integer Jira sprint IDs that do not match any `week-YYYY-Www` period ID are retained in their Jira-returned period, not dropped | ✓ Met | `test_dedup_kanban_string_sprint_ids`, `test_dedup_kanban_keeps_issues_with_sprint_field` |
| MC-V-SA-007 | Issues without a `key` field are not moved by deduplication | A ticket lacking a `key` is not tracked in the deduplication map and remains in its original sprint bucket | ✓ Met | `test_dedup_issue_without_key_not_moved` |
| MC-V-SA-008 | Sprints passed in newest-first order (as returned by `jira_client`) are still attributed correctly | Passing `[sprint_2, sprint_1]` produces the same attribution as `[sprint_1, sprint_2]`; the issue ends up in the higher-ID sprint | ✓ Met | `test_dedup_newest_first_input_still_keeps_issue_in_most_recent` |

---

## 4. Velocity Aggregation

Controls how `compute_velocity()` sums story points across a sprint's attributed, done issues.

| ID | Requirement | Acceptance Criterion | Status | Tests |
|----|-------------|----------------------|--------|-------|
| MC-V-AG-001 | All done issues' story points are summed per sprint | Two done issues with 5 and 3 points yield `velocity = 8.0` and `issue_count = 2` | ✓ Met | `test_compute_velocity_all_done` |
| MC-V-AG-002 | Non-done issues are excluded from the velocity sum | A sprint with one done issue (5 pts) and two in-progress issues (3 + 2 pts) yields `velocity = 5.0` and `issue_count = 1` | ✓ Met | `test_compute_velocity_mixed_statuses` |
| MC-V-AG-003 | A sprint with no issues returns `velocity = 0.0` and `issue_count = 0` | `compute_velocity([sprint], {sprint_id: []})` returns one row with both values zero | ✓ Met | `test_compute_velocity_no_issues` |
| MC-V-AG-004 | A sprint missing entirely from the issues dict returns `velocity = 0.0` | `compute_velocity([sprint], {})` — no key for the sprint — returns one row with `velocity = 0.0` | ✓ Met | `test_compute_velocity_sprint_absent_from_issues_dict` |
| MC-V-AG-005 | Velocity is rounded to 1 decimal place | Two done issues each with 1.05 points yield `velocity = 2.1` (not `2.1000...`) | ✓ Met | `test_compute_velocity_rounding` |
| MC-V-AG-006 | A sprint without an `id` field is skipped and omitted from the output list | A sprint dict with no `"id"` key results in an empty return list, not a crash | ✓ Met | `test_compute_velocity_missing_sprint_id` |
| MC-V-AG-007 | The sprint name is preserved in the output row | The `sprint_name` in the output row matches the `name` field of the input sprint | ✓ Met | `test_compute_velocity_preserves_sprint_name` |
| MC-V-AG-008 | Kanban week periods with `resolutiondate`-based done issues compute correctly | A Kanban period (string ID) with an issue whose status is `"Released"` and `resolutiondate` is set contributes its story points to velocity | ✓ Met | `test_compute_velocity_kanban_periods` |
| MC-V-AG-009 | Schema-configured story points field and done statuses are applied when passed as arguments | `compute_velocity([sprint], issues, story_points_field="cf_sp", done_statuses=frozenset({"shipped"}))` counts only issues with status `"Shipped"` and reads points from `cf_sp` | ✓ Met | `test_compute_velocity_custom_field_and_statuses` |

---

## 5. Estimation Type Mode

Controls how `build_metrics_dict()` post-processes velocity rows based on `ESTIMATION_TYPE`.

| ID | Requirement | Acceptance Criterion | Status | Tests |
|----|-------------|----------------------|--------|-------|
| MC-V-ET-001 | In `StoryPoints` mode, `velocity` is the sum of story points for done issues | `ESTIMATION_TYPE=StoryPoints` with two done issues (5 + 3 pts) yields `velocity = 8.0` | ✓ Met | `test_build_metrics_dict_story_points_velocity_unchanged` |
| MC-V-ET-002 | In `JiraTickets` mode, `velocity` is overwritten with the count of done issues | `ESTIMATION_TYPE=JiraTickets` with two done issues yields `velocity = 2` (count), not `8.0` (points) | ✓ Met | `test_build_metrics_dict_jira_tickets_velocity_uses_issue_count` |
| MC-V-ET-003 | `issue_count` always reflects the count of done issues regardless of estimation type | In both `StoryPoints` and `JiraTickets` modes, `issue_count` equals the number of done issues, not story points | ✓ Met | `test_build_metrics_dict_story_points_velocity_unchanged`, `test_build_metrics_dict_jira_tickets_velocity_uses_issue_count` |

---

## 6. Output Shape

Defines the required keys in each velocity row returned by `build_metrics_dict()`.

| ID | Requirement | Acceptance Criterion | Status | Tests |
|----|-------------|----------------------|--------|-------|
| MC-V-OUT-001 | Each velocity row contains all required keys | Every item in `metrics_dict["velocity"]` has keys: `sprint_id`, `sprint_name`, `start_date`, `end_date`, `velocity`, `issue_count` | ✓ Met | `test_velocity_row_has_required_keys` |
| MC-V-OUT-002 | `start_date` and `end_date` are ISO-8601 strings or `None` | Date fields are never absent; they hold an ISO-8601 string when the sprint has dates, or `None` when dates are missing | ✓ Met | `test_velocity_row_start_end_date_are_iso_or_none` |
| MC-V-OUT-003 | `sprint_id` matches the `id` field of the input sprint | The `sprint_id` in the output row equals the `id` value from the corresponding input sprint dict | ✓ Met | `test_velocity_row_sprint_id_matches_input` |

---

## 7. Metric Value Types and Percentage Display

Defines which metric fields are computed and stored as percentage values (0–100) and which are
absolute values, and how each must be displayed in charts and tables. This is the authoritative
reference for any reporter or template that renders metric data.

### 7.1 Value Type Classification

| ID | Metric | Field(s) | Value Type | Range | Acceptance Criterion | Status | Tests |
|----|--------|----------|------------|-------|----------------------|--------|-------|
| MC-FMT-001 | Velocity | `velocity` | **Absolute** — story points or issue count | ≥ 0.0 | `velocity` holds a raw numeric sum (story points) or count (issues); it is never divided by a total and never multiplied by 100 | ✓ Met | `test_compute_velocity_all_done`, `test_compute_velocity_rounding` |
| MC-FMT-002 | AI Assistance Trend | `ai_sp`, `total_sp` | **Absolute** — story points | ≥ 0.0 | `ai_sp` and `total_sp` are plain story-point sums; neither field carries a `%` suffix or is normalised to 0–100 | ✓ Met | `test_compute_ai_trend_basic`, `test_ai_trend_all_done_ai_assisted` |
| MC-FMT-003 | AI Assistance Trend | `ai_pct` | **Percentage** — share of done SP that is AI-assisted | 0.0 – 100.0 | `ai_pct = (ai_sp / total_sp) × 100`, rounded to 1 dp; equals `0.0` when `total_sp` is 0 (no division-by-zero); equals `100.0` when every done SP is AI-assisted | ✓ Met | `test_ai_trend_basic_percentage`, `test_ai_trend_no_done_issues`, `test_ai_trend_all_done_ai_assisted` |
| MC-FMT-004 | AI Usage Details | `pct` per tool / action label | **Percentage** — share of AI-assisted issues carrying that label | 0.0 – any (can exceed 100%) | `pct(label) = count(label) / ai_assisted_issue_count × 100`; individual values may exceed 100% because a single issue can carry multiple tool or action labels simultaneously | ✓ Met | `test_ai_usage_details_tool_breakdown_pct`, `test_ai_usage_details_action_breakdown_pct` |
| MC-FMT-005 | Cycle Time | `mean_days`, `median_days`, `min_days`, `max_days` | **Absolute** — calendar days | ≥ 0.0 | All cycle time fields are durations expressed in days; none are normalised or expressed as percentages | ✓ Met | `test_cycle_time_fields_are_absolute_days` |
| MC-FMT-006 | DAU (snapshot) | `team_avg` | **Absolute** — average working days per week | 0.0 – 5.0 | `team_avg` is the mean of respondents' days-per-week scores on a 0–5 scale; it is not a percentage | ✓ Met | `test_compute_dau_metrics_team_avg`, `test_compute_dau_metrics_no_data` |
| MC-FMT-007 | DAU (snapshot) | `team_avg_pct` | **Percentage** — team average as a share of the maximum score | 0.0 – 100.0 | `team_avg_pct = (team_avg / 5) × 100`, rounded to 1 dp; equals `None` when there are no responses | ✓ Met | `test_compute_dau_metrics_team_avg_pct`, `test_compute_dau_metrics_no_data` |
| MC-FMT-008 | DAU Trend | `team_avg_pct` per week | **Percentage** | 0.0 – 100.0 | Each weekly row's `team_avg_pct` follows the same formula as the snapshot; used as the primary plotted value in the DAU trend chart | ✓ Met | `test_compute_dau_trend_team_avg_pct` |

---

### 7.2 Chart and Table Display Format

Defines how each metric's values must be rendered in HTML charts and data tables.
Implementation location: `templates/report.html.j2`.

| ID | Metric | Chart / Table | Must show `%` | Acceptance Criterion | Status | Tests |
|----|--------|---------------|---------------|----------------------|--------|-------|
| MC-FMT-101 | Velocity | Bar chart Y axis | **No** | Y-axis ticks are plain numbers (e.g. `8`, `20`); the axis title equals `unit_abbr` (e.g. "pts" or "issues"); no `%` callback on ticks; no `%` suffix in tooltips or data labels | ✓ Met | `test_velocity_chart_y_axis_has_no_percent_suffix`, `test_t01_velocity_alone_no_pct`, `test_t05_ai_usage_plus_velocity`, `test_t06_ai_trend_plus_velocity`, `test_t07_dau_trend_plus_velocity`, `test_t11_ai_usage_plus_velocity_plus_dau_trend`, `test_t12_ai_trend_plus_velocity_plus_dau_trend`, `test_t14_all_sections_correct_pct_labels` |
| MC-FMT-102 | Velocity | Data table | **No** | The "Velocity" column and "Total (selected period)" row display plain numeric values without a `%` suffix | ✓ Met | `test_velocity_table_values_have_no_percent_suffix` |
| MC-FMT-103 | AI Assistance Trend | Line chart Y axis | **Yes** | Y-axis is bounded 0–100; ticks use a callback that appends `%` (e.g. `"50%"`); point labels and tooltips also append `%` | ✓ Met | `test_ai_assistance_sprint_and_pct_present`, `test_t03_ai_trend_alone_pct`, `test_t06_ai_trend_plus_velocity`, `test_t09_ai_trend_plus_dau_trend`, `test_t12_ai_trend_plus_velocity_plus_dau_trend`, `test_t13_ai_usage_plus_ai_trend_plus_dau_trend`, `test_t14_all_sections_correct_pct_labels` |
| MC-FMT-104 | AI Assistance Trend | Data table | **Yes** | The `ai_pct` column is rendered as `{{ row.ai_pct }}%`; raw `ai_sp` / `total_sp` columns are rendered as plain numbers | ✓ Met | `test_ai_assistance_sprint_and_pct_present` |
| MC-FMT-105 | AI Usage Details | Pie charts | **Yes** | Each pie chart segment label includes the `pct` value with a `%` suffix; the count is shown separately | ✓ Met | `test_ai_usage_pie_chart_pct_labels_present`, `test_t02_ai_usage_alone_pie_pct`, `test_t05_ai_usage_plus_velocity`, `test_t08_ai_usage_plus_dau_trend`, `test_t11_ai_usage_plus_velocity_plus_dau_trend`, `test_t13_ai_usage_plus_ai_trend_plus_dau_trend`, `test_t14_all_sections_correct_pct_labels` |
| MC-FMT-106 | Cycle Time | Statistical table | **No** | Mean, median, min, max are displayed as plain numbers with a "days" label; no `%` suffix appears | ✓ Met | `test_cycle_time_fields_are_absolute_days` |
| MC-FMT-107 | DAU (snapshot) | Summary line | **Both** | The summary paragraph renders `team_avg` as `X / 5` (absolute) and `team_avg_pct` as `(Y%)` in parentheses; both values are shown together | ✓ Met | `test_dau_team_avg_shown_in_html` |
| MC-FMT-108 | DAU Trend | Line chart — primary Y axis (left) | **No** | Left Y axis is bounded 0–5 with integer steps; title reads "Avg (days)"; no `%` on this axis | ✓ Met | — |
| MC-FMT-109 | DAU Trend | Line chart — secondary Y axis (right) | **Yes** | Right Y axis is bounded 0–100 with step 20; ticks use a callback that appends `%`; axis title reads "%" | ✓ Met | `test_t04_dau_trend_alone_pct`, `test_t07_dau_trend_plus_velocity`, `test_t08_ai_usage_plus_dau_trend`, `test_t09_ai_trend_plus_dau_trend`, `test_t11_ai_usage_plus_velocity_plus_dau_trend`, `test_t12_ai_trend_plus_velocity_plus_dau_trend`, `test_t13_ai_usage_plus_ai_trend_plus_dau_trend`, `test_t14_all_sections_correct_pct_labels` |

---

## 8. Future Enhancements

| ID | Requirement | Rationale | Status |
|----|-------------|-----------|--------|
| MC-V-FUT-001 | Log a warning when a ticket is dropped because its owner sprint is outside the fetch window | Silent drops are hard to diagnose when velocity unexpectedly decreases; a `logger.debug` or `logger.warning` entry would confirm the attribution decision | Proposed |
| MC-V-FUT-002 | Expose a `running_average` field in each velocity row | The HTML report overlays a running average line using client-side JS; pre-computing it in `compute_velocity()` would make it available to the Markdown reporter too | Proposed |
| MC-V-FUT-003 | Add a `sprint_state` field to each velocity row | Knowing whether a sprint was `closed` or `active` at report time lets reporters flag the current sprint's partial velocity without a separate data source | Proposed |
