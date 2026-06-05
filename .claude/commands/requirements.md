# /requirements

Reference for locating and updating product requirements when implementing a feature or fixing a bug.

## Quick-lookup: ID Prefix Map

All requirement files are in `docs/product/requirements/`. Find the right file by feature area:

| File | Topic Area | ID Prefix(es) |
|------|-----------|---------------|
| `app-non-functional-requirements.md` | Performance, security, usability, reliability, data privacy, compatibility, accessibility | `NFR-P-`, `NFR-S-`, `NFR-U-`, `NFR-R-`, `NFR-D-`, `NFR-C-`, `NFR-A-` |
| `dau-survey-requirements.md` | DAU survey UI, file save, metric computation, report rendering | `DAU-F-`, `DAU-NFR-` |
| `jira-connection-requirements.md` | Authentication, config validation, SSL | `JCR-A-`, `JCR-C-`, `JCR-SSL-` |
| `jira-data-fetching-requirements.md` | Board discovery, sprint fetching, issue fetching, changelog, filter scoping | `JDF-B-`, `JDF-SP-`, `JDF-IS-`, `JDF-CL-`, `JDF-F-` |
| `jira-filter-management-requirements.md` | Default filter, CRUD operations, UI behaviour | `JFM-D-`, `JFM-C-`, `JFM-U-` |
| `jira-schema-requirements.md` | Schema loading, field lookup, status mapping, auto-detection | `JSR-L-`, `JSR-F-`, `JSR-S-`, `JSR-D-` |
| `logging-requirements.md` | Log file creation, log level, log format, log cleanup | `LOG-` |
| `report-generation-requirements.md` | Report generation config, project type, estimation type, metric toggles, UI controls, template labels | `RG-` |

Special (no standard ID prefix):
| `installation-requirements.md` | Zip contents, setup steps, uninstall | Descriptive sections only |
| `technical-requirements.md` | OS compatibility, Python version, dependencies | Descriptive sections only |

---

## Valid Status Values

Use exactly these three values in the `Status` column — no other variations:

| Value | Meaning |
|-------|---------|
| `✓ Met` | Acceptance criterion is satisfied and verified |
| `✗ Not met` | Acceptance criterion is not yet satisfied |
| `⬜ N/T` | Not yet tested; implementation may exist but is unverified |

---

## Rules

1. **Update Status column only** — never add new rows, never create new files.
2. **Update all affected rows** — if your change impacts multiple requirements, update each one.
3. **Do not edit `app-nfr-gap-analysis.md`** — that is a companion document (findings/notes only), not a requirements file.

---

## Typical Workflow

During `/implement`, `/fix`, or `/sync`:

1. Identify the feature area affected (e.g., "fixing Jira schema detection" → `jira-schema-requirements.md`)
2. Open the relevant file from the map above
3. Find rows whose acceptance criterion matches your change
4. Update `Status` to `✓ Met` (if now satisfied), `✗ Not met` (if partially implemented), or `⬜ N/T` (if unverified)
5. After all code/tests/docs are complete, re-check to confirm final status

