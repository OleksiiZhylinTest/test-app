---
name: Architecture Map
description: Lightweight anchor for implement, fix, sync, extend. Use this before loading full architecture docs.
type: reference
---

# Architecture Map — test-app

> Lightweight anchor. Load this before the full architecture doc.

## Entry Points

| File | Kind | Delegates to |
|------|------|-------------|
| `main.py` | `main` | *(see module map below)* |
| `server.py` | `server` | *(see module map below)* |
| `tools/claude_session_stats.py` | `server` | *(see module map below)* |
| `tools/copilot_session_stats.py` | `main` | *(see module map below)* |
| `tools/copilot_telemetry_stats.py` | `main` | *(see module map below)* |
| `tools/docs_audit.py` | `main` | *(see module map below)* |
| `tools/fetch_ssl_cert.py` | `server` | *(see module map below)* |
| `tools/new_adr.py` | `main` | *(see module map below)* |
| `tools/take_screenshots.py` | `main` | *(see module map below)* |
| `.claude/tools/claude_session_stats.py` | `server` | *(see module map below)* |
| `.github/hooks/pre_tool_copilot_boundary.py` | `main` | *(see module map below)* |
| `app/server/__init__.py` | `server` | *(see module map below)* |
| `tests/runners/run_all_checks.py` | `main` | *(see module map below)* |
| `tests/runners/run_performance_tests.py` | `main` | *(see module map below)* |
| `tests/runners/run_security_checks.py` | `main` | *(see module map below)* |
| `tests/tools/agent_review_prep.py` | `server` | *(see module map below)* |
| `tests/tools/complexity_report.py` | `server` | *(see module map below)* |
| `tests/tools/coverage_gap_audit.py` | `server` | *(see module map below)* |
| `tests/tools/doc_sync_check.py` | `server` | *(see module map below)* |
| `tests/tools/feature_screenshot_audit.py` | `main` | *(see module map below)* |
| `tests/tools/requirements_status.py` | `main` | *(see module map below)* |
| `tests/tools/smoke_test_setup.py` | `server` | *(see module map below)* |
| `tests/tools/test_coverage.py` | `server` | *(see module map below)* |
| `tools/agents/changelog_prep.py` | `main` | *(see module map below)* |
| `tools/agents/check_req_status.py` | `main` | *(see module map below)* |
| `tools/agents/doc_drift.py` | `main` | *(see module map below)* |
| `tools/agents/ux_spec_scaffold.py` | `main` | *(see module map below)* |

Both entry points should be intentionally thin — no business logic.

## Module Map

| File | Purpose | Classes | Functions |
|------|---------|---------|-----------|
| `main.py` | main | — | — |
| `server.py` | server | — | — |
| `app/cli.py` | cli | — | main |
| `app/exceptions.py` | exceptions | AppError, ConfigError, JiraClientError, JiraNetworkError, JiraAuthError, JiraApiError, SchemaError, DataImportError | — |
| `app/__init__.py` | __init__ | — | — |
| `tests/conftest.py` | conftest | — | make_sprint, make_issue, make_issue_with_changelog, make_issue_with_labels, server_url, attach_logs_to_allure, attach_stdout_stderr_to_allure |
| `tests/__init__.py` | __init__ | — | — |
| `tools/claude_session_stats.py` | claude_session_stats | — | main |
| `tools/copilot_session_stats.py` | copilot_session_stats | — | build_session_report, generate_session_report, main |
| `tools/copilot_telemetry_stats.py` | copilot_telemetry_stats | — | build_stats, generate_stats, main |
| `tools/docs_audit.py` | docs_audit | Finding, DocFile | discover_docs, discover_code_modules, check_stubs, check_placeholders, check_heading_hierarchy, check_broken_links, check_orphans, check_naming_conventions, check_code_coverage, check_duplicate_titles, check_empty_sections, check_missing_overview, generate_report, audit, main |
| `tools/fetch_ssl_cert.py` | fetch_ssl_cert | — | fetch_and_save_cert |
| `tools/new_adr.py` | new_adr | — | slugify, main |
| `tools/take_screenshots.py` | take_screenshots | — | take_screenshots |
| `tools/_diag_cert_ui.py` | _diag_cert_ui | — | — |
| `.claude/tools/claude_session_stats.py` | claude_session_stats | — | main |
| `.github/hooks/pre_tool_copilot_boundary.py` | pre_tool_copilot_boundary | — | main |
| `app/core/complexity_audit.py` | complexity_audit | — | discover_modules, score_module_source, build_complexity_report |
| `app/core/config.py` | config | — | validate_config |
| `app/core/dau_importer.py` | dau_importer | — | import_dau_excel, import_dau_excel_b64 |
| `app/core/dau_normalizer.py` | dau_normalizer | — | normalize_dau_responses, get_dau_records |
| `app/core/jira_client.py` | jira_client | — | create_client, get_board_id, get_sprints, get_filter_jql, get_issues_for_sprint, fetch_sprint_data, fetch_kanban_data |
| `app/core/metrics.py` | metrics | — | deduplicate_sprint_issues, compute_velocity, compute_ai_assistance_trend, compute_ai_usage_details, compute_sprint_issue_details, compute_dau_metrics, compute_dau_trend, get_done_issue_keys_for_changelog, compute_cycle_time, build_metrics_dict |
| `app/core/migration.py` | migration | — | run_first_time_migration |
| `app/core/schema.py` | schema | — | load_schemas, get_schema, get_active_schema, save_schema, delete_schema, get_field_id, get_field_jql_name, get_done_statuses, get_in_progress_statuses, get_excluded_statuses, build_schema_from_fields |
| `app/core/user_data.py` | user_data | — | user_data_dir, ensure_user_data_dirs |
| `app/core/__init__.py` | __init__ | — | — |
| `app/reporters/report_complexity_html.py` | report_complexity_html | — | generate_complexity_html |
| `app/reporters/report_complexity_md.py` | report_complexity_md | — | generate_complexity_md |
| `app/reporters/report_html.py` | report_html | — | generate_html |
| `app/reporters/report_md.py` | report_md | — | generate_md |
| `app/reporters/__init__.py` | __init__ | — | — |
| `app/server/cert_handlers.py` | cert_handlers | CertHandlerMixin | — |
| `app/server/complexity_handlers.py` | complexity_handlers | ComplexityHandlerMixin | — |
| `app/server/config_handlers.py` | config_handlers | ConfigHandlerMixin | — |
| `app/server/connection_handlers.py` | connection_handlers | ConnectionHandlerMixin | — |
| `app/server/data_handlers.py` | data_handlers | DataHandlerMixin | — |
| `app/server/dau_handlers.py` | dau_handlers | DauHandlerMixin | — |
| `app/server/filter_handlers.py` | filter_handlers | FilterHandlerMixin | jql_quote |
| `app/server/generate_handlers.py` | generate_handlers | GenerateHandlerMixin | emit |
| `app/server/schema_handlers.py` | schema_handlers | SchemaHandlerMixin | — |
| `app/server/_base.py` | _base | Server, HandlerBase | guess_mime, handle_error, log_message, do_OPTIONS, do_GET, do_POST, do_DELETE |
| `app/server/__init__.py` | __init__ | Handler | run |
| `app/utils/cert_utils.py` | cert_utils | — | validate_cert |
| `app/utils/logging_setup.py` | logging_setup | — | setup_logging |
| `app/utils/__init__.py` | __init__ | — | — |
| `tests/component/conftest.py` | conftest | — | minimal_metrics_dict, empty_metrics_dict |
| `tests/component/test_complexity_api.py` | test_complexity_api | — | test_complexity_audit_returns_200_json_with_required_top_keys, test_complexity_audit_each_score_has_required_keys, test_complexity_audit_summary_has_required_keys, test_complexity_audit_classification_values_are_valid |
| `tests/component/test_complexity_cli.py` | test_complexity_cli | — | test_complexity_audit_cli_exits_zero_creates_md_within_60s, test_complexity_audit_cli_creates_html_alongside_md, test_complexity_audit_md_contains_expected_sections, test_complexity_audit_md_includes_non_app_modules |
| `tests/component/test_contracts.py` | test_contracts | — | test_sprint_factory_has_keys_used_by_compute_velocity, test_sprint_factory_has_keys_used_by_ai_trend, test_issue_factory_matches_is_done_expectations, test_issue_with_labels_factory_matches_get_labels, test_build_metrics_dict_has_all_expected_keys, test_velocity_row_has_required_keys, test_ai_trend_row_has_required_keys, test_ai_usage_details_shape, test_template_variables_exist_in_metrics_dict, test_validate_cert_response_has_all_keys_when_valid, test_validate_cert_response_has_all_keys_when_missing |
| `tests/component/test_cross_section_chart_labels.py` | test_cross_section_chart_labels | — | test_t01_velocity_alone_no_pct, test_t02_ai_usage_alone_pie_pct, test_t03_ai_trend_alone_pct, test_t04_dau_trend_alone_pct, test_t05_ai_usage_plus_velocity, test_t06_ai_trend_plus_velocity, test_t07_dau_trend_plus_velocity, test_t08_ai_usage_plus_dau_trend, test_t09_ai_trend_plus_dau_trend, test_t11_ai_usage_plus_velocity_plus_dau_trend, test_t12_ai_trend_plus_velocity_plus_dau_trend, test_t13_ai_usage_plus_ai_trend_plus_dau_trend, test_t14_all_sections_correct_pct_labels |
| `tests/component/test_dau_report.py` | test_dau_report | — | test_md_has_dau_heading_when_data_present, test_md_dau_shows_team_avg, test_md_dau_shows_role_in_table, test_md_dau_section_absent_when_no_responses, test_html_has_dau_section_when_data_present, test_html_dau_shows_team_avg, test_dau_team_avg_shown_in_html, test_html_dau_section_absent_when_no_responses, test_html_dau_section_hidden_when_visibility_false, test_md_has_dau_trend_heading, test_md_dau_trend_shows_week, test_md_dau_trend_absent_when_empty, test_html_has_dau_trend_section, test_html_dau_trend_absent_when_empty, test_html_dau_trend_hidden_when_visibility_false |
| `tests/component/test_release_zip.py` | test_release_zip | — | release_zip, zip_entries, test_zip_name_format, test_zip_contains_required_folder, test_zip_contains_required_root_file, test_zip_contains_fetch_ssl_cert, test_zip_excludes_venv, test_zip_excludes_generated, test_zip_excludes_dev_requirements, test_zip_excludes_tests, test_zip_excludes_dotenv, test_zip_excludes_pycache, test_zip_excludes_data |
| `tests/component/test_report_html.py` | test_report_html | — | test_templates_dir_exists, test_template_file_exists, test_templates_dir_not_inside_app, test_file_created, test_doctype_present, test_title_present, test_date_present, test_sprint_name_present, test_velocity_value_present, test_chart_canvas_present_when_velocity_nonempty, test_empty_velocity_shows_no_data_message, test_chart_script_absent_when_velocity_empty, test_velocity_totals_row_present, test_ai_assistance_section_present, test_ai_assistance_chart_canvas_present, test_ai_assistance_sprint_and_pct_present, test_ai_assistance_section_hidden_when_section_visibility_false, test_ai_assistance_no_data_message_when_empty, test_ai_usage_details_section_present, test_ai_usage_tools_canvas_present, test_ai_usage_cases_canvas_present, test_ai_usage_section_hidden_when_section_visibility_false, test_velocity_section_hidden_when_section_visibility_false, test_filter_name_shown_when_present, test_project_key_shown_when_present, test_project_type_shown_in_header, test_estimation_type_shown_in_header, test_velocity_header_reflects_estimation_type_tickets, test_velocity_chart_y_axis_has_no_percent_suffix, test_velocity_table_values_have_no_percent_suffix, test_ai_usage_pie_chart_pct_labels_present |
| `tests/component/test_report_md.py` | test_report_md | — | test_file_created, test_title_present, test_date_present, test_sprint_name_present, test_velocity_value_present, test_no_velocity_data_message, test_bar_chart_present_when_velocity_nonzero, test_md_table_header_row, test_md_table_separator_row, test_md_table_data_row, test_md_report_ai_assistance_section_present, test_md_report_ai_assistance_shows_pct, test_md_report_ai_assistance_table_headers, test_md_report_ai_assistance_shows_label, test_md_report_ai_assistance_empty_data, test_md_report_ai_assistance_hidden_when_toggled_off, test_md_report_ai_usage_section_present, test_md_report_ai_usage_shows_count, test_md_report_ai_usage_tool_breakdown, test_md_report_ai_usage_action_breakdown, test_md_report_ai_usage_hidden_when_toggled_off, test_md_report_sprint_issues_section_present, test_md_report_sprint_issues_shows_issue_keys, test_md_report_sprint_issues_shows_ai_flag, test_md_report_sprint_issues_absent_when_no_data, test_md_report_sprint_issues_hidden_when_toggled_off, test_md_report_diagnostics_section_present, test_md_report_diagnostics_cycle_time_stats, test_md_report_diagnostics_no_cycle_time_message, test_md_report_diagnostics_jira_config, test_md_report_diagnostics_hidden_when_toggled_off, test_project_type_shown_in_md_header, test_estimation_type_shown_in_md_header, test_velocity_header_label_story_points, test_velocity_header_label_jira_tickets, test_velocity_section_hidden_when_section_visibility_false, test_dau_section_hidden_when_section_visibility_false |
| `tests/component/test_report_performance.py` | test_report_performance | — | test_report_generation_completes_within_time_limit |
| `tests/component/test_server.py` | test_server | — | test_get_root_returns_200, test_get_index_html_returns_200, test_get_unknown_returns_404, test_get_version_returns_ok_and_version, test_options_returns_204_with_cors, test_test_connection_missing_fields, test_test_connection_invalid_json, test_test_connection_valid_creds, test_test_connection_http_error, test_test_connection_empty_body, test_post_unknown_returns_404, test_generate_returns_sse_content_type, test_generate_ends_with_close_event, test_generate_passes_filter_jql_env_var, test_get_reports_returns_empty_list_when_no_reports, test_get_reports_returns_sorted_list, test_delete_report_removes_files_and_folder, test_delete_report_keeps_folder_when_other_files_remain, test_delete_report_returns_404_for_missing, test_delete_report_rejects_invalid_params, test_cert_status_no_cert_returns_exists_false, test_cert_status_with_valid_cert_returns_enriched_fields, test_cert_status_with_corrupt_cert_returns_error, test_fetch_cert_missing_url_returns_400, test_fetch_cert_invalid_url_returns_400, test_fetch_cert_unreachable_host_returns_error, test_fetch_cert_saves_full_ca_bundle, test_handle_error_swallows_connection_aborted_error, test_get_schemas_returns_list, test_get_schema_by_name, test_get_schema_not_found, isolated_schema_file, test_post_schema_missing_schema_key, test_post_schema_missing_name, test_post_schema_rejects_non_dict_fields, test_post_schema_rejects_invalid_status_mapping, test_post_schema_rejects_non_list_excluded_statuses, test_post_schema_accepts_excluded_statuses_list, test_post_schema_accepts_absent_excluded_statuses, test_post_schema_creates_new_entry, test_post_schema_updates_existing, test_post_schema_rename_collision_overwrites, test_delete_schema_no_name_returns_400, test_delete_default_schema_returns_400, test_delete_nonexistent_schema_returns_404, test_fetch_cert_saves_pem_without_crlf_line_endings, fake_popen |
| `tests/component/test_server_config.py` | test_server_config | TestWriteEnvFields, TestGetConfig, TestPostConfig, TestGetConfigExtended | temp_root, test_replaces_existing_key, test_uncomments_commented_key, test_appends_missing_key, test_creates_env_from_example_when_env_missing, test_example_file_is_not_modified, test_creates_env_from_scratch_when_both_absent, test_duplicate_key_only_first_occurrence_replaced, test_token_with_equals_in_value, test_crlf_file_does_not_crash, test_write_creates_newline_terminated_file, test_multiple_keys_written_in_one_call, test_preserves_other_credential_keys_when_updating_url, test_partial_update_preserves_untouched_key, test_preserves_unrelated_optional_env_vars, test_preserves_comment_lines_and_blanks, test_returns_configured_true_when_all_fields_set, test_token_always_masked_as_stars, test_partial_env_returns_configured_false, test_missing_env_file_returns_empty_config, test_commented_out_lines_not_returned, test_empty_value_not_included, test_optional_fields_included_when_present, test_line_without_equals_skipped, test_unknown_keys_not_included_in_response, test_get_config_returns_json_content_type, test_overwrites_existing_env_fields, test_creates_env_from_example_template, test_example_not_modified_after_create, test_star_token_not_overwritten, test_subset_of_keys_only_updates_those_keys, test_creates_env_from_scratch_when_both_absent, test_invalid_json_returns_400, test_empty_body_is_noop_and_returns_ok, test_round_trip_url_email_token, test_token_with_equals_sign_round_trip, test_post_config_route_exists, test_post_saves_filter_fields_to_env, test_post_ignores_ai_labels, test_post_saves_board_id_to_env, test_round_trip_all_fields, test_post_config_ignores_unknown_keys, test_ai_label_fields_never_returned, test_board_id_returned_when_present, test_board_id_absent_when_not_set, test_only_whitelisted_keys_returned |
| `tests/component/test_server_filters.py` | test_server_filters | — | restore_filters, test_get_filters_default_is_first, test_get_filters_always_includes_default_after_user_delete, test_delete_default_filter_returns_error, test_post_filter_creates_new_and_get_returns_it, test_post_filter_upserts_on_duplicate_name, test_delete_filter_removes_entry, test_delete_unknown_slug_returns_not_found, test_filter_persists_across_server_restart, test_post_filter_round_trip_preserves_schema_name, test_post_filter_round_trip_preserves_report_name, test_post_filter_report_name_defaults_to_filter_name |
| `tests/component/__init__.py` | __init__ | — | — |
| `tests/e2e/conftest.py` | conftest | ThreadedServer | pytest_collection_modifyitems, live_server_url, browser_type_launch_args, pytest_runtest_makereport, handle_error |
| `tests/e2e/test_dau_survey_ui.py` | test_dau_survey_ui | — | test_survey_page_loads_with_title, test_form_visible_and_confirmation_hidden_on_load, test_submit_button_initially_disabled, test_progress_starts_at_zero, test_progress_increments_with_each_field, test_username_valid_input_applies_valid_class, test_username_rejects_underscore, test_username_rejects_space, test_username_too_short_shows_error, test_submit_enabled_only_when_all_fields_are_valid, test_radio_card_click_marks_it_selected, test_radio_card_keyboard_navigation, test_submit_hides_form_and_shows_confirmation, test_confirmation_displays_submitted_data, test_submit_writes_valid_json_to_mocked_fs, test_submit_timestamp_format, test_survey_payload_has_no_week_field, test_username_saved_to_localstorage_after_submit, test_username_restored_from_localstorage_on_page_load, test_filename_matches_dau_username_timestamp_pattern, test_fs_api_abort_keeps_form_intact, test_fs_api_non_abort_error_falls_back_to_download, test_fs_api_unavailable_falls_back_to_download, test_new_survey_button_returns_to_form, test_new_survey_button_clears_role_and_usage_but_keeps_username |
| `tests/e2e/test_e2e_connection.py` | test_e2e_connection | — | test_required_star_visible_on_jira_url_label, test_required_star_visible_on_email_label, test_required_star_visible_on_token_label, test_save_button_disabled_on_load_with_empty_config, test_save_button_disabled_on_load_even_with_prefilled_config, test_fields_prepopulated_from_server_config, test_token_placeholder_updated_when_server_token_exists, test_fields_empty_when_config_not_configured, test_partial_config_populates_only_present_fields, test_badge_shows_connected_on_success, test_badge_shows_error_on_401, test_badge_shows_error_on_403, test_badge_shows_error_when_fields_empty, test_save_enabled_after_successful_test_connection, test_save_remains_disabled_after_failed_test_connection, test_save_disabled_after_editing_url_following_success, test_save_disabled_after_editing_email_following_success, test_save_disabled_after_editing_token_following_success, test_save_not_enabled_when_token_missing_despite_success, test_save_posts_correct_payload, test_save_shows_flash_confirmation, test_save_with_new_token_sends_real_token, test_save_with_server_token_sends_star_token, test_can_re_test_after_field_edit_to_re_enable_save, test_save_persists_values_to_localstorage, test_badge_neutral_on_initial_load, test_multiple_test_connection_attempts_last_result_wins, test_saved_credentials_prefill_on_reload, test_cert_badge_shows_no_certificate_when_no_cert, test_cert_badge_shows_valid_when_cert_valid, test_cert_badge_shows_expiring_soon, test_cert_badge_shows_expired_when_cert_invalid, test_cert_badge_shows_unreadable_on_error, test_fetch_cert_button_label_is_fetch_when_no_cert, test_fetch_cert_button_label_is_refresh_when_cert_valid, test_fetch_cert_requires_url_to_be_filled, test_fetch_cert_success_updates_badge, test_fetch_cert_failure_shows_error_in_log, test_btn_clear_cert_log_clears_log_output, test_positive_e2e_no_cert_is_acceptable_state, test_positive_e2e_fetch_cert_then_badge_shows_valid |
| `tests/e2e/test_e2e_filters.py` | test_e2e_filters | — | test_filter_name_prepopulated_on_empty_load, test_filter_name_not_overwritten_after_user_edit, test_filter_list_displayed_on_load, test_default_filter_has_no_remove_button, test_user_filter_has_remove_button, test_remove_filter_updates_list, test_filter_schema_dropdown_populated_on_load, test_filter_name_dropdown_lists_existing_filters, test_selecting_existing_filter_loads_form, test_new_filter_option_resets_form, test_save_sends_schema_from_filter_dropdown, test_filter_builder_schema_does_not_write_localstorage, test_save_disabled_when_default_filter_selected, test_loading_filter_with_project_opens_jql_builder, test_selecting_filter_loads_sprint_name_filter_active_sprint_and_count_cap |
| `tests/e2e/test_e2e_report_content.py` | test_e2e_report_content | — | sprint_metrics_report_url, test_report_renders_velocity_and_ai_metrics_for_sprint_filter |
| `tests/e2e/test_e2e_schema_ui.py` | test_e2e_schema_ui | — | test_schema_tab_visible_between_connection_and_filter, test_schema_load_into_editor_on_select, test_schema_save_round_trip, test_schema_delete_button_disabled_for_default, test_schema_invalid_json_shows_error, test_schema_setup_does_not_set_active_schema_for_filter |
| `tests/e2e/test_e2e_ui.py` | test_e2e_ui | — | test_page_loads_with_title, test_default_tab_is_generate, test_all_three_tabs_visible, test_click_connection_tab, test_click_filter_tab, test_keyboard_arrow_right_navigation, test_save_connection_valid_inputs, test_validation_error_empty_fields, test_validation_error_invalid_url, test_token_show_hide_toggle, test_test_connection_missing_fields, test_test_connection_unreachable_server, test_save_filter_missing_required_fields, test_save_filter_success, test_remove_filter, test_generate_without_filter_selected, test_generate_with_filter_sse_streaming, test_log_clear_button, test_cert_status_badge_no_cert, test_cert_status_badge_valid_cert, test_fetch_cert_button_success, test_project_type_radios_visible, test_estimation_type_radios_visible, test_metric_toggle_checkboxes_visible, test_project_type_persists_in_localstorage, test_estimation_type_persists_in_localstorage, test_metric_toggles_persist_in_localstorage, test_generate_button_disabled_when_all_metrics_unchecked, test_reports_list_links_only_html, test_dynamic_regions_have_aria_live, test_required_fields_have_aria_required, test_decorative_icons_have_aria_hidden |
| `tests/e2e/test_e2e_version.py` | test_e2e_version | — | test_index_header_shows_version_badge, test_index_version_badge_text_matches_semver, test_dau_survey_header_shows_version_badge, test_dau_survey_version_badge_text_matches_semver |
| `tests/e2e/test_positive_e2e_flow.py` | test_positive_e2e_flow | — | test_positive_end_to_end_flow |
| `tests/e2e/__init__.py` | __init__ | — | — |
| `tests/integration/conftest.py` | conftest | — | — |
| `tests/integration/test_cli_server.py` | test_cli_server | — | test_cli_clean_via_subprocess, test_cli_no_credentials_via_subprocess, test_server_health_check |
| `tests/integration/test_copilot_telemetry_stats.py` | test_copilot_telemetry_stats | — | test_generate_stats_writes_json_and_markdown, test_generate_stats_subprocess_smoke |
| `tests/integration/test_fetch_ssl_cert.py` | test_fetch_ssl_cert | — | test_fetch_cert_happy_path, test_fetch_cert_creates_certs_dir, test_fetch_cert_overwrites_existing, test_fetch_cert_parses_custom_port, test_fetch_cert_bundle_contains_certifi_cas, test_fetch_cert_exits_when_url_empty, test_fetch_cert_exits_when_hostname_unparseable, test_fetch_cert_exits_on_ssl_error, test_fetch_cert_exits_on_os_error, test_fetch_cert_subprocess_smoke |
| `tests/integration/test_integration.py` | test_integration | — | test_main_pipeline_success, test_main_pipeline_config_fail, test_main_clean_removes_reports, test_filter_metadata_in_html, test_server_test_connection_json_shape, test_server_generate_sse_format, test_main_pipeline_sprint_name_filter_with_active_and_count_cap, test_main_pipeline_sprint_filter_with_velocity_and_ai_metrics |
| `tests/integration/__init__.py` | __init__ | — | — |
| `tests/runners/run_all_checks.py` | run_all_checks | Stage | main |
| `tests/runners/run_performance_tests.py` | run_performance_tests | — | main |
| `tests/runners/run_security_checks.py` | run_security_checks | — | main |
| `tests/tools/agent_review_prep.py` | agent_review_prep | — | main |
| `tests/tools/complexity_report.py` | complexity_report | — | collect_raw_loc, collect_cc, collect_mi, collect_dependencies, extract_test_count, build_refactor_signals, render_report, main |
| `tests/tools/coverage_gap_audit.py` | coverage_gap_audit | TestFileInfo, ModuleCoverage | discover_source_modules, module_key, module_stem_variants, analyze_test_files, build_coverage_matrix, collect_requirement_gaps, build_extension_plan, print_matrix, print_req_gaps, build_markdown_report, main, covered_at, gap_layers, gap_score, coverage_summary |
| `tests/tools/doc_sync_check.py` | doc_sync_check | — | main |
| `tests/tools/feature_screenshot_audit.py` | feature_screenshot_audit | — | main |
| `tests/tools/requirements_map.py` | requirements_map | — | — |
| `tests/tools/requirements_status.py` | requirements_status | FileStats | main, total |
| `tests/tools/smoke_test_setup.py` | smoke_test_setup | — | test_creates_env_when_missing, test_keeps_existing_env_by_default, test_backs_up_and_recreates_existing_env, test_invalid_choice_defaults_to_keep, test_missing_template_warns_and_skips_creation, test_keep_flag_skips_prompt_and_preserves_env, test_refresh_flag_backs_up_and_recreates_env, test_conflicting_env_flags_fail_fast, main |
| `tests/tools/test_coverage.py` | test_coverage | — | count_tests_in_file, collect_stats, build_pyramid, update_md, print_report, print_requirements_report, collect_requirements_stats, build_requirements_summary, build_coverage_detail, write_detail_files, main |
| `tests/unit/conftest.py` | conftest | — | mock_jira |
| `tests/unit/test_cert_handlers.py` | test_cert_handlers | — | test_get_windows_ca_certs_returns_empty_on_non_windows, test_get_windows_ca_certs_returns_empty_on_enum_certificates_error, test_get_windows_ca_certs_returns_pem_list_on_windows, test_get_windows_ca_certs_mocked_returns_pem_strings |
| `tests/unit/test_cert_validation.py` | test_cert_validation | — | test_validate_cert_valid_future, test_validate_cert_expired, test_validate_cert_expiring_soon, test_validate_cert_missing_file, test_validate_cert_corrupt_file |
| `tests/unit/test_cli.py` | test_cli | — | test_main_returns_1_when_config_invalid, test_main_returns_1_when_fetch_sprint_data_fails, test_main_returns_1_when_jira_client_error_raised, test_main_keeps_running_when_filter_name_lookup_fails, test_main_generates_reports_in_parallel |
| `tests/unit/test_complexity_audit.py` | test_complexity_audit | — | test_discover_modules_returns_only_py_files, test_discover_modules_excludes_excluded_dirs, test_discover_modules_empty_dir_returns_empty, test_score_simple_module_is_low, test_score_complex_module_has_higher_coupling_and_cohesion, test_score_syntax_error_source_returns_error_classification, test_build_report_module_count_matches_files_created, test_build_report_scores_sorted_high_before_low, test_build_report_summary_counts_sum_to_module_count, test_high_module_generates_at_least_one_recommendation, test_low_module_generates_no_recommendations, test_high_module_classification_and_recommendation_count, test_generate_complexity_md_creates_file_with_header, test_generate_complexity_md_contains_improvement_plan_section, test_generate_complexity_md_no_recs_shows_empty_message |
| `tests/unit/test_config.py` | test_config | — | test_validate_config_all_set, test_validate_config_missing_url, test_validate_config_missing_email, test_validate_config_missing_token, test_validate_config_all_missing, test_board_id_numeric, test_board_id_non_numeric, test_sprint_count_default, test_sprint_count_custom, test_filter_id_numeric, test_filter_id_empty, test_env_path_points_to_project_root, test_jira_ssl_cert_returns_true_when_no_file, test_jira_ssl_cert_returns_path_when_file_exists, test_jira_url_trailing_slash_stripped, test_jira_url_multiple_trailing_slashes_stripped, test_jira_url_no_trailing_slash_unchanged, test_jira_url_empty_string_safe, test_validate_config_warns_trailing_slash, test_ai_assisted_label_default, test_ai_assisted_label_custom, test_ai_exclude_labels_empty, test_ai_exclude_labels_parsed, test_ai_tool_labels_parsed, test_ai_action_labels_parsed, test_jira_schema_name_default, test_jira_schema_name_custom, test_project_type_default_scrum, test_project_type_kanban, test_project_type_invalid_falls_back, test_jira_filter_jql_default_empty, test_jira_filter_jql_from_env, test_estimation_type_default_story_points, test_estimation_type_jira_tickets, test_estimation_type_invalid_falls_back, test_env_bool_values, test_metric_toggles_default_true, test_dau_path_env_var_drives_responses_dir, test_dau_path_env_var_drives_normalized_dir, test_dau_path_absolute_env_var_used_verbatim, test_dau_responses_dir_env_overrides_dau_path, test_dau_normalized_dir_env_overrides_dau_path, test_dau_path_falls_back_to_default_filter_when_env_unset, test_metric_toggles_explicit_false |
| `tests/unit/test_copilot_customization_assets.py` | test_copilot_customization_assets | — | test_hook_detects_claude_owned_windows_path, test_hook_warns_on_heavy_docs_without_summary, test_hook_allows_heavy_docs_when_summary_is_present, test_hook_collects_nested_candidates, test_summaries_reference_existing_sources, test_summaries_stay_smaller_than_sources |
| `tests/unit/test_dau_metrics.py` | test_dau_metrics | — | test_empty_dir_returns_zero_count, test_missing_dir_returns_zero_count, test_three_response_files_counted, test_non_dau_files_are_ignored, test_mixed_scores_correct_avg, test_all_not_used_avg_is_zero, test_unknown_usage_falls_back_to_zero, test_by_role_sorted_alphabetically, test_by_role_correct_avg_and_count, test_breakdown_sorted_descending_by_count, test_malformed_json_file_is_skipped, test_build_metrics_dict_includes_dau_key, test_dau_responses_dir_env_var_overrides_default, test_load_dau_records_returns_list, test_load_dau_records_skips_malformed, test_load_dau_records_empty_dir, test_load_dau_records_reads_from_subdirectory, test_compute_dau_metrics_subdirectory_files, test_compute_dau_trend_subdirectory_files, test_dedup_keeps_latest_per_user_week, test_dedup_different_weeks_kept_separate, test_dedup_empty_list, test_compute_dau_trend_single_week, test_compute_dau_trend_multiple_weeks_sorted, test_compute_dau_trend_empty_dir, test_compute_dau_trend_dedup_applied, test_compute_dau_metrics_dedup_applied, test_load_dau_records_derives_week_from_timestamp, test_load_dau_records_preserves_existing_week, test_compute_dau_metrics_team_avg, test_compute_dau_metrics_no_data, test_compute_dau_metrics_team_avg_pct, test_compute_dau_trend_team_avg_pct |
| `tests/unit/test_dau_normalizer.py` | test_dau_normalizer | — | test_derive_iso_week_monday, test_derive_iso_week_sunday, test_derive_iso_week_week_boundary, test_derive_iso_week_zulu_suffix, test_compact_timestamp_format, test_compact_timestamp_midnight, test_empty_raw_dir_creates_normalized_dir_and_returns_zero, test_creates_normalized_dir_if_missing, test_single_file_without_week_gets_week_derived, test_single_file_with_existing_week_keeps_it, test_dedup_keeps_latest_per_user_week, test_dedup_different_weeks_both_kept, test_dedup_different_users_same_week_both_kept, test_stale_normalized_files_cleared_on_rerun, test_malformed_json_skipped_no_exception, test_non_dau_files_ignored, test_output_filename_format, test_nested_folders_are_traversed, test_nested_folder_structure_mirrored, test_dedup_per_directory_independent, test_stale_nested_normalized_files_cleared_on_rerun |
| `tests/unit/test_exceptions.py` | test_exceptions | — | test_app_error_is_exception, test_domain_errors_are_app_error_subclasses, test_jira_subclasses_are_jira_client_error, test_jira_subclasses_caught_by_parent, test_domain_errors_caught_by_app_error, test_schema_error_preserves_cause |
| `tests/unit/test_filter_handlers.py` | test_filter_handlers | _FakeProc | test_default_filter_entry_is_present_and_correct, test_load_filters_creates_file_when_missing, test_load_filters_injects_default_when_absent_from_file, test_delete_default_filter_is_blocked, test_delete_unknown_slug_returns_not_found, test_post_filter_rejects_blank_project_and_filter_id, test_post_filter_accepts_filter_id_without_project, test_post_filter_creates_new_entry, test_post_filter_updates_existing_entry, test_build_jql_from_params, test_build_jql_status_always_done, test_post_filter_uses_schema_team_jql_field, test_filter_data_persists_across_loads, test_default_filter_carries_dau_path, test_post_filter_defaults_dau_path_from_slug, test_post_filter_creates_dau_original_folder_with_gitkeep, test_post_filter_normalises_backslashes_in_dau_path, test_delete_filter_does_not_remove_dau_data, test_generate_applies_filter_params_to_subprocess_env, wait |
| `tests/unit/test_imports.py` | test_imports | — | test_import_app_config, test_import_app_metrics, test_import_app_report_md, test_import_app_report_html, test_import_app_jira_client, test_import_app_cert_utils, test_import_app_logging_setup, test_main_imports_resolve |
| `tests/unit/test_jira_client.py` | test_jira_client | — | test_create_client_returns_jira_instance, test_create_client_uses_config_values, test_create_client_passes_verify_ssl, test_get_board_id_from_config, test_get_board_id_raises_when_not_configured, test_get_sprints_sorted_desc_by_start_date, test_get_sprints_capped_at_sprint_count, test_get_sprints_empty, test_get_sprints_returns_newest_when_paginated, test_get_sprints_excludes_active_when_closed_only, test_get_sprints_includes_active_when_closed_only_false, test_get_sprints_active_sprint_comes_first, test_get_sprints_filtered_by_name_substring, test_get_sprints_name_filter_case_insensitive, test_get_sprints_empty_name_filter_returns_all, test_get_sprints_name_filter_and_count_cap_combined, test_get_sprints_count_cap_is_applied_after_name_filter, test_get_sprints_name_filter_with_count_returns_newest_not_oldest, test_get_sprints_name_filter_active_sprint_and_count_cap, test_get_filter_jql_none, test_get_filter_jql_valid, test_get_filter_jql_api_error, test_get_filter_jql_strips_trailing_order_by, test_get_filter_jql_strips_order_by_case_insensitive, test_get_filter_jql_no_order_by_unchanged, test_get_issues_for_sprint_single_page, test_get_issues_for_sprint_pagination, test_get_issues_for_sprint_empty, test_fetch_kanban_data_jql_uses_updated_not_resolutiondate, test_fetch_kanban_data_groups_issues_by_updated_date, test_fetch_kanban_data_prefers_resolutiondate_over_updated, test_fetch_kanban_data_closed_sprints_only_excludes_current_week, test_fetch_kanban_data_open_sprints_includes_current_week, test_fetch_kanban_data_uses_config_filter_jql_as_fallback, test_fetch_kanban_data_strips_order_by_from_local_filter_jql, test_fetch_kanban_data_filter_id_jql_takes_precedence_over_config_jql, test_fetch_sprint_data_orchestration, test_fetch_sprint_data_passes_filter_jql_to_each_sprint, test_fetch_sprint_data_skips_sprints_without_id, test_create_client_url_kwarg_matches_config_exactly, test_create_client_no_credentials_in_url_kwarg, test_create_client_credentials_in_auth_kwargs_only, test_create_client_passes_timeout, test_sanitise_error_replaces_url, test_sanitise_error_replaces_email_and_token, test_sanitise_error_handles_none_config_values |
| `tests/unit/test_logging_setup.py` | test_logging_setup | — | clean_root_logger, test_success_level_value, test_success_level_name_registered, test_logger_has_success_method, test_setup_logging_returns_logger_and_path, test_setup_logging_creates_log_file, test_setup_logging_log_filename_matches_pattern, test_setup_logging_creates_log_directory, test_setup_logging_default_level_is_debug, test_setup_logging_level_configurable_via_env, test_setup_logging_unknown_level_falls_back_to_debug, test_setup_logging_attaches_file_handler, test_setup_logging_attaches_stream_handler, test_log_file_format, test_success_level_message_written_to_file, test_credentials_not_in_log_output |
| `tests/unit/test_main_helpers.py` | test_main_helpers | — | test_timestamp_folder_name_valid_iso, test_timestamp_folder_name_empty_string, test_timestamp_folder_name_none, test_parse_args_no_args, test_parse_args_clean_flag |
| `tests/unit/test_metrics.py` | test_metrics | — | test_is_done, test_is_done_missing_fields, test_is_done_resolutiondate_fallback, test_is_done_no_resolutiondate_custom_status, test_is_excluded, test_is_excluded_resolutiondate_does_not_override, test_is_excluded_missing_fields, test_compute_velocity_kanban_periods, test_get_story_points_numeric_float, test_get_story_points_integer_stored_as_int, test_get_story_points_none, test_get_story_points_non_numeric_string, test_get_story_points_missing_field, test_get_story_points_custom_field, test_get_story_points_nested_value_dict, test_compute_velocity_all_done, test_compute_velocity_mixed_statuses, test_compute_velocity_no_issues, test_compute_velocity_missing_sprint_id, test_compute_velocity_sprint_absent_from_issues_dict, test_compute_velocity_rounding, test_compute_velocity_preserves_sprint_name, test_compute_velocity_excluded_statuses, test_compute_velocity_no_excluded_statuses_backward_compat, test_build_metrics_dict_keys, test_build_metrics_dict_report_name_defaults_to_none, test_build_metrics_dict_generated_at_is_iso, test_parse_iso, test_get_labels_normal, test_get_labels_empty_list, test_get_labels_missing_key, test_get_labels_missing_fields, test_ai_trend_ai_labeled_done_issues, test_ai_trend_no_done_issues, test_ai_trend_exclude_labels, test_ai_trend_multiple_sprints, test_ai_trend_no_ai_label, test_ai_trend_jira_tickets_mode_counts_issues_not_story_points, test_ai_trend_fallback_uses_tool_labels_when_assisted_label_empty, test_ai_trend_excluded_statuses, test_ai_trend_fallback_uses_action_labels_when_assisted_label_empty, test_ai_trend_fallback_no_labels_yields_zero, test_ai_trend_explicit_label_overrides_fallback, test_ai_usage_tool_breakdown, test_ai_usage_action_breakdown, test_ai_usage_dedup_across_sprints, test_ai_usage_no_ai_issues, test_ai_usage_empty_labels, test_ai_usage_fallback_uses_tool_or_action_labels, test_ai_usage_explicit_label_overrides_fallback, test_get_story_points_with_custom_field, test_get_story_points_custom_field_missing, test_is_done_with_custom_statuses, test_is_done_custom_statuses_case_insensitive, test_compute_velocity_custom_field_and_statuses, test_build_metrics_dict_with_schema, test_build_metrics_dict_without_schema_backward_compat, test_build_metrics_dict_jira_tickets_velocity_uses_issue_count, test_build_metrics_dict_story_points_velocity_unchanged, test_dedup_basic_issue_kept_in_last_sprint, test_dedup_three_sprints_kept_in_last, test_dedup_no_duplicates_unchanged, test_dedup_kanban_string_sprint_ids, test_dedup_kanban_keeps_issues_with_sprint_field, test_dedup_issue_without_key_not_moved, test_dedup_mixed_unique_and_duplicate, test_dedup_newest_first_input_still_keeps_issue_in_most_recent, test_dedup_drops_issue_owned_by_active_sprint_outside_fetch, test_dedup_keeps_issue_in_active_sprint_when_fetched, test_dedup_attributes_to_latest_sprint_field_id_not_jira_membership, test_dedup_falls_back_when_sprint_field_missing, test_velocity_excludes_ticket_carried_to_unfetched_active_sprint, test_velocity_row_start_end_date_are_iso_or_none, test_velocity_row_sprint_id_matches_input, test_compute_ai_trend_basic, test_ai_trend_all_done_ai_assisted, test_ai_trend_basic_percentage, test_ai_usage_details_tool_breakdown_pct, test_ai_usage_details_action_breakdown_pct, test_cycle_time_fields_are_absolute_days, test_sprint_issue_details_basic_shape, test_sprint_issue_details_issue_fields, test_sprint_issue_details_excludes_non_done, test_sprint_issue_details_excluded_flag, test_sprint_issue_details_ai_flag_independent_of_exclusion, test_sprint_issue_details_multiple_sprints, test_sprint_issue_details_empty_sprint, test_build_metrics_dict_sprint_issue_details_key_present, test_build_metrics_dict_sprint_issue_details_issue_shape |
| `tests/unit/test_schema.py` | test_schema | — | test_load_schemas_returns_list_from_file, test_load_schemas_missing_file, test_resolve_schema_path_prefers_user_data_dir, test_resolve_schema_path_falls_back_to_project_root, test_load_schemas_invalid_json, test_get_schema_found, test_get_schema_not_found, test_get_active_schema_by_name, test_get_active_schema_falls_back_to_default, test_get_active_schema_no_file_returns_hardcoded_default, test_get_active_schema_hardcoded_uses_builtin_story_points, test_save_schema_creates_file, test_save_schema_updates_existing, test_save_schema_appends_new, test_delete_schema_removes_entry, test_delete_schema_refuses_default, test_delete_schema_not_found, test_get_field_id, test_get_field_jql_name_with_explicit_jql_name, test_get_field_jql_name_falls_back_to_id, test_get_done_statuses, test_get_done_statuses_defaults, test_get_in_progress_statuses, test_get_in_progress_statuses_defaults, test_build_schema_from_fields_detects_sprint, test_build_schema_from_fields_detects_story_points_by_name, test_build_schema_from_fields_preserves_defaults_for_missing, test_build_schema_from_fields_preserves_team_jql_name, test_build_schema_from_fields_detects_story_points_by_float_type, test_build_schema_from_fields_disambiguates_float_fields_by_name, test_build_schema_from_fields_uses_populated_fields_for_disambiguation, test_build_schema_from_fields_populated_fields_breaks_equal_name_score, test_build_schema_from_fields_applies_board_statuses, test_build_schema_from_fields_partial_board_statuses_only_done, test_build_schema_from_fields_none_board_statuses_uses_defaults, test_build_schema_from_fields_tolerates_null_and_incomplete_entries, test_get_active_schema_named_fallback_uses_default |
| `tests/unit/test_server_handlers.py` | test_server_handlers | _FakeProc, _FakeProc, _FakeProc, _FakeProc, _FakeProc | test_slugify_returns_safe_filename, test_read_env_credentials_reads_values_from_env_file, test_resolve_report_path_allows_files_under_reports, test_resolve_report_path_rejects_path_traversal, test_post_schema_requires_schema_key, test_post_schema_requires_schema_name, test_post_schema_requires_dict_fields, test_post_schema_requires_status_mapping_lists, test_post_schema_inserts_new_entry, test_post_schema_updates_existing_entry, test_handle_generate_emits_error_event_for_nonzero_exit, test_handle_generate_emits_error_when_main_file_missing, test_post_filter_saves_report_name, test_post_filter_report_name_defaults_to_filter_name, test_generate_exports_filter_schema_name_to_subprocess, test_generate_exports_report_name_to_subprocess, test_generate_uses_stored_report_name_when_no_param, test_generate_empty_sprint_name_filter_overrides_defaults, test_post_filter_normalizes_missing_param_keys, test_handle_test_connection_returns_user_details_on_success, test_handle_test_connection_uses_custom_ssl_context, test_run_defaults_host_to_loopback, test_client_disconnect_tuple_includes_all_error_types, test_serve_file_catches_client_disconnect, test_handle_cert_status_returns_validity_fields_for_valid_cert, test_handle_cert_status_returns_error_key_when_cert_unreadable, wait, wait, wait, wait, wait |
| `tests/unit/test_user_data.py` | test_user_data | — | test_ensure_user_data_dirs_creates_data_dau, test_ensure_user_data_dirs_creates_all_subdirs, test_user_data_dir_uses_localappdata |
| `tests/unit/test_version.py` | test_version | — | test_version_is_not_unknown, test_version_matches_semver, test_version_matches_pyproject_toml, test_pyproject_toml_fallback_uses_file_relative_path |
| `tests/unit/__init__.py` | __init__ | — | — |
| `tools/agents/changelog_prep.py` | changelog_prep | — | get_last_tag, get_commits_since, categorize, format_entry, main |
| `tools/agents/check_req_status.py` | check_req_status | — | parse_status_counts, extract_unmet_rows, report_file, main |
| `tools/agents/doc_drift.py` | doc_drift | — | extract_module_map, main |
| `tools/agents/ux_spec_scaffold.py` | ux_spec_scaffold | — | main |

## Layer Map

```
main.py ← main
server.py ← server
app/cli.py ← cli
app/exceptions.py ← exceptions
app/__init__.py ← __init__
tests/conftest.py ← conftest
tests/__init__.py ← __init__
tools/claude_session_stats.py ← claude_session_stats
tools/copilot_session_stats.py ← copilot_session_stats
tools/copilot_telemetry_stats.py ← copilot_telemetry_stats
tools/docs_audit.py ← docs_audit
tools/fetch_ssl_cert.py ← fetch_ssl_cert
tools/new_adr.py ← new_adr
tools/take_screenshots.py ← take_screenshots
tools/_diag_cert_ui.py ← _diag_cert_ui
.claude/tools/claude_session_stats.py ← claude_session_stats
.github/hooks/pre_tool_copilot_boundary.py ← pre_tool_copilot_boundary
app/core/complexity_audit.py ← complexity_audit
app/core/config.py ← config
app/core/dau_importer.py ← dau_importer
app/core/dau_normalizer.py ← dau_normalizer
app/core/jira_client.py ← jira_client
app/core/metrics.py ← metrics
app/core/migration.py ← migration
app/core/schema.py ← schema
app/core/user_data.py ← user_data
app/core/__init__.py ← __init__
app/reporters/report_complexity_html.py ← report_complexity_html
app/reporters/report_complexity_md.py ← report_complexity_md
app/reporters/report_html.py ← report_html
app/reporters/report_md.py ← report_md
app/reporters/__init__.py ← __init__
app/server/cert_handlers.py ← cert_handlers
app/server/complexity_handlers.py ← complexity_handlers
app/server/config_handlers.py ← config_handlers
app/server/connection_handlers.py ← connection_handlers
app/server/data_handlers.py ← data_handlers
app/server/dau_handlers.py ← dau_handlers
app/server/filter_handlers.py ← filter_handlers
app/server/generate_handlers.py ← generate_handlers
app/server/schema_handlers.py ← schema_handlers
app/server/_base.py ← _base
app/server/__init__.py ← __init__
app/utils/cert_utils.py ← cert_utils
app/utils/logging_setup.py ← logging_setup
app/utils/__init__.py ← __init__
tests/component/conftest.py ← conftest
tests/component/test_complexity_api.py ← test_complexity_api
tests/component/test_complexity_cli.py ← test_complexity_cli
tests/component/test_contracts.py ← test_contracts
tests/component/test_cross_section_chart_labels.py ← test_cross_section_chart_labels
tests/component/test_dau_report.py ← test_dau_report
tests/component/test_release_zip.py ← test_release_zip
tests/component/test_report_html.py ← test_report_html
tests/component/test_report_md.py ← test_report_md
tests/component/test_report_performance.py ← test_report_performance
tests/component/test_server.py ← test_server
tests/component/test_server_config.py ← test_server_config
tests/component/test_server_filters.py ← test_server_filters
tests/component/__init__.py ← __init__
tests/e2e/conftest.py ← conftest
tests/e2e/test_dau_survey_ui.py ← test_dau_survey_ui
tests/e2e/test_e2e_connection.py ← test_e2e_connection
tests/e2e/test_e2e_filters.py ← test_e2e_filters
tests/e2e/test_e2e_report_content.py ← test_e2e_report_content
tests/e2e/test_e2e_schema_ui.py ← test_e2e_schema_ui
tests/e2e/test_e2e_ui.py ← test_e2e_ui
tests/e2e/test_e2e_version.py ← test_e2e_version
tests/e2e/test_positive_e2e_flow.py ← test_positive_e2e_flow
tests/e2e/__init__.py ← __init__
tests/integration/conftest.py ← conftest
tests/integration/test_cli_server.py ← test_cli_server
tests/integration/test_copilot_telemetry_stats.py ← test_copilot_telemetry_stats
tests/integration/test_fetch_ssl_cert.py ← test_fetch_ssl_cert
tests/integration/test_integration.py ← test_integration
tests/integration/__init__.py ← __init__
tests/runners/run_all_checks.py ← run_all_checks
tests/runners/run_performance_tests.py ← run_performance_tests
tests/runners/run_security_checks.py ← run_security_checks
tests/tools/agent_review_prep.py ← agent_review_prep
tests/tools/complexity_report.py ← complexity_report
tests/tools/coverage_gap_audit.py ← coverage_gap_audit
tests/tools/doc_sync_check.py ← doc_sync_check
tests/tools/feature_screenshot_audit.py ← feature_screenshot_audit
tests/tools/requirements_map.py ← requirements_map
tests/tools/requirements_status.py ← requirements_status
tests/tools/smoke_test_setup.py ← smoke_test_setup
tests/tools/test_coverage.py ← test_coverage
tests/unit/conftest.py ← conftest
tests/unit/test_cert_handlers.py ← test_cert_handlers
tests/unit/test_cert_validation.py ← test_cert_validation
tests/unit/test_cli.py ← test_cli
tests/unit/test_complexity_audit.py ← test_complexity_audit
tests/unit/test_config.py ← test_config
tests/unit/test_copilot_customization_assets.py ← test_copilot_customization_assets
tests/unit/test_dau_metrics.py ← test_dau_metrics
tests/unit/test_dau_normalizer.py ← test_dau_normalizer
tests/unit/test_exceptions.py ← test_exceptions
tests/unit/test_filter_handlers.py ← test_filter_handlers
tests/unit/test_imports.py ← test_imports
tests/unit/test_jira_client.py ← test_jira_client
tests/unit/test_logging_setup.py ← test_logging_setup
tests/unit/test_main_helpers.py ← test_main_helpers
tests/unit/test_metrics.py ← test_metrics
tests/unit/test_schema.py ← test_schema
tests/unit/test_server_handlers.py ← test_server_handlers
tests/unit/test_user_data.py ← test_user_data
tests/unit/test_version.py ← test_version
tests/unit/__init__.py ← __init__
tools/agents/changelog_prep.py ← changelog_prep
tools/agents/check_req_status.py ← check_req_status
tools/agents/doc_drift.py ← doc_drift
tools/agents/ux_spec_scaffold.py ← ux_spec_scaffold
```


## Test Pyramid

```
tests/component/test_complexity_api.py ← component (4 tests)
tests/component/test_complexity_cli.py ← component (4 tests)
tests/component/test_contracts.py ← component (11 tests)
tests/component/test_cross_section_chart_labels.py ← component (13 tests)
tests/component/test_dau_report.py ← component (15 tests)
tests/component/test_release_zip.py ← component (11 tests)
tests/component/test_report_html.py ← component (31 tests)
tests/component/test_report_md.py ← component (37 tests)
tests/component/test_report_performance.py ← component (1 tests)
tests/component/test_server.py ← component (45 tests)
tests/component/test_server_config.py ← component (45 tests)
tests/component/test_server_filters.py ← component (11 tests)
tests/e2e/test_dau_survey_ui.py ← e2e (25 tests)
tests/e2e/test_e2e_connection.py ← e2e (41 tests)
tests/e2e/test_e2e_filters.py ← e2e (15 tests)
tests/e2e/test_e2e_report_content.py ← e2e (1 tests)
tests/e2e/test_e2e_schema_ui.py ← e2e (6 tests)
tests/e2e/test_e2e_ui.py ← e2e (32 tests)
tests/e2e/test_e2e_version.py ← e2e (4 tests)
tests/e2e/test_positive_e2e_flow.py ← e2e (1 tests)
tests/integration/test_cli_server.py ← integration (3 tests)
tests/integration/test_copilot_telemetry_stats.py ← integration (2 tests)
tests/integration/test_fetch_ssl_cert.py ← integration (10 tests)
tests/integration/test_integration.py ← integration (8 tests)
tests/unit/test_cert_handlers.py ← unit (4 tests)
tests/unit/test_cert_validation.py ← unit (5 tests)
tests/unit/test_cli.py ← unit (5 tests)
tests/unit/test_complexity_audit.py ← unit (15 tests)
tests/unit/test_config.py ← unit (44 tests)
tests/unit/test_copilot_customization_assets.py ← unit (6 tests)
tests/unit/test_dau_metrics.py ← unit (33 tests)
tests/unit/test_dau_normalizer.py ← unit (21 tests)
tests/unit/test_exceptions.py ← unit (6 tests)
tests/unit/test_filter_handlers.py ← unit (19 tests)
tests/unit/test_imports.py ← unit (8 tests)
tests/unit/test_jira_client.py ← unit (46 tests)
tests/unit/test_logging_setup.py ← unit (15 tests)
tests/unit/test_main_helpers.py ← unit (5 tests)
tests/unit/test_metrics.py ← unit (89 tests)
tests/unit/test_schema.py ← unit (37 tests)
tests/unit/test_server_handlers.py ← unit (26 tests)
tests/unit/test_user_data.py ← unit (3 tests)
tests/unit/test_version.py ← unit (4 tests)
```

| Layer | Count |
|-------|-------|
| `component` | 228 |
| `e2e` | 125 |
| `integration` | 23 |
| `unit` | 391 |

## Config Surface

| Name | Default | Source |
|------|---------|--------|
| `VSCODE_TARGET_SESSION_LOG` | `` | `env` |
| `VSCODE_TARGET_SESSION_LOG` | `` | `env` |
| `JIRA_URL` | `` | `env` |
| `NEXUS_DEBUG_DIR` | `generated/debug` | `env` |
| `NEXUS_DEBUG_DIR` | `generated/debug` | `env` |
| `NEXUS_DEBUG_DIR` | `generated/debug` | `env` |
| `JIRA_EMAIL` | `` | `env` |
| `JIRA_API_TOKEN` | `` | `env` |
| `DAU_RESPONSES_DIR` | `` | `env` |
| `DAU_NORMALIZED_DIR` | `` | `env` |
| `JIRA_URL` | `` | `env` |
| `JIRA_URL` | `` | `env` |
| `JIRA_BOARD_ID` | `` | `env` |
| `JIRA_SPRINT_COUNT` | `10` | `env` |
| `JIRA_SPRINT_NAME_FILTER` | `` | `env` |
| `JIRA_FILTER_ID` | `` | `env` |
| `JIRA_ISSUE_TYPES` | `` | `env` |
| `AI_ASSISTED_LABEL` | `` | `env` |
| `JIRA_FILTER_JQL` | `` | `env` |
| `ESTIMATION_TYPE` | `StoryPoints` | `env` |
| `REPORT_NAME` | `` | `env` |
| `PORT` | `8080` | `env` |
| `COMPLEXITY_MEDIUM_THRESHOLD` | `3.5` | `env` |
| `COMPLEXITY_HIGH_THRESHOLD` | `7.0` | `env` |
| `JIRA_SCHEMA_NAME` | `` | `env` |
| `JIRA_PROJECT` | `` | `env` |
| `DAU_PATH` | `` | `env` |
| `AI_EXCLUDE_LABELS` | `` | `env` |
| `AI_TOOL_LABELS` | `` | `env` |
| `AI_ACTION_LABELS` | `` | `env` |
| `PROJECT_TYPE` | `SCRUM` | `env` |
| `LOCALAPPDATA` | `` | `env` |
| `JIRA_URL` | `` | `env` |
| `HOST` | `127.0.0.1` | `env` |
| `APP_PROFILE` | `` | `env` |
| `LOG_LEVEL` | `` | `env` |
| `PATH` | `` | `env` |
| `SYSTEMROOT` | `` | `env` |

## Key Dependencies

- `atlassian-python-api`
- `cryptography`
- `python-dotenv`
- `pandas`
- `jinja2`
- `requests`
- `openpyxl`
- `radon`

## Module Ownership (single responsibility)

- `main.py` — main
- `server.py` — server
- `app/cli.py` — cli
- `app/exceptions.py` — exceptions
- `app/__init__.py` — __init__
- `tests/conftest.py` — conftest
- `tests/__init__.py` — __init__
- `tools/claude_session_stats.py` — claude_session_stats
- `tools/copilot_session_stats.py` — copilot_session_stats
- `tools/copilot_telemetry_stats.py` — copilot_telemetry_stats
- `tools/docs_audit.py` — docs_audit
- `tools/fetch_ssl_cert.py` — fetch_ssl_cert
- `tools/new_adr.py` — new_adr
- `tools/take_screenshots.py` — take_screenshots
- `tools/_diag_cert_ui.py` — _diag_cert_ui
- `.claude/tools/claude_session_stats.py` — claude_session_stats
- `.github/hooks/pre_tool_copilot_boundary.py` — pre_tool_copilot_boundary
- `app/core/complexity_audit.py` — complexity_audit
- `app/core/config.py` — config
- `app/core/dau_importer.py` — dau_importer
- `app/core/dau_normalizer.py` — dau_normalizer
- `app/core/jira_client.py` — jira_client
- `app/core/metrics.py` — metrics
- `app/core/migration.py` — migration
- `app/core/schema.py` — schema
- `app/core/user_data.py` — user_data
- `app/core/__init__.py` — __init__
- `app/reporters/report_complexity_html.py` — report_complexity_html
- `app/reporters/report_complexity_md.py` — report_complexity_md
- `app/reporters/report_html.py` — report_html
- `app/reporters/report_md.py` — report_md
- `app/reporters/__init__.py` — __init__
- `app/server/cert_handlers.py` — cert_handlers
- `app/server/complexity_handlers.py` — complexity_handlers
- `app/server/config_handlers.py` — config_handlers
- `app/server/connection_handlers.py` — connection_handlers
- `app/server/data_handlers.py` — data_handlers
- `app/server/dau_handlers.py` — dau_handlers
- `app/server/filter_handlers.py` — filter_handlers
- `app/server/generate_handlers.py` — generate_handlers
- `app/server/schema_handlers.py` — schema_handlers
- `app/server/_base.py` — _base
- `app/server/__init__.py` — __init__
- `app/utils/cert_utils.py` — cert_utils
- `app/utils/logging_setup.py` — logging_setup
- `app/utils/__init__.py` — __init__
- `tests/component/conftest.py` — conftest
- `tests/component/test_complexity_api.py` — test_complexity_api
- `tests/component/test_complexity_cli.py` — test_complexity_cli
- `tests/component/test_contracts.py` — test_contracts
- `tests/component/test_cross_section_chart_labels.py` — test_cross_section_chart_labels
- `tests/component/test_dau_report.py` — test_dau_report
- `tests/component/test_release_zip.py` — test_release_zip
- `tests/component/test_report_html.py` — test_report_html
- `tests/component/test_report_md.py` — test_report_md
- `tests/component/test_report_performance.py` — test_report_performance
- `tests/component/test_server.py` — test_server
- `tests/component/test_server_config.py` — test_server_config
- `tests/component/test_server_filters.py` — test_server_filters
- `tests/component/__init__.py` — __init__
- `tests/e2e/conftest.py` — conftest
- `tests/e2e/test_dau_survey_ui.py` — test_dau_survey_ui
- `tests/e2e/test_e2e_connection.py` — test_e2e_connection
- `tests/e2e/test_e2e_filters.py` — test_e2e_filters
- `tests/e2e/test_e2e_report_content.py` — test_e2e_report_content
- `tests/e2e/test_e2e_schema_ui.py` — test_e2e_schema_ui
- `tests/e2e/test_e2e_ui.py` — test_e2e_ui
- `tests/e2e/test_e2e_version.py` — test_e2e_version
- `tests/e2e/test_positive_e2e_flow.py` — test_positive_e2e_flow
- `tests/e2e/__init__.py` — __init__
- `tests/integration/conftest.py` — conftest
- `tests/integration/test_cli_server.py` — test_cli_server
- `tests/integration/test_copilot_telemetry_stats.py` — test_copilot_telemetry_stats
- `tests/integration/test_fetch_ssl_cert.py` — test_fetch_ssl_cert
- `tests/integration/test_integration.py` — test_integration
- `tests/integration/__init__.py` — __init__
- `tests/runners/run_all_checks.py` — run_all_checks
- `tests/runners/run_performance_tests.py` — run_performance_tests
- `tests/runners/run_security_checks.py` — run_security_checks
- `tests/tools/agent_review_prep.py` — agent_review_prep
- `tests/tools/complexity_report.py` — complexity_report
- `tests/tools/coverage_gap_audit.py` — coverage_gap_audit
- `tests/tools/doc_sync_check.py` — doc_sync_check
- `tests/tools/feature_screenshot_audit.py` — feature_screenshot_audit
- `tests/tools/requirements_map.py` — requirements_map
- `tests/tools/requirements_status.py` — requirements_status
- `tests/tools/smoke_test_setup.py` — smoke_test_setup
- `tests/tools/test_coverage.py` — test_coverage
- `tests/unit/conftest.py` — conftest
- `tests/unit/test_cert_handlers.py` — test_cert_handlers
- `tests/unit/test_cert_validation.py` — test_cert_validation
- `tests/unit/test_cli.py` — test_cli
- `tests/unit/test_complexity_audit.py` — test_complexity_audit
- `tests/unit/test_config.py` — test_config
- `tests/unit/test_copilot_customization_assets.py` — test_copilot_customization_assets
- `tests/unit/test_dau_metrics.py` — test_dau_metrics
- `tests/unit/test_dau_normalizer.py` — test_dau_normalizer
- `tests/unit/test_exceptions.py` — test_exceptions
- `tests/unit/test_filter_handlers.py` — test_filter_handlers
- `tests/unit/test_imports.py` — test_imports
- `tests/unit/test_jira_client.py` — test_jira_client
- `tests/unit/test_logging_setup.py` — test_logging_setup
- `tests/unit/test_main_helpers.py` — test_main_helpers
- `tests/unit/test_metrics.py` — test_metrics
- `tests/unit/test_schema.py` — test_schema
- `tests/unit/test_server_handlers.py` — test_server_handlers
- `tests/unit/test_user_data.py` — test_user_data
- `tests/unit/test_version.py` — test_version
- `tests/unit/__init__.py` — __init__
- `tools/agents/changelog_prep.py` — changelog_prep
- `tools/agents/check_req_status.py` — check_req_status
- `tools/agents/doc_drift.py` — doc_drift
- `tools/agents/ux_spec_scaffold.py` — ux_spec_scaffold

## Extension Patterns (quick ref)

- **New module**: add file in appropriate layer → import in entry point if needed → add unit test
- **New config var**: add to `.env.example` (credential) or defaults file (non-sensitive) → `os.getenv()` in config module → test
- **New route**: add handler function → register in routing dispatch → add component test

---

Generated by nexus-agentic-sdlc 1.0.0
