# AI Adoption Metrics Report

## Overview

**AI Adoption Metrics Report** is a Python 3.12+ tool for engineering teams that want to measure the impact of AI tooling on their delivery. It connects to Jira Cloud, fetches sprint and issue data, computes a set of engineering metrics, and generates self-contained reports in two formats: an interactive HTML report with charts and a Markdown report with tables. Both formats are produced in parallel from a single data fetch.

The tool ships with a browser-based UI for configuration and on-demand report generation, and also supports a CLI mode for scripted or automated runs.

## Key Features

- **Velocity trend** — completed story points per sprint, visualised as a bar chart
- **AI Assistance Trend** — percentage of done story points carrying an AI-assisted label, per sprint
- **AI Usage Breakdown** — distribution of AI tool and use-case labels across all AI-assisted issues
- **DAU Survey** — team daily-active-usage average from self-reported survey data plus week-over-week trend
- **Live report generation** — browser UI streams generation output in real time via SSE
- **Dual output** — HTML (interactive charts) and Markdown (plain tables) produced in parallel
- **Named filter registry** — save and reuse JQL filters, each bound to a Jira field schema

## Architecture

The application has two entry points: a CLI (`main.py` → `app/cli.py`) and a local HTTP server (`server.py` → `app/server/`). Both share the same pipeline: validate config → fetch Jira data → compute metrics → render reports.

| Layer | Module | Responsibility |
|---|---|---|
| Config | `app/core/config.py` | Loads `.env` and `config/defaults.env`; exposes all constants |
| Fetch | `app/core/jira_client.py` | Jira REST wrapper; returns `(sprints, sprint_issues)` |
| Compute | `app/core/metrics.py` | Pure metric computation; produces the dict both reporters consume |
| Schema | `app/core/schema.py` | Jira field schema registry (`config/jira_schema.json`) |
| HTML report | `app/reporters/report_html.py` | Renders `ui/templates/report.html.j2` via Jinja2 |
| MD report | `app/reporters/report_md.py` | Builds and writes the Markdown report |
| Server | `app/server/` | Stdlib `HTTPServer`; serves the UI and all `/api/*` routes |

For full architecture documentation see [`docs/development/architecture.md`](docs/development/architecture.md).

## Documentation

| Topic | Link |
|---|---|
| Architecture & module map | [`docs/development/architecture.md`](docs/development/architecture.md) |
| Metrics reference | [`docs/product/metrics/README.md`](docs/product/metrics/README.md) |
| Features (browser UI) | [`docs/product/features/features.md`](docs/product/features/features.md) |
| Requirements | [`docs/product/requirements/README.md`](docs/product/requirements/README.md) |
| Jira API reference | [`docs/development/jira/README.md`](docs/development/jira/README.md) |
| CI/CD pipeline | [`docs/development/pipeline.md`](docs/development/pipeline.md) |

## Releases

Latest release and download: **[GitHub Releases](https://github.com/Azhilin/test-app/releases)**

Each release ships a self-contained ZIP (`ai_adoption_manager_vX.Y.Z.zip`) — extract and run, no build step needed.

---

## Setup

### Before you begin — where to extract the application

Extract the ZIP to a **permanent folder that you own**, for example:

- `C:\Users\<your-username>\Apps\AIMetrics`
- `C:\Apps\AIMetrics`

**Avoid** these locations:

| Location | Why |
|---|---|
| `Downloads\` | Often cleaned automatically; easy to delete by accident |
| `Desktop\` | Synced by OneDrive/SharePoint on many corporate machines — large files slow sync |
| `C:\Program Files\` | Requires administrator rights to write |

> **Your data is safe across upgrades.** Credentials, reports, filters, DAU data, and certificates are stored in `%LOCALAPPDATA%\AIMetrics` (e.g. `C:\Users\<your-username>\AppData\Local\AIMetrics`) — completely outside the application folder. Upgrading means unzipping a new version anywhere and running it; your data migrates automatically on first launch.

### Step 1 - Install Python, dependencies, and bootstrap config (run once)

Double-click **`project_setup.bat`**.

This detects or installs Python 3.12 (per-user, no admin rights needed), creates a `.venv`, installs all required packages, and creates `.env` from `.env.example`.

### Step 2 - Configure Jira credentials

Open `.env` and fill in:

- `JIRA_URL` – e.g. `https://your-domain.atlassian.net`
- `JIRA_EMAIL` – your Atlassian account email
- `JIRA_API_TOKEN` – create at [Atlassian API tokens](https://id.atlassian.com/manage-profile/security/api-tokens)

That is all that `.env` needs. Non-sensitive settings (`JIRA_BOARD_ID`, `JIRA_SPRINT_COUNT`, `JIRA_SCHEMA_NAME`, AI labels, metric toggles, etc.) live in `config/defaults.env` — edit that file to change project-wide defaults.

---

## Run

### Using the browser UI (recommended)

Double-click **`start_app.bat`** — this starts a local server bound to `127.0.0.1` and opens the app in your browser at `http://localhost:8080`.

Use the UI to configure your Jira connection, select a filter, and generate reports. On the **Filter Builder** tab, pick an **Active Schema** before saving a filter — the saved filter's `schema_name` determines which schema the pipeline uses when the filter is run.

If your Jira instance uses a custom CA certificate, use the Jira Connection tab to fetch it or place the PEM bundle at `certs/jira_ca_bundle.pem`.

For full UI documentation see [`docs/product/features/features.md`](docs/product/features/features.md).
