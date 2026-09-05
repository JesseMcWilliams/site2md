from __future__ import annotations

from pathlib import Path

from .crawler import PageRecord


def write_index(output_dir: Path, records: list[PageRecord]) -> None:
    lines = ["# Site Index", ""]
    for rec in sorted(records, key=lambda r: str(r.relpath)):
        title = rec.title or rec.url
        rel = rec.relpath.as_posix()
        lines.append(f"- [{title}]({rel}) — {rec.url}")
    (output_dir / "index.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
