#!/usr/bin/env python3
"""docs_audit.py — Portable documentation audit for any repository.

Scans all documentation files, runs structural/content/format/link/gap checks,
and emits a scored markdown report with a prioritized improvement plan.

Usage:
    python tools/docs_audit.py [ROOT_DIR] [--output PATH] [--json]

    ROOT_DIR defaults to the current working directory.
    --output writes the report to a file; default is stdout.
    --json   also writes a machine-readable JSON findings file alongside the report.
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# ── Configuration ─────────────────────────────────────────────────────────────

DOC_EXTENSIONS = {".md", ".rst"}
CODE_EXTENSIONS = {".py", ".ts", ".js", ".go", ".java", ".rb", ".cs", ".cpp", ".c", ".rs"}

EXCLUDE_DIRS = {
    "node_modules", ".git", ".github", ".venv", "venv", "__pycache__",
    "dist", "build", ".claude", "generated", ".mypy_cache",
    ".pytest_cache", "htmlcov", ".tox",
}

PLACEHOLDER_PATTERNS = [
    r"\bTODO\b",
    r"\bTBD\b",
    r"\bFIXME\b",
    r"\[NEEDS CLARIFICATION\]",
    r"\[PLACEHOLDER\]",
    r"\[WIP\]",
    r"Lorem ipsum",
]

STUB_WORD_THRESHOLD = 50
MIN_SECTION_WORDS = 15

SEVERITY_CRITICAL = "Critical"
SEVERITY_WARNING = "Warning"
SEVERITY_INFO = "Info"

# Files whose purpose is to be entry-points, not linked from elsewhere
ROOT_ENTRY_NAMES = {"readme", "index", "toc", "contents", "changelog", "contributing", "license", "claude", "agents"}

# Filenames exempt from kebab-case convention
CONVENTION_EXEMPT = {"README", "CHANGELOG", "CLAUDE", "AGENTS", "CONTRIBUTING", "LICENSE", "CODEOWNERS", "MEMORY"}


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class Finding:
    severity: str
    category: str
    file: str
    message: str
    line: int = 0


@dataclass
class DocFile:
    path: Path
    rel_path: str
    content: str
    lines: list
    word_count: int
    headings: list       # [(level: int, text: str, line_num: int)]
    internal_links: list  # [(text: str, target: str, line_num: int)]


# ── Discovery ─────────────────────────────────────────────────────────────────

def _is_excluded(path: Path) -> bool:
    return any(part in EXCLUDE_DIRS for part in path.parts)


def _read_safe(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""


def _extract_headings_md(lines: list) -> list:
    result = []
    in_fence = False
    for i, line in enumerate(lines, 1):
        if re.match(r"^(`{3,}|~{3,})", line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = re.match(r"^(#{1,6})\s+(.+)", line)
        if m:
            result.append((len(m.group(1)), m.group(2).strip(), i))
    return result


def _extract_headings_rst(lines: list) -> list:
    # RST headings: line followed by a line of punctuation chars of equal or greater length
    ADORNMENT = set("!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~")
    result = []
    levels: dict = {}
    level_counter = 0
    for i in range(len(lines) - 1):
        text = lines[i].rstrip()
        under = lines[i + 1].rstrip()
        if (
            under
            and len(under) >= len(text)
            and len(set(under)) == 1
            and under[0] in ADORNMENT
            and text
        ):
            char = under[0]
            if char not in levels:
                level_counter += 1
                levels[char] = level_counter
            result.append((levels[char], text, i + 1))
    return result


def _extract_links(lines: list, suffix: str) -> list:
    links = []
    if suffix == ".md":
        in_fence = False
        for i, line in enumerate(lines, 1):
            if re.match(r"^(`{3,}|~{3,})", line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", line):
                links.append((m.group(1), m.group(2), i))
    return links


def discover_docs(root: Path) -> list:
    docs = []
    for path in sorted(root.rglob("*")):
        if _is_excluded(path):
            continue
        if not path.is_file() or path.suffix.lower() not in DOC_EXTENSIONS:
            continue
        content = _read_safe(path)
        lines = content.splitlines()
        suffix = path.suffix.lower()
        docs.append(DocFile(
            path=path,
            rel_path=str(path.relative_to(root)).replace("\\", "/"),
            content=content,
            lines=lines,
            word_count=len(content.split()),
            headings=_extract_headings_md(lines) if suffix == ".md" else _extract_headings_rst(lines),
            internal_links=_extract_links(lines, suffix),
        ))
    return docs


def discover_code_modules(root: Path) -> list:
    modules = []
    for path in sorted(root.rglob("*")):
        if _is_excluded(path) or not path.is_file():
            continue
        if path.suffix.lower() in CODE_EXTENSIONS:
            modules.append(path)
    return modules


# ── Checks ────────────────────────────────────────────────────────────────────

def check_stubs(docs: list) -> list:
    findings = []
    for doc in docs:
        if doc.word_count < STUB_WORD_THRESHOLD:
            sev = SEVERITY_CRITICAL if doc.word_count < 10 else SEVERITY_WARNING
            findings.append(Finding(
                sev, "Content", doc.rel_path,
                f"Stub file ({doc.word_count} words, threshold {STUB_WORD_THRESHOLD})",
            ))
    return findings


def check_placeholders(docs: list) -> list:
    pattern = re.compile("|".join(PLACEHOLDER_PATTERNS), re.IGNORECASE)
    findings = []
    for doc in docs:
        for i, line in enumerate(doc.lines, 1):
            if pattern.search(line):
                findings.append(Finding(
                    SEVERITY_WARNING, "Content", doc.rel_path,
                    f"Placeholder text: `{line.strip()[:80]}`", i,
                ))
    return findings


def check_heading_hierarchy(docs: list) -> list:
    findings = []
    for doc in docs:
        if not doc.headings:
            if doc.word_count >= STUB_WORD_THRESHOLD:
                findings.append(Finding(
                    SEVERITY_WARNING, "Format", doc.rel_path,
                    "No headings — document lacks structure",
                ))
            continue
        prev = 0
        for level, text, line_num in doc.headings:
            if prev and level > prev + 1:
                findings.append(Finding(
                    SEVERITY_WARNING, "Format", doc.rel_path,
                    f"Heading jump H{prev}->H{level} at `{text}`", line_num,
                ))
            prev = level
    return findings


def check_broken_links(docs: list, root: Path) -> list:
    findings = []
    for doc in docs:
        for text, target, line_num in doc.internal_links:
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_path = target.split("#")[0]
            if not target_path:
                continue
            # Skip template placeholders (e.g. NNNN-slug.md in ADR templates)
            if re.search(r"\bNNNN\b", target_path):
                continue
            resolved = (doc.path.parent / target_path).resolve()
            if not resolved.exists():
                findings.append(Finding(
                    SEVERITY_CRITICAL, "Links", doc.rel_path,
                    f"Broken link: `[{text}]({target})`", line_num,
                ))
    return findings


def check_orphans(docs: list, root: Path) -> list:
    all_targets: set = set()
    for doc in docs:
        for _, target, _ in doc.internal_links:
            if target.startswith(("http://", "https://", "#", "mailto:")):
                continue
            target_clean = target.split("#")[0]
            if not target_clean:
                continue
            resolved = (doc.path.parent / target_clean).resolve()
            try:
                all_targets.add(str(resolved.relative_to(root)).replace("\\", "/"))
            except ValueError:
                pass

    findings = []
    for doc in docs:
        if doc.path.stem.lower() in ROOT_ENTRY_NAMES:
            continue
        if doc.path.parent == root:
            continue
        if doc.rel_path not in all_targets:
            findings.append(Finding(
                SEVERITY_INFO, "Structure", doc.rel_path,
                "Orphaned document — not referenced by any other doc",
            ))
    return findings


def check_naming_conventions(docs: list) -> list:
    findings = []
    for doc in docs:
        stem = doc.path.stem
        if stem in CONVENTION_EXEMPT:
            continue
        if re.search(r"[A-Z]", stem):
            findings.append(Finding(
                SEVERITY_INFO, "Format", doc.rel_path,
                f"Mixed-case filename `{doc.path.name}` — prefer kebab-case",
            ))
        elif "_" in stem:
            findings.append(Finding(
                SEVERITY_INFO, "Format", doc.rel_path,
                f"Underscore in filename `{doc.path.name}` — prefer kebab-case",
            ))
    return findings


def check_code_coverage(docs: list, modules: list, root: Path) -> list:
    SKIP_STEMS = {"__init__", "__main__", "conftest", "setup", "settings", "manage"}
    doc_corpus = " ".join(d.content.lower() for d in docs)
    doc_stems = {d.path.stem.lower() for d in docs}

    findings = []
    for module in modules:
        stem = module.stem.lower()
        if stem in SKIP_STEMS:
            continue
        rel = str(module.relative_to(root)).replace("\\", "/")
        if stem not in doc_stems and stem not in doc_corpus:
            findings.append(Finding(
                SEVERITY_INFO, "Gaps", rel,
                f"Code module `{rel}` has no documentation mention",
            ))
    return findings


def check_duplicate_titles(docs: list) -> list:
    """Flag H1 titles that appear in multiple files — likely duplication or contradiction."""
    h1_sources: dict = defaultdict(list)
    for doc in docs:
        for level, text, _ in doc.headings:
            if level == 1:
                h1_sources[text.lower().strip()].append(doc.rel_path)

    findings = []
    for title, sources in h1_sources.items():
        if len(sources) > 1:
            findings.append(Finding(
                SEVERITY_WARNING, "Contradictions", sources[0],
                f"H1 `{title}` appears in {len(sources)} files: {', '.join(f'`{s}`' for s in sources)} — duplication or contradiction",
            ))
    return findings


def check_empty_sections(docs: list) -> list:
    findings = []
    for doc in docs:
        headings = doc.headings
        for i, (level, text, line_num) in enumerate(headings):
            if level > 2:
                continue
            # If the next heading is a sub-level, this section uses sub-sections — not thin
            if i + 1 < len(headings) and headings[i + 1][0] > level:
                continue
            start = line_num  # 1-indexed; lines[] is 0-indexed → lines[line_num:]
            end = headings[i + 1][2] - 1 if i + 1 < len(headings) else len(doc.lines)
            section_words = sum(len(l.split()) for l in doc.lines[start:end] if l.strip())
            if section_words < MIN_SECTION_WORDS:
                findings.append(Finding(
                    SEVERITY_INFO, "Content", doc.rel_path,
                    f"Thin section `{'#' * level} {text}` ({section_words} words)", line_num,
                ))
    return findings


def check_missing_overview(docs: list, root: Path) -> list:
    """Warn if a docs subdirectory contains no README or index file."""
    doc_dirs: set = set()
    for doc in docs:
        if doc.path.parent != root:
            doc_dirs.add(doc.path.parent)

    findings = []
    for d in sorted(doc_dirs):
        has_index = any(
            (d / name).exists()
            for ext in DOC_EXTENSIONS
            for name in (f"README{ext}", f"index{ext}", f"README{ext.upper()}")
        )
        if not has_index:
            rel = str(d.relative_to(root)).replace("\\", "/")
            findings.append(Finding(
                SEVERITY_INFO, "Structure", rel + "/",
                "Directory has no README or index file",
            ))
    return findings


# ── Report ────────────────────────────────────────────────────────────────────

def _sev_order(f: Finding) -> int:
    return {SEVERITY_CRITICAL: 0, SEVERITY_WARNING: 1, SEVERITY_INFO: 2}.get(f.severity, 3)


def generate_report(findings: list, docs: list, modules: list, root: Path) -> str:
    by_sev: dict = defaultdict(list)
    by_cat: dict = defaultdict(list)
    for f in findings:
        by_sev[f.severity].append(f)
        by_cat[f.category].append(f)

    n_critical = len(by_sev.get(SEVERITY_CRITICAL, []))
    n_warning = len(by_sev.get(SEVERITY_WARNING, []))
    n_info = len(by_sev.get(SEVERITY_INFO, []))
    score = max(0, 100 - n_critical * 10 - n_warning * 3 - n_info)

    lines = [
        "# Documentation Audit Report",
        "",
        f"**Repository:** `{root}`",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        f"**Docs scanned:** {len(docs)}  |  "
        f"**Code modules:** {len(modules)}  |  "
        f"**Total findings:** {len(findings)}",
        "",
        f"## Health Score: {score}/100",
        "",
        "| Severity | Count |",
        "|----------|------:|",
        f"| Critical | {n_critical} |",
        f"| Warning  | {n_warning} |",
        f"| Info     | {n_info} |",
        "",
    ]

    # Prioritized improvement plan
    lines += [
        "## Improvement Plan",
        "",
        "### P0 — Fix Immediately (Critical)",
    ]
    crits = sorted(by_sev.get(SEVERITY_CRITICAL, []), key=lambda f: f.file)
    if crits:
        for f in crits:
            loc = f" :{f.line}" if f.line else ""
            lines.append(f"- [ ] `{f.file}`{loc} — {f.message}")
    else:
        lines.append("_None._")

    lines += ["", "### P1 — Fix Before Next Release (Warnings)"]
    warns = sorted(by_sev.get(SEVERITY_WARNING, []), key=lambda f: (f.category, f.file))
    if warns:
        for f in warns:
            loc = f" :{f.line}" if f.line else ""
            lines.append(f"- [ ] `{f.file}`{loc} — {f.message}")
    else:
        lines.append("_None._")

    lines += ["", "### P2 — Improve When Possible (Info)"]
    infos = sorted(by_sev.get(SEVERITY_INFO, []), key=lambda f: (f.category, f.file))
    if infos:
        for f in infos:
            loc = f" :{f.line}" if f.line else ""
            lines.append(f"- [ ] `{f.file}`{loc} — {f.message}")
    else:
        lines.append("_None._")

    # Findings by category
    lines += ["", "---", "", "## Findings by Category"]
    for cat in sorted(by_cat):
        cat_findings = sorted(by_cat[cat], key=_sev_order)
        lines += ["", f"### {cat} ({len(cat_findings)} findings)"]
        for f in cat_findings:
            loc = f" :{f.line}" if f.line else ""
            lines.append(f"- **[{f.severity}]** `{f.file}`{loc} — {f.message}")

    # Document inventory
    file_issue_count: dict = defaultdict(int)
    for f in findings:
        file_issue_count[f.file] += 1

    lines += [
        "", "---", "", "## Document Inventory",
        "",
        "| File | Words | Headings | Issues |",
        "|------|------:|---------:|-------:|",
    ]
    for doc in sorted(docs, key=lambda d: d.rel_path):
        issues = file_issue_count.get(doc.rel_path, 0)
        lines.append(
            f"| `{doc.rel_path}` | {doc.word_count} | {len(doc.headings)} | {issues} |"
        )

    return "\n".join(lines) + "\n"


# ── Entry point ───────────────────────────────────────────────────────────────

def audit(root: Path) -> tuple:
    docs = discover_docs(root)
    modules = discover_code_modules(root)

    findings: list = []
    findings += check_stubs(docs)
    findings += check_placeholders(docs)
    findings += check_heading_hierarchy(docs)
    findings += check_broken_links(docs, root)
    findings += check_orphans(docs, root)
    findings += check_naming_conventions(docs)
    findings += check_code_coverage(docs, modules, root)
    findings += check_duplicate_titles(docs)
    findings += check_empty_sections(docs)
    findings += check_missing_overview(docs, root)

    return findings, docs, modules


def main() -> None:
    parser = argparse.ArgumentParser(description="Documentation audit tool")
    parser.add_argument("root", nargs="?", default=".", help="Repository root (default: .)")
    parser.add_argument("--output", "-o", default=None, help="Output file (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Write JSON findings alongside report")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.exists():
        print(f"Error: {root} does not exist", file=sys.stderr)
        sys.exit(1)

    findings, docs, modules = audit(root)
    report = generate_report(findings, docs, modules, root)

    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
        print(f"Report written to {out}")
        if args.json:
            json_out = out.with_suffix(".json")
            json_out.write_text(
                json.dumps(
                    [{"severity": f.severity, "category": f.category,
                      "file": f.file, "message": f.message, "line": f.line}
                     for f in findings],
                    indent=2,
                ),
                encoding="utf-8",
            )
            print(f"JSON findings written to {json_out}")
    else:
        sys.stdout.buffer.write(report.encode("utf-8", errors="replace"))
        sys.stdout.buffer.flush()


if __name__ == "__main__":
    main()
