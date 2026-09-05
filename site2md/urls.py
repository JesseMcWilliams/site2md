from __future__ import annotations

from urllib.parse import urljoin, urlsplit, urlunsplit

_SKIP_SCHEMES = ("mailto:", "tel:", "javascript:", "data:")


def normalize_url(url: str) -> str:
    """Strip the fragment, lowercase scheme/host, and drop trailing default state."""
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    path = parts.path or "/"
    return urlunsplit((scheme, netloc, path, parts.query, ""))


def resolve(base_url: str, href: str) -> str | None:
    """Resolve href against base_url, or return None if it isn't a fetchable page/asset link."""
    href = (href or "").strip()
    if not href or href.startswith("#") or href.lower().startswith(_SKIP_SCHEMES):
        return None
    joined = urljoin(base_url, href)
    if not joined.lower().startswith(("http://", "https://")):
        return None
    return normalize_url(joined)


def same_site(url: str, root_netloc: str, path_prefix: str | None, allow_subdomains: bool) -> bool:
    parts = urlsplit(url)
    netloc = parts.netloc.lower()
    if allow_subdomains:
        if netloc != root_netloc and not netloc.endswith("." + root_netloc):
            return False
    elif netloc != root_netloc:
        return False
    if path_prefix and not parts.path.startswith(path_prefix):
        return False
    return True
