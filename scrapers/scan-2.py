"""Scrape every public tyre product listed on https://gcco.ae.

Run from this directory (or the repository root):

    scrapy runspider scan-2.py

Redesigned to no longer depend on GCCO's separate api.gcco.ae backend, which
(as of this rewrite) is unreachable -- Cloudflare returns Error 525 (SSL
handshake failed between Cloudflare and the origin) for every request to it,
confirmed independent of this scraper (a plain HTTP client gets the same
error). The main gcco.ae site itself is unaffected: it's a server-rendered
Next.js storefront with its own sitemap and JSON-LD structured data on every
product page, so this spider now gets everything from gcco.ae directly:

  1. https://gcco.ae/sitemap.xml lists every /product/... URL directly
     (~6,000 as of writing) -- no pagination/API calls needed to discover them.
  2. Each product page embeds a <script type="application/ld+json"> block
     with @type "Product" (name, sku, brand, price, availability, image,
     description) -- the same schema.org markup search engines read.

Tyre size/width/aspect-ratio/rim/load-speed-index aren't in that JSON-LD, so
they're parsed out of the product name via regex (e.g. "175/70 R13 82H"),
same approach the old API-based version already used as its own fallback
when the API's specification fields were missing.
"""

import csv
import json
import os
import re
import sys
from collections import OrderedDict
from datetime import datetime

from scrapy import Request, Spider
from scrapy.selector import Selector

SIZE_RE = re.compile(r"\b(\d{3})/(\d{2,3})\s*R(\d{2}(?:\.\d+)?)\b", re.I)
LOAD_SPEED_RE = re.compile(r"\b\d{2,3}(?:/\d{2,3})?[A-Z]\b", re.I)
YEAR_RE = re.compile(r"\((\d{4})\)")


class GCCOScraper(Spider):
    name = "gcco"

    DEFAULT_SITEMAP_URL = "https://gcco.ae/sitemap.xml"

    # This script lives in scrapers/, but its default output stays anchored
    # to the project root (one level up), same convention as the other
    # scrapers in this folder -- not the scrapers/ folder itself.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.now().strftime("%d-%m-%Y")

    # An output path can be passed as the first CLI arg, same convention as
    # the other scraper scripts in this folder.
    output_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        base_dir, f"gcco_data_{today}.xlsx"
    )

    custom_settings = {
        "FEED_EXPORTERS": {"xlsx": "scrapy_xlsx.XlsxItemExporter"},
        "FEEDS": {output_file: {"format": "xlsx", "encoding": "utf8", "store_empty": False}},
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_DELAY": 0.2,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [429, 500, 502, 503, 504],
        "LOG_LEVEL": "INFO",
    }

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Upgrade-Insecure-Requests": "1",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.done_sources = set()

    @classmethod
    def _load_sitemap_url(cls):
        """A CSV with a single sitemap URL can be passed as the second CLI arg."""
        if len(sys.argv) > 2:
            with open(sys.argv[2], newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if row and row[0].strip():
                        return row[0].strip()
        return cls.DEFAULT_SITEMAP_URL

    def emit_status(self, url, status, parent=None, url_type=None):
        print(f"URL_STATUS|{url}|{status}|{parent or ''}|{url_type or ''}", flush=True)

    def finish_source(self, source_url, blocked=False):
        if source_url in self.done_sources:
            return
        self.done_sources.add(source_url)
        self.emit_status(source_url, 'blocked' if blocked else 'done', url_type='sitemap')

    def start_requests(self):
        sitemap_url = self._load_sitemap_url()
        self.emit_status(sitemap_url, 'running', url_type='sitemap')
        yield Request(
            sitemap_url,
            headers=self.headers,
            callback=self.parse_sitemap,
            errback=self.handle_error,
            meta={'source_url': sitemap_url, 'dont_merge_cookies': True},
        )

    async def start(self):
        for req in self.start_requests():
            yield req

    def handle_error(self, failure):
        source_url = failure.request.meta.get('source_url', failure.request.url)
        display_url = failure.request.meta.get('display_url', failure.request.url)
        response = getattr(failure.value, "response", None)
        if response is not None:
            self.logger.error("REQUEST ERROR: status=%s url=%s", response.status, response.url)
        else:
            self.logger.error("REQUEST ERROR: %s (%s)", failure.request.url, failure.value)

        if display_url and display_url != source_url:
            self.emit_status(display_url, 'blocked', parent=source_url, url_type='product')
        else:
            self.finish_source(source_url, blocked=True)

    def parse_sitemap(self, response):
        source_url = response.meta.get('source_url', response.url)
        urls = Selector(text=response.text).css("loc::text").getall()
        if not urls:
            urls = Selector(text=response.text).xpath("//*[local-name()='loc']/text()").getall()
        product_urls = [u.strip() for u in urls if u and "/product/" in u]
        self.logger.info("Found %s product URLs in sitemap", len(product_urls))

        for url in product_urls:
            self.emit_status(url, 'pending', parent=source_url, url_type='product')
            yield response.follow(
                url,
                headers=self.headers,
                callback=self.parse_detail,
                errback=self.handle_error,
                meta={'source_url': source_url, 'display_url': url, 'dont_merge_cookies': True},
            )

        self.finish_source(source_url)

    def parse_detail(self, response):
        source_url = response.meta.get('source_url', response.url)
        display_url = response.meta.get('display_url', response.url)
        self.emit_status(display_url, 'running', parent=source_url, url_type='product')

        try:
            product = self._product_ld_json(response)
            if not product:
                self.logger.warning("No Product JSON-LD found on %s", response.url)
                self.emit_status(display_url, 'blocked', parent=source_url, url_type='product')
                return

            name = product.get("name", "").strip()
            offers = product.get("offers") or {}
            images = product.get("image") or []

            item = OrderedDict()
            item["Name"] = name
            item["Brand"] = (product.get("brand") or {}).get("name", "")
            item["SKU"] = product.get("sku", "")
            item["Tire Size"] = self._tire_size(name)
            item["Width"] = self._dimension(name, 1)
            item["Aspect Ratio"] = self._dimension(name, 2)
            item["Rim Diameter"] = self._dimension(name, 3)
            item["Load/Speed Index"] = self._load_speed(name)
            item["Year"] = self._year(name)
            item["Category"] = product.get("category", "")
            item["Price"] = offers.get("price", "")
            item["Currency"] = offers.get("priceCurrency", "")
            item["In Stock"] = self._in_stock(offers.get("availability", ""))
            item["Image URL"] = images[0] if images else ""
            item["Description"] = product.get("description", "")
            item["Source"] = response.url

            yield item
        finally:
            self.emit_status(display_url, 'done', parent=source_url, url_type='product')

    @staticmethod
    def _product_ld_json(response):
        """Returns the schema.org @type:"Product" block from the page's
        JSON-LD <script> tags (a product page has several -- store info,
        website search action, breadcrumbs -- only one is the product itself).
        """
        for script in response.css('script[type="application/ld+json"]::text').getall():
            try:
                data = json.loads(script)
            except json.JSONDecodeError:
                continue
            if data.get("@type") == "Product":
                return data
        return None

    @staticmethod
    def _in_stock(availability):
        availability = (availability or "").lower()
        if "outofstock" in availability or "discontinued" in availability:
            return "No"
        if "instock" in availability or "limitedavailability" in availability or "preorder" in availability:
            return "Yes"
        return "Unknown"

    @staticmethod
    def _tire_size(text):
        match = SIZE_RE.search(text)
        return match.group(0) if match else ""

    @staticmethod
    def _dimension(text, group):
        match = SIZE_RE.search(text)
        return match.group(group) if match else ""

    @staticmethod
    def _load_speed(text):
        match = LOAD_SPEED_RE.search(text)
        return match.group(0) if match else ""

    @staticmethod
    def _year(text):
        match = YEAR_RE.search(text)
        return match.group(1) if match else ""


from scrapy.crawler import CrawlerProcess

if __name__ == "__main__":
    process = CrawlerProcess(GCCOScraper.custom_settings)
    process.crawl(GCCOScraper)
    process.start()
