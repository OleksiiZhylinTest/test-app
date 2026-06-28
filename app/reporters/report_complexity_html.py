"""Generate HTML complexity audit report via Jinja2."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).resolve().parent.parent.parent / "ui" / "templates"


def generate_complexity_html(report: dict[str, Any], output_path: Path) -> None:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=True)
    template = env.get_template("complexity_audit.html.j2")
    html = template.render(report=report)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(html, encoding="utf-8")
