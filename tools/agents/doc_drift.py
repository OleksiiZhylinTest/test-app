"""
Detect documentation drift between AGENTS.md module map, disk, and README.md.

Usage:
  python tools/agents/doc_drift.py
  python tools/agents/doc_drift.py --verbose
"""

import argparse
import re
from pathlib import Path


AGENTS_MD = Path("AGENTS.md")
README_MD = Path("README.md")


def extract_module_map(text: str) -> list[tuple[str, str]]:
    """Extract rows from the '| File | One-line purpose |' table in AGENTS.md."""
    in_table = False
    rows = []
    for line in text.splitlines():
        if "| File |" in line and "One-line purpose" in line:
            in_table = True
            continue
        if in_table:
            if not line.startswith("|"):
                break
            if line.startswith("| ---") or line.startswith("|---"):
                continue
            parts = [p.strip() for p in line.split("|") if p.strip()]
            if len(parts) >= 2:
                rows.append((parts[0].strip("`"), parts[1]))
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Check for documentation drift.")
    parser.add_argument("--verbose", action="store_true", help="Show all checked items.")
    args = parser.parse_args()

    if not AGENTS_MD.exists():
        print(f"Error: {AGENTS_MD} not found. Run from repo root.")
        return

    agents_text = AGENTS_MD.read_text(encoding="utf-8")
    readme_text = README_MD.read_text(encoding="utf-8") if README_MD.exists() else ""
    module_rows = extract_module_map(agents_text)

    missing_files = []
    missing_in_readme = []

    for file_path, purpose in module_rows:
        path = Path(file_path)
        exists = path.exists()

        if not exists:
            missing_files.append(file_path)
        elif args.verbose:
            print(f"  ✓ {file_path} exists")

        if file_path.startswith("app/") and file_path not in readme_text:
            missing_in_readme.append(file_path)

    print("\n=== Doc Drift Report ===")
    print(f"Module map entries checked: {len(module_rows)}")

    if missing_files:
        print(f"\n✗ Files listed in AGENTS.md but missing on disk ({len(missing_files)}):")
        for f in missing_files:
            print(f"  - {f}")
    else:
        print("\n✓ All files listed in AGENTS.md exist on disk.")

    if missing_in_readme:
        print(f"\n⚠ app/ modules in AGENTS.md not mentioned in README.md ({len(missing_in_readme)}):")
        for f in missing_in_readme:
            print(f"  - {f}")
    else:
        print("✓ All app/ modules are mentioned in README.md.")

    print()


if __name__ == "__main__":
    main()
