"""
tests/tools/doc_sync_check.py
==============================
Given a list of changed source files (from stdin or --files), reports which
documentation files likely need updating based on the rules in CLAUDE.md.

Usage
-----
    # Pipe git diff output
    git diff --name-only HEAD~1 | python tests/tools/doc_sync_check.py

    # Pass files explicitly
    python tests/tools/doc_sync_check.py --files app/core/metrics.py ui/index.html

    # Dry-run: print rules only, do not check files
    python tests/tools/doc_sync_check.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path, PurePosixPath

REPO_ROOT = Path(__file__).resolve().parents[2]

# Documentation update rules from CLAUDE.md.
# Each rule: (glob_patterns, doc_target, reason)
_RULES: list[tuple[list[str], str, str]] = [
    (
        ["docs/product/metrics/*", "app/core/metrics.py"],
        "docs/product/metrics/",
        "metric behaviour or output shape changed",
    ),
    (
        [
            "app/core/*.py",
            "app/reporters/*.py",
            "app/server/**",
            "app/utils/*.py",
        ],
        "docs/development/architecture.md",
        "modules added, removed, or restructured",
    ),
    (
        [
            "README.md",
            "requirements*.txt",
            "pyproject.toml",
            "*.bat",
            "project_setup*",
        ],
        "README.md",
        "setup steps, commands, or project purpose changed",
    ),
    (
        [
            "ui/**",
            "app/reporters/report_html.py",
            "app/server/**",
        ],
        "docs/product/features/features.md",
        "UI or user-visible behaviour changed",
    ),
]


def _matches_pattern(file_path: str, pattern: str) -> bool:
    pp = PurePosixPath(file_path.replace("\\", "/"))
    pat = PurePosixPath(pattern)
    # Simple glob: support *, **, and exact matches
    try:
        return pp.match(pattern) or pp.full_match(pattern)
    except (AttributeError, TypeError):
        return pp.match(pattern)


def _check_file(file_path: str) -> list[tuple[str, str]]:
    hits: list[tuple[str, str]] = []
    for patterns, doc_target, reason in _RULES:
        for pat in patterns:
            if _matches_pattern(file_path, pat):
                hits.append((doc_target, reason))
                break
    return hits


def _print_rules() -> None:
    print("Documentation update rules (from CLAUDE.md):\n")
    for patterns, doc_target, reason in _RULES:
        print(f"  When: {', '.join(patterns)}")
        print(f"  Update: {doc_target}")
        print(f"  Reason: {reason}\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Doc sync check")
    parser.add_argument(
        "--files",
        nargs="*",
        metavar="FILE",
        help="Changed files to check (default: read from stdin, one per line)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print rules only")
    args = parser.parse_args(argv)

    if args.dry_run:
        _print_rules()
        return 0

    if args.files is not None:
        changed_files = args.files
    else:
        if sys.stdin.isatty():
            parser.print_help()
            return 2
        changed_files = [line.strip() for line in sys.stdin if line.strip()]

    if not changed_files:
        print("No changed files provided.")
        return 0

    # Collect unique (doc_target, reason) pairs across all changed files
    doc_updates: dict[str, list[str]] = {}
    for f in changed_files:
        for doc_target, reason in _check_file(f):
            doc_updates.setdefault(doc_target, [])
            if reason not in doc_updates[doc_target]:
                doc_updates[doc_target].append(reason)

    if not doc_updates:
        print("No documentation updates required for the listed files.")
        return 0

    print(f"Documentation files that likely need updating ({len(doc_updates)}):\n")
    for doc_target, reasons in sorted(doc_updates.items()):
        print(f"  {doc_target}")
        for reason in reasons:
            print(f"    <- {reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
