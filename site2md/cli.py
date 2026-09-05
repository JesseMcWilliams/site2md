from __future__ import annotations

import argparse
import logging
from datetime import datetime, timezone
from pathlib import Path

from .crawler import CrawlOptions, crawl
from .indexer import write_index
from .manifest import write_manifest


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="site2md",
        description="Crawl a site (following same-site links) and convert every page to Markdown.",
    )
    p.add_argument("start_url", help="Page to start crawling from")
    p.add_argument("-o", "--output", default="output", help="Output directory (default: ./output)")
    p.add_argument("--max-pages", type=int, default=200, help="Stop after this many pages (default: 200)")
    p.add_argument("--delay", type=float, default=0.5, help="Seconds to wait between page fetches (default: 0.5)")
    p.add_argument("--path-prefix", default=None, help="Only crawl URLs whose path starts with this prefix")
    p.add_argument("--allow-subdomains", action="store_true", help="Also follow links to subdomains of the start URL's host")
    p.add_argument("--force-js", action="store_true", help="Always render pages with a headless browser")
    p.add_argument("--no-js", action="store_true", help="Never fall back to a headless browser")
    p.add_argument("--no-images", action="store_true", help="Don't download images into per-page images/ folders")
    p.add_argument("--ignore-robots", action="store_true", help="Ignore robots.txt (use responsibly)")
    p.add_argument("--user-agent", default=None, help="Override the User-Agent header")
    p.add_argument("-v", "--verbose", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(level=logging.INFO if args.verbose else logging.WARNING, format="%(message)s")

    options = CrawlOptions(
        max_pages=args.max_pages,
        delay=args.delay,
        allow_subdomains=args.allow_subdomains,
        path_prefix=args.path_prefix,
        force_js=args.force_js,
        disable_js=args.no_js,
        download_images=not args.no_images,
        respect_robots=not args.ignore_robots,
    )
    if args.user_agent:
        options.user_agent = args.user_agent

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc)
    records = crawl(args.start_url, output_dir, options)
    finished_at = datetime.now(timezone.utc)

    write_index(output_dir, records)
    write_manifest(output_dir, args.start_url, started_at, finished_at, records)

    print(f"Converted {len(records)} page(s) into {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
