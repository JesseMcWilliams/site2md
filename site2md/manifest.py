from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .crawler import PageRecord


def write_manifest(
    output_dir: Path,
    start_url: str,
    started_at: datetime,
    finished_at: datetime,
    records: list[PageRecord],
) -> None:
    lines = [
        "# Capture Manifest",
        "",
        f"- Start URL: {start_url}",
        f"- Crawl started: {started_at.isoformat(timespec='seconds')}",
        f"- Crawl finished: {finished_at.isoformat(timespec='seconds')}",
        f"- Pages captured: {len(records)}",
        "",
        "| URL | Local file | Captured at (UTC) | Mode |",
        "| --- | --- | --- | --- |",
    ]
    for rec in sorted(records, key=lambda r: str(r.relpath)):
        lines.append(
            f"| {rec.url} | {rec.relpath.as_posix()} | {rec.captured_at.isoformat(timespec='seconds')} | {rec.mode} |"
        )
    (output_dir / "manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
