"""
Persistent Cloudflare/SG-Security challenge solver.

Runs as a long-lived subprocess (not inside Scrapy/Twisted's asyncio reactor,
which forces a SelectorEventLoop on Windows that can't spawn subprocesses --
Playwright launches its browser as one). Talks to the parent over stdin/stdout
using newline-delimited JSON so a single browser session can be reused for
the whole crawl instead of paying the ~20-40s challenge cost per request.

Protocol (one JSON object per line):
  request:  {"url": "https://..."}
  response: {"status": 200, "body": "...", "final_url": "..."}
            {"error": "..."}
  request:  {"cmd": "close"}  -> process exits
"""
import sys
import json
import time

from playwright.sync_api import sync_playwright

STEALTH_JS = """
Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
window.chrome = { runtime: {} };
"""

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
)

CHALLENGE_TIMEOUT = 45  # seconds to wait for the JS proof-of-work challenge
STABLE_FOR = 2          # seconds the URL must stay off the challenge page


def wait_for_challenge(page):
    deadline = time.time() + CHALLENGE_TIMEOUT
    stable_since = None
    last_url = None
    while time.time() < deadline:
        page.wait_for_timeout(1000)
        cur = page.url
        if "sgcaptcha" not in cur and "/.well-known/captcha" not in cur:
            if cur == last_url and stable_since and time.time() - stable_since > STABLE_FOR:
                return
            if cur != last_url:
                stable_since = time.time()
        else:
            stable_since = None
        last_url = cur


def _launch(playwright):
    browser = playwright.chromium.launch(
        headless=False,
        args=["--disable-blink-features=AutomationControlled"],
    )
    context = browser.new_context(
        user_agent=USER_AGENT,
        viewport={"width": 1366, "height": 768},
        locale="en-US",
    )
    context.add_init_script(STEALTH_JS)
    page = context.new_page()
    return browser, context, page


def main():
    with sync_playwright() as playwright:
        browser, context, page = _launch(playwright)

        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            req = json.loads(line)

            if req.get("cmd") == "close":
                break

            url = req["url"]
            try:
                page.goto(url, wait_until="load", timeout=60000)
                wait_for_challenge(page)
                resp = context.request.get(url)
                out = {
                    "status": resp.status,
                    "body": resp.text(),
                    "final_url": page.url,
                    "cookies": {c["name"]: c["value"] for c in context.cookies()},
                }
            except Exception as e:
                out = {"error": str(e)}
                # Any failure here (page crash, "Connection closed while
                # reading from the driver", etc.) can leave the page --  or
                # the whole browser process under it -- unusable for future
                # navigations, which would otherwise doom every subsequent
                # request for the rest of the crawl. Recover unconditionally:
                # try a fresh page first; if creating *that* also fails, the
                # driver connection itself is dead, so relaunch the browser.
                try:
                    try:
                        page.close()
                    except Exception:
                        pass
                    page = context.new_page()
                except Exception:
                    try:
                        browser.close()
                    except Exception:
                        pass
                    browser, context, page = _launch(playwright)

            sys.stdout.write(json.dumps(out) + "\n")
            sys.stdout.flush()

        browser.close()


if __name__ == "__main__":
    main()
