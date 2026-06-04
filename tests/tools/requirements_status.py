"""
tests/tools/requirements_status.py
====================================
Scans all docs/product/requirements/*.md files and reports Status column counts
(Met / Not met / Not tested) per file.

Exits non-zero when any row carries "✗ Not met" status.

Usage
-----
    # Print summary table
    python tests/tools/requirements_status.py

    # Suppress table; exit code only (useful in CI)
    python tests/tools/requirements_status.py --quiet
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
REQUIREMENTS_DIR = REPO_ROOT / "docs" / "product" / "requirements"

STATUS_MET = "✓ Met"
STATUS_NOT_MET = "✗ Not met"
STATUS_NT = "⬜ N/T"

_STATUS_PATTERN = re.compile(
    r"\|\s*(?P<status>[✓✗⬜][^|]*?)\s*\|?\s*$"
)
_TABLE_ROW = re.compile(r"^\|[^|]+\|")
_SEPARATOR_ROW = re.compile(r"^\|[-| :]+\|")


@dataclass
class FileStats:
    path: Path
    met: int = 0
    not_met: int = 0
    not_tested: int = 0
    unknown: int = 0

    @property
    def total(self) -> int:
        return self.met + self.not_met + self.not_tested + self.unknown


def _find_status_column_index(header_row: str) -> int | None:
    cells = [c.strip() for c in header_row.strip().strip("|").split("|")]
    for i, cell in enumerate(cells):
        if cell.lower() == "status":
            return i
    return None


def _parse_file(md_path: Path) -> FileStats:
    stats = FileStats(path=md_path)
    status_col: int | None = None
    in_table = False

    for line in md_path.read_text(encoding="utf-8").splitlines():
        if not _TABLE_ROW.match(line):
            in_table = False
            status_col = None
            continue
        if _SEPARATOR_ROW.match(line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if status_col is None:
            # Try to identify this as a header row
            idx = _find_status_column_index(line)
            if idx is not None:
                status_col = idx
                in_table = True
            continue
        if not in_table:
            continue
        if status_col >= len(cells):
            continue
        val = cells[status_col]
        if STATUS_MET in val:
            stats.met += 1
        elif STATUS_NOT_MET in val:
            stats.not_met += 1
        elif STATUS_NT in val:
            stats.not_tested += 1
        elif val:
            stats.unknown += 1

    return stats


def _collect() -> list[FileStats]:
    md_files = sorted(REQUIREMENTS_DIR.glob("*.md"))
    if not md_files:
        print(f"No .md files found under {REQUIREMENTS_DIR}", file=sys.stderr)
        sys.exit(2)
    return [_parse_file(p) for p in md_files if p.name != "README.md"]


def _print_table(stats: list[FileStats]) -> None:
    col_w = max(len(s.path.name) for s in stats) + 2
    header = f"{'File':<{col_w}}  {'Total':>6}  {'[MET]':>7}  {'[FAIL]':>8}  {'[N/T]':>7}  {'Unknown':>8}"
    print(header)
    print("-" * len(header))
    for s in stats:
        flag = "  <- FAIL" if s.not_met else ""
        print(
            f"{s.path.name:<{col_w}}  {s.total:>6}  {s.met:>7}  {s.not_met:>8}  {s.not_tested:>7}  {s.unknown:>8}{flag}"
        )
    print("-" * len(header))
    totals = FileStats(path=REQUIREMENTS_DIR)
    for s in stats:
        totals.met += s.met
        totals.not_met += s.not_met
        totals.not_tested += s.not_tested
        totals.unknown += s.unknown
    print(
        f"{'TOTAL':<{col_w}}  {totals.total:>6}  {totals.met:>7}  {totals.not_met:>8}  {totals.not_tested:>7}  {totals.unknown:>8}"
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Requirements status audit")
    parser.add_argument("--quiet", action="store_true", help="Suppress output; exit code only")
    args = parser.parse_args(argv)

    all_stats = _collect()
    failing = [s for s in all_stats if s.not_met > 0]

    if not args.quiet:
        _print_table(all_stats)
        if failing:
            print(f"\n{len(failing)} file(s) have unmet requirements:")
            for s in failing:
                print(f"  {s.path.name}: {s.not_met} [FAIL]")

    return 1 if failing else 0


if __name__ == "__main__":
    sys.exit(main())
