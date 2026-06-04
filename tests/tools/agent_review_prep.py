"""
tests/tools/agent_review_prep.py
=================================
Produces a Dev Lead review-prep summary for a set of changed files.

Sections
--------
  1. Affected modules     — matched against the AGENTS.md module map
  2. Requirements to check — which docs/product/requirements/*.md files are relevant
  3. Docs needing update  — doc sync rules from CLAUDE.md
  4. Test coverage snapshot — totals from tests/coverage/test_coverage.md

Usage
-----
    # From git diff (most common — run before a Dev Lead review session)
    git diff --name-only HEAD | python tests/tools/agent_review_prep.py

    # Pass files explicitly
    python tests/tools/agent_review_prep.py --files app/core/metrics.py ui/index.html

    # Dry-run: show mapping rules only, no file input needed
    python tests/tools/agent_review_prep.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]
COVERAGE_FILE = REPO_ROOT / "tests" / "coverage" / "test_coverage.md"

# ── Module map (from AGENTS.md) ───────────────────────────────────────────────
# Each entry: (file_patterns, display_name, one_line_purpose)
# More specific entries must come before broader wildcard entries.

_MODULE_MAP: list[tuple[list[str], str, str]] = [
    (["main.py"], "main.py", "Thin CLI entry-point; delegates to app.cli"),
    (["server.py"], "server.py", "Thin server entry-point; delegates to app.server"),
    (["app/cli.py"], "app/cli.py", "Full report pipeline: config → fetch → metrics → parallel HTML+MD output"),
    (["app/core/config.py"], "app/core/config.py", "Loads .env, exposes all constants, validate_config()"),
    (["app/core/jira_client.py"], "app/core/jira_client.py", "Jira REST wrapper; fetch_sprint_data()"),
    (["app/core/metrics.py"], "app/core/metrics.py", "Pure metric functions; build_metrics_dict()"),
    (["app/core/schema.py"], "app/core/schema.py", "Jira field schema registry backed by config/jira_schema.json"),
    (["app/reporters/report_html.py"], "app/reporters/report_html.py", "Renders ui/templates/report.html.j2 via Jinja2"),
    (["app/reporters/report_md.py"], "app/reporters/report_md.py", "Builds Markdown report string and writes to disk"),
    (["app/utils/logging_setup.py"], "app/utils/logging_setup.py", "setup_logging(); custom SUCCESS level"),
    (["app/utils/cert_utils.py"], "app/utils/cert_utils.py", "PEM certificate validation via cryptography library"),
    (["app/server/**"], "app/server/", "Stdlib HTTPServer package; serves ui/index.html and all /api/* routes"),
    (["app/core/**"], "app/core/ (other)", "Core module change — verify architecture.md"),
    (["app/reporters/**"], "app/reporters/ (other)", "Reporter change — verify feature docs"),
    (["app/utils/**"], "app/utils/ (other)", "Utility module change"),
    (["config/jira_schema.json"], "config/jira_schema.json", "Jira field/status definitions per instance"),
    (["config/jira_filters.json"], "config/jira_filters.json", "Named JQL filter presets"),
    (["config/**"], "config/ (other)", "Configuration file change"),
    (["ui/templates/**"], "ui/templates/", "Jinja2 report template"),
    (["ui/index.html"], "ui/index.html", "Dev server index page"),
    (["ui/css/**"], "ui/css/", "Stylesheet assets"),
    (["ui/js/**"], "ui/js/", "Client-side scripts"),
    (["ui/**"], "ui/ (other)", "Frontend asset change"),
    (["tests/conftest.py"], "tests/conftest.py", "Shared test factories: make_sprint, make_issue, etc."),
    (["tests/unit/**"], "tests/unit/", "Unit test layer — pure functions, no I/O"),
    (["tests/component/**"], "tests/component/", "Component test layer — filesystem + HTTP"),
    (["tests/integration/**"], "tests/integration/", "Integration test layer — real multi-module flows"),
    (["tests/e2e/**"], "tests/e2e/", "E2E test layer — Playwright browser tests"),
    (["tests/tools/**"], "tests/tools/", "Developer tooling scripts"),
    (["docs/product/metrics/**"], "docs/product/metrics/", "Metric definitions — verify computation logic"),
    (["docs/development/**"], "docs/development/", "Architecture or pipeline documentation"),
]

# ── Requirements mapping ──────────────────────────────────────────────────────
# Each entry: (file_patterns, requirements_file, reason)

_REQUIREMENTS_MAP: list[tuple[list[str], str, str]] = [
    (
        ["app/utils/logging_setup.py"],
        "docs/product/requirements/logging_requirements.md",
        "logging behavior changed",
    ),
    (
        ["app/core/jira_client.py", "config/jira_filters.json"],
        "docs/product/requirements/jira_data_fetching_requirements.md",
        "Jira data fetching logic changed",
    ),
    (
        ["app/core/config.py"],
        "docs/product/requirements/jira_connection_requirements.md",
        "connection config behavior changed",
    ),
    (
        ["config/jira_schema.json", "app/core/schema.py"],
        "docs/product/requirements/jira_schema_requirements.md",
        "schema registry changed",
    ),
    (
        ["config/jira_filters.json", "app/server/**"],
        "docs/product/requirements/jira_filter_management_requirements.md",
        "filter management behavior changed",
    ),
    (
        ["app/core/metrics.py"],
        "docs/product/requirements/metric_computation_requirements.md",
        "metric computation logic changed",
    ),
    (
        ["app/reporters/**", "ui/**", "app/server/**"],
        "docs/product/requirements/report_generation_requirements.md",
        "report generation or UI changed",
    ),
    (
        ["ui/**", "app/reporters/report_html.py"],
        "docs/product/requirements/dau_survey_requirements.md",
        "UI/report rendering changed — check DAU survey requirements",
    ),
    (
        ["requirements*.txt", "pyproject.toml"],
        "docs/product/requirements/installation_requirements.md",
        "setup or dependency changed",
    ),
    (
        ["requirements*.txt", "pyproject.toml", "app/core/**", "app/utils/**"],
        "docs/product/requirements/technical_requirements.md",
        "technical dependencies or core modules changed",
    ),
    (
        ["app/**", "ui/**"],
        "docs/product/requirements/app_non_functional_requirements.md",
        "application change — check NFR impact (perf, security, reliability)",
    ),
]

# ── Doc sync rules (mirrors doc_sync_check.py rules from CLAUDE.md) ──────────
# Each entry: (file_patterns, doc_target, reason)

_DOC_RULES: list[tuple[list[str], str, str]] = [
    (
        ["docs/product/metrics/**", "app/core/metrics.py"],
        "docs/product/metrics/",
        "metric behaviour or output shape changed",
    ),
    (
        ["app/core/**", "app/reporters/**", "app/server/**", "app/utils/**"],
        "docs/development/architecture.md",
        "modules added, removed, or restructured",
    ),
    (
        ["README.md", "requirements*.txt", "pyproject.toml"],
        "README.md",
        "setup steps, commands, or project purpose changed",
    ),
    (
        ["ui/**", "app/reporters/report_html.py", "app/server/**"],
        "docs/product/features/features.md",
        "UI or user-visible behaviour changed",
    ),
]


def _normalize(path: str) -> str:
    return path.replace("\\", "/")


def _matches(file_path: str, pattern: str) -> bool:
    pp = PurePosixPath(_normalize(file_path))
    try:
        return pp.match(pattern) or pp.full_match(pattern)
    except (AttributeError, TypeError):
        return pp.match(pattern)


def _match_list(file_path: str, patterns: list[str]) -> bool:
    return any(_matches(file_path, p) for p in patterns)


def _affected_modules(files: list[str]) -> list[tuple[str, str]]:
    seen: dict[str, str] = {}
    for f in files:
        for patterns, name, purpose in _MODULE_MAP:
            if name not in seen and _match_list(f, patterns):
                seen[name] = purpose
                break
    return list(seen.items())


def _requirements_to_check(files: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for f in files:
        for patterns, req_file, reason in _REQUIREMENTS_MAP:
            if _match_list(f, patterns):
                result.setdefault(req_file, [])
                if reason not in result[req_file]:
                    result[req_file].append(reason)
    return result


def _docs_to_update(files: list[str]) -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for f in files:
        for patterns, doc_target, reason in _DOC_RULES:
            if _match_list(f, patterns):
                result.setdefault(doc_target, [])
                if reason not in result[doc_target]:
                    result[doc_target].append(reason)
    return result


def _coverage_snapshot() -> list[str]:
    if not COVERAGE_FILE.exists():
        return ["  (tests/coverage/test_coverage.md not found)"]

    text = COVERAGE_FILE.read_text(encoding="utf-8").encode("ascii", errors="replace").decode("ascii")
    lines: list[str] = []

    # Parse test pyramid counts
    pyramid_match = re.search(r"```text\n(.*?)```", text, re.DOTALL)
    if pyramid_match:
        for line in pyramid_match.group(1).strip().splitlines():
            if re.search(r"\d+ tests", line):
                lines.append("  " + line.strip())

    # Parse totals row from requirements summary table
    summary_match = re.search(r"\|\s*\*\*All\*\*.*?\|", text)
    if summary_match:
        row = summary_match.group(0)
        nums = re.findall(r"\*\*(\d+)\*\*", row)
        if len(nums) >= 2:
            lines.append(f"\n  Requirements: total={nums[0]}, covered={nums[1]}")

    return lines if lines else ["  (no data found in test_coverage.md)"]


def _print_rules() -> None:
    print("=== Module map rules ===")
    for pats, name, _ in _MODULE_MAP:
        print(f"  {name}: {', '.join(pats)}")
    print("\n=== Requirements mapping rules ===")
    for pats, req, reason in _REQUIREMENTS_MAP:
        print(f"  {req}")
        print(f"    triggers on: {', '.join(pats)}")
        print(f"    reason: {reason}")
    print("\n=== Doc sync rules ===")
    for pats, doc, reason in _DOC_RULES:
        print(f"  {doc}")
        print(f"    triggers on: {', '.join(pats)}")
        print(f"    reason: {reason}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Review prep summary for Dev Lead",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  git diff --name-only HEAD | python tests/tools/agent_review_prep.py\n"
            "  python tests/tools/agent_review_prep.py --files app/core/metrics.py ui/index.html"
        ),
    )
    parser.add_argument(
        "--files",
        nargs="*",
        metavar="FILE",
        help="Changed files to analyse (default: read from stdin, one per line)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print mapping rules only")
    args = parser.parse_args(argv)

    if args.dry_run:
        _print_rules()
        return 0

    if args.files is not None:
        files = args.files
    else:
        if sys.stdin.isatty():
            parser.print_help()
            return 2
        files = [line.strip() for line in sys.stdin if line.strip()]

    if not files:
        print("No changed files provided.")
        return 0

    sep = "-" * 52
    print("=" * 52)
    print(f"  REVIEW PREP SUMMARY  ({len(files)} changed file{'s' if len(files) != 1 else ''})")
    print("=" * 52)

    # 1. Affected modules
    modules = _affected_modules(files)
    print(f"\n1. AFFECTED MODULES ({len(modules)})")
    print(sep)
    if modules:
        max_name = max(len(n) for n, _ in modules)
        for name, purpose in modules:
            print(f"  {name:<{max_name}}  --  {purpose}")
    else:
        print("  (none matched — verify file paths are relative to repo root)")

    # 2. Requirements to check
    reqs = _requirements_to_check(files)
    print(f"\n2. REQUIREMENTS TO CHECK ({len(reqs)})")
    print(sep)
    if reqs:
        for req_file, reasons in sorted(reqs.items()):
            print(f"  {req_file}")
            for r in reasons:
                print(f"    <- {r}")
        print("\n  Verify: python tests/tools/requirements_status.py")
    else:
        print("  No requirements files flagged.")

    # 3. Docs needing update
    docs = _docs_to_update(files)
    print(f"\n3. DOCS LIKELY NEEDING UPDATE ({len(docs)})")
    print(sep)
    if docs:
        for doc_file, reasons in sorted(docs.items()):
            print(f"  {doc_file}")
            for r in reasons:
                print(f"    <- {r}")
    else:
        print("  No documentation updates required.")

    # 4. Test coverage snapshot
    print("\n4. TEST COVERAGE SNAPSHOT")
    print(sep)
    for line in _coverage_snapshot():
        print(line)

    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
