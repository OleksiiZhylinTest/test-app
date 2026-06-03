# Copilot Summary: Architecture Module Map

Use this summary before loading `docs/development/architecture.md` when the task only needs module ownership or data-flow orientation.

## Source of Truth

- `AGENTS.md`
- `docs/development/architecture.md`

## Entry Points

- `main.py` -> `app/cli.py`
- `server.py` -> `app/server/`

Both entry points are intentionally thin.

## Core Runtime Layers

- `app/core/config.py` loads `.env` and exposes config constants.
- `app/core/jira_client.py` wraps Jira access and returns `(sprints, sprint_issues)`.
- `app/core/metrics.py` computes the metrics dict consumed by reporters.
- `app/core/schema.py` owns Jira field schema lookups from `config/jira_schema.json`.

## Output Layers

- `app/reporters/report_html.py` renders `ui/templates/report.html.j2`.
- `app/reporters/report_md.py` builds the Markdown report.

Reporters format data only; they should not own fetch or computation logic.

## Server Layer

- `app/server/_base.py` is the routing base.
- `app/server/` handlers split API responsibilities by feature: config, connection, filters, schemas, generation, data, certificates, and DAU.

## Shared Conventions

- Keep business logic in `app/core/`.
- Keep entry points thin.
- Keep reporters presentation-only.
- Keep persistent config in `config/`.
- Put generated runtime artifacts in `generated/`.

## Escalate To Full Architecture Doc When

- you need data-flow details across multiple layers
- you need route-by-route server behavior
- you need exact configuration or output-shape documentation
- you are changing architecture rather than just locating ownership