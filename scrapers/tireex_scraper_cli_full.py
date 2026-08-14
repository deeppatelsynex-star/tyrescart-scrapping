
"""
Tireex single-file scraper for web applications.

Features:
    1. Direct product URL(s)
    2. Sitemap URL
    3. Persistent Playwright browser session
    4. Cloudflare / SG-Security challenge handling
    5. curl_cffi for normal product requests
    6. XLSX output
    7. JSON status output for a web-app parent process
    8. Can be used from CMD or subprocess.Popen()

Examples:

    Direct URL:
        python tireex_scraper.py \
            --url "https://tireex.com/en/product/example"

    Multiple URLs:
        python tireex_scraper.py \
            --url "URL1" \
            --url "URL2"

    Sitemap:
        python tireex_scraper.py \
            --sitemap "https://tireex.com/product-sitemap.xml"

    Custom output:
        python tireex_scraper.py \
            --sitemap "https://tireex.com/product-sitemap.xml" \
            --output "result.xlsx"

Web-app JSON input mode:

    echo {"input_type":"url","urls":["URL1","URL2"]} | python tireex.py --stdin

    echo {"input_type":"sitemap","sitemap_url":"SITEMAP_URL"} | python tireex.py --stdin

Output:

    JSON status lines are printed to stdout:

    {"type":"status","url":"...","status":"running"}
    {"type":"status","url":"...","status":"done"}
    {"type":"status","url":"...","status":"failed"}

    Final:

    {"type":"complete","output":"...","scraped":10}
"""

import argparse
import json
import os
import sys
import time
from collections import OrderedDict
from datetime import datetime

from curl_cffi import requests as cffi_requests
from lxml import etree
from playwright.sync_api import sync_playwright
from scrapy import Selector


# ======================================================================
# CONFIGURATION
# ======================================================================

SITE_URL = "https://tireex.com"

DEFAULT_SITEMAP_URL = (
    "https://tireex.com/product-sitemap.xml"
)

CHALLENGE_TIMEOUT = 45
CHALLENGE_STABLE_TIME = 2

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/128.0.0.0 Safari/537.36"
)

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

TODAY = datetime.now().strftime("%d-%m-%Y")

DEFAULT_OUTPUT = os.path.join(
    BASE_DIR,
    f"tireex_data_{TODAY}.xlsx",
)


# ======================================================================
# STEALTH JAVASCRIPT
# ======================================================================

STEALTH_JS = """
Object.defineProperty(
    navigator,
    'webdriver',
    {
        get: () => undefined
    }
);

Object.defineProperty(
    navigator,
    'languages',
    {
        get: () => ['en-US', 'en']
    }
);

Object.defineProperty(
    navigator,
    'plugins',
    {
        get: () => [1, 2, 3, 4, 5]
    }
);

window.chrome = {
    runtime: {}
};
"""


# ======================================================================
# STATUS
# ======================================================================

def send_status(
    status,
    url="",
    parent="",
    url_type="",
    **extra,
):
    """
    Send one JSON status message.

    This is intended for Flask/FastAPI/subprocess integration.
    """

    message = {
        "type": "status",
        "status": status,
        "url": url,
        "parent": parent,
        "url_type": url_type,
        **extra,
    }

    print(
        json.dumps(
            message,
            ensure_ascii=False,
        ),
        flush=True,
    )


def send_error(message):
    print(
        json.dumps(
            {
                "type": "error",
                "message": message,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


# ======================================================================
# URL NORMALIZATION
# ======================================================================

def normalize_product_url(url):
    url = url.strip()

    if (
        "/product/" in url
        and "/en/product/" not in url
    ):
        url = url.replace(
            "tireex.com/product/",
            "tireex.com/en/product/",
            1,
        )

    return url


# ======================================================================
# BROWSER
# ======================================================================

def launch_browser(playwright):
    browser = playwright.chromium.launch(
        headless=False,
        args=[
            "--disable-blink-features=AutomationControlled"
        ],
    )

    context = browser.new_context(
        user_agent=USER_AGENT,
        viewport={
            "width": 1366,
            "height": 768,
        },
        locale="en-US",
    )

    context.add_init_script(
        STEALTH_JS
    )

    page = context.new_page()

    return browser, context, page


def wait_for_challenge(page):
    deadline = (
        time.time()
        + CHALLENGE_TIMEOUT
    )

    stable_since = None
    last_url = None

    while time.time() < deadline:

        page.wait_for_timeout(1000)

        current_url = page.url

        challenge = (
            "sgcaptcha" in current_url
            or "/.well-known/captcha"
            in current_url
        )

        if not challenge:

            if (
                current_url == last_url
                and stable_since
                and (
                    time.time()
                    - stable_since
                    >= CHALLENGE_STABLE_TIME
                )
            ):
                return True

            if current_url != last_url:
                stable_since = time.time()

        else:
            stable_since = None

        last_url = current_url

    return False


# ======================================================================
# BROWSER FETCH
# ======================================================================

def browser_fetch(
    playwright,
    browser,
    context,
    page,
    url,
):
    """
    Fetch a URL using the persistent browser.

    Returns:
        response_data,
        browser,
        context,
        page
    """

    try:

        page.goto(
            url,
            wait_until="load",
            timeout=60000,
        )

        wait_for_challenge(page)

        response = context.request.get(
            url,
            timeout=60000,
        )

        cookies = {
            cookie["name"]: cookie["value"]
            for cookie in context.cookies()
        }

        data = {
            "status": response.status,
            "body": response.text(),
            "final_url": page.url,
            "cookies": cookies,
        }

        return (
            data,
            browser,
            context,
            page,
        )

    except Exception as exc:

        # Try replacing the page first.
        try:

            try:
                page.close()
            except Exception:
                pass

            page = context.new_page()

            return (
                {
                    "error": str(exc)
                },
                browser,
                context,
                page,
            )

        except Exception:

            # Browser/driver itself may be dead.
            try:
                browser.close()
            except Exception:
                pass

            try:

                browser, context, page = (
                    launch_browser(playwright)
                )

                return (
                    {
                        "error": str(exc),
                        "browser_restarted": True,
                    },
                    browser,
                    context,
                    page,
                )

            except Exception as restart_error:

                return (
                    {
                        "error": (
                            f"{exc}; "
                            f"browser restart failed: "
                            f"{restart_error}"
                        )
                    },
                    browser,
                    context,
                    page,
                )


# ======================================================================
# SITEMAP
# ======================================================================

def extract_product_urls(xml):
    root = etree.fromstring(
        xml.encode("utf-8")
    )

    namespace = {
        "ns": (
            "http://www.sitemaps.org/"
            "schemas/sitemap/0.9"
        )
    }

    urls = []

    for loc in root.findall(
        ".//ns:url/ns:loc",
        namespace,
    ):

        if not loc.text:
            continue

        url = loc.text.strip()

        if "/product/" not in url:
            continue

        if url.lower().endswith(
            (
                ".webp",
                ".jpg",
                ".jpeg",
                ".png",
            )
        ):
            continue

        urls.append(
            normalize_product_url(url)
        )

    return list(
        dict.fromkeys(urls)
    )


# ======================================================================
# PRODUCT PARSER
# ======================================================================

def parse_product(url, html):
    selector = Selector(
        text=html
    )

    title = selector.css(
        ".product-title-wrapper "
        "h1.product_title::text"
    ).get(
        ""
    ).strip()

    if not title:
        return None

    item = OrderedDict()

    meta_title = selector.css(
        "title::text"
    ).get(
        ""
    ).strip()

    item["meta_title"] = meta_title

    if " - " in meta_title:
        item["new_patern"] = (
            meta_title
            .split(" - ", 1)[0]
            .strip()
        )
    else:
        item["new_patern"] = ""

    item["Name"] = title

    sku_values = selector.css(
        "div.sku-label::text"
    ).getall()

    item["SKU"] = (
        sku_values[-1].strip()
        if sku_values
        else ""
    )

    warranty_values = selector.css(
        "div.warranty-label::text"
    ).getall()

    item["Warranty"] = (
        warranty_values[-1].strip()
        if warranty_values
        else ""
    )

    base_price = selector.css(
        "p.price del bdi::text"
    ).get()

    offer_price = selector.css(
        "p.price ins bdi::text"
    ).get()

    if offer_price:

        item["Base Price"] = (
            base_price.strip()
            if base_price
            else ""
        )

        item["Offer Price"] = (
            offer_price.strip()
        )

    else:

        normal_price = selector.css(
            "p.price bdi::text"
        ).get()

        item["Base Price"] = (
            normal_price.strip()
            if normal_price
            else ""
        )

        item["Offer Price"] = ""

    stock = selector.css(
        "p.stock.in-stock span::text"
    ).get(
        ""
    ).strip()

    item["In Stock"] = (
        "Yes"
        if stock.lower() == "in stock"
        else "No"
    )

    item["Origin"] = ""
    item["Year of Production"] = ""
    item["Pattern"] = ""

    for li in selector.css(
        "ul.product-specifications-list li"
    ):

        key = li.css(
            "p::text"
        ).get(
            ""
        ).strip()

        values = li.css(
            "h6::text"
        ).getall()

        value = " ".join(
            x.strip()
            for x in values
            if x.strip()
        )

        if key:
            item[key] = value

    image_url = selector.css(
        "figure.woocommerce-product-gallery__image "
        "img.wp-post-image::attr(src)"
    ).get(
        ""
    )

    item["Image URL"] = (
        image_url.strip()
        if image_url
        else ""
    )

    item["Source"] = url

    return item


# ======================================================================
# XLSX
# ======================================================================

def save_xlsx(items, output_file):
    """
    Save scraped items using openpyxl.

    This keeps the script independent of Scrapy.
    """

    from openpyxl import Workbook

    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Products"

    if not items:
        workbook.save(output_file)
        return

    headers = []

    for item in items:
        for key in item.keys():
            if key not in headers:
                headers.append(key)

    worksheet.append(headers)

    for item in items:

        worksheet.append(
            [
                item.get(
                    header,
                    "",
                )
                for header in headers
            ]
        )

    workbook.save(
        output_file
    )


# ======================================================================
# SCRAPER
# ======================================================================

def scrape(
    urls=None,
    sitemap_url=None,
    output_file=DEFAULT_OUTPUT,
):
    """
    Main scraper function.

    Can be called directly by Flask/FastAPI:

        scrape(
            urls=["https://..."],
            output_file="result.xlsx"
        )

    or:

        scrape(
            sitemap_url="https://...",
            output_file="result.xlsx"
        )
    """

    if not urls and not sitemap_url:
        raise ValueError(
            "Provide urls or sitemap_url"
        )

    if urls and sitemap_url:
        raise ValueError(
            "Use either urls or sitemap_url, not both"
        )

    urls = urls or []

    items = []

    session = cffi_requests.Session(
        impersonate="chrome",
        headers={
            "Accept-Language": (
                "en-US,en;q=0.9"
            ),
            "Referer": SITE_URL + "/",
        },
    )

    with sync_playwright() as playwright:

        browser, context, page = (
            launch_browser(playwright)
        )

        try:

            # ==========================================================
            # SITEMAP MODE
            # ==========================================================

            if sitemap_url:

                send_status(
                    "running",
                    sitemap_url,
                    url_type="sitemap",
                )

                sitemap_response, browser, context, page = (
                    browser_fetch(
                        playwright,
                        browser,
                        context,
                        page,
                        sitemap_url,
                    )
                )

                if sitemap_response.get(
                    "status"
                ) != 200:

                    send_status(
                        "failed",
                        sitemap_url,
                        url_type="sitemap",
                    )

                    raise RuntimeError(
                        "Sitemap request failed: "
                        + str(
                            sitemap_response.get(
                                "error",
                                sitemap_response.get(
                                    "status"
                                ),
                            )
                        )
                    )

                session.cookies.update(
                    sitemap_response.get(
                        "cookies",
                        {},
                    )
                )

                urls = extract_product_urls(
                    sitemap_response["body"]
                )

                send_status(
                    "done",
                    sitemap_url,
                    url_type="sitemap",
                    total=len(urls),
                )

            # ==========================================================
            # PRODUCT MODE
            # ==========================================================

            total = len(urls)

            for index, raw_url in enumerate(
                urls,
                start=1,
            ):

                url = normalize_product_url(
                    raw_url
                )

                send_status(
                    "running",
                    url,
                    url_type="product",
                    index=index,
                    total=total,
                )

                try:

                    # --------------------------------------------------
                    # Fast request
                    # --------------------------------------------------

                    response = session.get(
                        url,
                        timeout=30,
                    )

                    if response.status_code == 200:

                        html = response.text

                    else:

                        # ----------------------------------------------
                        # Browser fallback
                        # ----------------------------------------------

                        browser_response, browser, context, page = (
                            browser_fetch(
                                playwright,
                                browser,
                                context,
                                page,
                                url,
                            )
                        )

                        if browser_response.get(
                            "status"
                        ) != 200:

                            send_status(
                                "failed",
                                url,
                                url_type="product",
                                index=index,
                                total=total,
                            )

                            continue

                        session.cookies.update(
                            browser_response.get(
                                "cookies",
                                {},
                            )
                        )

                        html = browser_response[
                            "body"
                        ]

                    # --------------------------------------------------
                    # Parse
                    # --------------------------------------------------

                    item = parse_product(
                        url,
                        html,
                    )

                    if item is None:

                        send_status(
                            "failed",
                            url,
                            url_type="product",
                            reason="product data not found",
                            index=index,
                            total=total,
                        )

                        continue

                    items.append(item)

                    send_status(
                        "done",
                        url,
                        url_type="product",
                        index=index,
                        total=total,
                        scraped=len(items),
                    )

                except Exception as exc:

                    send_status(
                        "failed",
                        url,
                        url_type="product",
                        error=str(exc),
                        index=index,
                        total=total,
                    )

            # ==========================================================
            # OUTPUT
            # ==========================================================

            save_xlsx(
                items,
                output_file,
            )

            print(
                json.dumps(
                    {
                        "type": "complete",
                        "status": "done",
                        "output": os.path.abspath(
                            output_file
                        ),
                        "scraped": len(items),
                        "total": len(urls),
                    },
                    ensure_ascii=False,
                ),
                flush=True,
            )

            return {
                "status": "done",
                "output": os.path.abspath(
                    output_file
                ),
                "scraped": len(items),
                "total": len(urls),
            }

        finally:

            try:
                browser.close()
            except Exception:
                pass


# ======================================================================
# STDIN WEB-APP MODE
# ======================================================================

def run_stdin_mode(output_file):
    """
    Read one JSON object from stdin.

    Example:

        {"input_type":"url","urls":["URL1","URL2"]}

    or:

        {"input_type":"sitemap","sitemap_url":"URL"}
    """

    line = sys.stdin.readline().strip()

    if not line:
        raise ValueError(
            "No JSON input received"
        )

    data = json.loads(line)

    input_type = data.get(
        "input_type"
    )

    if input_type == "url":

        urls = data.get(
            "urls",
            [],
        )

        if isinstance(urls, str):
            urls = [urls]

        return scrape(
            urls=urls,
            output_file=output_file,
        )

    if input_type == "sitemap":

        sitemap_url = data.get(
            "sitemap_url"
        )

        if not sitemap_url:
            raise ValueError(
                "sitemap_url is required"
            )

        return scrape(
            sitemap_url=sitemap_url,
            output_file=output_file,
        )

    raise ValueError(
        "input_type must be 'url' or 'sitemap'"
    )


# ======================================================================
# CLI
# ======================================================================

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Tireex single-file scraper"
        )
    )

    source = parser.add_mutually_exclusive_group()

    source.add_argument(
        "--url",
        action="append",
        dest="urls",
        help=(
            "Product URL. "
            "Can be specified multiple times."
        ),
    )

    source.add_argument(
        "--sitemap",
        dest="sitemap_url",
        help="Product sitemap URL.",
    )

    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help="Output XLSX path.",
    )

    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read scraper input as JSON from stdin.",
    )

    args = parser.parse_args()

    try:

        if args.stdin:

            run_stdin_mode(
                args.output
            )

        elif args.urls:

            scrape(
                urls=args.urls,
                output_file=args.output,
            )

        elif args.sitemap:

            scrape(
                sitemap_url=args.sitemap,
                output_file=args.output,
            )

        else:

            parser.error(
                "Provide --url, --sitemap, "
                "or --stdin."
            )

    except KeyboardInterrupt:

        send_error(
            "Scraper stopped by user"
        )

        sys.exit(130)

    except Exception as exc:

        send_error(
            str(exc)
        )

        sys.exit(1)


if __name__ == "__main__":
    main()
