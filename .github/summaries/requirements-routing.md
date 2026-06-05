# Copilot Summary: Requirements Routing

Use this summary before loading multiple requirement files. Its job is to route you to the right requirement document quickly.

## Source of Truth

- `docs/product/requirements/README.md`

## First Stop

- Start with `docs/product/requirements/README.md` when a task changes behavior, constraints, or verification expectations.

## Requirement File Routing

- Performance, security, usability, reliability, privacy, compatibility, accessibility -> `app_non_functional_requirements.md`
- DAU survey UI, storage, DAU metric computation, DAU report rendering -> `dau_survey_requirements.md`
- Jira authentication, config validation, SSL -> `jira_connection_requirements.md`
- Board discovery, sprint fetching, issue fetching, changelog, filter scoping -> `jira_data_fetching_requirements.md`
- Filter CRUD and filter UI behavior -> `jira_filter_management_requirements.md`
- Schema loading, field lookup, status mapping, auto-detection -> `jira_schema_requirements.md`
- Logging behavior -> `logging_requirements.md`
- Velocity, done-status logic, story points, sprint attribution, estimation type -> `metric_computation_requirements.md`
- Report generation config, toggles, labels, UI controls -> `report_generation_requirements.md`
- Setup/uninstall flow -> `installation_requirements.md`
- Python/runtime/dependency constraints -> `technical_requirements.md`

## Status Rules

Only use these values in requirement tables:

- `✓ Met`
- `✗ Not met`
- `⬜ N/T`

Do not add new rows or new requirement files unless the user explicitly changes the requirements system.

## Escalate Beyond This Summary When

- the task affects multiple feature areas
- you need exact requirement IDs or acceptance criteria
- the task is mainly about NFRs, installation, or metric contracts