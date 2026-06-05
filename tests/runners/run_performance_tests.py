"""
Performance test runner — runs pytest tests/ -m performance and saves output.

Usage:
    python tests/runners/run_performance_tests.py

Exit codes:
    Mirrors pytest exit code (0 = pass, 1 = some tests failed).
    Exits 0 if no tests match the performance marker (not an error).
"""

from __future__ import annotations

import datetime
import os
import subprocess
import sys

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(os.path.dirname(_SCRIPT_DIR))
os.chdir(_PROJECT_ROOT)

TMP_DIR = os.path.join(_PROJECT_ROOT, "generated", "tmp")

SEP = "=" * 73


def _ensure_tmp_dir() -> None:
    os.makedirs(TMP_DIR, exist_ok=True)


def main() -> int:
    _ensure_tmp_dir()

    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    output_file = os.path.join(TMP_DIR, f"performance-run-{timestamp}.txt")

    print(SEP)
    print("Performance Test Runner")
    print(SEP)
    print(f"  Timestamp : {timestamp}")
    print(f"  Output    : {output_file}")
    print()

    python = sys.executable
    cmd = [python, "-m", "pytest", "tests/", "-m", "performance", "-v"]

    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    output = result.stdout or ""

    with open(output_file, "w", encoding="utf-8") as fh:
        fh.write(f"Performance test run — {timestamp}\n")
        fh.write(f"Command: {' '.join(cmd)}\n")
        fh.write(SEP + "\n")
        fh.write(output)

    print(output)

    # pytest exit code 5 = no tests collected
    if result.returncode == 5:
        print(
            "No tests found matching @pytest.mark.performance.\n"
            "Add performance tests or register the marker in pyproject.toml."
        )
        return 0

    print(f"\n{SEP}")
    if result.returncode == 0:
        print(f"RESULT: PASS — Output saved to {output_file}")
    else:
        print(f"RESULT: FAIL (exit code {result.returncode}) — Output saved to {output_file}")

    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
