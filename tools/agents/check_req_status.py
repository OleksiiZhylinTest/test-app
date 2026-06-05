"""
Scan all docs/product/requirements/*_requirements.md files and report status counts.

Usage:
  python tools/agents/check_req_status.py
  python tools/agents/check_req_status.py --file jira-connection-requirements.md
  python tools/agents/check_req_status.py --unmet-only
"""

import argparse
import re
from pathlib import Path


REQUIREMENTS_DIR = Path("docs/product/requirements")
STATUS_MET = "✓ Met"
STATUS_UNMET = "✗ Not met"
STATUS_NT = "⬜ N/T"


def parse_status_counts(text: str) -> dict:
    return {
        "met": text.count(STATUS_MET),
        "unmet": text.count(STATUS_UNMET),
        "nt": text.count(STATUS_NT),
    }


def extract_unmet_rows(text: str) -> list[str]:
    unmet = []
    for line in text.splitlines():
        if STATUS_UNMET in line:
            # Extract the requirement description from the table row
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if parts:
                unmet.append(parts[0])
    return unmet


def report_file(path: Path, unmet_only: bool) -> None:
    text = path.read_text(encoding="utf-8")
    counts = parse_status_counts(text)
    total = counts["met"] + counts["unmet"] + counts["nt"]

    if unmet_only and counts["unmet"] == 0:
        return

    print(f"\n{'='*60}")
    print(f"File: {path.name}")
    print(f"  ✓ Met:     {counts['met']}")
    print(f"  ✗ Not met: {counts['unmet']}")
    print(f"  ⬜ N/T:    {counts['nt']}")
    print(f"  Total:     {total}")

    if counts["unmet"] > 0:
        print("  Unmet rows:")
        for row in extract_unmet_rows(text):
            print(f"    - {row}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Report requirement status counts.")
    parser.add_argument("--file", help="Check a single requirements file by name.")
    parser.add_argument("--unmet-only", action="store_true", help="Show only files with unmet requirements.")
    args = parser.parse_args()

    if args.file:
        target = REQUIREMENTS_DIR / args.file
        if not target.exists():
            print(f"Error: {target} not found.")
            return
        files = [target]
    else:
        files = sorted(REQUIREMENTS_DIR.glob("*-requirements.md"))

    if not files:
        print(f"No requirements files found in {REQUIREMENTS_DIR}")
        return

    for path in files:
        report_file(path, args.unmet_only)

    print()


if __name__ == "__main__":
    main()
