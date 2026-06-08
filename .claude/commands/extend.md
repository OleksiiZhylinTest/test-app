# /extend

Reference for extending the application: data contracts and step-by-step recipes.

## metrics_dict shape

Built by `build_metrics_dict` in the application source (see `.claude/summaries/architecture-map.md`); consumed by both reporters.

```python
{
    "generated_at": str,          # ISO-8601 UTC
    "schema_name": str|None,      # active schema name, or None if default
    "velocity": [
        {sprint_id, sprint_name, start_date, end_date, velocity: float, issue_count: int}
    ],
    "ai_assistance_trend": [
        {sprint_id, sprint_name, start_date, end_date, total_sp, ai_sp, ai_pct: float}
    ],                             # per-sprint AI-assisted story-point percentage
    "ai_usage_details": {
        ai_assisted_issue_count: int,
        tool_breakdown: [{label, count, pct}],
        action_breakdown: [{label, count, pct}]
    },
    "dau": {
        team_avg: float|None, response_count: int,
        by_role: [{role, avg, count}], breakdown: [{answer, count}]
    },
    # enriched after fetch:
    "filter_name": str|None,
    "filter_id": int|None,
    "filter_jql": str|None,
    "project_key": str|None,
}
```

Full Sprint and Issue dict shapes: see architecture documentation in `docs/development/architecture.md`.

## Adding a new metric

1. Add `compute_<name>(sprints, sprint_issues) -> list[dict]` to the metrics module (see `.claude/summaries/architecture-map.md` for location); each dict must include `sprint_id` and `sprint_name`. Accept optional schema-driven parameters if the metric depends on configurable field IDs or status names.
2. Call it in `build_metrics_dict()` and add result to the returned dict.
3. Add rendering in the Markdown reporter.
4. Add rendering in the HTML report template.
5. Add unit tests using `make_sprint()` and `make_issue()` or `make_issue_with_labels()` factories from `tests/conftest.py`.

## Adding a new data source field to the schema

1. Add the field entry to `_DEFAULT_SCHEMA["fields"]` in the schema module.
2. Add the same entry to the default schema in `config/`.
3. If the field has a known `schema.custom` identifier, add it to `KNOWN_FIELD_SCHEMAS`.
4. If it should be detected by name, add patterns to `KNOWN_NAME_PATTERNS`.
5. Add tests in the schema unit test file.

## Adding a new config var

1. Add to `.env.example` with a comment.
2. Add `os.getenv()` in the config module as module-level constant.
3. Add to `validate_config()` if required.
4. Test using `monkeypatch` + `importlib.reload(config)` pattern.

## Extending the dev server

Add a method `_handle_<name>(self)` to the `Handler` class in the server base module (see `.claude/summaries/architecture-map.md`), then route it from `do_GET` or `do_POST`. Cover it in `tests/component/test_server.py` using the `server_url` fixture.
