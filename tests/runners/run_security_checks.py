"""
Security check runner — runs pip-audit (CVE scan) and bandit (static analysis).

Usage:
    python tests/runners/run_security_checks.py

Exit codes:
    0  No HIGH or CRITICAL findings
    1  HIGH or CRITICAL findings found
    2  Required tool (pip-audit or bandit) not installed
"""

from __future__ import annotations

import json
import os
import subprocess
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
os.chdir(_PROJECT_ROOT)

DEBUG_DIR = os.path.join(_PROJECT_ROOT, "generated", "debug")
BANDIT_REPORT = os.path.join(DEBUG_DIR, "bandit-report.json")

SEP = "=" * 73


def _ensure_debug_dir() -> None:
    os.makedirs(DEBUG_DIR, exist_ok=True)


def _run_pip_audit() -> tuple[int, list[dict]]:
    """Run pip-audit and return (exit_code, vulnerabilities_list)."""
    candidates = [
        [sys.executable, "-m", "pip_audit", "--format", "json"],
        ["pip-audit", "--format", "json"],
    ]
    cmd: list[str] | None = None
    for candidate in candidates:
        try:
            subprocess.run(
                candidate[:2] + ["--version"],
                capture_output=True,
                check=True,
            )
            cmd = candidate
            break
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

    if cmd is None:
        print(
            "ERROR: pip-audit is not installed.\n"
            "Install it with: pip install pip-audit",
            file=sys.stderr,
        )
        return 2, []

    result = subprocess.run(cmd, capture_output=True, text=True)
    vulnerabilities: list[dict] = []
    if result.stdout.strip():
        try:
            data = json.loads(result.stdout)
            for dep in data.get("dependencies", []):
                for vuln in dep.get("vulns", []):
                    vulnerabilities.append(
                        {
                            "package": dep.get("name", "unknown"),
                            "version": dep.get("version", "unknown"),
                            "id": vuln.get("id", ""),
                            "description": vuln.get("description", ""),
                        }
                    )
        except (json.JSONDecodeError, KeyError):
            pass
    return result.returncode, vulnerabilities


def _run_bandit() -> tuple[int, list[dict]]:
    """Run bandit static analysis and return (exit_code, high_critical_issues)."""
    candidates = [
        [sys.executable, "-m", "bandit"],
        ["bandit"],
    ]
    cmd: list[str] | None = None
    for candidate in candidates:
        try:
            subprocess.run(
                candidate + ["--version"],
                capture_output=True,
                check=True,
            )
            cmd = candidate
            break
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

    if cmd is None:
        print(
            "ERROR: bandit is not installed.\n"
            "Install it with: pip install bandit",
            file=sys.stderr,
        )
        return 2, []

    full_cmd = cmd + ["-r", "app/", "-f", "json", "-o", BANDIT_REPORT]
    result = subprocess.run(full_cmd, capture_output=True, text=True)

    high_critical: list[dict] = []
    if os.path.exists(BANDIT_REPORT):
        try:
            with open(BANDIT_REPORT, encoding="utf-8") as fh:
                data = json.load(fh)
            for issue in data.get("results", []):
                severity = issue.get("issue_severity", "").upper()
                if severity in ("HIGH", "CRITICAL"):
                    high_critical.append(
                        {
                            "file": issue.get("filename", ""),
                            "line": issue.get("line_number", 0),
                            "severity": severity,
                            "confidence": issue.get("issue_confidence", ""),
                            "text": issue.get("issue_text", ""),
                            "test_id": issue.get("test_id", ""),
                        }
                    )
        except (json.JSONDecodeError, OSError):
            pass

    return result.returncode, high_critical


def main() -> int:
    _ensure_debug_dir()

    print(SEP)
    print("Security Check Runner")
    print(SEP)

    print("\n[1/2] Running pip-audit (CVE scan)...")
    pip_rc, vulns = _run_pip_audit()
    if pip_rc == 2:
        return 2

    if vulns:
        print(f"  FOUND {len(vulns)} vulnerability/ies:")
        for v in vulns:
            print(f"    {v['package']}=={v['version']}  {v['id']}: {v['description'][:100]}")
    else:
        print("  OK — no known CVEs found.")

    print(f"\n[2/2] Running bandit static analysis (output: {BANDIT_REPORT})...")
    bandit_rc, hc_issues = _run_bandit()
    if bandit_rc == 2:
        return 2

    if hc_issues:
        print(f"  FOUND {len(hc_issues)} HIGH/CRITICAL issue(s):")
        for issue in hc_issues:
            print(
                f"    [{issue['severity']}] {issue['file']}:{issue['line']} "
                f"({issue['test_id']}) — {issue['text']}"
            )
    else:
        print("  OK — no HIGH or CRITICAL bandit findings.")

    print(f"\n  Full bandit report written to: {BANDIT_REPORT}")

    print(f"\n{SEP}")
    has_critical = bool(vulns) or bool(hc_issues)
    if has_critical:
        print("RESULT: FAIL — HIGH or CRITICAL findings require remediation before merge.")
        return 1

    print("RESULT: PASS — No HIGH or CRITICAL security findings.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
