"""Generate Markdown complexity audit report."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def generate_complexity_md(report: dict[str, Any], output_path: Path) -> None:
    s = report["summary"]
    lines = [
        "# Design Complexity Audit Report",
        "",
        f"Generated: {report['generated_at']}",
        f"Modules scanned: {report['module_count']} "
        f"(High: {s['high_count']}, Medium: {s['medium_count']}, Low: {s['low_count']}, Error: {s['error_count']})",
        "",
        "## Module Scores",
        "",
        "| Module | LOC | Functions | CC | LOC Score | Coupling | Cohesion | Composite | Class |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for score in report["scores"]:
        if score["classification"] == "Error":
            lines.append(f"| {score['module']} | N/A | N/A | N/A | N/A | N/A | N/A | N/A | Error ⚠ |")
        else:
            lines.append(
                f"| {score['module']} "
                f"| {score['loc']} "
                f"| {score['function_count']} "
                f"| {score['cc_score']:.1f} "
                f"| {score['loc_score']:.1f} "
                f"| {score['coupling_score']:.1f} "
                f"| {score['cohesion_score']:.1f} "
                f"| {score['composite_score']:.2f} "
                f"| {score['classification']} |"
            )

    recs = report["recommendations"]
    lines += ["", "## Improvement Plan", ""]
    if not recs:
        lines.append("No high-complexity modules found.")
    else:
        current_module = None
        for rec in recs:
            if rec["module"] != current_module:
                current_module = rec["module"]
                lines.append(f"### {current_module}")
            lines.append(f"- {rec['action']}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
