# site2md

Crawl a site — following same-site links — and convert every page to Markdown
using [Microsoft MarkItDown](https://github.com/microsoft/markitdown). Pages
are fetched statically first; if a page looks like an unhydrated JS/SPA shell,
it's re-rendered with a headless browser (Playwright), which also expands
`<details>` elements and anything with `aria-expanded="false"` before capture.

## Setup

```
python -m venv .venv
.venv\Scripts\pip install -e .
.venv\Scripts\python -m playwright install chromium
```

## Usage

```
site2md <start-url> -o <output-dir> [options]
```

For the full option reference, output layout, and guidance on scoping crawls,
handling bot-blocking or JS-rendered sites, and troubleshooting, see
[User_Docs/Usage.md](User_Docs/Usage.md).
