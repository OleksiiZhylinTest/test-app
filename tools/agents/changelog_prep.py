"""
Scaffold a CHANGELOG.md entry from git commits since the last tag.

Usage:
  python tools/agents/changelog_prep.py
  python tools/agents/changelog_prep.py --write
  python tools/agents/changelog_prep.py --dry-run
"""

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path


CHANGELOG_MD = Path("CHANGELOG.md")
TMP_DIR = Path("generated/tmp")

CATEGORY_MAP = {
    "feat": "Added",
    "fix": "Fixed",
    "refactor": "Changed",
    "perf": "Changed",
    "docs": "Changed",
    "remove": "Removed",
    "revert": "Removed",
    "BREAKING": "Breaking",
    "break": "Breaking",
}


def get_last_tag() -> str:
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def get_commits_since(tag: str) -> list[str]:
    ref = f"{tag}..HEAD" if tag else "HEAD"
    try:
        result = subprocess.run(
            ["git", "log", ref, "--oneline"],
            capture_output=True, text=True, check=True,
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        return []


def categorize(commits: list[str]) -> dict[str, list[str]]:
    categories: dict[str, list[str]] = {c: [] for c in ["Added", "Changed", "Fixed", "Removed", "Breaking"]}
    for commit in commits:
        parts = commit.split(" ", 1)
        message = parts[1] if len(parts) > 1 else commit
        matched = False
        for prefix, category in CATEGORY_MAP.items():
            if message.lower().startswith(prefix.lower()):
                categories[category].append(message)
                matched = True
                break
        if not matched:
            categories["Changed"].append(message)
    return categories


def format_entry(categories: dict[str, list[str]], tag: str) -> str:
    today = date.today().isoformat()
    version = "Unreleased" if not tag else f"Post-{tag}"
    lines = [f"## [{version}] — {today}\n"]
    for section in ["Added", "Changed", "Fixed", "Removed", "Breaking"]:
        items = categories.get(section, [])
        if items:
            lines.append(f"### {section}")
            for item in items:
                lines.append(f"- {item}")
            lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a CHANGELOG entry from recent commits.")
    parser.add_argument("--write", action="store_true", help="Prepend entry to CHANGELOG.md.")
    parser.add_argument("--dry-run", action="store_true", help="Print entry; do not write anything.")
    args = parser.parse_args()

    tag = get_last_tag()
    commits = get_commits_since(tag)

    if not commits:
        print("No commits found since last tag (or no tags exist).")
        sys.exit(0)

    categories = categorize(commits)
    entry = format_entry(categories, tag)

    print(entry)

    if args.dry_run:
        return

    if args.write:
        TMP_DIR.mkdir(parents=True, exist_ok=True)
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        tmp_path = TMP_DIR / f"changelog_prep_{timestamp}.md"
        tmp_path.write_text(entry, encoding="utf-8")
        print(f"Saved to: {tmp_path}")

        if CHANGELOG_MD.exists():
            existing = CHANGELOG_MD.read_text(encoding="utf-8")
            CHANGELOG_MD.write_text(entry + "\n" + existing, encoding="utf-8")
        else:
            CHANGELOG_MD.write_text(entry, encoding="utf-8")
        print(f"Prepended to: {CHANGELOG_MD}")


if __name__ == "__main__":
    main()
