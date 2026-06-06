"""
tests/tools/coverage_gap_audit.py
==================================
Automated test coverage gap audit across all source modules and test layers.

For each source module in app/, main.py, server.py:
  - Detects which test files reference it (imports + string mentions)
  - Classifies coverage by layer (unit / component / integration / e2e)
  - Computes a gap score (missing critical layers weighted by importance)

Also pulls requirement gaps from requirements_map.py.

Outputs:
  - Console summary table
  - generated/coverage_gap_audit.md (prioritized gap + extension plan)

Usage
-----
    python tests/tools/coverage_gap_audit.py [--dry-run]
"""

from __future__ import annotations

import ast
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

# Ensure REPO_ROOT is importable so `tests.tools.requirements_map` resolves
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
TESTS_DIR = REPO_ROOT / "tests"
APP_DIR = REPO_ROOT / "app"
GENERATED_DIR = REPO_ROOT / "generated"
OUTPUT_FILE = GENERATED_DIR / "coverage_gap_audit.md"

# Layers in priority order (index 0 = highest priority)
LAYERS = ["unit", "component", "integration", "e2e"]
LAYER_DIRS = {
    "unit": TESTS_DIR / "unit",
    "component": TESTS_DIR / "component",
    "integration": TESTS_DIR / "integration",
    "e2e": TESTS_DIR / "e2e",
}

# Weight assigned to each missing layer (higher = more critical gap)
LAYER_WEIGHTS = {"unit": 4, "component": 3, "integration": 2, "e2e": 1}

# Modules that are intentionally not tested at certain layers
# (false-positive suppression — add entries if needed)
KNOWN_EXCLUSIONS: dict[str, set[str]] = {
    # e.g. "app/core/config.py": {"e2e"}
}

# Modules so thin that unit tests aren't expected
INIT_ONLY_PATTERNS = {"__init__"}


# ---------------------------------------------------------------------------
# Source module discovery
# ---------------------------------------------------------------------------


def discover_source_modules() -> list[Path]:
    """Return all testable source modules (app/**/*.py + main.py + server.py)."""
    modules: list[Path] = []
    for py in sorted(APP_DIR.rglob("*.py")):
        if py.stem in INIT_ONLY_PATTERNS:
            continue
        modules.append(py)
    for name in ("main.py", "server.py"):
        p = REPO_ROOT / name
        if p.exists():
            modules.append(p)
    return modules


def module_key(path: Path) -> str:
    """Return a short display key like 'app/core/config.py'."""
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.name


def module_stem_variants(path: Path) -> set[str]:
    """Return the set of strings a test file might use to reference this module.

    Includes dotted import names, file stems, and partial paths.
    """
    rel = path.relative_to(REPO_ROOT).as_posix()  # e.g. app/core/config.py
    no_ext = rel[: -len(".py")]  # app/core/config
    dotted = no_ext.replace("/", ".")  # app.core.config
    stem = path.stem  # config
    # Also match the parent package segment (e.g. "core.config")
    parts = no_ext.split("/")
    tail_pairs = {".".join(parts[i:]) for i in range(max(0, len(parts) - 2), len(parts))}
    return {rel, no_ext, dotted, stem, *tail_pairs}


# ---------------------------------------------------------------------------
# Test file analysis
# ---------------------------------------------------------------------------


@dataclass
class TestFileInfo:
    path: Path
    layer: str
    references: set[str] = field(default_factory=set)  # module keys it covers


def _extract_imports(source: str, filepath: Path) -> set[str]:
    """Return the set of dotted module names imported in a Python file."""
    names: set[str] = set()
    try:
        tree = ast.parse(source, filename=str(filepath))
    except SyntaxError:
        return names
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                names.add(node.module)
    return names


def _string_mentions(source: str, variants: set[str]) -> bool:
    """Return True if any variant string appears literally in the source."""
    for v in variants:
        if v in source:
            return True
    return False


def analyze_test_files(source_modules: list[Path]) -> list[TestFileInfo]:
    """Build a TestFileInfo for every test file, recording which modules it covers."""
    result: list[TestFileInfo] = []

    # Pre-build variants map
    variants_map: dict[str, set[str]] = {module_key(m): module_stem_variants(m) for m in source_modules}

    for layer, layer_dir in LAYER_DIRS.items():
        for tf in sorted(layer_dir.glob("test_*.py")):
            source = tf.read_text(encoding="utf-8", errors="replace")
            imports = _extract_imports(source, tf)
            info = TestFileInfo(path=tf, layer=layer)

            for mod_key, variants in variants_map.items():
                # Check import-level match
                import_hit = any(
                    imp == v or imp.startswith(v + ".") or v.startswith(imp) for imp in imports for v in variants
                )
                # Fallback: string occurrence in source (catches string-based references)
                string_hit = _string_mentions(source, variants)
                if import_hit or string_hit:
                    info.references.add(mod_key)

            result.append(info)

    return result


# ---------------------------------------------------------------------------
# Coverage matrix computation
# ---------------------------------------------------------------------------


@dataclass
class ModuleCoverage:
    key: str  # e.g. "app/core/config.py"
    covered_by: dict[str, list[Path]] = field(default_factory=dict)  # layer → test files

    def covered_at(self, layer: str) -> bool:
        return bool(self.covered_by.get(layer))

    def gap_layers(self) -> list[str]:
        excluded = KNOWN_EXCLUSIONS.get(self.key, set())
        return [L for L in LAYERS if not self.covered_at(L) and L not in excluded]

    def gap_score(self) -> int:
        return sum(LAYER_WEIGHTS[L] for L in self.gap_layers())

    def coverage_summary(self) -> str:
        return " ".join(("Y" if self.covered_at(L) else "-") for L in LAYERS)


def build_coverage_matrix(source_modules: list[Path], test_files: list[TestFileInfo]) -> list[ModuleCoverage]:
    cov_map: dict[str, ModuleCoverage] = {module_key(m): ModuleCoverage(key=module_key(m)) for m in source_modules}

    for tf in test_files:
        for mod_key in tf.references:
            if mod_key in cov_map:
                cov_map[mod_key].covered_by.setdefault(tf.layer, []).append(tf.path)

    return sorted(cov_map.values(), key=lambda c: (-c.gap_score(), c.key))


# ---------------------------------------------------------------------------
# Requirements gap extraction
# ---------------------------------------------------------------------------


def collect_requirement_gaps() -> list[dict]:
    try:
        from tests.tools.requirements_map import ALL_REQUIREMENTS, _derive_status
    except ImportError:
        return []

    gaps: list[dict] = []
    for source_key, reqs in ALL_REQUIREMENTS.items():
        for req in reqs:
            status = _derive_status(req)
            if status == "gap":
                gaps.append(
                    {
                        "id": req["id"],
                        "description": req["description"],
                        "section": req.get("section", ""),
                        "source": source_key.replace("_", " ").title(),
                    }
                )
    return gaps


# ---------------------------------------------------------------------------
# Extension plan generation
# ---------------------------------------------------------------------------


def _suggest_test_file(mod_key: str, layer: str) -> str:
    """Suggest a test file name for a module + layer pair."""
    stem = Path(mod_key).stem  # e.g. "config"
    return f"tests/{layer}/test_{stem}.py"


def build_extension_plan(matrix: list[ModuleCoverage]) -> list[dict]:
    """Return prioritized list of gap items with suggested actions."""
    plan: list[dict] = []
    for mc in matrix:
        for layer in mc.gap_layers():
            plan.append(
                {
                    "priority": LAYER_WEIGHTS[layer],
                    "module": mc.key,
                    "layer": layer,
                    "suggested_file": _suggest_test_file(mc.key, layer),
                    "action": f"Add {layer} tests for `{mc.key}`",
                }
            )
    return sorted(plan, key=lambda p: -p["priority"])


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------


def print_matrix(matrix: list[ModuleCoverage]) -> None:
    hdr = f"{'Module':<45} {'U':>2} {'C':>2} {'I':>2} {'E':>2}  {'Score':>5}"
    print("\n" + hdr)
    print("-" * len(hdr))
    for mc in matrix:
        cols = " ".join(("Y" if mc.covered_at(L) else "-") for L in ["unit", "component", "integration", "e2e"])
        score_str = f"[{mc.gap_score()}]" if mc.gap_score() > 0 else "  ok "
        print(f"{mc.key:<45} {cols}  {score_str:>5}")
    print()


def print_req_gaps(gaps: list[dict]) -> None:
    if not gaps:
        print("Requirements: no gaps detected.\n")
        return
    print(f"Requirement gaps ({len(gaps)}):")
    print("-" * 60)
    for g in gaps:
        print(f"  [{g['id']}] {g['description'][:60]}  ({g['source']})")
    print()


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

_PRIORITY_LABELS = {4: "P1 — Critical", 3: "P2 — High", 2: "P3 — Medium", 1: "P4 — Low"}


def build_markdown_report(
    matrix: list[ModuleCoverage],
    req_gaps: list[dict],
    plan: list[dict],
) -> str:
    lines: list[str] = []
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines.append(f"# Test Coverage Gap Audit — {ts}\n")
    lines.append(
        "> Generated by `tests/tools/coverage_gap_audit.py`.  \n> Re-run after adding tests to refresh this report.\n"
    )

    # ── 1. Module Coverage Matrix ────────────────────────────────────────
    lines.append("## Module Coverage Matrix\n")
    lines.append("Columns: **U**nit · **C**omponent · **I**ntegration · **E**2E.  ")
    lines.append("`Y` = at least one test file references this module, `-` = gap, `skip` = intentionally excluded.\n")
    lines.append("| Module | U | C | I | E | Gap Score |")
    lines.append("|--------|---|---|---|---|-----------|")
    for mc in sorted(matrix, key=lambda c: c.key):
        cols = " | ".join("Y" if mc.covered_at(L) else "-" for L in LAYERS)
        score_cell = f"**{mc.gap_score()}**" if mc.gap_score() > 0 else "—"
        lines.append(f"| `{mc.key}` | {cols} | {score_cell} |")

    # ── 2. Requirement Gaps ───────────────────────────────────────────────
    lines.append("\n## Requirement Gaps\n")
    if req_gaps:
        lines.append(f"**{len(req_gaps)} functional requirements** have no test coverage:\n")
        lines.append("| ID | Requirement | Source |")
        lines.append("|----|-------------|--------|")
        for g in req_gaps:
            desc = g["description"][:72] + ("…" if len(g["description"]) > 72 else "")
            lines.append(f"| {g['id']} | {desc} | {g['source']} |")
    else:
        lines.append("No requirement gaps detected.")

    # ── 3. Extension Plan ────────────────────────────────────────────────
    lines.append("\n## Extension Plan\n")
    lines.append("Gaps ordered by priority (P1 = unit tests missing = highest risk).\n")

    current_priority: int | None = None
    for item in plan:
        if item["priority"] != current_priority:
            current_priority = item["priority"]
            label = _PRIORITY_LABELS.get(current_priority, f"P{5 - current_priority}")
            lines.append(f"\n### {label}\n")
            lines.append("| Module | Layer | Suggested File |")
            lines.append("|--------|-------|----------------|")
        lines.append(f"| `{item['module']}` | {item['layer']} | `{item['suggested_file']}` |")

    # ── 4. Summary Stats ─────────────────────────────────────────────────
    total = len(matrix)
    fully_covered = sum(1 for mc in matrix if mc.gap_score() == 0)
    gap_count = total - fully_covered
    lines.append("\n## Summary\n")
    lines.append("| Metric | Value |")
    lines.append("|--------|-------|")
    lines.append(f"| Source modules audited | {total} |")
    covered_pct = round(fully_covered / total * 100) if total else 0
    lines.append(f"| Fully covered (all layers) | {fully_covered} ({covered_pct}%) |")
    lines.append(f"| Modules with gaps | {gap_count} ({round(gap_count / total * 100) if total else 0}%) |")
    lines.append(f"| Requirement gaps | {len(req_gaps)} |")
    lines.append(f"| Extension plan items | {len(plan)} |")

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main() -> None:
    dry_run = "--dry-run" in sys.argv

    print("Discovering source modules…")
    source_modules = discover_source_modules()
    print(f"  Found {len(source_modules)} modules.\n")

    print("Analyzing test files…")
    test_files = analyze_test_files(source_modules)
    print(f"  Analyzed {len(test_files)} test files.\n")

    matrix = build_coverage_matrix(source_modules, test_files)
    req_gaps = collect_requirement_gaps()
    plan = build_extension_plan(matrix)

    print_matrix(matrix)
    print_req_gaps(req_gaps)

    gap_count = sum(1 for mc in matrix if mc.gap_score() > 0)
    print(f"Modules with gaps: {gap_count} / {len(matrix)}")
    print(f"Extension plan items: {len(plan)}")
    print(f"Requirement gaps: {len(req_gaps)}\n")

    report = build_markdown_report(matrix, req_gaps, plan)

    if dry_run:
        print("[dry-run] Report preview (first 80 lines):")
        for line in report.splitlines()[:80]:
            print(line)
        print("\n[dry-run] No files written.")
    else:
        GENERATED_DIR.mkdir(exist_ok=True)
        OUTPUT_FILE.write_text(report, encoding="utf-8")
        print(f"Report written: {OUTPUT_FILE.relative_to(REPO_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
