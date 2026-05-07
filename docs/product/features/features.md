# Features — AI Adoption Metrics Report

User-visible features of the browser UI and generated reports. Update this file whenever a
tab, control, or report section is added, changed, or removed.

---

## Browser UI

The UI is a single-page application served by `app/server/` at `http://localhost:8080`.
It is the primary interface for configuring credentials, managing filters, and generating reports.

### Tabs

| Tab | ID | Default |
|-----|----|---------|
| Generate Report | `panel-generate` | yes (opens on load) |
| Filter Builder | `panel-filter` | — |
| Jira Connection | `panel-connection` | — |
| Jira Field Schema | `panel-schema` | — |

---

### Generate Report tab

The main workflow tab. Triggers report generation and displays live output.

#### Controls

| Control | Description |
|---------|-------------|
| **Saved Filter** dropdown | Selects the JQL filter used to scope sprint issues. Populated from `config/jira_filters.json`. Required — the Generate button stays disabled until a filter is selected. |
| **Report Name** field | Optional free-text name for the generated report. Auto-fills from the selected filter's `report_name` when a filter is chosen. When changed and the report is generated, the new value is saved back to the filter in `config/jira_filters.json`, used as the report `<h1>` / `# ` heading, and as the output filename stem (slugified). |
| **Generate Report** button | Runs `python main.py` on the server and streams stdout/stderr as Server-Sent Events into the output panel. |
| **Report Options** (collapsible) | Expands to reveal per-run configuration. |

#### Report Options panel

| Option | Values | Default | Persisted |
|--------|--------|---------|-----------|
| **Metric Sections** checkboxes | Velocity Trend, AI Assistance Trend, AI Usage Details, DAU Survey, DAU Trend | all enabled | `localStorage` |

At least one metric section must be enabled; the Generate button is disabled when all are unchecked.

> **Project Type** and **Estimation Type** are configured per-filter in the Filter Builder tab (under **Report Scope**), not here.

#### Output panel

Live SSE output from the generation subprocess. Displays each stdout/stderr line as it is
produced. Shows a success or error banner on completion.

#### Last Generated Reports list

Lists all previously generated reports under `generated/reports/`, sorted newest first.
Each entry is a clickable link to the corresponding `report.html`.

---

### Filter Builder tab

Create and manage named JQL filters that scope which Jira issues are included in a report.
Filters are stored in `config/jira_filters.json` and appear in the Generate Report dropdown.
Each filter is the source of truth for which Jira field schema (`params.schema_name`) the
report pipeline uses when that filter is run.

| Feature | Description |
|---------|-------------|
| **Active Schema** dropdown | Populated from `/api/schemas`. Chosen value is saved on the filter as `params.schema_name` and is what the pipeline reads when generating a report. Independent of the Schema Setup tab. |
| **Filter Name** dropdown | Lists `— New filter —` plus every saved filter (the default is tagged `(default)`). Picking a filter loads its params into the form for in-place editing; picking `— New filter —` clears the form and reveals a text input pre-populated with `Default_Jira_Filter_<YYYY-MM-DD>`. |
| **Report Name** field | Optional text input for the report title/filename. Auto-fills from the filter name when a filter is selected or the filter name is typed. Saved alongside the filter as `report_name` in `config/jira_filters.json`. |
| Filter form | Project Key, optional Team ID, Issue Types, Closed-sprints-only, Project Type, Estimation Type, Board ID, Sprint Count, Sprint Name Filter (optional substring match on sprint names), optional Jira Filter ID & page size, plus AI Adoption Labels (see below) |
| Save button | Upserts the filter — including AI Adoption Labels — by name via `POST /api/filters`; disabled while `Default_Jira_Filter` is selected (the default is read-only) |
| Filter list | All saved filters, default first; non-default entries show a Remove button |
| Default filter protection | The default filter cannot be deleted or overwritten via the UI |

#### JQL Builder section (collapsible, inside Data Source)

Collapsible `<details>` nested inside **Data Source**. Visible hint in the form reads *"or expand the JQL Builder below to build a query from project settings"*. Generates a JQL string from the current filter params (project key, issue types, team label, sprint count, etc.). Output appears in the filter log panel below the form.

| Feature | Description |
|---------|-------------|
| Builds JQL from project settings | Combines project key, issue types, team filter, date range, and other params into a valid JQL string |
| Copy JQL button | Copies the last built JQL to the clipboard |
| Clear button | Clears the filter log output panel |

#### Filter log output panel

Displays the result of Save and JQL Builder actions. Located below the filter form. Includes a **Copy JQL** button and a **Clear** button in its header.

---

#### AI Adoption Labels section (collapsible, below Data Source)

Collapsible `<details>` section directly below **Data Source**. Inline configuration for the
Jira labels used by AI metrics. Values are stored per filter in
`config/jira_filters.json` (under `params.AI_*`) and persisted as part of the main
**Save Filter** action — there is no separate save button. When generating a report
from a filter, those values override `defaults.env` for the run.

| Field | Param key | Description |
|-------|-----------|-------------|
| AI Assisted Label | `AI_ASSISTED_LABEL` | Label that marks an issue as AI-assisted (default in `Default_Jira_Filter`: `ai_assisted`) |
| Exclude Labels | `AI_EXCLUDE_LABELS` | Comma-separated labels excluded from the AI % denominator |
| Tool Labels | `AI_TOOL_LABELS` | Labels identifying AI tools (e.g. `AI_Tool_Copilot,AI_Tool_ChatGPT`) |
| Action Labels | `AI_ACTION_LABELS` | Labels identifying AI use-cases (e.g. `AI_Case_CodeGen,AI_Case_Review`) |

#### DAU Survey Data section (collapsible)

Collapsible `<details>` section for configuring the per-filter DAU survey response folder.
Each filter keeps its own `data/dau/<slug>/` tree so survey responses are not mixed between teams or projects.
The folder is auto-created on save.

| Field | Param key | Description |
|-------|-----------|-------------|
| DAU Path | `DAU_PATH` | Path relative to the project root where survey responses are stored. Responses live under `<DAU Path>/original/`; the normalised set is regenerated under `<DAU Path>/normalized/` on every report run. Default: `data/dau/<filter-slug>`. |

---

### Jira Connection tab

Configures and verifies the Jira Cloud connection. Settings are saved to `.env` via
`POST /api/config`.

| Section | Controls |
|---------|----------|
| **Credentials** | Jira URL, Jira Email, API Token (masked); Save and Test Connection buttons |
| **Sprint Settings** | Board ID (optional), Sprint Count; saved to `config/defaults.env` |
| **SSL Certificate** | Certificate status badge (Valid / Expired / No certificate); Fetch Certificate and Remove Certificate buttons |

The **Test Connection** button proxies a credential check to `JIRA_URL/rest/api/3/myself`
with a 12-second timeout and reports success or HTTP error status.

---

### Schema Setup tab

Manages the Jira field schema used to locate story-points, sprint, team, and status fields
on each Jira instance. Schemas are stored in `config/jira_schema.json`; the tab sits between
**Jira Connection** and **Filter Builder**.

| Feature | Description |
|---------|-------------|
| Schema dropdown | Lists every schema from `config/jira_schema.json`; `Default_Jira_Cloud` is always present and selected by default |
| JSON editor | Full schema body is shown as pretty-printed JSON in a textarea; all fields (`schema_name`, `description`, `fields`, `status_mapping`, ...) are editable in one place |
| New Schema | Loads a blank template into the editor; user sets `schema_name` directly in the JSON body before saving |
| Save | Upserts the schema by `schema_name` via `POST /api/schemas`; client-side JSON validation blocks malformed bodies before the request is sent |
| Delete | Removes any non-default schema entry; disabled while `Default_Jira_Cloud` is selected |
| Active schema selection | The Schema Setup tab is an editor and does not select the schema used for metrics. The active schema for a report run is determined by the selected filter's `params.schema_name` in `config/jira_filters.json`; for CLI-only runs, `JIRA_SCHEMA_NAME` in `.env` / `config/defaults.env` is used as a fallback. |

---

---

### DAU Survey page (`ui/dau_survey.html`)

A self-contained survey form served statically by the dev server (and usable as a standalone file). Team members open it to submit their weekly AI usage frequency. Submissions are stored as `dau_*.json` files in the active filter's `<DAU_PATH>/original/` directory and processed by `app/core/dau_normalizer.py` before each report run.

| Field | Description |
|-------|-------------|
| Username | Alphanumeric identifier (min 2 chars); required |
| Role | Dropdown (Developer, QA, BA, Lead, Other) |
| Usage frequency | Four options: Every day / Most days / Rarely / Not used |
| Submit | Writes a `dau_<username>_<timestamp>.json` file via `POST /api/dau` |

---

### First-run banner

A dismissible `role="alert"` banner (`#first-run-banner`) shown on first page load when the server detects that `.env` has not yet been configured (credentials empty). Prompts the user to open the Jira Connection tab and save their credentials. Hidden automatically once credentials are saved.

---

### File-mode note

When `ui/index.html` (or `ui/dau_survey.html`) is opened directly as a local file (`file://` URL) without the dev server running, a note (`#cert-file-mode-note`) appears on the Jira Connection tab explaining that certificate fetching and credential saving require the local server to be running.

---

## Generated Reports

Each `python main.py` run writes to `generated/reports/<YYYY-MM-DDTHH-MM-SS>/`:

| File | Format | Description |
|------|--------|-------------|
| `report.html` | HTML | Self-contained, fully inline (CSS + Chart.js + data). Opens in any browser without a server. |
| `report.md` | Markdown | Plain-text summary with ASCII bar charts and tables. |

### Report sections

Each section can be independently toggled via the **Metric Sections** checkboxes in the UI
(or via `METRIC_*` env vars for CLI runs).

| Section | Toggle | HTML | Markdown | Description |
|---------|--------|------|----------|-------------|
| **Velocity Trend** (or **Throughput Trend** for Kanban) | `METRIC_VELOCITY` | bar chart + running-average line | ASCII bar chart + table | Story points (or issue count) of done issues per sprint |
| **Cycle Time** | _(always shown — no toggle)_ | stats card (mean, median, min, max) | summary table | Days from "In Progress" to "Done" per issue. Requires `issues_with_changelog` data; shows "No data" when the pipeline runs without changelog fetching (current default). |
| **AI Assistance Trend** | `METRIC_AI_TREND` | line chart + per-sprint table | table | Per-sprint % of done story points carrying the AI-assisted label |
| **AI Usage Details** | `METRIC_AI_USAGE` | two donut/bar charts (tools + use-cases) | tables | Breakdown of AI tool labels and AI use-case labels across AI-assisted issues |
| **DAU Survey** | `METRIC_DAU` | team-average card + by-role table + usage-frequency bar chart | summary + by-role table | Team Daily Active Usage average from self-reported survey data |
| **DAU Trend** | `METRIC_DAU_TREND` | combo bar+line chart (avg days + adoption %) | ASCII bar chart + table | Week-over-week DAU average and adoption percentage |

### Label adaptation

Report column headers and chart labels adapt to the selected **Project Type** and
**Estimation Type**:

| Project Type | Velocity section title | Period column |
|---|---|---|
| Scrum | Velocity trend | Sprint |
| Kanban | Throughput trend | Period |

| Estimation Type | Velocity unit label |
|---|---|
| Story Points | points |
| Jira Tickets | issues (count of done issues) |
