# AI Adoption Metrics Report — User Guide

A self-service Knowledge Base for engineering teams, managers, and stakeholders using the **AI Adoption Metrics Report** tool.

---

## Overview

### What It Does

AI Adoption Metrics Report connects to your Jira Cloud instance and automatically generates sprint-level reports that measure team productivity and AI adoption. Each report run produces a self-contained **HTML report** (interactive charts) and a **Markdown report** (plain-text tables and diagnostics) covering:

- Team velocity or throughput per sprint
- What percentage of completed work was AI-assisted
- Which AI tools your team uses (Copilot, ChatGPT, etc.)
- Which AI use cases are most common (code generation, review, etc.)
- Daily Active Usage (DAU) from team surveys

### Who Should Use It

| Role | Use case |
|------|----------|
| Engineering teams | Tag their Jira issues with AI labels; view per-sprint adoption |
| Engineering managers / team leads | Track AI adoption trends and velocity changes over time |
| Product / business stakeholders | Review impact reports; share HTML files without needing the tool |

### Key Concepts

| Concept | Description |
|---------|-------------|
| **Filter** | A named JQL query that scopes which Jira issues are included in a report. Stored in `config/jira_filters.json`. |
| **Schema** | A mapping of Jira custom-field IDs to pipeline-readable names (story points, sprint, team, status). Stored in `config/jira_schema.json`. |
| **AI Labels** | Jira issue labels that mark AI-assisted work. Configured in the Filter Builder tab. |
| **Sprint Count** | How many sprints (or Kanban periods) to look back when generating a report. |

---

## Getting Started

### Prerequisites

- **Windows** machine (the setup script targets Windows)
- **Python 3.10–3.13** — Python 3.12 is installed automatically by `project_setup.bat` if no compatible version is found
- **Jira Cloud** access with an Atlassian account
- **Atlassian API token** — generate one at [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

> **Note:** Never use your Atlassian account password as the API token — create a dedicated token at the link above.

### Step 1 — Installation

1. Open the project folder
2. Double-click **`project_setup.bat`**
3. The script will:
   - Detect a compatible Python (3.10–3.13) or install Python 3.12 (no admin rights required)
   - Create a `.venv` virtual environment
   - Install all dependencies from `requirements.txt`
   - Create `.env` from `.env.example` (if `.env` doesn't exist yet)
   - Export trusted Windows CA certificates for SSL verification
   - Initialize the user data directory (`%LOCALAPPDATA%\AIMetrics\`)

### Step 2 — Configure Jira Credentials

The recommended way is to use the **Jira Connection** tab in the UI (after launching in Step 3). Enter your Jira URL, email, and API token, then click **Save** — credentials are written to `%LOCALAPPDATA%\AIMetrics\.env` and never touch the project folder.

| Variable | Example | Description |
|----------|---------|-------------|
| `JIRA_URL` | `https://your-domain.atlassian.net` | Jira Cloud base URL — no trailing slash |
| `JIRA_EMAIL` | `you@company.com` | Your Atlassian account email |
| `JIRA_API_TOKEN` | `ATATT3x...` | API token from id.atlassian.com |

> **Alternative:** You can also edit the project `.env` file directly with the same variables above — useful if you need to pre-configure before the first launch.

> **Tip:** If your Confluence instance uses a different Atlassian account, also set `CONFLUENCE_EMAIL` and `CONFLUENCE_API_TOKEN`. If both share the same account, leave those blank.

### Step 3 — Launch the App

Double-click **`start_app.bat`**. The local server starts at **`http://localhost:8080`** and opens in your default browser.

> **Port conflict?** If port 8080 is in use, set `PORT=9000` (or any free port) in `config/defaults.env` or in `%LOCALAPPDATA%\AIMetrics\.env`, and restart.

---

## Using the App

The UI has **five** tabs. Follow this order the first time:

### Step 1 — Jira Connection Tab

Configure and verify your Jira connection.

| Section | What to do |
|---------|-----------|
| **Credentials** | Enter Jira URL, email, and API token; use the eye icon to toggle token visibility; click **Save**, then **Test Connection** |
| **Sprint Settings** | Optionally set a default Board ID and Sprint Count |
| **SSL Certificate** | If your Jira uses a custom CA, click **Fetch Certificate** to cache the TLS cert |

The **Test Connection** button checks `JIRA_URL/rest/api/3/myself` with a 12-second timeout and shows a success or error badge next to the button.

The **certificate status badge** shows one of: `Valid`, `Expired`, or `No certificate`. Use **Remove Certificate** to clear a cached cert.

### Step 2 — Schema Setup Tab

Schemas tell the pipeline which Jira custom-field IDs map to story points, sprint, team, and status. The default schema (`Default_Jira_Cloud`) ships with the standard Jira Cloud field IDs and works for most instances out of the box — you only need a custom schema when your instance uses different IDs.

#### Schema JSON Structure

A schema is a JSON object with the following shape:

```json
{
  "schema_name": "My Company Schema",
  "description": "Optional — human-readable label",
  "fields": {
    "story_points": { "id": "customfield_10016", "type": "number" },
    "sprint":       { "id": "customfield_10020", "type": "array"  },
    "team":         { "id": "customfield_10001", "type": "string",
                      "jql_name": "Team[Team]" },
    "labels":       { "id": "labels",            "type": "array"  },
    "status":       { "id": "status",            "type": "string" }
  },
  "status_mapping": {
    "done_statuses":        ["Done", "Closed", "Resolved"],
    "in_progress_statuses": ["In Progress", "In Review"],
    "excluded_statuses":    ["Cancelled"]
  }
}
```

| Key | Required | Purpose |
|-----|----------|---------|
| `schema_name` | **Yes** | Unique name shown in the Filter Builder dropdown |
| `fields.story_points` | Recommended | Velocity and AI % calculations; falls back to `customfield_10016` if absent |
| `fields.sprint` | Recommended | Sprint grouping for Scrum projects; falls back to `customfield_10020` if absent |
| `fields.team` | Optional | Team-scoped filtering; add `"jql_name"` when the JQL name differs from the field ID |
| `status_mapping.done_statuses` | **Yes** | Issues in these statuses count as completed — must be non-empty |
| `status_mapping.in_progress_statuses` | **Yes** | Used for work-in-progress indicators — must be non-empty |
| `status_mapping.excluded_statuses` | No | Issues in these statuses are dropped from all metric denominators |

Status names are matched case-insensitively. Standard fields (`labels`, `status`, `priority`) use the same IDs across all Jira Cloud instances and do not need to be changed.

#### Finding Your Custom Field IDs

Call the Jira REST API on any issue from your project to see which field IDs your instance uses:

```
GET https://<your-domain>.atlassian.net/rest/api/3/issue/<issue-id-or-key>
Authorization: Basic <base64(your-email:your-api-token)>
```

**Example:**
```
https://testprojectforanatolii.atlassian.net/rest/api/3/issue/10051
```

In the response, look inside the `fields` object:

```json
{
  "fields": {
    "customfield_10016": 5,
    "customfield_10020": [
      { "id": 23, "name": "Sprint 4", "state": "active" }
    ],
    "customfield_10001": "Platform",
    "status": { "name": "In Progress" },
    "labels": ["ai_assisted"]
  }
}
```

| What you see | Maps to |
|-------------|---------|
| `"customfield_10016": 5` | `fields.story_points.id` |
| `"customfield_10020": [...]` | `fields.sprint.id` |
| `"customfield_10001": "..."` | `fields.team.id` |
| `"status": { "name": "In Progress" }` | add `"In Progress"` to `status_mapping.in_progress_statuses` |
| `"labels": [...]` | standard field — always `"labels"`, no change needed |

**Tips:**
- Any key prefixed `customfield_` is instance-specific — copy it verbatim into your schema.
- Check several issues across different workflow states to build a complete `status_mapping` list.
- Wrong `story_points` ID → velocity shows as zero. This is the most impactful field to get right.
- `team` field only matters if you scope filters to a specific team; skip it otherwise.

#### Managing Schemas

| Action | Steps |
|--------|-------|
| Create | Click **New Schema** → edit the JSON in the editor → click **Save** |
| Edit | Select from dropdown → edit JSON → click **Save** |
| Delete | Select schema → click **Delete Schema** (not available for `Default_Jira_Cloud`) |

Validation errors appear in the log below the editor immediately after Save.

> **Note:** The Schema Setup tab is an editor only. The schema used for a specific report run is set per-filter in the **Filter Builder** tab.

### Step 3 — Filter Builder Tab

Create a named filter that scopes your report to a specific team or project.

**Save Jira Filter fields:**

| Field | Description |
|-------|-------------|
| **Filter Name** | A unique name (e.g., `My Team Q2 2026`) |
| **Report Name** | Display name used in the report header and output filename (defaults to Filter Name if left blank) |
| **Active Schema** | Select the schema for this filter's Jira instance |

**Data Source** (collapsible):

| Field | Description |
|-------|-------------|
| **Jira Filter ID** | Enter a saved Jira Filter ID to use its JQL directly instead of the builder below |
| **Filter Page Size** | Number of issues fetched per Jira API page (1–100; default 100) |

**JQL Builder** (nested collapsible):

| Field | Description |
|-------|-------------|
| **Project Key(s)** | Jira project key(s) to include (e.g., `MYPROJ`) |
| **Team ID** | Optional — scope to a specific team |
| **Issue Types** | E.g., `Story,Bug,Task` |
| **Include Active Sprint** | Toggle — include the currently active (in-progress) sprint in metrics |

Use **Copy JQL** to copy the generated query to the clipboard for verification in Jira.

**Report Scope** (collapsible):

| Field | Description |
|-------|-------------|
| **Project Type** | Scrum (sprint-based) or Kanban (continuous flow) |
| **Estimation Type** | Story Points or Jira Tickets (issue count) |
| **Board ID** | Required — find it in your Jira agile board URL |
| **Sprint Count** | How many sprints to look back (e.g., `8`) |
| **Sprint Name Filter** | Optional — case-insensitive substring to match sprint names (e.g., `2026 Q2`) |

**DAU Survey Data** (collapsible):

| Field | Description |
|-------|-------------|
| **DAU Path** | Path to the folder containing DAU survey input files for this filter |

Click **Save Filter** — the filter appears in the Generate Report dropdown. Previously saved filters are listed in the searchable **Last Created Filters** panel (last 20 entries).

**AI Adoption Labels** (collapsible, below Data Source): expand to set the labels (`AI_ASSISTED_LABEL`, `AI_EXCLUDE_LABELS`, `AI_TOOL_LABELS`, `AI_ACTION_LABELS`) used by AI metrics. Click **Save AI Labels** to persist them to `.env`.

### Step 4 — DAU Data Tab

Manage team roster and Daily Active Usage survey records that feed the DAU sections of the report.

| Section | What to do |
|---------|-----------|
| **Team / Filter selector** | Choose which filter's DAU data to view and edit |
| **Import from Excel** | Upload a DAU survey Excel file to bulk-import records; the importer maps columns to the expected schema automatically |
| **Team Roster** | Add or remove team members and assign their role (e.g., Developer, QA, PM); roles are used for the by-role DAU breakdown in reports |
| **Records table** | View, add, edit, or delete individual DAU survey records; supports pagination (50 / 100 / 200 / all) and bulk delete |

#### Collecting DAU Data via MS Teams Polls

The recommended way to gather DAU data is to run a weekly poll in your MS Teams team chat asking how often team members used AI tools during the week. After the poll closes, export the responses to Excel and import the file here.

**How to collect and export:**

1. Open your MS Teams channel or group chat
2. Create a **Poll** (via the Forms app or the "..." menu → Poll)
3. Ask the question: *"How often did you use AI tools last week?"*
4. Include frequency options such as:
   - `Every Day - all working days`
   - `Most Days: 3-4 days last week`
   - `Some Days: 1-2 days last week`
   - `Not at all`
5. After the poll closes, open the poll results and click **Export to Excel** — Teams downloads the file automatically

#### Expected Excel Format

The exported file must have one header row followed by one row per respondent. The importer reads these columns:

| Column | Example value | Notes |
|--------|--------------|-------|
| `ID` | `1` | Auto-generated row number — not used by the importer |
| `Start time` | `2026-05-22 15:23:20` | Timestamp of the response submission |
| `Completion time` | `2026-05-22 15:23:20` | Usually the same as Start time for polls |
| `Email` | `oleksii_zhylin@company.com` | Used to match respondents to the Team Roster |
| `Name` | `Oleksii Zhylin` | Display name of the respondent |
| Poll question column | `Every Day - all working days` | The full poll question text becomes the column header; the cell value is the selected frequency option |

**Example rows:**

| ID | Start time | Completion time | Email | Name | How often did you use AI tools last week? |
|----|-----------|----------------|-------|------|------------------------------------------|
| 1 | 2026-05-22 15:23:20 | 2026-05-22 15:23:20 | oleksii_zhylin@company.com | Oleksii Zhylin | Every Day - all working days |
| 2 | 2026-05-22 15:24:01 | 2026-05-22 15:24:01 | dmytro_leliavskyi@company.com | Dmytro Leliavskyi | Every Day - all working days |
| 3 | 2026-05-22 15:24:39 | 2026-05-22 15:24:39 | oleksandr_zadvornyi@company.com | Oleksandr Zadvornyi | Most Days: 3-4 days last week |
| 4 | 2026-05-22 15:26:15 | 2026-05-22 15:26:15 | yuliia_lysak@company.com | Yuliia Lysak | Most Days: 3-4 days last week |

> **Tip:** The poll question column header does not need to match exactly — the importer identifies the frequency column by its position and by recognising the known frequency values. Only the `Email` column is used to join records to the Team Roster.

#### Importing the Excel File

1. Go to the **DAU Data** tab and select the target filter from the dropdown
2. Expand **Import from Excel**
3. Click **Choose file** and select the exported `.xlsx` file
4. Click **Import** — the importer parses each row and adds it to the Records table
5. Review the imported records; use the Records table to correct or delete any rows as needed

> **Tip:** DAU report sections only populate when records exist for the selected filter. If the DAU sections of your report are empty, check that records are loaded here first.

### Step 5 — Generate Report Tab

This is your main working tab.

1. **Select a filter** from the **Saved Filter** dropdown
2. Optionally set a **Report Name** override (defaults to the filter's Report Name)
3. Expand **Report Options** to toggle which metric sections to include:
   - **Velocity** — Velocity Trend (Scrum) or Throughput Trend (Kanban)
   - **AI Trend** — AI Assistance Trend
   - **AI Usage** — AI Usage Details
   - **DAU** — DAU Survey
   - **DAU Trend** — DAU Trend
4. Click **Generate Report**

> **Note:** Project Type and Estimation Type are set per-filter in the **Filter Builder** tab, not here.

Live output streams in the output panel. When complete, the report appears in the **Last Generated Reports** list — click the link to open the HTML report.

---

## Report Sections Explained

Each section can be toggled independently in **Report Options**.

| Section | Toggle | Output | What It Shows |
|---------|--------|--------|---------------|
| **Velocity Trend** (Scrum) / **Throughput Trend** (Kanban) | Velocity | HTML + MD | Story points (or issue count) of done issues per sprint, with a running average line |
| **AI Assistance Trend** | AI Trend | HTML + MD | Per-sprint percentage of done story points marked AI-assisted |
| **AI Usage Details** | AI Usage | HTML + MD | Breakdown of AI tool labels and AI use-case labels across AI-assisted issues |
| **DAU Survey** | DAU | HTML + MD | Team Daily Active Usage average from self-reported survey; by-role breakdown and usage-frequency bar chart |
| **DAU Trend** | DAU Trend | HTML + MD | Week-over-week DAU average and adoption percentage |
| **Sprint Issues** | *(always on)* | MD only | Table of individual issues per sprint with status and labels |
| **Diagnostics** | *(always on)* | MD only | Run metadata, active Jira config, and AI label config |

Reports are saved to `%LOCALAPPDATA%\AIMetrics\reports\<report-slug>\`:

| File | Description |
|------|-------------|
| `<slug>_<timestamp>.html` | Self-contained HTML with interactive Chart.js charts; opens in any browser |
| `<slug>_<timestamp>.md` | Plain-text summary with ASCII bar charts, tables, sprint issues, and diagnostics |

> **Example:** a filter named "My Team" produces `my_team_2026-05-25T14-32-10.html` and `my_team_2026-05-25T14-32-10.md`.

---

## Jira Labeling Guide

For AI metrics to work, team members must label their Jira issues **before closing them**.

### Required Labels

| Label type | Env var | Default value | Purpose |
|------------|---------|---------------|---------|
| AI Assisted | `AI_ASSISTED_LABEL` | `ai_assisted` | Marks an issue as AI-assisted — required for any AI metric |

### Optional Labels

| Label type | Env var | Default values | Purpose |
|------------|---------|----------------|---------|
| AI Tool | `AI_TOOL_LABELS` | `gemini`, `github_copilot`, `rovo` | Which AI tool was used |
| AI Action / Use Case | `AI_ACTION_LABELS` | `ai_automation`, `ai_dev`, `ai_test`, `ai_test_cases` | How AI was used |
| Exclude | `AI_EXCLUDE_LABELS` | `ai_not_applicable` | Issues excluded from the AI % denominator (non-delivery work) |

> **Tip:** Default label values come from the Default Jira Filter. You can override all of them in the **AI Adoption Labels** section of the Filter Builder tab — changes are saved to `.env` automatically.

### How to Apply Labels in Jira

1. Open the Jira issue
2. Find the **Labels** field in the issue detail panel
3. Add the appropriate labels before moving the issue to Done

---

## CLI Usage

The tool can also be driven from the terminal without the UI:

```
python main.py                 # generate a report using current .env config
python main.py --clean         # delete all saved reports and exit
python main.py --clean-logs    # delete all saved logs and exit
```

---

## Advanced Configuration

The file `config/defaults.env` contains all system defaults. You can override any of these values in your `.env` file.

| Setting | Default | Description |
|---------|---------|-------------|
| `PORT` | `8080` | Port the local server listens on; can also be set in `%LOCALAPPDATA%\AIMetrics\.env` |
| `LOG_LEVEL` | `INFO` | Log verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `METRIC_VELOCITY` | `true` | Pre-enable the Velocity metric section |
| `METRIC_AI_ASSISTANCE_TREND` | `false` | Pre-enable the AI Assistance Trend section |
| `METRIC_AI_USAGE_DETAILS` | `false` | Pre-enable the AI Usage Details section |
| `METRIC_DAU` | `false` | Pre-enable the DAU Survey section |
| `METRIC_DAU_TREND` | `false` | Pre-enable the DAU Trend section |
| `JIRA_SPRINT_COUNT` | `10` | Default number of sprints to look back |
| `JIRA_FILTER_PAGE_SIZE` | `100` | Default Jira API page size (1–100) |

> **Note:** Settings changed in `defaults.env` apply to all filters. Settings saved via the UI (Filter Builder, Jira Connection tab) override `defaults.env` for the relevant filter.

---

## Troubleshooting

### Can't connect to Jira

| Symptom | Fix |
|---------|-----|
| "Connection failed" on Test Connection | Verify `JIRA_URL` has no trailing slash; confirm email and API token are correct |
| HTTP 401 Unauthorized | API token may be expired — generate a new one at id.atlassian.com |
| HTTP 403 Forbidden | Your account may lack API access; contact your Jira admin |

### Port 8080 in use

Set `PORT=9000` (or any available port) in either location and restart `start_app.bat`:

- `config/defaults.env` — applies to all users of this project folder
- `%LOCALAPPDATA%\AIMetrics\.env` — applies to your user only; takes precedence over `config/defaults.env`

### SSL certificate errors

If your company uses a custom Certificate Authority:

1. Go to the **Jira Connection** tab
2. Click **Fetch Certificate** — this caches the TLS cert bundle at `%LOCALAPPDATA%\AIMetrics\certs\jira_ca_bundle.pem`
3. Retry the connection

Alternatively, run from the terminal: `python tools/fetch_ssl_cert.py`

### Report sections missing or empty

| Symptom | Fix |
|---------|-----|
| Velocity section missing | Ensure at least one metric section is checked in Report Options |
| AI metrics show 0% | Confirm issues have the `ai_assisted` label (or your configured label) in Jira |
| DAU section empty | Check the **DAU Data** tab — records must exist for the selected filter before the DAU sections will populate |
| Charts render blank | Ensure you're opening the HTML file in a modern browser (Chrome, Edge, Firefox) |

---

## FAQ

**Q: What's the difference between Scrum and Kanban project types?**
Scrum uses sprint boundaries to group issues into periods. Kanban uses fixed time windows (rolling periods). The report section is labeled "Velocity Trend" for Scrum and "Throughput Trend" for Kanban.

**Q: Story Points vs Jira Tickets — which should I use?**
Use **Story Points** if your team consistently estimates issues. Use **Jira Tickets** (issue count) if story point coverage is inconsistent or your team doesn't estimate.

**Q: Can I have multiple schemas for different Jira instances?**
Yes. Create one schema per instance in the **Schema Setup** tab, then select the appropriate schema when building each filter in the **Filter Builder** tab.

**Q: Where are reports saved?**
All reports are saved under `%LOCALAPPDATA%\AIMetrics\reports\<report-slug>\`. The `Last Generated Reports` list in the UI links directly to each HTML report.

**Q: Can I share the HTML report with someone who doesn't have the tool?**
Yes. The HTML report file is fully self-contained — all CSS, JavaScript, and data are inlined. Send the file as an attachment; it opens in any modern browser.

**Q: How do I update the Jira credentials without editing `.env` manually?**
Use the **Jira Connection** tab — enter the values and click **Save**. Changes are written to `.env` automatically.

**Q: The default filter can't be deleted — is that intentional?**
Yes. `Default_Jira_Filter` is a read-only reference filter that ships with the tool. Create a new named filter for your team's use.

**Q: The Markdown report has sections I don't see in the HTML report — is that expected?**
Yes. The Markdown report always includes two additional sections not in the HTML: **Sprint Issues** (a table of individual issues per sprint) and **Diagnostics** (run metadata, Jira config, and AI label config). These are intended for debugging and audit trails.
