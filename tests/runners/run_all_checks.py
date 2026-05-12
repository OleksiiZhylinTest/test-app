"""
Parallel CI stage runner — orchestrates all run_all_checks stages concurrently.
Called by tests/runners/run_all_checks.bat; can also be invoked directly.

Usage:
    python tests/runners/run_all_checks.py                    # full suite (all stages)
    python tests/runners/run_all_checks.py --smoke            # cross-layer smoke (~1-2 min)
    python tests/runners/run_all_checks.py --sanity           # smoke + sanity (~5-10 min)
    python tests/runners/run_all_checks.py --full             # explicit full suite
    python tests/runners/run_all_checks.py --skip-integration # full suite minus integration
    python tests/runners/run_all_checks.py --skip-e2e         # full suite minus e2e
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import threading
import time

# Ensure stdout uses UTF-8 on Windows (cp1252 can't encode replacement chars
# that appear when subprocess output contains non-Latin bytes).
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── Ensure CWD is project root (mirrors `cd /d "%~dp0..\.."` in the bat) ────
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(os.path.dirname(_SCRIPT_DIR)))

SEP = "=" * 73


class Stage:
    def __init__(self, name: str, cmd: list[str], skip: bool = False) -> None:
        self.name = name
        self.cmd = cmd
        self.skip = skip
        self.returncode: int | None = None
        self.output: str = ""


def _run(stage: Stage) -> None:
    try:
        proc = subprocess.Popen(
            stage.cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding="utf-8",
            errors="replace",
        )
        stage.output, _ = proc.communicate()
        stage.returncode = proc.returncode
    except FileNotFoundError as exc:
        stage.output = f"ERROR: command not found — {exc}\n"
        stage.returncode = 1


def _venv_tool(name: str) -> str:
    """Return the venv path for a tool if it exists, otherwise fall back to PATH."""
    candidate = os.path.join(".venv", "Scripts", name + ".exe")
    return candidate if os.path.exists(candidate) else name


def _find_pip_audit(python: str) -> list[str] | None:
    """Return a working pip-audit invocation, or None if not installed."""
    for candidate in ([python, "-m", "pip_audit"], ["pip-audit"]):
        try:
            subprocess.run(candidate + ["--version"], capture_output=True, check=True)
            return candidate
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass
    return None


def main() -> int:
    parser = argparse.ArgumentParser()
    tier = parser.add_mutually_exclusive_group()
    tier.add_argument("--smoke", action="store_true", help="cross-layer smoke tier (~1-2 min)")
    tier.add_argument("--sanity", action="store_true", help="smoke + sanity tier (~5-10 min)")
    tier.add_argument("--full", action="store_true", help="full suite (default when no tier flag)")
    parser.add_argument("--skip-integration", action="store_true")
    parser.add_argument("--skip-e2e", action="store_true")
    args = parser.parse_args()

    python = r".venv\Scripts\python.exe" if os.path.exists(r".venv\Scripts\python.exe") else "python"
    pip_audit = _find_pip_audit(python)
    ruff = _venv_tool("ruff")
    mypy = _venv_tool("mypy")
    bandit = _venv_tool("bandit")

    xdist = ["-n", "auto", "--dist=loadscope", "--tb=short"]

    if args.smoke or args.sanity:
        marker = "smoke" if args.smoke else "smoke or sanity"
        stages = [
            Stage("Ruff", ["cmd", "/c", f"{ruff} check app/ tests/ && {ruff} format --check app/ tests/"]),
            Stage("Mypy", [mypy, "app/", "--ignore-missing-imports", "--python-version", "3.12"]),
            Stage("Bandit", [bandit, "-r", "app/", "-q"]),
            Stage(f"Tests ({marker})", [python, "-m", "pytest", "tests", "-m", marker, *xdist]),
        ]
        if args.sanity:
            stages.append(Stage("Security", (pip_audit or ["pip-audit"]) + ["-r", "requirements.txt"]))
    else:
        stages = [
            Stage("Ruff", ["cmd", "/c", f"{ruff} check app/ tests/ && {ruff} format --check app/ tests/"]),
            Stage("Mypy", [mypy, "app/", "--ignore-missing-imports", "--python-version", "3.12"]),
            Stage("Bandit", [bandit, "-r", "app/", "-q"]),
            Stage("Unit", ["cmd", "/c", "tests\\runners\\run_unit_tests.bat"]),
            Stage("Component", ["cmd", "/c", "tests\\runners\\run_component_tests.bat"]),
            Stage("Windows", [python, "-m", "pytest", "tests", "-m", "windows_only", *xdist]),
            Stage("Security", (pip_audit or ["pip-audit"]) + ["-r", "requirements.txt"]),
            Stage(
                "Integration",
                ["cmd", "/c", "tests\\runners\\run_integration_tests.bat"],
                skip=args.skip_integration,
            ),
            Stage(
                "E2E",
                ["cmd", "/c", "tests\\runners\\run_e2e_tests.bat"],
                skip=args.skip_e2e,
            ),
        ]

    active = [s for s in stages if not s.skip]

    # ── Header ────────────────────────────────────────────────────────────────
    print(f"\n{SEP}")
    print("  LOCAL CI CHECKS  (parallel)")
    print(SEP)
    if pip_audit is None:
        print("\n  WARNING: pip-audit not found — Security stage will FAIL.")
        print("           Install with: pip install pip-audit")
    print(f"\n  Running {len(active)} stage(s) concurrently: {', '.join(s.name for s in active)}\n")

    # ── Launch all active stages in parallel ──────────────────────────────────
    threads = [threading.Thread(target=_run, args=(s,), daemon=True) for s in active]
    t0 = time.monotonic()
    for t in threads:
        t.start()

    spin = "|/-\\"
    i = 0
    while any(t.is_alive() for t in threads):
        done = sum(1 for s in active if s.returncode is not None)
        elapsed = time.monotonic() - t0
        print(
            f"\r  {spin[i % 4]}  {done}/{len(active)} done  ({elapsed:.0f}s elapsed)",
            end="",
            flush=True,
        )
        i += 1
        time.sleep(0.3)
    for t in threads:
        t.join()
    print(f"\r  Completed in {time.monotonic() - t0:.1f}s{' ' * 30}")

    # ── Show output of failed stages ──────────────────────────────────────────
    any_failed = any(s.returncode != 0 for s in active)
    for s in active:
        if s.returncode != 0:
            text = f"\n{SEP}\n  FAILED: {s.name}\n{SEP}\n{s.output}\n"
            sys.stdout.buffer.write(text.encode("utf-8", errors="replace"))
            sys.stdout.flush()

    # ── Summary ───────────────────────────────────────────────────────────────
    print(f"\n{SEP}\n  SUMMARY\n{SEP}\n")
    print(f"  {'Stage':<25} Result")
    print(f"  {'-' * 23} {'-' * 6}")
    for s in stages:
        if s.skip:
            label = "SKIP"
        elif s.returncode == 0:
            label = "PASS"
        else:
            label = "FAIL"
        print(f"  {s.name:<25} {label}")
    result_line = "One or more stages FAILED." if any_failed else "All stages passed or were skipped."
    print(f"\n  RESULT: {result_line}")
    print(f"\n{SEP}\n")

    return 1 if any_failed else 0


if __name__ == "__main__":
    sys.exit(main())
