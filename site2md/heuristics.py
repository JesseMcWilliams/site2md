from __future__ import annotations

from bs4 import BeautifulSoup

# Below this many visible characters in <body>, assume the static fetch only got an
# unhydrated SPA shell and a headless-browser render is needed.
MIN_BODY_TEXT_CHARS = 300

_SPA_ROOT_IDS = {"root", "app", "__next", "___gatsby", "___next"}


def looks_like_js_shell(html: str) -> bool:
    soup = BeautifulSoup(html, "lxml")
    body = soup.body
    if body is None:
        return True

    text = body.get_text(separator=" ", strip=True)
    if len(text) >= MIN_BODY_TEXT_CHARS:
        return False

    for el in soup.find_all(id=True):
        if el.get("id", "").strip().lower() in _SPA_ROOT_IDS:
            return True

    return len(text) < 100
