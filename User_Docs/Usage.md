# site2md — Usage Guide

A complete walkthrough of site2md's options and behavior. For a quick overview and
install steps, see [README.md](../README.md).

## Contents

- [Quick start](#quick-start)
- [Scoping the crawl](#scoping-the-crawl)
- [Static fetch vs. headless-browser render](#static-fetch-vs-headless-browser-render)
- [Sites that block non-browser requests](#sites-that-block-non-browser-requests)
- [robots.txt](#robotstxt)
- [Rate limiting](#rate-limiting)
- [Images](#images)
- [Output layout](#output-layout)
- [Troubleshooting](#troubleshooting)
- [Option reference](#option-reference)

## Quick start

```
site2md https://docs.example.com/guide/intro -o output/example-docs
```

This starts at the given URL, follows every link that stays on `docs.example.com`,
converts each page to Markdown, and writes the result under `output/example-docs/`.
Open `output/example-docs/index.md` afterward for a linked table of contents.

## Scoping the crawl

By default, a link is followed only if it's on the exact same host as the start
URL. Two flags widen or narrow that:

```
# Also follow links to subdomains (e.g. api.example.com from docs.example.com)
site2md https://docs.example.com/ -o output/example --allow-subdomains

# Stay under one section of the site, even if other same-host pages exist
site2md https://docs.example.com/v2/guide/intro -o output/example --path-prefix /v2/guide
```

`--path-prefix` matches against the URL path only (not the host), and is a plain
prefix check — `/v2/guide` also matches `/v2/guide-advanced`, so prefer a trailing
slash (`/v2/guide/`) if that's not what you want.

Cap the crawl with `--max-pages` (default 200) so a misconfigured scope can't run
away across an entire site.

## Static fetch vs. headless-browser render

Each page is fetched with a plain HTTP GET first. If the resulting HTML has very
little visible text in `<body>` (the heuristic in `site2md/heuristics.py`), that's
treated as a sign the page is an unhydrated single-page-app shell, and the page is
re-fetched with a headless Chromium browser (Playwright) instead.

The headless render also runs a best-effort "expand everything" pass before
capturing the page: it force-opens every native `<details>` element, and clicks
anything with `aria-expanded="false"` so framework `onClick` handlers fire and
mount content that only exists in the DOM after interaction. Elements inside a
real `<a href>` link are skipped, since on some sites those are sidebar navigation
items rather than in-page accordions — clicking them would navigate away from the
page instead of expanding it.

Override the heuristic when you already know the answer for a given site:

```
site2md https://spa-docs.example.com/ -o output/spa-docs --force-js   # always render
site2md https://plain-docs.example.com/ -o output/plain --no-js       # never render
```

`--force-js` is slower (it launches a browser per page) but is the safer default
for a site you know is JS-rendered. `--no-js` is faster and useful once you've
confirmed a site needs no rendering at all.

## Sites that block non-browser requests

Some sites return a 404 or 403 to any request whose User-Agent doesn't look like a
real browser — independent of what their robots.txt actually allows. If pages that
clearly exist (you can open them in a browser) come back as "could not fetch",
try a browser User-Agent string:

```
site2md https://docs.example.com/ -o output/example \
  --user-agent "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
```

## robots.txt

By default, site2md fetches and honors the target site's `robots.txt` before
crawling any page. Use `--ignore-robots` only when you have a clear basis for
doing so (e.g. you operate the site, or you have explicit permission to crawl it
regardless of its stated rules).

## Rate limiting

`--delay` (default 0.5 seconds) is a fixed pause between page fetches, to avoid
hammering the target site. Raise it for a slower, more polite crawl of a large
site; lower it (e.g. `0`) only for small, low-traffic, or local test targets.

## Images

Every `<img>` on a page is downloaded into an `images/` folder next to that page's
Markdown file, and the page's `<img src>` is rewritten to point at the local
copy before conversion — so the resulting Markdown works offline. Pass
`--no-images` to skip this and leave original (remote) image URLs in the output.

Images larger than 15 MB are skipped rather than downloaded.

## Output layout

```
<output-dir>/
  index.md                    # title + link + source URL, one line per page
  manifest.md                 # start URL, crawl start/end time, and a table of
                               # URL / local file / capture timestamp / mode per page
  <host>/<path>.md             # one file per page, mirroring the site's URL structure
  <host>/<dir>/images/          # images referenced by pages in that directory
```

A URL's path becomes its file path directly (`/guide/intro.htm` →
`<host>/guide/intro.md`); a path ending in `/` becomes `index.md` in that
directory, and a query string is folded into the filename as a short hash suffix
so that `?tab=a` and `?tab=b` versions of the same page don't collide.

## Troubleshooting

- **A page you can see in a browser comes back as "could not fetch."** Check the
  URL still exists — try opening it in a normal browser tab and watch for
  redirects, or run with `-v` and check the underlying status code. Docs sites
  restructure fairly often (version paths and filenames both drift), and a
  changed URL will 404 without it being a scraping problem. If the page does
  exist but the fetch still fails, see [Sites that block non-browser
  requests](#sites-that-block-non-browser-requests).
- **Captured content doesn't match the page you asked for.** This can happen on
  SPA sites during the "expand everything" pass if a click triggers client-side
  navigation. site2md detects when this happens and restores the original page,
  but if you still see mismatched content on a particular site, try `--no-js` (if
  the content doesn't actually need rendering) and file an issue with the URL.
- **`--path-prefix` doesn't seem to match anything, when run from Git Bash.**
  Git Bash rewrites any argument that starts with `/` into a Windows path rooted
  at the Git installation directory (e.g. `/v2/guide` becomes
  `C:/Program Files/Git/v2/guide`) before your program ever sees it. Run from
  PowerShell instead, or set `MSYS_NO_PATHCONV=1` for the command.

## Option reference

| Option | Default | Description |
| --- | --- | --- |
| `-o, --output DIR` | `output` | Output directory |
| `--max-pages N` | `200` | Stop after N pages |
| `--delay SECONDS` | `0.5` | Pause between page fetches |
| `--path-prefix PREFIX` | none | Only crawl URLs whose path starts with this prefix |
| `--allow-subdomains` | off | Also follow links to subdomains of the start host |
| `--force-js` | off | Always render pages with a headless browser |
| `--no-js` | off | Never fall back to a headless browser |
| `--no-images` | off | Don't download images into per-directory `images/` folders |
| `--ignore-robots` | off | Ignore robots.txt (use responsibly) |
| `--user-agent UA` | a `site2md/0.1` identifying string | Override the User-Agent header |
| `-v, --verbose` | off | Log each page as it's fetched |
