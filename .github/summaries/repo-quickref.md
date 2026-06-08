# Repo Quick Reference — test-app

Lean orientation anchor for Copilot agents. For full conventions see `AGENTS.md`.

## Module Map

| File | One-line purpose |
|------|-----------------|
| `main.py` | main |
| `server.py` | server |
| `app/cli.py` | cli |
| `app/exceptions.py` | exceptions |
| `app/__init__.py` | __init__ |
| `tests/conftest.py` | conftest |
| `tests/__init__.py` | __init__ |
| `tools/claude_session_stats.py` | claude_session_stats |
| `tools/copilot_session_stats.py` | copilot_session_stats |
| `tools/copilot_telemetry_stats.py` | copilot_telemetry_stats |
| `tools/docs_audit.py` | docs_audit |
| `tools/fetch_ssl_cert.py` | fetch_ssl_cert |
| `tools/new_adr.py` | new_adr |
| `tools/take_screenshots.py` | take_screenshots |
| `tools/_diag_cert_ui.py` | _diag_cert_ui |
| `.claude/tools/claude_session_stats.py` | claude_session_stats |
| `.github/hooks/pre_tool_copilot_boundary.py` | pre_tool_copilot_boundary |
| `app/core/complexity_audit.py` | complexity_audit |
| `app/core/config.py` | config |
| `app/core/dau_importer.py` | dau_importer |
| `app/core/dau_normalizer.py` | dau_normalizer |
| `app/core/jira_client.py` | jira_client |
| `app/core/metrics.py` | metrics |
| `app/core/migration.py` | migration |
| `app/core/schema.py` | schema |
| `app/core/user_data.py` | user_data |
| `app/core/__init__.py` | __init__ |
| `app/reporters/report_complexity_html.py` | report_complexity_html |
| `app/reporters/report_complexity_md.py` | report_complexity_md |
| `app/reporters/report_html.py` | report_html |
| `app/reporters/report_md.py` | report_md |
| `app/reporters/__init__.py` | __init__ |
| `app/server/cert_handlers.py` | cert_handlers |
| `app/server/complexity_handlers.py` | complexity_handlers |
| `app/server/config_handlers.py` | config_handlers |
| `app/server/connection_handlers.py` | connection_handlers |
| `app/server/data_handlers.py` | data_handlers |
| `app/server/dau_handlers.py` | dau_handlers |
| `app/server/filter_handlers.py` | filter_handlers |
| `app/server/generate_handlers.py` | generate_handlers |
| `app/server/schema_handlers.py` | schema_handlers |
| `app/server/_base.py` | _base |
| `app/server/__init__.py` | __init__ |
| `app/utils/cert_utils.py` | cert_utils |
| `app/utils/logging_setup.py` | logging_setup |
| `app/utils/__init__.py` | __init__ |
| `tests/component/conftest.py` | conftest |
| `tests/component/test_complexity_api.py` | test_complexity_api |
| `tests/component/test_complexity_cli.py` | test_complexity_cli |
| `tests/component/test_contracts.py` | test_contracts |
| `tests/component/test_cross_section_chart_labels.py` | test_cross_section_chart_labels |
| `tests/component/test_dau_report.py` | test_dau_report |
| `tests/component/test_release_zip.py` | test_release_zip |
| `tests/component/test_report_html.py` | test_report_html |
| `tests/component/test_report_md.py` | test_report_md |
| `tests/component/test_report_performance.py` | test_report_performance |
| `tests/component/test_server.py` | test_server |
| `tests/component/test_server_config.py` | test_server_config |
| `tests/component/test_server_filters.py` | test_server_filters |
| `tests/component/__init__.py` | __init__ |
| `tests/e2e/conftest.py` | conftest |
| `tests/e2e/test_dau_survey_ui.py` | test_dau_survey_ui |
| `tests/e2e/test_e2e_connection.py` | test_e2e_connection |
| `tests/e2e/test_e2e_filters.py` | test_e2e_filters |
| `tests/e2e/test_e2e_report_content.py` | test_e2e_report_content |
| `tests/e2e/test_e2e_schema_ui.py` | test_e2e_schema_ui |
| `tests/e2e/test_e2e_ui.py` | test_e2e_ui |
| `tests/e2e/test_e2e_version.py` | test_e2e_version |
| `tests/e2e/test_positive_e2e_flow.py` | test_positive_e2e_flow |
| `tests/e2e/__init__.py` | __init__ |
| `tests/integration/conftest.py` | conftest |
| `tests/integration/test_cli_server.py` | test_cli_server |
| `tests/integration/test_copilot_telemetry_stats.py` | test_copilot_telemetry_stats |
| `tests/integration/test_fetch_ssl_cert.py` | test_fetch_ssl_cert |
| `tests/integration/test_integration.py` | test_integration |
| `tests/integration/__init__.py` | __init__ |
| `tests/runners/run_all_checks.py` | run_all_checks |
| `tests/runners/run_performance_tests.py` | run_performance_tests |
| `tests/runners/run_security_checks.py` | run_security_checks |
| `tests/tools/agent_review_prep.py` | agent_review_prep |
| `tests/tools/complexity_report.py` | complexity_report |
| `tests/tools/coverage_gap_audit.py` | coverage_gap_audit |
| `tests/tools/doc_sync_check.py` | doc_sync_check |
| `tests/tools/feature_screenshot_audit.py` | feature_screenshot_audit |
| `tests/tools/requirements_map.py` | requirements_map |
| `tests/tools/requirements_status.py` | requirements_status |
| `tests/tools/smoke_test_setup.py` | smoke_test_setup |
| `tests/tools/test_coverage.py` | test_coverage |
| `tests/unit/conftest.py` | conftest |
| `tests/unit/test_cert_handlers.py` | test_cert_handlers |
| `tests/unit/test_cert_validation.py` | test_cert_validation |
| `tests/unit/test_cli.py` | test_cli |
| `tests/unit/test_complexity_audit.py` | test_complexity_audit |
| `tests/unit/test_config.py` | test_config |
| `tests/unit/test_copilot_customization_assets.py` | test_copilot_customization_assets |
| `tests/unit/test_dau_metrics.py` | test_dau_metrics |
| `tests/unit/test_dau_normalizer.py` | test_dau_normalizer |
| `tests/unit/test_exceptions.py` | test_exceptions |
| `tests/unit/test_filter_handlers.py` | test_filter_handlers |
| `tests/unit/test_imports.py` | test_imports |
| `tests/unit/test_jira_client.py` | test_jira_client |
| `tests/unit/test_logging_setup.py` | test_logging_setup |
| `tests/unit/test_main_helpers.py` | test_main_helpers |
| `tests/unit/test_metrics.py` | test_metrics |
| `tests/unit/test_schema.py` | test_schema |
| `tests/unit/test_server_handlers.py` | test_server_handlers |
| `tests/unit/test_user_data.py` | test_user_data |
| `tests/unit/test_version.py` | test_version |
| `tests/unit/__init__.py` | __init__ |
| `tools/agents/changelog_prep.py` | changelog_prep |
| `tools/agents/check_req_status.py` | check_req_status |
| `tools/agents/doc_drift.py` | doc_drift |
| `tools/agents/ux_spec_scaffold.py` | ux_spec_scaffold |

## Entry Points

- `main.py` (`main`) — thin entry point; keep business logic out
- `server.py` (`server`) — thin entry point; keep business logic out
- `tools/claude_session_stats.py` (`server`) — thin entry point; keep business logic out
- `tools/copilot_session_stats.py` (`main`) — thin entry point; keep business logic out
- `tools/copilot_telemetry_stats.py` (`main`) — thin entry point; keep business logic out
- `tools/docs_audit.py` (`main`) — thin entry point; keep business logic out
- `tools/fetch_ssl_cert.py` (`server`) — thin entry point; keep business logic out
- `tools/new_adr.py` (`main`) — thin entry point; keep business logic out
- `tools/take_screenshots.py` (`main`) — thin entry point; keep business logic out
- `.claude/tools/claude_session_stats.py` (`server`) — thin entry point; keep business logic out
- `.github/hooks/pre_tool_copilot_boundary.py` (`main`) — thin entry point; keep business logic out
- `app/server/__init__.py` (`server`) — thin entry point; keep business logic out
- `tests/runners/run_all_checks.py` (`main`) — thin entry point; keep business logic out
- `tests/runners/run_performance_tests.py` (`main`) — thin entry point; keep business logic out
- `tests/runners/run_security_checks.py` (`main`) — thin entry point; keep business logic out
- `tests/tools/agent_review_prep.py` (`server`) — thin entry point; keep business logic out
- `tests/tools/complexity_report.py` (`server`) — thin entry point; keep business logic out
- `tests/tools/coverage_gap_audit.py` (`server`) — thin entry point; keep business logic out
- `tests/tools/doc_sync_check.py` (`server`) — thin entry point; keep business logic out
- `tests/tools/feature_screenshot_audit.py` (`main`) — thin entry point; keep business logic out
- `tests/tools/requirements_status.py` (`main`) — thin entry point; keep business logic out
- `tests/tools/smoke_test_setup.py` (`server`) — thin entry point; keep business logic out
- `tests/tools/test_coverage.py` (`server`) — thin entry point; keep business logic out
- `tools/agents/changelog_prep.py` (`main`) — thin entry point; keep business logic out
- `tools/agents/check_req_status.py` (`main`) — thin entry point; keep business logic out
- `tools/agents/doc_drift.py` (`main`) — thin entry point; keep business logic out
- `tools/agents/ux_spec_scaffold.py` (`main`) — thin entry point; keep business logic out

## Key Commands

```bash
python main.py                 # run CLI / main entry point
python server.py                 # start dev server
python tools/claude_session_stats.py                 # start dev server
python tools/copilot_session_stats.py                 # run CLI / main entry point
python tools/copilot_telemetry_stats.py                 # run CLI / main entry point
python tools/docs_audit.py                 # run CLI / main entry point
python tools/fetch_ssl_cert.py                 # start dev server
python tools/new_adr.py                 # run CLI / main entry point
python tools/take_screenshots.py                 # run CLI / main entry point
python .claude/tools/claude_session_stats.py                 # start dev server
python .github/hooks/pre_tool_copilot_boundary.py                 # run CLI / main entry point
python app/server/__init__.py                 # start dev server
python tests/runners/run_all_checks.py                 # run CLI / main entry point
python tests/runners/run_performance_tests.py                 # run CLI / main entry point
python tests/runners/run_security_checks.py                 # run CLI / main entry point
python tests/tools/agent_review_prep.py                 # start dev server
python tests/tools/complexity_report.py                 # start dev server
python tests/tools/coverage_gap_audit.py                 # start dev server
python tests/tools/doc_sync_check.py                 # start dev server
python tests/tools/feature_screenshot_audit.py                 # run CLI / main entry point
python tests/tools/requirements_status.py                 # run CLI / main entry point
python tests/tools/smoke_test_setup.py                 # start dev server
python tests/tools/test_coverage.py                 # start dev server
python tools/agents/changelog_prep.py                 # run CLI / main entry point
python tools/agents/check_req_status.py                 # run CLI / main entry point
python tools/agents/doc_drift.py                 # run CLI / main entry point
python tools/agents/ux_spec_scaffold.py                 # run CLI / main entry point
```

## Key Conventions

- **Generated output**: all runtime artifacts go to `generated/` (gitignored); never write to source tree
- **Logging**: `logger = logging.getLogger(__name__)` per module; never root logger or `print()`
- **Tests**: run with `pytest` — see test pyramid below
- **Config**: new env vars → add to `.env.example` first, then the config module

## Test Pyramid

| Layer | File | Count |
|-------|------|-------|
| `component` | `tests/component/test_complexity_api.py` | 4 |
| `component` | `tests/component/test_complexity_cli.py` | 4 |
| `component` | `tests/component/test_contracts.py` | 11 |
| `component` | `tests/component/test_cross_section_chart_labels.py` | 13 |
| `component` | `tests/component/test_dau_report.py` | 15 |
| `component` | `tests/component/test_release_zip.py` | 11 |
| `component` | `tests/component/test_report_html.py` | 31 |
| `component` | `tests/component/test_report_md.py` | 37 |
| `component` | `tests/component/test_report_performance.py` | 1 |
| `component` | `tests/component/test_server.py` | 45 |
| `component` | `tests/component/test_server_config.py` | 45 |
| `component` | `tests/component/test_server_filters.py` | 11 |
| `e2e` | `tests/e2e/test_dau_survey_ui.py` | 25 |
| `e2e` | `tests/e2e/test_e2e_connection.py` | 41 |
| `e2e` | `tests/e2e/test_e2e_filters.py` | 15 |
| `e2e` | `tests/e2e/test_e2e_report_content.py` | 1 |
| `e2e` | `tests/e2e/test_e2e_schema_ui.py` | 6 |
| `e2e` | `tests/e2e/test_e2e_ui.py` | 32 |
| `e2e` | `tests/e2e/test_e2e_version.py` | 4 |
| `e2e` | `tests/e2e/test_positive_e2e_flow.py` | 1 |
| `integration` | `tests/integration/test_cli_server.py` | 3 |
| `integration` | `tests/integration/test_copilot_telemetry_stats.py` | 2 |
| `integration` | `tests/integration/test_fetch_ssl_cert.py` | 10 |
| `integration` | `tests/integration/test_integration.py` | 8 |
| `unit` | `tests/unit/test_cert_handlers.py` | 4 |
| `unit` | `tests/unit/test_cert_validation.py` | 5 |
| `unit` | `tests/unit/test_cli.py` | 5 |
| `unit` | `tests/unit/test_complexity_audit.py` | 15 |
| `unit` | `tests/unit/test_config.py` | 44 |
| `unit` | `tests/unit/test_copilot_customization_assets.py` | 6 |
| `unit` | `tests/unit/test_dau_metrics.py` | 33 |
| `unit` | `tests/unit/test_dau_normalizer.py` | 21 |
| `unit` | `tests/unit/test_exceptions.py` | 6 |
| `unit` | `tests/unit/test_filter_handlers.py` | 19 |
| `unit` | `tests/unit/test_imports.py` | 8 |
| `unit` | `tests/unit/test_jira_client.py` | 46 |
| `unit` | `tests/unit/test_logging_setup.py` | 15 |
| `unit` | `tests/unit/test_main_helpers.py` | 5 |
| `unit` | `tests/unit/test_metrics.py` | 89 |
| `unit` | `tests/unit/test_schema.py` | 37 |
| `unit` | `tests/unit/test_server_handlers.py` | 26 |
| `unit` | `tests/unit/test_user_data.py` | 3 |
| `unit` | `tests/unit/test_version.py` | 4 |

## Authoritative References

| Topic | File |
|-------|------|
| Module responsibilities, data flow | `.claude/summaries/architecture-map.md` |
| Agent roster | `.claude/summaries/agent-index.md` |
| Full conventions | `AGENTS.md` |

---

Generated by nexus-agentic-sdlc 1.0.0
