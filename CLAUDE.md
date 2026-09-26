# site2md: Claude Code project notes

site2md is a Python 3.10+ CLI tool (installed via `pip install -e .`, entry
point `site2md`) that crawls a site following same-site links and converts
each page to Markdown via Microsoft MarkItDown, falling back to a headless
Playwright browser for JS-rendered pages. No linter/formatter/test-runner is
configured in `pyproject.toml`.

## Folder map
- `site2md/` — the package (11 modules, ~554 lines total; largest is `crawler.py` at 173 lines — none over ~1,000 lines, read any of them in full).
  - `cli.py` — argument parsing, entry point for `site2md.cli:main`.
  - `crawler.py` — crawl loop and `CrawlOptions`.
  - `convert.py`, `fetch_static.py`, `fetch_dynamic.py`, `heuristics.py`, `images.py`, `indexer.py`, `manifest.py`, `pathmap.py`, `urls.py` — supporting modules.
- `tests/` — currently empty; no test files exist yet.
- `pyproject.toml` — project metadata, dependencies, entry point. No test/lint/format config declared.
- `README.md` — root overview: setup + quick usage, links out to `User_Docs/Usage.md`.
- `User_Docs/Usage.md` — full option reference, crawl-scoping, static-vs-headless behavior, output layout, troubleshooting.
- Gitignored, don't read: `_test-output/` (manual-test crawl output), `.venv/`, `site2md.egg-info/`, `site2md/__pycache__/`, `*.local.md`.
- External references are in `C:\Code\References\`. Check there before guessing at API behavior.

## Tests
<!-- TODO: no test command can be confirmed. `tests/` is an empty directory and pyproject.toml has no [tool.pytest] or other test-runner config. There is currently no runnable test suite — confirm/add one before documenting exact commands. -->

## Code rules (details in the linked sections, not repeated here)
<!-- TODO: no coding conventions are currently documented or enforced. pyproject.toml has no [tool.ruff]/[tool.black]/[tool.mypy] section, and neither README.md nor User_Docs/Usage.md documents code-style rules. Fill this in once a linter/formatter is configured or a convention is written down. -->

## Documentation layout
- `README.md` (root): overview — setup and quick usage, links into `User_Docs/`.
- `User_Docs/Usage.md`: full option reference, behavior, and troubleshooting for people running the CLI.
- No `Claude_Docs/` docs exist yet — nothing here is a proposal, a design writeup, or a lessons-learned log yet. Add one with the matching stage prefix (`Planning_`/`Design_`/`Reference_`) the first time such a doc is needed.
- Rename docs with `git mv`, and update every link to them in the same change.

## Docs: what to update for each kind of change
| Change | Update |
|---|---|
| New feature (CLI flag/behavior) | `User_Docs/Usage.md` option reference + relevant behavior section; `README.md` only if the quick-start example changes |
| Bug fix | `User_Docs/Usage.md` "Troubleshooting", if user-visible |
| Design decision | `User_Docs/Usage.md`, relevant section — no separate design-docs folder exists yet |
| New gotcha | `User_Docs/Usage.md` "Troubleshooting" |

- For "verify the docs are updated", use a subagent to diff the branch against this checklist and report the gaps only.

## Git
- Don't work directly on `main`. Create a topic branch named `YYYY-MM-DD-<topic>` and open a PR into `main` with `gh`.
- Commit, push, open a PR or merge only when asked. "Commit and push" means both.

## Live testing
- Lab environment details are in `Live-Testing.local.md` in the project root. That file is gitignored. **Read it only when a task involves live testing.** Never copy its contents into tracked files, commit messages or PR descriptions.
- If `Live-Testing.local.md` is missing, ask for the details. Don't guess.
- Never write secrets into any file, log or commit message, including `Live-Testing.local.md`. That file names *where* the credentials live, not the credentials themselves.
- When an example, doc or test needs a password placeholder, use `ThisIsMy_FAKE_Password6!`. It's obviously fake, and it satisfies typical complexity rules.
