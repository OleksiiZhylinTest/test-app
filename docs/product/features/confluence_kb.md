# AI Adoption Metrics Report — User Guide

A self-service Knowledge Base for engineering teams, managers, and stakeholders using the **AI Adoption Metrics Report** tool.

---

## Overview

### What It Does

AI Adoption Metrics Report connects to your Jira Cloud instance and automatically generates sprint-level reports that measure team productivity and AI adoption. Each report run produces a self-contained **HTML report** (interactive charts) and a **Markdown report** (plain-text tables) covering:

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
| **AI Labels** | Jira issue labels that mark AI-assisted work. Configured in the Generate Report tab. |
| **Sprint Count** | How many sprints (or Kanban periods) to look back when generating a report. |

---

## Getting Started

### Prerequisites

- **Windows** machine (the setup script targets Windows)
- **Python 3.12** — installed automatically by `project_setup.bat` if not present
- **Jira Cloud** access with an Atlassian account
- **Atlassian API token** — generate one at [https://id.atlassian.com/manage-profile/security/api-tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

> **Note:** Never use your Atlassian account password as the API token — create a dedicated token at the link above.

### Step 1 — Installation

1. Open the project folder
2. Double-click **`project_setup.bat`**
3. The script will:
   - Detect or install Python 3.12 (no admin rights required)
   - Create a `.venv` virtual environment
   - Install all dependencies from `requirements.txt`
   - Create `.env` from `.env.example` (if `.env` doesn't exist yet)

### Step 2 — Configure Jira Credentials

Open the `.env` file created in your project root and fill in the three required fields:

| Variable | Example | Description |
|----------|---------|-------------|
| `JIRA_URL` | `https://your-domain.atlassian.net` | Jira Cloud base URL — no trailing slash |
| `JIRA_EMAIL` | `you@company.com` | Your Atlassian account email |
| `JIRA_API_TOKEN` | `ATATT3x...` | API token from id.atlassian.com |

> **Tip:** If your Confluence instance uses a different Atlassian account, also set `CONFLUENCE_EMAIL` and `CONFLUENCE_API_TOKEN`. If both share the same account, leave those blank.

You can also set these values through the **Jira Connection** tab in the UI (see below).

### Step 3 — Launch the App

Double-click **`start_app.bat`**. The local server starts at **`http://localhost:8080`** and opens in your default browser.

> **Port conflict?** If port 8080 is in use, edit `config/defaults.env`, set `PORT=9000` (or any free port), and restart.

---

## Using the App

The UI has four tabs. Follow this order the first time:

### Step 1 — Jira Connection Tab

Configure and verify your Jira connection.

| Section | What to do |
|---------|-----------|
| **Credentials** | Enter Jira URL, email, and API token; click **Save**, then **Test Connection** |
| **Sprint Settings** | Optionally set a default Board ID and Sprint Count |
| **SSL Certificate** | If your Jira uses a custom CA, click **Fetch Certificate** to cache the TLS cert |

The **Test Connection** button checks `JIRA_URL/rest/api/3/myself` with a 12-second timeout and shows a success or error badge.

The **certificate status badge** shows one of: `Valid`, `Expired`, or `No certificate`. Use **Remove Certificate** to clear a cached cert.

### Step 2 — Schema Setup Tab

Schemas tell the pipeline which Jira custom-field IDs map to story points, sprint, team, and status. The default schema (`Default_Jira_Cloud`) works for most standard Jira Cloud instances.

| When to create a custom schema | How |
|-------------------------------|-----|
| Your Jira uses non-standard custom field IDs for story points or sprint | Click **New Schema**, edit the JSON to match your field IDs, and click **Save** |
| You have multiple Jira instances with different field setups | Create one schema per instance |

> **Note:** The Schema Setup tab is an editor only. The schema used for a specific report run is set per-filter in the **Filter Builder** tab.

### Step 3 — Filter Builder Tab

Create a named filter that scopes your report to a specific team or project.

| Field | Description |
|-------|-------------|
| **Filter Name** | A unique name (e.g., `My Team Q2 2026`) |
| **Active Schema** | Select the schema for this filter's Jira instance |
| **Project Key(s)** | Jira project key(s) to include (e.g., `MYPROJ`) |
| **Team ID** | Optional — scope to a specific team |
| **Issue Types** | E.g., `Story,Bug,Task` |
| **Project Type** | Scrum (sprint-based) or Kanban (continuous flow) |
| **Estimation Type** | Story Points or Jira Tickets (issue count) |
| **Board ID** | Required — find it in your Jira agile board URL |
| **Sprint Count** | How many sprints to look back (e.g., `8`) |

Click **Save Filter** — the filter appears in the Generate Report dropdown.

> **Tip:** You can also enter a Jira Filter ID directly instead of building a JQL query.

### Step 4 — Generate Report Tab

This is your main working tab.

1. **Select a filter** from the **Saved Filter** dropdown
2. Optionally set a **Report Name** (defaults to the filter name)
3. Expand **Report Options** to adjust:
   - **Project Type**: Scrum or Kanban
   - **Estimation Type**: Story Points or Jira Tickets
   - **Metric Sections**: Toggle which charts/tables to include
4. Review the **AI Adoption Labels** card — ensure the labels match what your team uses in Jira
5. Click **Generate Report**

Live output streams in the output panel. When complete, the report appears in the **Last Generated Reports** list — click the link to open the HTML report.

---

## Report Sections Explained

Each section can be toggled independently in **Report Options**.

| Section | Toggle | What It Shows |
|---------|--------|---------------|
| **Velocity Trend** (Scrum) / **Throughput Trend** (Kanban) | Velocity | Story points (or issue count) of done issues per sprint, with a running average line |
| **AI Assistance Trend** | AI Trend | Per-sprint percentage of done story points marked AI-assisted |
| **AI Usage Details** | AI Usage | Breakdown of AI tool labels and AI use-case labels across AI-assisted issues |
| **DAU Survey** | DAU | Team Daily Active Usage average from self-reported survey; by-role breakdown and usage-frequency bar chart |
| **DAU Trend** | DAU Trend | Week-over-week DAU average and adoption percentage |

Reports are saved to `generated/reports/<YYYY-MM-DDTHH-MM-SS>/`:

| File | Description |
|------|-------------|
| `report.html` | Self-contained HTML with interactive Chart.js charts; opens in any browser |
| `report.md` | Plain-text summary with ASCII bar charts and tables |

---

## Jira Labeling Guide

For AI metrics to work, team members must label their Jira issues **before closing them**.

### Required Labels

| Label type | Env var | Default value | Purpose |
|------------|---------|---------------|---------|
| AI Assisted | `AI_ASSISTED_LABEL` | `AI_assistance` | Marks an issue as AI-assisted — required for any AI metric |

### Optional Labels

| Label type | Env var | Example values | Purpose |
|------------|---------|----------------|---------|
| AI Tool | `AI_TOOL_LABELS` | `AI_Tool_Copilot`, `AI_Tool_ChatGPT` | Which AI tool was used |
| AI Action / Use Case | `AI_ACTION_LABELS` | `AI_Case_CodeGen`, `AI_Case_Review` | How AI was used |
| Exclude | `AI_EXCLUDE_LABELS` | `spike`, `ops` | Issues excluded from the AI % denominator (non-delivery work) |

### How to Apply Labels in Jira

1. Open the Jira issue
2. Find the **Labels** field in the issue detail panel
3. Add the appropriate labels before moving the issue to Done

> **Tip:** Configure all label values once in the **AI Adoption Labels** card on the Generate Report tab. They are saved to `.env` automatically.

---

## Troubleshooting

### Can't connect to Jira

| Symptom | Fix |
|---------|-----|
| "Connection failed" on Test Connection | Verify `JIRA_URL` has no trailing slash; confirm email and API token are correct |
| HTTP 401 Unauthorized | API token may be expired — generate a new one at id.atlassian.com |
| HTTP 403 Forbidden | Your account may lack API access; contact your Jira admin |

### Port 8080 in use

Edit `config/defaults.env`, change `PORT=9000` (or any available port), and restart `start_app.bat`.

### SSL certificate errors

If your company uses a custom Certificate Authority:

1. Go to the **Jira Connection** tab
2. Click **Fetch Certificate** — this caches the TLS cert at `certs/jira_ca_bundle.pem`
3. Retry the connection

Alternatively, run from the terminal: `python tools/fetch_ssl_cert.py`

### Report sections missing or empty

| Symptom | Fix |
|---------|-----|
| Velocity section missing | Ensure at least one metric section is checked in Report Options |
| AI metrics show 0% | Confirm issues have the `AI_assistance` label (or your configured label) in Jira |
| DAU section empty | DAU data requires self-reported survey issues in Jira; check your team's workflow |
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
All reports are saved under `generated/reports/<timestamp>/` in the project folder. The `Last Generated Reports` list in the UI links directly to each `report.html`.

**Q: Can I share the HTML report with someone who doesn't have the tool?**
Yes. The `report.html` file is fully self-contained — all CSS, JavaScript, and data are inlined. Send the file as an attachment; it opens in any modern browser.

**Q: How do I update the Jira credentials without editing `.env` manually?**
Use the **Jira Connection** tab — enter the values and click **Save**. Changes are written to `.env` automatically.

**Q: The default filter can't be deleted — is that intentional?**
Yes. `Default_Jira_Filter` is a read-only reference filter that ships with the tool. Create a new named filter for your team's use.
