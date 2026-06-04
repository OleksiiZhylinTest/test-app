#!/usr/bin/env python3
"""
Scaffold a new Architecture Decision Record draft in generated/tmp/.

Usage:
    python tools/new_adr.py "Short decision title"

Output:
    generated/tmp/adr-draft-<slugified-title>.md

The file is a draft only. Move it to docs/development/adr/ and rename it
following the existing sequence (e.g. 0004-title.md) only after human approval.
"""
import re
import sys
from datetime import date
from pathlib import Path

TEMPLATE = """\
# ADR-DRAFT: {title}

- **Date**: {date}
- **Status**: Draft
- **Deciders**: GH Principal Solution Architect, (add names)

## Context

<!-- What is the issue or constraint that motivates this decision? -->

## Decision

<!-- What is the chosen option? -->

## Options Considered

| Option | Pro | Con |
|--------|-----|-----|
| (A) | | |
| (B) | | |

## Consequences

<!-- What are the positive and negative outcomes of this decision? -->

## Risks

<!-- What could go wrong? What is the mitigation? -->

## References

<!-- Links to relevant code, docs, or external standards -->
"""


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s_]+", "-", text)


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tools/new_adr.py \"Short decision title\"", file=sys.stderr)
        sys.exit(1)

    title = " ".join(sys.argv[1:])
    slug = slugify(title)
    out_dir = Path("generated/tmp")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"adr-draft-{slug}.md"

    out_path.write_text(
        TEMPLATE.format(title=title, date=date.today().isoformat()),
        encoding="utf-8",
    )
    print(f"ADR draft created: {out_path}")
    print("Review, fill in the sections, then move to docs/development/adr/ after human approval.")


if __name__ == "__main__":
    main()
