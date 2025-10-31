"""Render build summaries and expose them to GitHub Actions."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def _load_report(report_path: Path) -> dict:
    if not report_path.exists():
        return {"status": "unknown", "artifacts": [], "missing": True}
    return json.loads(report_path.read_text(encoding="utf-8"))


def _render_summary(report: dict) -> str:
    lines = [f"### Build Status — {report.get('status', 'unknown').capitalize()}", ""]

    artifacts = report.get("artifacts", [])
    if artifacts:
        lines.append("| Source | Destination | Result |")
        lines.append("| --- | --- | --- |")
        for entry in artifacts:
            result = "Copied" if entry.get("copied") else entry.get("error", "Unknown")
            lines.append(f"| {entry.get('source', '')} | {entry.get('destination', '')} | {result} |")
        lines.append("")
    else:
        lines.append("No artifacts were processed.\n")

    archive = report.get("archive")
    if archive:
        lines.append(f"Archive: `{archive}`\n")

    return "\n".join(lines)


def _set_outputs(summary: str, status: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        handle.write("summary<<EOF\n")
        handle.write(summary)
        if not summary.endswith("\n"):
            handle.write("\n")
        handle.write("EOF\n")
        handle.write(f"status={status}\n")


def _append_summary(summary: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as handle:
            handle.write(summary)
            if not summary.endswith("\n"):
                handle.write("\n")


def main() -> None:
    parser = argparse.ArgumentParser(description="Report build results")
    parser.add_argument(
        "--report",
        type=Path,
        default=Path("ci_reports/build_report.json"),
        help="Path to the JSON report created during the build step.",
    )
    parser.add_argument(
        "--write-summary",
        type=Path,
        help="Persist the summary markdown to the specified path.",
    )
    parser.add_argument(
        "--set-outputs",
        action="store_true",
        help="Expose summary information through GitHub step outputs.",
    )
    parser.add_argument(
        "--suppress-print",
        action="store_true",
        help="Avoid printing the summary to stdout.",
    )

    args = parser.parse_args()

    report = _load_report(args.report)
    summary = _render_summary(report)
    status = report.get("status", "unknown")

    if args.write_summary:
        destination = args.write_summary
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(summary, encoding="utf-8")

    if args.set_outputs:
        _set_outputs(summary, status)

    if not args.suppress_print:
        print(summary)
        _append_summary(summary)


if __name__ == "__main__":
    main()
