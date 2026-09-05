from __future__ import annotations

import hashlib
import re
from pathlib import Path
from urllib.parse import urlsplit

_INVALID = re.compile(r'[<>:"|?*]')
_DOC_EXTENSIONS = {"htm", "html", "php", "asp", "aspx", "jsp"}


def url_to_relpath(url: str) -> Path:
    """Map a URL to a local .md path that mirrors the site's directory structure."""
    parts = urlsplit(url)
    segments = [s for s in parts.path.split("/") if s]
    ends_with_slash = parts.path.endswith("/") or not parts.path

    if not segments or ends_with_slash:
        segments.append("index")

    last = segments[-1]
    stem, dot, ext = last.rpartition(".")
    if dot and ext.lower() in _DOC_EXTENSIONS:
        last = stem
    segments[-1] = last

    if parts.query:
        digest = hashlib.sha1(parts.query.encode("utf-8")).hexdigest()[:8]
        segments[-1] = f"{segments[-1]}__q{digest}"

    safe_segments = [_INVALID.sub("_", seg) or "_" for seg in segments]
    return Path(parts.netloc.lower(), *safe_segments).with_suffix(".md")
