# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

## [Unreleased]

### Added
- **Design Complexity Audit** (`--complexity-audit` CLI flag): structural complexity scoring for all Python modules in the repository. Scores four dimensions (cyclomatic complexity, LOC, coupling, cohesion) via `radon` + `ast`, classifies modules as Low / Medium / High, and produces a prioritised improvement plan with actionable recommendations. Output: `complexity_report.md` + `complexity_report.html` in `generated/reports/<timestamp>/`. No Jira credentials required.
- `GET /api/complexity/audit` HTTP endpoint: returns the full audit result as JSON for CI integration and dashboards.
- `app/core/complexity_audit.py`: pure scoring engine with `discover_modules()`, `score_module_source()`, and `build_complexity_report()`.
- `app/reporters/report_complexity_md.py`, `app/reporters/report_complexity_html.py`: Markdown and HTML reporters for complexity audit results.
- `app/server/complexity_handlers.py`: HTTP handler mixin for the new API endpoint.
- `ui/templates/complexity_audit.html.j2`: Jinja2 template for the HTML complexity report.
- `COMPLEXITY_MEDIUM_THRESHOLD` and `COMPLEXITY_HIGH_THRESHOLD` env vars (defaults: 3.5 and 7.0) for configurable classification thresholds.
- `radon>=6.0,<7` promoted to `requirements.txt` as a runtime dependency.

## [1.1.1] - 2026-05-21
### Fixed
- **Version not shown in UI**: `pyproject.toml` is now included in the release ZIP so `app.__version__` resolves correctly when the package is not pip-installed
- **User data files created in app folder**: `project_setup.bat` now calls `ensure_user_data_dirs()` and `run_first_time_migration()` after dependency installation, so `%LOCALAPPDATA%\AIMetrics` is populated at setup time instead of only on first app launch
- **`excluded_statuses` defaulting to empty**: restored `["Cancelled"]` in all three schemas in `config/jira_schema.json`; `get_schema()` now also applies the default when the field is present but empty (`[]`); new schemas created via the UI now default to `["Cancelled"]`

## [1.0.0] - 2026-05-20
### Added
- Initial release versioning and release workflow
- `pyproject.toml` project metadata with canonical `version`
- `app.__version__` exposed from source
- `create_app_zip.bat` now embeds the release version in ZIP names
- GitHub release workflow triggered by `vX.Y.Z` tags
