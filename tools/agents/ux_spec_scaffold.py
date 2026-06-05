"""
Generate a standard UX specification document for a new feature area.

Usage:
  python tools/agents/ux_spec_scaffold.py <feature-name>
  python tools/agents/ux_spec_scaffold.py dashboard-filters
"""

import argparse
import sys
from datetime import date, datetime
from pathlib import Path


TMP_DIR = Path("generated/tmp")

TEMPLATE = """\
# UX Specification — {title}

**Date:** {date}
**Status:** Draft
**Feature area:** {feature_name}
**Spec author:** GH Business Analyst
**Review required by:** GH Product Owner

---

## Overview

> Describe the user-facing feature and its purpose in 2–3 sentences.

## User Goal

> As a [role], I want [action], so that [outcome].

## User Flow

> Step-by-step description of the interaction from entry point to completion.

1. User navigates to...
2. User selects...
3. System responds with...
4. User confirms...

## Component Inventory

| Component | Type | Location | Notes |
|-----------|------|----------|-------|
| | | | |

## Accessibility Requirements

- [ ] All interactive controls have `aria-label` attributes.
- [ ] Color contrast meets WCAG AA (4.5:1 normal text, 3:1 large text).
- [ ] Keyboard navigation is fully supported.
- [ ] Focus order is logical and follows visual layout.
- [ ] Error states are announced via ARIA live regions.

## Responsive Behavior

| Breakpoint | Layout behavior |
|-----------|----------------|
| Mobile (< 768px) | |
| Tablet (768–1024px) | |
| Desktop (> 1024px) | |

## Design Constraints

- No fixed-width `px` values for containers (use `%`, `rem`, Grid, or Flexbox).
- No logic in `.j2` templates — pre-compute all values in `report_html.py`.
- Semantic HTML only: `<section>`, `<table>`, `<figure>`, `<nav>`.

## Open Questions

1. [ ] Question 1
2. [ ] Question 2

---

*Review this spec with `gh-product-owner` before handing to `gh-developer`.*
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Scaffold a UX specification document.")
    parser.add_argument("feature_name", help="Feature name (use hyphens for spaces, e.g. dashboard-filters)")
    args = parser.parse_args()

    feature_name = args.feature_name.strip().lower().replace(" ", "-")
    title = feature_name.replace("-", " ").title()
    today = date.today().isoformat()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    content = TEMPLATE.format(title=title, date=today, feature_name=feature_name)

    TMP_DIR.mkdir(parents=True, exist_ok=True)
    output_path = TMP_DIR / f"ux_spec_{feature_name}_{timestamp}.md"
    output_path.write_text(content, encoding="utf-8")

    print(f"UX spec created: {output_path}")


if __name__ == "__main__":
    main()
