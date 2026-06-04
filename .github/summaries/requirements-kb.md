# Requirements Knowledge Base — Routing Index

Use this summary to route to the correct requirements file without loading all 13 files.
Full index: `docs/product/requirements/README.md`

| File | Topic area | ID prefix | Approx. rows |
|------|-----------|-----------|-------------|
| installation_requirements.md | Zip contents, setup steps (Windows/macOS/Linux), update/reinstall, troubleshooting | None (descriptive sections, no standard ID rows) | ~15 descriptive entries |
| jira_connection_requirements.md | Authentication, config validation, test-connection endpoint, SSL/TLS certificate handling, client timeouts | `JCR-A-`, `JCR-C-`, `JCR-T-`, `JCR-SSL-`, `JCR-TO-` | ~29 rows |
| jira_data_fetching_requirements.md | Board discovery, sprint fetching, issue fetching, changelog fetching, filter JQL resolution, KANBAN period fetching | `JDF-B-`, `JDF-SP-`, `JDF-I-`, `JDF-CL-`, `JDF-F-`, `JDF-K-` | ~25 rows |
| jira_filter_management_requirements.md | Default filter template, filter persistence (CRUD API), UI filter name pre-population, filter list behaviour, active schema & filter editing | `JFM-D-`, `JFM-P-`, `JFM-UI-` | ~31 rows |
| jira_schema_requirements.md | Schema loading, active schema resolution, schema save & delete, field ID & JQL name lookups, status mappings, auto-detection from Jira fields, schema management UI | `JSR-L-`, `JSR-R-`, `JSR-SD-`, `JSR-F-`, `JSR-SM-`, `JSR-AD-`, `JSR-UI-` | ~40 rows |
| metric_computation_requirements.md | Done-status resolution, excluded statuses, story points extraction, sprint attribution/deduplication, velocity aggregation, estimation type, output shape, metric value types and chart display format | `MC-V-DS-`, `MC-V-ES-`, `MC-V-SP-`, `MC-V-SA-`, `MC-V-AG-`, `MC-V-ET-`, `MC-V-OUT-`, `MC-FMT-` | ~62 rows |
| report_generation_requirements.md | Filter selection, project type (SCRUM/KANBAN), estimation type, metric toggles, report output (HTML/MD), configuration env vars, non-functional requirements | `RG-FS-`, `RG-PT-`, `RG-ET-`, `RG-MT-`, `RG-RO-`, `RG-CF-`, `RG-NFR-` | ~37 rows |
| logging_requirements.md | Log file creation, log format, output channels, log levels (incl. custom SUCCESS), entry-point integration, code quality, security, performance, log retention | `LOG-` | ~18 rows |
| dau_survey_requirements.md | DAU survey UI, submission & storage (FS API / download fallback), metrics computation, report rendering, non-functional requirements | `DAU-F-`, `DAU-NFR-` | ~27 rows |
| technical_requirements.md | OS compatibility, Python version, runtime/dev dependencies, installation steps, browser requirements, network requirements, credentials, SSL/TLS support | None (descriptive sections, no standard ID rows) | ~20 descriptive entries |
| app_non_functional_requirements.md | Performance, security, usability, reliability & error handling, data privacy, compatibility, accessibility | `NFR-P-`, `NFR-S-`, `NFR-U-`, `NFR-R-`, `NFR-D-`, `NFR-C-`, `NFR-A-` | ~33 rows |
| app_nfr_gap_analysis.md | Gap analysis findings against app_non_functional_requirements.md — current behaviour, recommended fixes, resolution notes | None (narrative companion doc, not a requirements file) | ~5 gap entries |

## Routing Rules

| If the task involves... | Open this file |
|------------------------|----------------|
| Metric computation accuracy | metric_computation_requirements.md |
| DAU survey UI or import | dau_survey_requirements.md |
| Jira login, auth, certificate | jira_connection_requirements.md |
| Jira field shape, issue data | jira_data_fetching_requirements.md |
| Filter presets, JQL management | jira_filter_management_requirements.md |
| Jira schema config (jira_schema.json) | jira_schema_requirements.md |
| HTML or Markdown report output | report_generation_requirements.md |
| Log levels, log file behavior | logging_requirements.md |
| Setup, install, env variables | installation_requirements.md |
| Performance, security, NFR | app_non_functional_requirements.md |
| NFR gap analysis findings | app_nfr_gap_analysis.md |
| Build, test, Python version constraints | technical_requirements.md |

## Usage Pattern

1. Match task topic → table above → open only that file
2. If multiple areas are affected, open files one at a time — do not bulk-load all 13
3. Use `docs/product/requirements/README.md` only to look up exact row IDs
