"""
tests/tools/feature_screenshot_audit.py
=========================================
Compares feature section headings listed in docs/product/features/features.md
against screenshot filenames in docs/product/features/screenshots/.

Reports:
  - Features without any corresponding screenshot
  - Screenshots without a matching feature heading

Usage
-----
    python tests/tools/feature_screenshot_audit.py

    # Exit non-zero when mismatches are found
    python tests/tools/feature_screenshot_audit.py --strict
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
FEATURES_MD = REPO_ROOT / "docs" / "product" / "features" / "features.md"
SCREENSHOTS_DIR = REPO_ROOT / "docs" / "product" / "features" / "screenshots"

_HEADING_RE = re.compile(r"^#{2,4}\s+(.+)$", re.MULTILINE)
_SCREENSHOT_NUM_RE = re.compile(r"^\d+[a-z]?_")


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", "_", text.strip())
    return text


def _extract_feature_names(md_path: Path) -> list[str]:
    content = md_path.read_text(encoding="utf-8")
    return [m.group(1).strip() for m in _HEADING_RE.finditer(content)]


def _screenshot_stem(filename: str) -> str:
    name = Path(filename).stem
    name = _SCREENSHOT_NUM_RE.sub("", name)
    return name


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Feature/screenshot alignment audit")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit non-zero when any mismatch is found",
    )
    args = parser.parse_args(argv)

    if not FEATURES_MD.exists():
        print(f"features.md not found: {FEATURES_MD}", file=sys.stderr)
        return 2
    if not SCREENSHOTS_DIR.exists():
        print(f"Screenshots directory not found: {SCREENSHOTS_DIR}", file=sys.stderr)
        return 2

    feature_names = _extract_feature_names(FEATURES_MD)
    feature_keys = {_normalize(f): f for f in feature_names}

    screenshot_files = sorted(SCREENSHOTS_DIR.glob("*.png"))
    screenshot_keys = {_normalize(_screenshot_stem(p.name)): p.name for p in screenshot_files}

    unmatched_features: list[str] = []
    for key, name in sorted(feature_keys.items()):
        if not any(key in sk or sk in key for sk in screenshot_keys):
            unmatched_features.append(name)

    unmatched_screenshots: list[str] = []
    for key, filename in sorted(screenshot_keys.items()):
        if not any(key in fk or fk in key for fk in feature_keys):
            unmatched_screenshots.append(filename)

    has_issues = bool(unmatched_features or unmatched_screenshots)

    print(f"Features in features.md:   {len(feature_names)}")
    print(f"Screenshots in directory:  {len(screenshot_files)}")
    print()

    if unmatched_features:
        print(f"Features without a screenshot ({len(unmatched_features)}):")
        for name in unmatched_features:
            print(f"  [MISS] {name}")
        print()

    if unmatched_screenshots:
        print(f"Screenshots without a matching feature ({len(unmatched_screenshots)}):")
        for filename in unmatched_screenshots:
            print(f"  [ORPHAN] {filename}")
        print()

    if not has_issues:
        print("All features and screenshots are aligned.")

    return 1 if (args.strict and has_issues) else 0


if __name__ == "__main__":
    sys.exit(main())
