# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

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
