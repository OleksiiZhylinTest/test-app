# arch-conventions.md — Lean-Context Architecture Conventions Summary

Source of truth: `AGENTS.md` and `.claude/summaries/architecture-map.md`
This file is a standing-rules extract for `test-app`. Do NOT duplicate or override the full architecture doc.

## Layer Rules

| Rule | Constraint |
|------|-----------|
| L1 | `app/core/config.py` reads env only — no computation, no I/O beyond env loading |
| L2 | `app/core/metrics.py` computes only — no fetch logic, no rendering, no I/O |
| L3 | `app/reporters/report_complexity_html.py` renders only — no business logic, no computation |
| L4 | `app/reporters/report_complexity_md.py` renders only — no business logic, no computation |
| L5 | `app/reporters/report_html.py` renders only — no business logic, no computation |
| L6 | `app/reporters/report_md.py` renders only — no business logic, no computation |
| L7 | `app/reporters/__init__.py` renders only — no business logic, no computation |
| L8 | `app/server/config_handlers.py` reads env only — no computation, no I/O beyond env loading |
| L9 | `tests/component/test_dau_report.py` renders only — no business logic, no computation |
| L10 | `tests/component/test_report_html.py` renders only — no business logic, no computation |
| L11 | `tests/component/test_report_md.py` renders only — no business logic, no computation |
| L12 | `tests/component/test_report_performance.py` renders only — no business logic, no computation |
| L13 | `tests/component/test_server_config.py` reads env only — no computation, no I/O beyond env loading |
| L14 | `tests/e2e/test_e2e_report_content.py` renders only — no business logic, no computation |
| L15 | `tests/tools/complexity_report.py` renders only — no business logic, no computation |
| L16 | `tests/unit/test_config.py` reads env only — no computation, no I/O beyond env loading |
| L17 | `tests/unit/test_dau_metrics.py` computes only — no fetch logic, no rendering, no I/O |
| L18 | `tests/unit/test_metrics.py` computes only — no fetch logic, no rendering, no I/O |
| — | No new cross-module imports that violate the layer diagram in the architecture doc |

## Module Ownership

| Module pattern | Single responsibility |
|---------------|----------------------|
| `main.py` | main — owns nothing outside this responsibility |
| `server.py` | server — owns nothing outside this responsibility |
| `app/cli.py` | cli — owns nothing outside this responsibility |
| `app/exceptions.py` | exceptions — owns nothing outside this responsibility |
| `app/__init__.py` | __init__ — owns nothing outside this responsibility |
| `tests/conftest.py` | conftest — owns nothing outside this responsibility |
| `tests/__init__.py` | __init__ — owns nothing outside this responsibility |
| `tools/claude_session_stats.py` | claude_session_stats — owns nothing outside this responsibility |
| `tools/copilot_session_stats.py` | copilot_session_stats — owns nothing outside this responsibility |
| `tools/copilot_telemetry_stats.py` | copilot_telemetry_stats — owns nothing outside this responsibility |
| `tools/docs_audit.py` | docs_audit — owns nothing outside this responsibility |
| `tools/fetch_ssl_cert.py` | fetch_ssl_cert — owns nothing outside this responsibility |
| `tools/new_adr.py` | new_adr — owns nothing outside this responsibility |
| `tools/take_screenshots.py` | take_screenshots — owns nothing outside this responsibility |
| `tools/_diag_cert_ui.py` | _diag_cert_ui — owns nothing outside this responsibility |
| `.claude/tools/claude_session_stats.py` | claude_session_stats — owns nothing outside this responsibility |
| `.github/hooks/pre_tool_copilot_boundary.py` | pre_tool_copilot_boundary — owns nothing outside this responsibility |
| `app/core/complexity_audit.py` | complexity_audit — owns nothing outside this responsibility |
| `app/core/config.py` | config — owns nothing outside this responsibility |
| `app/core/dau_importer.py` | dau_importer — owns nothing outside this responsibility |
| `app/core/dau_normalizer.py` | dau_normalizer — owns nothing outside this responsibility |
| `app/core/jira_client.py` | jira_client — owns nothing outside this responsibility |
| `app/core/metrics.py` | metrics — owns nothing outside this responsibility |
| `app/core/migration.py` | migration — owns nothing outside this responsibility |
| `app/core/schema.py` | schema — owns nothing outside this responsibility |
| `app/core/user_data.py` | user_data — owns nothing outside this responsibility |
| `app/core/__init__.py` | __init__ — owns nothing outside this responsibility |
| `app/reporters/report_complexity_html.py` | report_complexity_html — owns nothing outside this responsibility |
| `app/reporters/report_complexity_md.py` | report_complexity_md — owns nothing outside this responsibility |
| `app/reporters/report_html.py` | report_html — owns nothing outside this responsibility |
| `app/reporters/report_md.py` | report_md — owns nothing outside this responsibility |
| `app/reporters/__init__.py` | __init__ — owns nothing outside this responsibility |
| `app/server/cert_handlers.py` | cert_handlers — owns nothing outside this responsibility |
| `app/server/complexity_handlers.py` | complexity_handlers — owns nothing outside this responsibility |
| `app/server/config_handlers.py` | config_handlers — owns nothing outside this responsibility |
| `app/server/connection_handlers.py` | connection_handlers — owns nothing outside this responsibility |
| `app/server/data_handlers.py` | data_handlers — owns nothing outside this responsibility |
| `app/server/dau_handlers.py` | dau_handlers — owns nothing outside this responsibility |
| `app/server/filter_handlers.py` | filter_handlers — owns nothing outside this responsibility |
| `app/server/generate_handlers.py` | generate_handlers — owns nothing outside this responsibility |
| `app/server/schema_handlers.py` | schema_handlers — owns nothing outside this responsibility |
| `app/server/_base.py` | _base — owns nothing outside this responsibility |
| `app/server/__init__.py` | __init__ — owns nothing outside this responsibility |
| `app/utils/cert_utils.py` | cert_utils — owns nothing outside this responsibility |
| `app/utils/logging_setup.py` | logging_setup — owns nothing outside this responsibility |
| `app/utils/__init__.py` | __init__ — owns nothing outside this responsibility |
| `tests/component/conftest.py` | conftest — owns nothing outside this responsibility |
| `tests/component/test_complexity_api.py` | test_complexity_api — owns nothing outside this responsibility |
| `tests/component/test_complexity_cli.py` | test_complexity_cli — owns nothing outside this responsibility |
| `tests/component/test_contracts.py` | test_contracts — owns nothing outside this responsibility |
| `tests/component/test_cross_section_chart_labels.py` | test_cross_section_chart_labels — owns nothing outside this responsibility |
| `tests/component/test_dau_report.py` | test_dau_report — owns nothing outside this responsibility |
| `tests/component/test_release_zip.py` | test_release_zip — owns nothing outside this responsibility |
| `tests/component/test_report_html.py` | test_report_html — owns nothing outside this responsibility |
| `tests/component/test_report_md.py` | test_report_md — owns nothing outside this responsibility |
| `tests/component/test_report_performance.py` | test_report_performance — owns nothing outside this responsibility |
| `tests/component/test_server.py` | test_server — owns nothing outside this responsibility |
| `tests/component/test_server_config.py` | test_server_config — owns nothing outside this responsibility |
| `tests/component/test_server_filters.py` | test_server_filters — owns nothing outside this responsibility |
| `tests/component/__init__.py` | __init__ — owns nothing outside this responsibility |
| `tests/e2e/conftest.py` | conftest — owns nothing outside this responsibility |
| `tests/e2e/test_dau_survey_ui.py` | test_dau_survey_ui — owns nothing outside this responsibility |
| `tests/e2e/test_e2e_connection.py` | test_e2e_connection — owns nothing outside this responsibility |
| `tests/e2e/test_e2e_filters.py` | test_e2e_filters — owns nothing outside this responsibility |
| `tests/e2e/test_e2e_report_content.py` | test_e2e_report_content — owns nothing outside this responsibility |
| `tests/e2e/test_e2e_schema_ui.py` | test_e2e_schema_ui — owns nothing outside this responsibility |
| `tests/e2e/test_e2e_ui.py` | test_e2e_ui — owns nothing outside this responsibility |
| `tests/e2e/test_e2e_version.py` | test_e2e_version — owns nothing outside this responsibility |
| `tests/e2e/test_positive_e2e_flow.py` | test_positive_e2e_flow — owns nothing outside this responsibility |
| `tests/e2e/__init__.py` | __init__ — owns nothing outside this responsibility |
| `tests/integration/conftest.py` | conftest — owns nothing outside this responsibility |
| `tests/integration/test_cli_server.py` | test_cli_server — owns nothing outside this responsibility |
| `tests/integration/test_copilot_telemetry_stats.py` | test_copilot_telemetry_stats — owns nothing outside this responsibility |
| `tests/integration/test_fetch_ssl_cert.py` | test_fetch_ssl_cert — owns nothing outside this responsibility |
| `tests/integration/test_integration.py` | test_integration — owns nothing outside this responsibility |
| `tests/integration/__init__.py` | __init__ — owns nothing outside this responsibility |
| `tests/runners/run_all_checks.py` | run_all_checks — owns nothing outside this responsibility |
| `tests/runners/run_performance_tests.py` | run_performance_tests — owns nothing outside this responsibility |
| `tests/runners/run_security_checks.py` | run_security_checks — owns nothing outside this responsibility |
| `tests/tools/agent_review_prep.py` | agent_review_prep — owns nothing outside this responsibility |
| `tests/tools/complexity_report.py` | complexity_report — owns nothing outside this responsibility |
| `tests/tools/coverage_gap_audit.py` | coverage_gap_audit — owns nothing outside this responsibility |
| `tests/tools/doc_sync_check.py` | doc_sync_check — owns nothing outside this responsibility |
| `tests/tools/feature_screenshot_audit.py` | feature_screenshot_audit — owns nothing outside this responsibility |
| `tests/tools/requirements_map.py` | requirements_map — owns nothing outside this responsibility |
| `tests/tools/requirements_status.py` | requirements_status — owns nothing outside this responsibility |
| `tests/tools/smoke_test_setup.py` | smoke_test_setup — owns nothing outside this responsibility |
| `tests/tools/test_coverage.py` | test_coverage — owns nothing outside this responsibility |
| `tests/unit/conftest.py` | conftest — owns nothing outside this responsibility |
| `tests/unit/test_cert_handlers.py` | test_cert_handlers — owns nothing outside this responsibility |
| `tests/unit/test_cert_validation.py` | test_cert_validation — owns nothing outside this responsibility |
| `tests/unit/test_cli.py` | test_cli — owns nothing outside this responsibility |
| `tests/unit/test_complexity_audit.py` | test_complexity_audit — owns nothing outside this responsibility |
| `tests/unit/test_config.py` | test_config — owns nothing outside this responsibility |
| `tests/unit/test_copilot_customization_assets.py` | test_copilot_customization_assets — owns nothing outside this responsibility |
| `tests/unit/test_dau_metrics.py` | test_dau_metrics — owns nothing outside this responsibility |
| `tests/unit/test_dau_normalizer.py` | test_dau_normalizer — owns nothing outside this responsibility |
| `tests/unit/test_exceptions.py` | test_exceptions — owns nothing outside this responsibility |
| `tests/unit/test_filter_handlers.py` | test_filter_handlers — owns nothing outside this responsibility |
| `tests/unit/test_imports.py` | test_imports — owns nothing outside this responsibility |
| `tests/unit/test_jira_client.py` | test_jira_client — owns nothing outside this responsibility |
| `tests/unit/test_logging_setup.py` | test_logging_setup — owns nothing outside this responsibility |
| `tests/unit/test_main_helpers.py` | test_main_helpers — owns nothing outside this responsibility |
| `tests/unit/test_metrics.py` | test_metrics — owns nothing outside this responsibility |
| `tests/unit/test_schema.py` | test_schema — owns nothing outside this responsibility |
| `tests/unit/test_server_handlers.py` | test_server_handlers — owns nothing outside this responsibility |
| `tests/unit/test_user_data.py` | test_user_data — owns nothing outside this responsibility |
| `tests/unit/test_version.py` | test_version — owns nothing outside this responsibility |
| `tests/unit/__init__.py` | __init__ — owns nothing outside this responsibility |
| `tools/agents/changelog_prep.py` | changelog_prep — owns nothing outside this responsibility |
| `tools/agents/check_req_status.py` | check_req_status — owns nothing outside this responsibility |
| `tools/agents/doc_drift.py` | doc_drift — owns nothing outside this responsibility |
| `tools/agents/ux_spec_scaffold.py` | ux_spec_scaffold — owns nothing outside this responsibility |

## Shared Module Rules

| Rule | Constraint |
|------|-----------|
| S1 | Exception types are defined once — add a new type only when it must be raised or caught across module boundaries |
| S2 | Shared test factories go in the root `conftest.py` — never duplicate fixture logic across test files |

## Escalate to Full Architecture Doc When

- Adding or removing a module from the application source
- Altering the core data contract shapes
- Adding a new HTTP route or API endpoint
- Introducing a new third-party dependency
- Any change that crosses two or more layers simultaneously

---

Generated by nexus-agentic-sdlc 1.0.0
