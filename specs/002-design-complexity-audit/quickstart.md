# Quickstart: Design Complexity Audit

## Run the CLI audit

```bash
python main.py --complexity-audit
```

No Jira credentials required. Output written to `generated/reports/<timestamp>/complexity_report.md` and `complexity_report.html`.

## Call the HTTP endpoint

```bash
# Start the dev server
python server.py

# Request the audit
curl http://localhost:8080/api/complexity/audit
```

Returns JSON with per-module scores and recommendations.

## Override classification thresholds

Set in `.env` or as environment variables before running:

```
COMPLEXITY_MEDIUM_THRESHOLD=4.0   # default 3.5 — scores below this → Low
COMPLEXITY_HIGH_THRESHOLD=6.5     # default 7.0 — scores at or above this → High
```

## Add a new scoring dimension

1. Implement a scorer function in `app/core/complexity_audit.py` that returns a normalised float 0–10.
2. Add its key and weight to `_DIMENSION_WEIGHTS` (re-normalise all weights to sum to 1.0).
3. Add the field to `ComplexityScore` in `data-model.md`.
4. Add a recommendation template to the action lookup table in `build_complexity_report()`.
