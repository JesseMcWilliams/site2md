from __future__ import annotations

import requests
from bs4 import BeautifulSoup

DEFAULT_USER_AGENT = "site2md/0.1 (generic docs crawler; contact: site owner)"


def fetch(
    url: str,
    *,
    session: requests.Session,
    timeout: float = 20.0,
    user_agent: str = DEFAULT_USER_AGENT,
) -> str | None:
    """Fetch a page with a plain HTTP GET. Returns the HTML text, or None on failure/non-HTML."""
    try:
        resp = session.get(url, timeout=timeout, headers={"User-Agent": user_agent}, allow_redirects=True)
    except requests.RequestException:
        return None

    if resp.status_code >= 400:
        return None

    content_type = resp.headers.get("content-type", "")
    if "html" not in content_type.lower() and not resp.content.lstrip().startswith((b"<", b"<!")):
        return None

    # Decode via BeautifulSoup's charset sniffing (meta tags / BOM / chardet) rather than
    # trusting resp.text, which defaults to Latin-1 whenever the Content-Type header omits
    # a charset — that silently mojibakes UTF-8 pages (e.g. "target's" -> "targetâs").
    return str(BeautifulSoup(resp.content, "lxml"))
