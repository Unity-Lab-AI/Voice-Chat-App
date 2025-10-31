"""Utility to execute every test module within the tests directory.

The script is intentionally lightweight so it can run without any external test
runner. Each test file is executed in its own Python subprocess, allowing us to
capture individual results for reporting and CI summarisation.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List


def _execute_test(test_file: Path) -> Dict[str, object]:
    """Execute a single test file and capture its outcome."""

    completed = subprocess.run(
        [sys.executable, str(test_file)],
        capture_output=True,
        text=True,
        check=False,
    )
    passed = completed.returncode == 0
    status_icon = "✅" if passed else "❌"
    print(f"{status_icon} {test_file.name}")
    return {
        "name": test_file.stem,
        "path": str(test_file),
        "returncode": completed.returncode,
        "passed": passed,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def main() -> None:
    tests_dir = Path(__file__).parent
    report_dir = Path.cwd() / "ci_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    test_files: List[Path] = sorted(
        file for file in tests_dir.glob("test_*.py") if file.is_file()
    )

    if not test_files:
        print("⚠️  No test files were discovered in the tests directory.")

    results = [_execute_test(test_file) for test_file in test_files]
    overall_status = "success" if all(result["passed"] for result in results) else "failure"

    summary = {
        "overall_status": overall_status,
        "tests": results,
    }

    report_path = report_dir / "test_results.json"
    report_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("Test execution complete. Detailed results stored at", report_path)


if __name__ == "__main__":
    main()
