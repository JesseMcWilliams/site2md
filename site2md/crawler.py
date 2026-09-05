from __future__ import annotations

import logging
import time
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlsplit

import requests
from bs4 import BeautifulSoup

from .convert import html_to_markdown
from .fetch_dynamic import render as fetch_dynamic
from .fetch_static import DEFAULT_USER_AGENT, fetch as fetch_static
from .heuristics import looks_like_js_shell
from .images import localize_images
from .pathmap import url_to_relpath
from .urls import normalize_url, resolve, same_site

log = logging.getLogger("site2md")


@dataclass
class CrawlOptions:
    max_pages: int = 200
    delay: float = 0.5
    allow_subdomains: bool = False
    path_prefix: str | None = None
    force_js: bool = False
    disable_js: bool = False
    respect_robots: bool = True
    download_images: bool = True
    user_agent: str = DEFAULT_USER_AGENT
    timeout: float = 20.0


@dataclass
class PageRecord:
    url: str
    relpath: Path
    title: str | None
    captured_at: datetime
    mode: str  # "static" or "js"


def _get_robots(start_url: str, session: requests.Session, user_agent: str) -> robotparser.RobotFileParser | None:
    """Fetch and parse robots.txt using our own session/User-Agent.

    RobotFileParser.read() uses urllib with Python's default User-Agent, which some
    sites block (403) independently of what they actually allow real crawlers to do.
    A 401/403 makes RobotFileParser assume "disallow everything", so fetching it the
    same way we fetch every other page avoids a false disallow caused by UA-sniffing
    rather than the site's real robots.txt rules.
    """
    parts = urlsplit(start_url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    rp = robotparser.RobotFileParser()
    rp.set_url(robots_url)
    try:
        resp = session.get(robots_url, timeout=10, headers={"User-Agent": user_agent})
    except requests.RequestException:
        return None
    if resp.status_code in (401, 403):
        rp.disallow_all = True
    elif resp.status_code >= 400:
        rp.allow_all = True
    else:
        rp.parse(resp.text.splitlines())
    return rp


def _extract_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        resolved = resolve(base_url, a["href"])
        if resolved:
            links.append(resolved)
    return links


def _page_title(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    if h1:
        return h1.get_text(strip=True)
    return None


def crawl(start_url: str, output_dir: Path, options: CrawlOptions) -> list[PageRecord]:
    start_url = normalize_url(start_url)
    root_netloc = urlsplit(start_url).netloc.lower()
    session = requests.Session()
    robots = _get_robots(start_url, session, options.user_agent) if options.respect_robots else None

    queue: deque[str] = deque([start_url])
    visited: set[str] = set()
    records: list[PageRecord] = []

    while queue and len(records) < options.max_pages:
        url = queue.popleft()
        if url in visited:
            continue
        visited.add(url)

        if not same_site(url, root_netloc, options.path_prefix, options.allow_subdomains):
            continue
        if robots is not None and not robots.can_fetch(options.user_agent, url):
            log.info("robots.txt disallows %s, skipping", url)
            continue

        html = None
        mode = "static"
        if not options.force_js:
            html = fetch_static(url, session=session, timeout=options.timeout, user_agent=options.user_agent)
            if html is not None and not options.disable_js and looks_like_js_shell(html):
                html = None  # looks like an unhydrated SPA shell; fall through to JS render

        if html is None and not options.disable_js:
            try:
                html = fetch_dynamic(url, user_agent=options.user_agent, timeout_ms=int(options.timeout * 1000))
                mode = "js"
            except Exception as exc:
                log.warning("JS render failed for %s: %s", url, exc)

        if html is None:
            log.warning("could not fetch %s", url)
            continue

        log.info("fetched %s [%s]", url, mode)

        links = _extract_links(html, url)
        title = _page_title(html)

        relpath = url_to_relpath(url)
        dest = output_dir / relpath
        dest.parent.mkdir(parents=True, exist_ok=True)

        if options.download_images:
            html = localize_images(
                html,
                url,
                dest.parent / "images",
                session=session,
                user_agent=options.user_agent,
                timeout=options.timeout,
            )

        markdown = html_to_markdown(html, url)
        dest.write_text(markdown, encoding="utf-8")

        records.append(
            PageRecord(
                url=url,
                relpath=relpath,
                title=title,
                captured_at=datetime.now(timezone.utc),
                mode=mode,
            )
        )

        for link in links:
            if link not in visited and same_site(link, root_netloc, options.path_prefix, options.allow_subdomains):
                queue.append(link)

        time.sleep(options.delay)

    return records
