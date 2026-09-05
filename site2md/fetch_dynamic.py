from __future__ import annotations

from playwright.sync_api import sync_playwright

# Best-effort "expand everything" pass, run repeatedly until nothing new opens:
#   1. force every native <details> element open
#   2. click anything advertising a collapsed ARIA state (but not inside a real
#      <a href> link, since on SPA doc sites those are nav items whose onClick
#      does client-side routing rather than expanding in-page content), so
#      framework onClick handlers fire and (for React/Vue-style conditional
#      rendering) actually mount the hidden content
#   3. drop `hidden` attributes left over from simple show/hide toggles
_EXPAND_JS = r"""
() => {
  document.querySelectorAll('details:not([open])').forEach(d => d.setAttribute('open', ''));

  const toggles = Array.from(document.querySelectorAll('[aria-expanded="false"]'))
    .filter(t => !t.closest('a[href]'));
  toggles.forEach(t => { try { t.click(); } catch (e) {} });

  document.querySelectorAll('[hidden]').forEach(el => el.removeAttribute('hidden'));

  return toggles.length;
}
"""


def render(url: str, *, user_agent: str, timeout_ms: int = 30000, expand_rounds: int = 4) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page(user_agent=user_agent)
            # "networkidle" hangs forever on sites with persistent websockets/analytics
            # polling (common on SPA doc platforms), so wait for the DOM instead and
            # give client-side rendering a fixed settle window before expanding.
            page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
            page.wait_for_timeout(2000)
            landed_url = page.url
            for _ in range(expand_rounds):
                newly_clicked = page.evaluate(_EXPAND_JS)
                page.wait_for_timeout(300)

                # A click-driven toggle can still turn out to be SPA client-side
                # navigation (no full page load, so goto's own tracking won't catch
                # it). If the URL moved off the page we were asked to capture,
                # restore it and stop clicking rather than risk capturing the
                # wrong page's content under this page's file name.
                if page.url != landed_url:
                    page.goto(landed_url, wait_until="domcontentloaded", timeout=timeout_ms)
                    page.wait_for_timeout(1000)
                    break

                if not newly_clicked:
                    break
            return page.content()
        finally:
            browser.close()
