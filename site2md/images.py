from __future__ import annotations

import hashlib
import mimetypes
import re
from pathlib import Path
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

from .urls import resolve

_INVALID = re.compile(r'[<>:"|?*]')
DEFAULT_MAX_IMAGE_BYTES = 15 * 1024 * 1024


def localize_images(
    html: str,
    page_url: str,
    images_dir: Path,
    *,
    session: requests.Session,
    user_agent: str,
    timeout: float = 20.0,
    max_bytes: int = DEFAULT_MAX_IMAGE_BYTES,
) -> str:
    """Download every <img> on the page into images_dir and rewrite src to point at the local copy."""
    soup = BeautifulSoup(html, "lxml")
    imgs = soup.find_all("img")
    if not imgs:
        return html

    seen: dict[str, str] = {}  # local filename -> content hash, for dedup within this directory

    for img in imgs:
        src = img.get("src")
        abs_url = resolve(page_url, src) if src else None
        if not abs_url:
            continue

        try:
            resp = session.get(abs_url, timeout=timeout, headers={"User-Agent": user_agent}, stream=True)
            resp.raise_for_status()
            content = resp.raw.read(max_bytes + 1, decode_content=True)
            if len(content) > max_bytes:
                continue
        except requests.RequestException:
            continue

        digest = hashlib.sha1(content).hexdigest()[:10]
        name = Path(urlsplit(abs_url).path).name
        stem, dot, ext = name.rpartition(".") if name else ("image", "", "")
        if not dot:
            stem = name or "image"
            ext = (mimetypes.guess_extension((resp.headers.get("content-type") or "").split(";")[0]) or ".bin").lstrip(".")
        stem = _INVALID.sub("_", stem) or "image"
        ext = _INVALID.sub("_", ext) or "bin"
        filename = f"{stem}.{ext}"

        if seen.get(filename, digest) != digest:
            filename = f"{stem}-{digest}.{ext}"
        seen[filename] = digest

        dest = images_dir / filename
        if not dest.exists():
            images_dir.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)

        img["src"] = f"images/{filename}"

    return str(soup)
