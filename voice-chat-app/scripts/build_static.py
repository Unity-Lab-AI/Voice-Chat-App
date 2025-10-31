"""Build the static site assets and record the build status."""

from __future__ import annotations

import json
import shutil
import tarfile
from pathlib import Path
from typing import List

SOURCE_FILES: List[Path] = [
    Path("index.html"),
    Path("app.js"),
    Path("style.css"),
]


def main() -> None:
    project_root = Path.cwd()
    dist_dir = project_root / "dist"
    report_dir = project_root / "ci_reports"
    report_dir.mkdir(parents=True, exist_ok=True)

    dist_dir.mkdir(exist_ok=True)

    artifacts = []
    status = "success"

    for source in SOURCE_FILES:
        destination = dist_dir / source.name
        try:
            shutil.copy2(source, destination)
            artifacts.append({
                "source": str(source),
                "destination": str(destination),
                "copied": True,
            })
        except FileNotFoundError:
            status = "failure"
            artifacts.append({
                "source": str(source),
                "destination": str(destination),
                "copied": False,
                "error": "File not found",
            })

    archive_path = report_dir / "static-site.tar.gz"
    try:
        with tarfile.open(archive_path, "w:gz") as archive:
            archive.add(dist_dir, arcname="dist")
        archive_created = True
    except FileNotFoundError:
        archive_created = False
        status = "failure"

    report = {
        "status": status,
        "artifacts": artifacts,
        "archive": str(archive_path) if archive_created else None,
    }

    (report_dir / "build_report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print("Build status:", status)
    if not artifacts:
        print("No source files were processed.")
    else:
        for entry in artifacts:
            outcome = "copied" if entry.get("copied") else "missing"
            print(f" - {entry['source']} -> {entry['destination']} ({outcome})")
    if archive_created:
        print("Archive created at", archive_path)
    else:
        print("Failed to create build archive.")


if __name__ == "__main__":
    main()
