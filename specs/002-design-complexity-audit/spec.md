# Feature Specification: Solution Architect Design Complexity Audit

**Feature Branch**: `002-design-complexity-audit`

**Created**: 2026-06-06

**Status**: Clarified

**Input**: User description: "Solution Architect audit for application design complexity — analyse the existing codebase modules, identify structural complexity hotspots, score complexity per module, and produce an actionable improvement plan with prioritised recommendations."

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 — Run Complexity Audit via CLI (Priority: P1)

As a Solution Architect reviewing the codebase, I want to run a single command that scores every module in the application for structural complexity so that I can quickly identify which modules pose the highest maintenance risk without reading the code manually.

**Why this priority**: The primary value of this feature is surfacing hidden structural risk. Without a CLI entry point, the audit is inaccessible to both architects and CI pipelines.

**Independent Test**: After running `python main.py --complexity-audit`, a Markdown file should appear in `generated/reports/` containing a table of per-module scores ranked from highest to lowest — verifiable without Jira credentials or any network connection.

**Acceptance Scenarios**:

1. **Given** the application codebase exists under `app/`, **When** the user invokes `python main.py --complexity-audit`, **Then** the system produces a complexity report for every Python module in `app/` without requiring Jira credentials.
2. **Given** the audit completes, **When** the report is opened, **Then** each module row contains: module path, LOC, function count, coupling score (direct import count), cohesion score (responsibility count), and a composite complexity score.
3. **Given** a module with a composite score above the High threshold, **When** the report is read, **Then** that module's row is classified as `High` and at least one actionable recommendation is present.

---

### User Story 2 — Review Improvement Plan (Priority: P2)

As a Developer assigned to reduce technical debt, I want an improvement plan that ranks modules by complexity and tells me exactly what to do so that I can prioritise refactoring work without needing architectural expertise.

**Why this priority**: A score table alone is insufficient for action. Developers need ranked, concrete recommendations to translate audit findings into sprint tasks.

**Independent Test**: The Markdown report should contain an "Improvement Plan" section listing modules in descending complexity order, each with ≥ 1 specific, actionable recommendation — readable and actionable without additional tooling.

**Acceptance Scenarios**:

1. **Given** a completed audit, **When** the Improvement Plan section is read, **Then** modules are listed in descending composite-score order — highest complexity first.
2. **Given** a module classified as `High` complexity, **When** its recommendation row is read, **Then** it includes at least one specific action (e.g., "Extract `<function>` into a dedicated module", "Reduce import coupling by injecting `<dependency>`").
3. **Given** all modules are classified as `Low` complexity, **When** the Improvement Plan section is read, **Then** the section states "No high-complexity modules found" rather than being absent or empty.

---

### User Story 3 — Access Audit Results via HTTP API (Priority: P3)

As a CI pipeline or dashboard consumer, I want to retrieve the latest complexity audit result as JSON via an HTTP endpoint so that I can integrate the scores into automated quality gates or dashboards without parsing Markdown.

**Why this priority**: Machine-readable output enables future CI enforcement (e.g., fail a build if a new High-complexity module appears). This is lower priority than human-readable output but required for integration use cases.

**Independent Test**: With the dev server running, a GET request to `/api/complexity/audit` should return a JSON response containing a list of module score objects — verifiable with `curl` or a browser without any authentication.

**Acceptance Scenarios**:

1. **Given** the dev server is running, **When** a GET request is sent to `/api/complexity/audit`, **Then** the response status is `200 OK` with `Content-Type: application/json` and a body containing a list of module score objects.
2. **Given** no audit has been run since server start, **When** `/api/complexity/audit` is called, **Then** the endpoint triggers an on-demand audit and returns results rather than a 404 or empty response.
3. **Given** a completed audit, **When** the JSON response is parsed, **Then** each object contains: `module`, `loc`, `function_count`, `coupling`, `cohesion`, `composite_score`, `classification` (`Low`, `Medium`, or `High`), and `recommendations` (array of strings).

---

### Edge Cases

- What happens when a Python module has syntax errors that prevent analysis? → That module's row should show `N/A` for scores that could not be computed and include a warning annotation; the audit continues for all other modules.
- What happens when `app/` contains zero Python files? → The audit exits immediately with a clear diagnostic message; no report file is written.
- What happens when thresholds are missing or misconfigured? → The system falls back to the built-in default thresholds defined in the scoring engine and logs a warning.
- What happens when both `--complexity-audit` and other CLI flags are provided simultaneously? → The audit runs independently of Jira pipeline flags; no Jira connectivity is initiated.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-1**: The system SHALL compute a per-module complexity score for every Python module discovered under `app/`, covering four dimensions: (a) average cyclomatic complexity per function/method via `radon.complexity.cc_visit()`, (b) coupling (direct import count), (c) cohesion (number of distinct responsibilities, approximated by exported symbol count), and (d) size (LOC).

  **Resolved**: The scoring engine SHALL use `radon` for cyclomatic complexity, maintainability index, and LOC metrics. `radon` SHALL be promoted from `requirements-dev.txt` to `requirements.txt` (runtime dependency). `ast` MAY supplement for import counting and exported-symbol enumeration where `radon` does not provide the metric directly. The existing `tests/tools/complexity_report.py` serves as reference prior art but is not reused directly.

- **FR-2**: The system SHALL derive a single composite complexity score per module from the four dimension scores and classify each module as `Low`, `Medium`, or `High` based on configurable thresholds. Default thresholds SHALL be defined in the scoring engine and SHALL be overridable via a configuration file or environment variable.

- **FR-3**: The system SHALL produce an ordered improvement plan — modules ranked by composite score descending — where every `High`-classified module has at least one specific, actionable recommendation. `Medium` modules SHALL have at most one recommendation. `Low` modules require no recommendation.

- **FR-4**: The system SHALL expose the audit capability via a new CLI flag (`--complexity-audit`) on the existing `main.py` entry point. The flag SHALL allow the audit to run without Jira credentials and SHALL produce a Markdown report file in `generated/reports/`.

  **Resolved**: `--complexity-audit` SHALL be added to the existing `main.py` entry point. When this flag is present, `app/core/config.py` Jira credential validation SHALL be bypassed so the audit runs without any Jira environment variables configured.

- **FR-5**: The audit result SHALL be available as both Markdown and HTML report formats, consistent with the existing reporter pattern (`report_md.py` / `report_html.py`). The HTML format SHALL use the existing Jinja2 template mechanism.

- **FR-6**: The dev server SHALL expose a `/api/complexity/audit` HTTP endpoint (GET) that returns the audit result as a JSON payload. The endpoint SHALL trigger an on-demand audit if no cached result is available.

  **Resolved**: The audit SHALL cover all Python source files in the repository, including `app/`, `tools/`, `tests/tools/`, and root-level scripts (`main.py`, `server.py`). The module discovery root is the repository root; files matching `**/*.py` are included. `__init__.py` files are included. Virtual environment directories (`venv/`, `.venv/`) and `generated/` are excluded from discovery.

---

### Key Entities

- **`ComplexityScore`**: A record holding the four dimension scores (cyclomatic proxy, coupling, cohesion, LOC) plus the derived composite score and classification (`Low` / `Medium` / `High`) for a single Python module.
- **`ImprovementRecommendation`**: A structured suggestion linked to a specific module and dimension; contains a short action description and the triggering score.
- **`ComplexityReport`**: The aggregate output of one audit run — a list of `ComplexityScore` records, the matching `ImprovementRecommendation` list, run timestamp, and module discovery root.

---

## Success Criteria *(mandatory)*

- **SC-1**: All Python modules discovered under the full repository scope (`app/`, `tools/`, `tests/tools/`, and root scripts `main.py`, `server.py`) are scored in a single audit run with no modules silently skipped. Virtual environment directories (`venv/`, `.venv/`) and `generated/` are excluded from discovery.
- **SC-2**: Every `High`-classified module in the improvement plan has at least one specific, actionable recommendation — verified by inspecting the plan section of the report.
- **SC-3**: A full audit run on the existing `app/` codebase completes in under 30 seconds on a standard development machine.
- **SC-4**: Unit test coverage on the scoring engine (dimension scoring functions, composite aggregation, classification logic, recommendation generation) is ≥ 80%.
- **SC-5**: The `/api/complexity/audit` endpoint returns a valid JSON response with `200 OK` within 30 seconds for the first call after server start.

---

## Assumptions

- The codebase is Python 3.x; source files end in `.py`; the `ast` stdlib module (and optionally `radon` if confirmed in clarification) is available in the analysis environment.
- A pre-existing complexity analysis script exists at `tests/tools/complexity_report.py` using `radon`. It serves as reference prior art; the new scoring engine is implemented independently in `app/core/` and does not import from or depend on the existing script.
- `radon` is promoted to `requirements.txt` as a runtime dependency.
- Complexity classification thresholds are team-configurable but must ship with well-reasoned defaults; the feature does not require external calibration data.
- The feature does not perform automated code refactoring — it only reports and recommends.
- External dependency analysis (transitive pip packages, import graphs beyond direct imports) is out of scope.
- Runtime profiling (execution time, memory usage) is out of scope.
- The audit is a developer/architect tool; it does not need to be accessible to end users of the Jira Metrics product.
- The HTTP endpoint is served on localhost only (same security posture as all existing `/api/*` routes).
