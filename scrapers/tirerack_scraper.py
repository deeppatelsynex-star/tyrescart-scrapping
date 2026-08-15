"""Scrape tyre catalogue at https://www.tirerack.com/
Conforms to TyresCart protocol (sys.argv[1]=output, sys.argv[2]=input_csv, URL_STATUS).
"""

import os
import re
import sys
import csv
import html
from collections import OrderedDict
from datetime import datetime

from scrapy import Spider, Request, Selector
from scrapy.crawler import CrawlerProcess


class TireRackScraper(Spider):
    name = "tirerack"
    allowed_domains = ["tirerack.com", "www.tirerack.com"]

    # ---- OUTPUT FILE with DATE (sys.argv[1]) ----
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.now().strftime("%d-%m-%Y")
    output_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        base_dir, f"tirerack_data_{today}.xlsx"
    )

    # ---- INPUT CSV (sys.argv[2]) ----
    csv_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        base_dir, "testurls.csv"
    )

    DEFAULT_SITEMAPS = [
        "https://www.tirerack.com/sitemaps/products/sitemap1.xml",
        "https://www.tirerack.com/sitemaps/vehicle/tires-sitemap1.xml",
        "https://www.tirerack.com/sitemaps/vehicle/tires-sitemap2.xml",
    ]

    # ---- SETTINGS ----
    custom_settings = {
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "PLAYWRIGHT_LAUNCH_OPTIONS": {
            "headless": True,
            "args": ["--disable-blink-features=AutomationControlled", "--no-sandbox"],
        },
        "PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT": 60000,
        "FEED_EXPORTERS": {"xlsx": "scrapy_xlsx.XlsxItemExporter"},
        "COOKIES_ENABLED": True,
        "FEEDS": {
            output_file: {"format": "xlsx", "encoding": "utf8", "store_empty": False}
        },
        "DOWNLOAD_DELAY": 1.0,
        "ROBOTSTXT_OBEY": False,
        "CONCURRENT_REQUESTS": 3,
        "LOG_LEVEL": "INFO",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    xml_headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
        ),
        "Accept": "text/xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pending_requests = {}
        self.failed_sources = set()
        self.seen_detail_urls = set()

    # ---- TYRESCART PROTOCOL (KEEP) ----
    def emit_status(self, url, status, parent=None, url_type=None):
        print(f"URL_STATUS|{url}|{status}|{parent or ''}|{url_type or ''}")

    def make_tracked_request(self, url, source_url, callback, use_playwright=True, headers=None):
        self.pending_requests[source_url] = self.pending_requests.get(source_url, 0) + 1
        meta = {"source_url": source_url, "display_url": url}
        if use_playwright:
            meta["playwright"] = True
            meta["playwright_page_goto_kwargs"] = {"wait_until": "domcontentloaded"}
        return Request(
            url=url,
            callback=callback,
            errback=self.request_failed,
            headers=headers or self.headers,
            meta=meta,
            dont_filter=True,
        )

    def finish_source_request(self, source_url):
        remaining = self.pending_requests.get(source_url, 1) - 1
        if remaining > 0:
            self.pending_requests[source_url] = remaining
            return
        self.pending_requests.pop(source_url, None)
        status = "blocked" if source_url in self.failed_sources else "done"
        self.emit_status(source_url, status)

    def request_failed(self, failure):
        source_url = failure.request.meta.get("source_url", failure.request.url)
        self.emit_status(
            failure.request.meta.get("display_url", failure.request.url), "blocked"
        )
        self.failed_sources.add(source_url)
        self.logger.error("Request failed: %s", failure.request.url)
        self.finish_source_request(source_url)

    # ---- ENTRY POINT: reads input CSV ----
    async def start(self):
        urls = []
        if os.path.exists(self.csv_file):
            with open(self.csv_file, newline="", encoding="utf-8") as f:
                for row in csv.reader(f):
                    if not row:
                        continue
                    src = row[0].strip()
                    if src.startswith("http"):
                        urls.append(src)

        if not urls:
            urls = self.DEFAULT_SITEMAPS

        for source_url in urls:
            self.emit_status(source_url, "pending", url_type="root")
            if source_url.endswith(".xml") or "sitemap" in source_url:
                yield self.make_tracked_request(
                    source_url, source_url, self.parse_sitemap, use_playwright=False, headers=self.xml_headers
                )
            else:
                yield self.make_tracked_request(
                    source_url, source_url, self.parse_input_url, use_playwright=True
                )

    # ---- SITEMAP PARSER ----
    def parse_sitemap(self, response):
        source_url = response.meta.get("source_url", response.url)
        self.emit_status(response.url, "running")
        try:
            urls = re.findall(r"<loc>(https?://[^<\s]+)</loc>", response.text)
            self.logger.info("Extracted %d URLs from sitemap %s", len(urls), response.url)
            is_product_sitemap = "products/sitemap" in response.url
            for raw_url in urls:
                url = html.unescape(raw_url.strip())
                if not url:
                    continue
                key = url.rstrip("/")
                if key in self.seen_detail_urls:
                    continue
                self.seen_detail_urls.add(key)
                if is_product_sitemap:
                    self.emit_status(url, "pending", parent=source_url, url_type="product")
                    yield self.make_tracked_request(url, source_url, self.parse_detail, use_playwright=True)
                else:
                    self.emit_status(url, "pending", parent=source_url, url_type="listing")
                    yield self.make_tracked_request(url, source_url, self.parse_listing, use_playwright=True)
        finally:
            self.emit_status(response.url, "done")
            self.finish_source_request(source_url)

    # ---- ROUTING: product vs listing ----
    def parse_input_url(self, response):
        sel = Selector(response)
        is_product = bool(
            sel.css("#productHeader .modelName, h1.product-title, .productSize").get()
        )
        if is_product:
            yield from self.parse_detail(response)
        else:
            yield from self.parse_listing(response)

    # ---- LISTING + PAGINATION ----
    def parse_listing(self, response):
        source_url = response.meta.get("source_url", response.url)
        self.emit_status(response.url, "running")
        try:
            sel = Selector(response)

            # Handle meta-refresh redirects
            meta_tag = sel.xpath('//meta[@http-equiv="refresh"]/@content').get()
            if meta_tag:
                redirect = re.search(r"URL=(.+)", meta_tag, re.I)
                if redirect:
                    redirect_url = response.urljoin(redirect.group(1).strip())
                    self.emit_status(
                        redirect_url, "pending", parent=source_url, url_type="listing"
                    )
                    yield self.make_tracked_request(
                        redirect_url, source_url, self.parse_listing, use_playwright=True
                    )
                    return

            product_links = sel.css(
                '.productHeader h2 a::attr(href), a[href*="/tires/"]::attr(href)'
            ).getall()
            self.logger.info(
                "Listing %s: found %d candidate links", response.url, len(product_links)
            )

            for product_url in set(product_links):
                full_url = response.urljoin(product_url)
                if full_url.endswith(
                    (".xml", ".jpg", ".jpeg", ".png", ".gif", ".css", ".js", ".pdf")
                ):
                    continue
                key = full_url.rstrip("/")
                if key in self.seen_detail_urls:
                    continue
                self.seen_detail_urls.add(key)
                self.emit_status(
                    full_url, "pending", parent=source_url, url_type="product"
                )
                yield self.make_tracked_request(
                    full_url, source_url, self.parse_detail, use_playwright=True
                )
        finally:
            self.emit_status(response.url, "done")
            self.finish_source_request(source_url)

    # ---- DETAIL EXTRACTION ----
    def parse_detail(self, response):
        source_url = response.meta.get("source_url", response.url)
        self.emit_status(response.url, "running")
        try:
            sel = Selector(response)
            item = OrderedDict()

            item["Scraped Date"] = datetime.now().strftime("%d-%m-%Y")
            item["Product Name"] = (
                sel.css("#productHeader .modelName::text").get()
                or sel.css("h1.product-title::text, h1::text").get()
                or sel.css('meta[property="og:title"]::attr(content)').get(default="")
            ).strip()
            item["Tyre Size"] = sel.css(
                ".productSize span::text, .tire-size::text"
            ).get(default="").strip()
            item["SKU"] = sel.css(
                ".skuValue::text, [data-sku]::attr(data-sku)"
            ).get(default="").strip()
            item["Price"] = sel.css(
                "#productPricing .pricingValue::text, .price::text"
            ).get(default="").strip()
            item["Set Price"] = sel.css(
                "#priceTotal .pricingValue::text"
            ).get(default="").strip()
            item["Load / Speed Index"] = sel.css(
                ".loadSpeedIndex::text"
            ).get(default="").strip()
            item["Manufactory Year"] = ""
            item["Origin"] = sel.css(".origin::text").get(default="").strip()
            item["Description"] = " ".join(
                sel.css(
                    "#productDescription *::text, .product-description *::text"
                ).getall()
            ).strip()
            item["Warranty"] = sel.css(".warrantyText::text").get(default="").strip()
            item["Manufacturer Warranty"] = sel.css(
                ".manufacturerWarranty::text"
            ).get(default="").strip()
            item["Display Name"] = sel.css(
                "#displayName::text"
            ).get(default="").strip()
            item["Brand"] = sel.css(
                ".brandName::text, .brand::text"
            ).get(default="").strip()
            item["Run Flat"] = "Yes" if sel.css(".runFlatIcon") else "No"
            item["Promotions and Offers"] = sel.css(
                ".promotionText::text"
            ).get(default="").strip()
            item["Parts Category"] = sel.css(
                ".partsCategory::text"
            ).get(default="").strip()
            item["Auto Stock"] = sel.css(".autoStock::text").get(default="").strip()
            item["Category Quality"] = sel.css(
                ".categoryQuality::text"
            ).get(default="").strip()
            item["Per Item"] = sel.css(".perItem::text").get(default="").strip()
            item["Image"] = (
                sel.css(".enlarge_contain img::attr(src)").get()
                or sel.css('meta[property="og:image"]::attr(content)').get(default="")
            )
            item["Product URL"] = response.url

            yield item
        finally:
            self.emit_status(response.url, "done")
            self.finish_source_request(source_url)


if __name__ == "__main__":
    process = CrawlerProcess(TireRackScraper.custom_settings)
    process.crawl(TireRackScraper)
    process.start()
