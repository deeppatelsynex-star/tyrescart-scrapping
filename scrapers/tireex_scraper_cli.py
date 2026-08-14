import argparse
import json
import os
import subprocess
import sys
from collections import OrderedDict
from datetime import datetime

from curl_cffi import requests as cffi_requests
from lxml import etree
from scrapy import Request, Spider
from scrapy.crawler import CrawlerProcess
from scrapy.http import HtmlResponse


class TyreScraper(Spider):
    name = "tireex"

    # ------------------------------------------------------------------
    # Paths / defaults
    # ------------------------------------------------------------------
    scrapers_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(scrapers_dir)
    today = datetime.now().strftime("%d-%m-%Y")

    DEFAULT_SITEMAP_URL = "https://tireex.com/product-sitemap.xml"

    # CLI arguments are initialized AFTER the class is created.
    # Do not call parse_cli_args() here.
    cli_args = None

    custom_settings = {
        "FEED_EXPORTERS": {
            "xlsx": "scrapy_xlsx.XlsxItemExporter",
        },
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_DELAY": 0.5,
        "LOG_LEVEL": "INFO",
    }

    # ------------------------------------------------------------------
    # CLI
    # ------------------------------------------------------------------
    @staticmethod
    def parse_cli_args(base_dir, today):
        parser = argparse.ArgumentParser(
            description=(
                "Tireex scraper. Use --url for direct product URLs "
                "or --sitemap for a sitemap XML URL."
            )
        )

        source = parser.add_mutually_exclusive_group(required=True)

        source.add_argument(
            "--url",
            action="append",
            dest="urls",
            help=(
                "Product URL to scrape. "
                "Use --url multiple times for multiple URLs."
            ),
        )

        source.add_argument(
            "--sitemap",
            dest="sitemap_url",
            help="Sitemap XML URL containing product URLs.",
        )

        parser.add_argument(
            "--output",
            dest="output_file",
            default=os.path.join(
                base_dir,
                f"tireex_data_{today}.xlsx",
            ),
            help="Output XLSX file path.",
        )

        return parser.parse_args()

    # ------------------------------------------------------------------
    # Status output
    # ------------------------------------------------------------------
    def emit_status(self, url, status, parent=None, url_type=None):
        print(
            f"URL_STATUS|{url}|{status}|"
            f"{parent or ''}|{url_type or ''}",
            flush=True,
        )

    # ------------------------------------------------------------------
    # Browser bridge
    # ------------------------------------------------------------------
    def _start_browser_bridge(self):
        """
        Start the persistent Playwright/Cloudflare browser bridge.

        The bridge is kept as a separate process because Scrapy/Twisted
        on Windows can have event-loop limitations when Playwright tries
        to spawn a browser subprocess.
        """
        fetcher_script = os.path.join(
            self.scrapers_dir,
            "_cf_cookie_fetcher.py",
        )

        if not os.path.exists(fetcher_script):
            raise FileNotFoundError(
                f"Browser bridge not found: {fetcher_script}"
            )

        self.logger.info(
            f"Starting browser bridge: {fetcher_script}"
        )

        self._bridge_proc = subprocess.Popen(
            [
                sys.executable,
                fetcher_script,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def _bridge_fetch(self, url, _retried=False):
        """
        Fetch URL through the persistent browser bridge.
        """
        bridge = getattr(self, "_bridge_proc", None)

        if bridge is None or bridge.poll() is not None:
            self.logger.warning(
                "Browser bridge is not running. Restarting."
            )
            self._start_browser_bridge()
            bridge = self._bridge_proc

        try:
            bridge.stdin.write(
                json.dumps({"url": url}) + "\n"
            )
            bridge.stdin.flush()

            line = bridge.stdout.readline()

        except Exception as exc:
            if not _retried:
                self.logger.warning(
                    f"Browser bridge request failed: {exc}. "
                    "Restarting and retrying once."
                )
                self._start_browser_bridge()
                return self._bridge_fetch(
                    url,
                    _retried=True,
                )

            raise RuntimeError(
                f"Browser bridge communication failed: {exc}"
            ) from exc

        if not line:
            stderr = ""

            try:
                stderr = bridge.stderr.read()
            except Exception:
                pass

            if not _retried:
                self.logger.warning(
                    "Browser bridge died during request. "
                    "Restarting and retrying once."
                )
                self._start_browser_bridge()
                return self._bridge_fetch(
                    url,
                    _retried=True,
                )

            raise RuntimeError(
                f"Browser bridge died: {stderr}"
            )

        try:
            data = json.loads(line)
        except json.JSONDecodeError as exc:
            raise RuntimeError(
                f"Invalid browser bridge response: {line!r}"
            ) from exc

        if "error" in data:
            raise RuntimeError(str(data["error"]))

        return data

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------
    @staticmethod
    def normalize_product_url(url):
        """
        Convert:
            https://tireex.com/product/abc
        to:
            https://tireex.com/en/product/abc

        URLs that already contain /en/product/ are unchanged.
        """
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

    @staticmethod
    def extract_product_urls(xml_body):
        """
        Extract product URLs from a standard sitemap XML.
        """
        root = etree.fromstring(
            xml_body.encode("utf-8")
        )

        namespace = {
            "ns": "http://www.sitemaps.org/schemas/sitemap/0.9"
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
                (".webp", ".jpg", ".jpeg", ".png")
            ):
                continue

            urls.append(
                TyreScraper.normalize_product_url(url)
            )

        # Preserve order while removing duplicates.
        return list(dict.fromkeys(urls))

    # ------------------------------------------------------------------
    # Scrapy start
    # ------------------------------------------------------------------
    async def start(self):
        self._start_browser_bridge()

        self.session = cffi_requests.Session(
            impersonate="chrome",
            headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://tireex.com/",
            },
        )

        # ==============================================================
        # MODE 1: DIRECT URL
        # ==============================================================
        if self.cli_args.urls:
            self.logger.info(
                f"Direct URL mode: "
                f"{len(self.cli_args.urls)} URL(s)"
            )

            for raw_url in self.cli_args.urls:
                url = raw_url.strip()

                if not url:
                    continue

                url = self.normalize_product_url(url)

                self.emit_status(
                    url,
                    "running",
                    url_type="url",
                )

                yield Request(
                    url,
                    callback=self.parse_detail,
                    dont_filter=True,
                    meta={
                        "handle_httpstatus_list": [520],
                        "parent_url": "",
                    },
                )

            return

        # ==============================================================
        # MODE 2: SITEMAP
        # ==============================================================
        sitemap_url = (
            self.cli_args.sitemap_url
            or self.DEFAULT_SITEMAP_URL
        )

        self.logger.info(
            f"Sitemap mode: {sitemap_url}"
        )

        self.emit_status(
            sitemap_url,
            "running",
            url_type="sitemap",
        )

        try:
            sitemap = self._bridge_fetch(
                sitemap_url
            )
        except Exception as exc:
            self.logger.error(
                f"Failed to fetch sitemap: {exc}"
            )

            self.emit_status(
                sitemap_url,
                "failed",
                url_type="sitemap",
            )

            return

        sitemap_status = sitemap.get("status")

        if sitemap_status != 200:
            self.logger.error(
                f"Failed to fetch sitemap: "
                f"HTTP {sitemap_status}"
            )

            self.emit_status(
                sitemap_url,
                "blocked",
                url_type="sitemap",
            )

            return

        # Seed curl_cffi with Cloudflare/challenge cookies.
        cookies = sitemap.get("cookies") or {}

        if cookies:
            self.session.cookies.update(cookies)

        try:
            product_urls = self.extract_product_urls(
                sitemap.get("body", "")
            )
        except Exception as exc:
            self.logger.error(
                f"Failed to parse sitemap XML: {exc}"
            )

            self.emit_status(
                sitemap_url,
                "failed",
                url_type="sitemap",
            )

            return

        self.logger.info(
            f"Found {len(product_urls)} product URLs "
            "in sitemap"
        )

        self.emit_status(
            sitemap_url,
            "done",
            url_type="sitemap",
        )

        for url in product_urls:
            self.emit_status(
                url,
                "pending",
                parent=sitemap_url,
                url_type="product",
            )

            yield Request(
                url,
                callback=self.parse_detail,
                dont_filter=True,
                meta={
                    "handle_httpstatus_list": [520],
                    "parent_url": sitemap_url,
                },
            )

    # ------------------------------------------------------------------
    # Product request
    # ------------------------------------------------------------------
    def parse_detail(self, response):
        url = response.url
        parent_url = response.meta.get(
            "parent_url",
            "",
        )

        self.emit_status(
            url,
            "running",
            parent=parent_url,
            url_type="product",
        )

        # --------------------------------------------------------------
        # First attempt: curl_cffi
        # --------------------------------------------------------------
        try:
            result = self.session.get(
                url,
                timeout=30,
            )

            if result.status_code == 200:
                response = HtmlResponse(
                    url=url,
                    body=result.content,
                    encoding="utf-8",
                )

            else:
                self.logger.info(
                    f"Got HTTP {result.status_code} "
                    f"for {url}. Retrying via browser."
                )

                bridged = self._bridge_fetch(url)

                if bridged.get("status") != 200:
                    self.logger.warning(
                        f"Browser also returned "
                        f"{bridged.get('status')} for {url}"
                    )

                    self.emit_status(
                        url,
                        "failed",
                        parent=parent_url,
                        url_type="product",
                    )

                    return

                response = HtmlResponse(
                    url=url,
                    body=bridged.get(
                        "body",
                        "",
                    ).encode("utf-8"),
                    encoding="utf-8",
                )

        except Exception as exc:
            self.logger.error(
                f"Failed to fetch {url}: {exc}"
            )

            self.emit_status(
                url,
                "failed",
                parent=parent_url,
                url_type="product",
            )

            return

        # --------------------------------------------------------------
        # Validate product page
        # --------------------------------------------------------------
        if "/en/product/" not in response.url:
            self.logger.warning(
                f"Skipping non-product page: {response.url}"
            )

            self.emit_status(
                url,
                "skipped",
                parent=parent_url,
                url_type="product",
            )

            return

        # --------------------------------------------------------------
        # Product title
        # --------------------------------------------------------------
        title = response.css(
            ".product-title-wrapper "
            "h1.product_title::text"
        ).get()

        if not title:
            self.logger.warning(
                f"Product title not found: {url}"
            )

            self.emit_status(
                url,
                "failed",
                parent=parent_url,
                url_type="product",
            )

            return

        # --------------------------------------------------------------
        # Stock
        # --------------------------------------------------------------
        stock_text = response.css(
            "p.stock.in-stock span::text"
        ).get(
            ""
        ).strip()

        # --------------------------------------------------------------
        # Item
        # --------------------------------------------------------------
        item = OrderedDict()

        # Meta title
        meta_title = response.css(
            "title::text"
        ).get(
            ""
        ).strip()

        item["meta_title"] = meta_title

        # New pattern
        if " - " in meta_title:
            item["new_patern"] = (
                meta_title.split(
                    " - ",
                    1,
                )[0].strip()
            )
        else:
            item["new_patern"] = ""

        # Name
        item["Name"] = response.css(
            ".product-title-wrapper "
            "h1.product_title::text"
        ).get(
            ""
        ).strip()

        # SKU
        sku_values = response.css(
            "div.sku-label::text"
        ).getall()

        item["SKU"] = (
            sku_values[-1].strip()
            if sku_values
            else ""
        )

        # Warranty
        warranty_values = response.css(
            "div.warranty-label::text"
        ).getall()

        item["Warranty"] = (
            warranty_values[-1].strip()
            if warranty_values
            else ""
        )

        # --------------------------------------------------------------
        # Price
        # --------------------------------------------------------------
        base_price = response.css(
            "p.price del bdi::text"
        ).get()

        offer_price = response.css(
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
            normal_price = response.css(
                "p.price bdi::text"
            ).get()

            item["Base Price"] = (
                normal_price.strip()
                if normal_price
                else ""
            )

            item["Offer Price"] = ""

        # --------------------------------------------------------------
        # Stock status
        # --------------------------------------------------------------
        item["In Stock"] = (
            "Yes"
            if stock_text.lower() == "in stock"
            else "No"
        )

        # --------------------------------------------------------------
        # Default fields
        # --------------------------------------------------------------
        item["Origin"] = ""
        item["Year of Production"] = ""
        item["Pattern"] = ""

        # --------------------------------------------------------------
        # Product specifications
        # --------------------------------------------------------------
        for li in response.css(
            "ul.product-specifications-list li"
        ):
            key = li.css(
                "p::text"
            ).get(
                ""
            )

            values = li.css(
                "h6::text"
            ).getall()

            key = key.strip()

            value = " ".join(
                value.strip()
                for value in values
                if value.strip()
            )

            if key:
                item[key] = value

        # --------------------------------------------------------------
        # Product image
        # --------------------------------------------------------------
        image_url = response.css(
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

        # --------------------------------------------------------------
        # Source
        # --------------------------------------------------------------
        item["Source"] = response.url

        # --------------------------------------------------------------
        # Success
        # --------------------------------------------------------------
        self.emit_status(
            response.url,
            "done",
            parent=parent_url,
            url_type="product",
        )

        yield item

    # ------------------------------------------------------------------
    # Close browser bridge
    # ------------------------------------------------------------------
    def closed(self, reason):
        bridge = getattr(
            self,
            "_bridge_proc",
            None,
        )

        if not bridge:
            return

        if bridge.poll() is not None:
            return

        try:
            bridge.stdin.write(
                json.dumps({"cmd": "close"}) + "\n"
            )
            bridge.stdin.flush()

            bridge.wait(timeout=10)

        except Exception:
            try:
                bridge.terminate()
            except Exception:
                pass


# ======================================================================
# MAIN
# ======================================================================
if __name__ == "__main__":
    # IMPORTANT:
    # This happens AFTER TyreScraper has been fully created.
    # Therefore base_dir/today are available and no class-scope NameError
    # can occur.
    TyreScraper.cli_args = TyreScraper.parse_cli_args(
        TyreScraper.base_dir,
        TyreScraper.today,
    )

    # Configure XLSX output using the CLI argument.
    TyreScraper.custom_settings["FEEDS"] = {
        TyreScraper.cli_args.output_file: {
            "format": "xlsx",
            "encoding": "utf8",
            "store_empty": False,
        }
    }

    print(
        f"Output file: "
        f"{TyreScraper.cli_args.output_file}"
    )

    if TyreScraper.cli_args.urls:
        print(
            f"Input mode: DIRECT URL "
            f"({len(TyreScraper.cli_args.urls)} URL(s))"
        )

    elif TyreScraper.cli_args.sitemap_url:
        print(
            f"Input mode: SITEMAP "
            f"({TyreScraper.cli_args.sitemap_url})"
        )

    process = CrawlerProcess(
        TyreScraper.custom_settings
    )

    process.crawl(TyreScraper)
    process.start()