"""Generate Markdown report from metrics dict."""

from __future__ import annotations

from pathlib import Path

DEFAULT_OUTPUT = Path(__file__).resolve().parent.parent.parent / "report.md"


def _md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Build a Markdown table."""
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


_SECTION_KEYS = [
    "velocity_trend",
    "ai_assistance_trend",
    "ai_usage_details",
    "dau",
    "dau_trend",
    "sprint_issues",
    "diagnostics",
]


def generate_md(
    metrics: dict,
    output_path: Path = DEFAULT_OUTPUT,
    section_visibility: dict | None = None,
) -> None:
    """Build Markdown from metrics dict and write to output_path.

    section_visibility controls which sections appear in the output.
    Defaults to all sections visible.
    """
    if section_visibility is None:
        section_visibility = {k: True for k in _SECTION_KEYS}
    unit_label = "tickets" if metrics.get("estimation_type") == "JiraTickets" else "points"
    report_name = metrics.get("report_name") or "AI Adoption Metrics Report"
    parts = [
        f"# {report_name}",
        "",
        f"Reported Date:  {(metrics.get('generated_at') or '')[:10]}",
    ]
    if metrics.get("project_type"):
        parts.append(f"Project Type:   {metrics['project_type']}")
    if metrics.get("estimation_type"):
        parts.append(f"Estimation:     {metrics['estimation_type']}")
    parts.append("")

    velocity = metrics.get("velocity") or []
    if section_visibility.get("velocity_trend", True):
        if velocity:
            parts.append("## Velocity trend")
            parts.append("")
            # Bar chart: proportional bars (max 40 chars width)
            max_vel = max((row.get("velocity") or 0) for row in velocity) or 1
            for row in velocity:
                v = row.get("velocity") or 0
                bar_len = int(40 * v / max_vel) if max_vel else 0
                bar = "█" * bar_len
                parts.append(f"- **{row.get('sprint_name', '')}**: {bar} {v}")
            parts.append("")

            def _date_fmt(s: str | None) -> str:
                return ((s or "")[:10] or "—").strip() or "—"

            headers = ["Sprint", "Start", "End", f"Velocity ({unit_label})", "Issues done"]
            rows = [
                [
                    row.get("sprint_name", ""),
                    _date_fmt(row.get("start_date")),
                    _date_fmt(row.get("end_date")),
                    row.get("velocity", 0),
                    row.get("issue_count", 0),
                ]
                for row in velocity
            ]
            parts.append(_md_table(headers, rows))
            parts.append("")
        else:
            parts.append("## Velocity trend")
            parts.append("")
            parts.append("*No velocity data.*")
            parts.append("")

    ai_trend = metrics.get("ai_assistance_trend") or []
    if section_visibility.get("ai_assistance_trend", True):
        parts.append("## AI Assistance Trend")
        parts.append("")
        ai_assisted_label = metrics.get("ai_assisted_label") or ""
        ai_exclude_labels = metrics.get("ai_exclude_labels") or []
        if ai_assisted_label:
            parts.append(f"AI-assisted label: `{ai_assisted_label}`")
        if ai_exclude_labels:
            parts.append(f"Excluded labels: {', '.join(f'`{lbl}`' for lbl in ai_exclude_labels)}")
        if ai_assisted_label or ai_exclude_labels:
            parts.append("")
        if ai_trend:
            max_pct = max((row.get("ai_pct") or 0) for row in ai_trend) or 1
            for row in ai_trend:
                pct = row.get("ai_pct") or 0
                bar_len = int(40 * pct / max_pct) if max_pct else 0
                bar = "█" * bar_len
                parts.append(f"- **{row.get('sprint_name', '')}**: {bar} {pct}%")
            parts.append("")

            def _date_fmt(s: str | None) -> str:
                return ((s or "")[:10] or "—").strip() or "—"

            sp_col = unit_label.capitalize()
            headers = ["Sprint", "Start", "End", f"Total {sp_col}", f"AI {sp_col}", "AI %"]
            rows = [
                [
                    row.get("sprint_name", ""),
                    _date_fmt(row.get("start_date")),
                    _date_fmt(row.get("end_date")),
                    row.get("total_sp", 0),
                    row.get("ai_sp", 0),
                    f"{row.get('ai_pct', 0)}%",
                ]
                for row in ai_trend
            ]
            parts.append(_md_table(headers, rows))
            parts.append("")
        else:
            parts.append("*No AI assistance data.*")
            parts.append("")

    ai_usage = metrics.get("ai_usage_details") or {}
    if section_visibility.get("ai_usage_details", True):
        parts.append("## AI Usage Details")
        parts.append("")
        total_ai = ai_usage.get("ai_assisted_issue_count", 0)
        parts.append(f"**{total_ai}** ticket(s) marked as AI-assisted")
        parts.append("")
        tool_breakdown = ai_usage.get("tool_breakdown") or []
        action_breakdown = ai_usage.get("action_breakdown") or []
        if tool_breakdown:
            parts.append("**AI Tools**")
            parts.append("")
            parts.append(
                _md_table(
                    ["Label", "Count", "%"],
                    [[r["label"], r["count"], f"{r['pct']}%"] for r in tool_breakdown],
                )
            )
            parts.append("")
        if action_breakdown:
            parts.append("**AI Use Cases**")
            parts.append("")
            parts.append(
                _md_table(
                    ["Label", "Count", "%"],
                    [[r["label"], r["count"], f"{r['pct']}%"] for r in action_breakdown],
                )
            )
            parts.append("")
        if not tool_breakdown and not action_breakdown and total_ai == 0:
            parts.append("*No AI usage data.*")
            parts.append("")

    dau = metrics.get("dau") or {}
    if section_visibility.get("dau", True) and dau.get("response_count"):
        parts.append("## Daily Active Usage (DAU)")
        parts.append("")
        pct_str = f" ({dau['team_avg_pct']}%)" if dau.get("team_avg_pct") is not None else ""
        parts.append(f"Team average: **{dau['team_avg']} / 5**{pct_str} across {dau['response_count']} response(s)")
        parts.append("")
        if dau.get("by_role"):
            headers = ["Role", "Avg days/week", "Avg %", "Responses"]
            rows = [
                [r["role"], r["avg"], f"{r.get('avg_pct', '')}%" if r.get("avg_pct") is not None else "—", r["count"]]
                for r in dau["by_role"]
            ]
            parts.append(_md_table(headers, rows))
            parts.append("")
        if dau.get("breakdown"):
            headers = ["Answer", "Count", "%"]
            rows = [
                [b["answer"], b["count"], f"{b.get('pct', '')}%" if b.get("pct") is not None else "—"]
                for b in dau["breakdown"]
            ]
            parts.append(_md_table(headers, rows))
            parts.append("")

    dau_trend = metrics.get("dau_trend") or []
    if section_visibility.get("dau_trend", True) and dau_trend:
        parts.append("## DAU Trend")
        parts.append("")
        max_avg = max((row.get("team_avg") or 0) for row in dau_trend) or 1
        for row in dau_trend:
            v = row.get("team_avg") or 0
            bar_len = int(30 * v / max_avg) if max_avg else 0
            bar = "█" * bar_len
            parts.append(f"- **{row.get('week', '')}**: {bar} {v} ({row.get('team_avg_pct', 0)}%)")
        parts.append("")
        headers = ["Week", "Team Avg", "Team Avg %", "Responses"]
        rows = [
            [
                row.get("week", ""),
                row.get("team_avg", 0),
                f"{row.get('team_avg_pct', 0)}%",
                row.get("response_count", 0),
            ]
            for row in dau_trend
        ]
        parts.append(_md_table(headers, rows))
        parts.append("")

    sprint_issue_details = metrics.get("sprint_issue_details") or []
    if section_visibility.get("sprint_issues", True) and sprint_issue_details:
        parts.append("## Sprint Issues")
        parts.append("")
        parts.append("Done issues used in metrics calculations.")
        parts.append("")
        for sprint_block in sprint_issue_details:
            sprint_name = sprint_block.get("sprint_name", "")
            issues = sprint_block.get("issues") or []
            if not issues:
                continue
            parts.append(f"### {sprint_name}")
            parts.append("")
            headers = ["Key", "Summary", "Points", "Status", "AI", "Excluded", "Labels"]
            rows = []
            for iss in issues:
                sp = iss.get("story_points") or 0
                sp_str = str(sp) if sp else "—"
                ai_flag = "✓" if iss.get("is_ai_assisted") else ""
                excl_flag = "✓" if iss.get("is_excluded") else ""
                labels_str = ", ".join(iss.get("labels") or []) or "—"
                summary = iss.get("summary") or ""
                if len(summary) > 60:
                    summary = summary[:57] + "..."
                rows.append(
                    [iss.get("key", ""), summary, sp_str, iss.get("status", ""), ai_flag, excl_flag, labels_str]
                )
            parts.append(_md_table(headers, rows))
            parts.append("")

    if section_visibility.get("diagnostics", True):
        parts.append("## Diagnostics")
        parts.append("")
        parts.append("*Configuration snapshot at report generation time.*")
        parts.append("")

        parts.append("### Run Info")
        parts.append("")
        run_rows = [
            ["Report name", metrics.get("report_name") or "—"],
            ["Generated at", (metrics.get("generated_at") or "—")],
        ]
        parts.append(_md_table(["Field", "Value"], run_rows))
        parts.append("")

        parts.append("### Jira Config")
        parts.append("")
        jira_rows = [
            ["project_type", metrics.get("project_type") or "—"],
            ["estimation_type", metrics.get("estimation_type") or "—"],
            ["schema_name", metrics.get("schema_name") or "—"],
            ["filter_name", metrics.get("filter_name") or "—"],
            ["filter_id", str(metrics.get("filter_id")) if metrics.get("filter_id") is not None else "—"],
            ["filter_jql", metrics.get("filter_jql") or "—"],
            ["project_key", metrics.get("project_key") or "—"],
        ]
        parts.append(_md_table(["Parameter", "Value"], jira_rows))
        parts.append("")

        ai_assisted_label = metrics.get("ai_assisted_label") or ""
        ai_exclude_labels = metrics.get("ai_exclude_labels") or []
        parts.append("### AI Label Config")
        parts.append("")
        ai_rows = [
            ["ai_assisted_label", f"`{ai_assisted_label}`" if ai_assisted_label else "—"],
            ["ai_exclude_labels", ", ".join(f"`{lbl}`" for lbl in ai_exclude_labels) if ai_exclude_labels else "—"],
        ]
        parts.append(_md_table(["Parameter", "Value"], ai_rows))
        parts.append("")

        cycle_time = metrics.get("cycle_time") or {}
        sample_size = cycle_time.get("sample_size") or 0
        parts.append("### Cycle Time")
        parts.append("")
        if sample_size:
            ct_rows = [
                ["Mean days", str(cycle_time.get("mean_days") or "—")],
                ["Median days", str(cycle_time.get("median_days") or "—")],
                ["Min days", str(cycle_time.get("min_days") or "—")],
                ["Max days", str(cycle_time.get("max_days") or "—")],
                ["Sample size", str(sample_size)],
            ]
            parts.append(_md_table(["Metric", "Value"], ct_rows))
        else:
            parts.append("*No cycle time data (no changelog fetched).*")
        parts.append("")

    output_path.write_text("\n".join(parts), encoding="utf-8")
