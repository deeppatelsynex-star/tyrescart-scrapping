"""Scrape every public tyre product listed on https://gcco.ae.

Run from this directory (or the repository root):

    scrapy runspider "scan 2.py"

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

import json
import os
import re
from collections import OrderedDict
from datetime import datetime

from scrapy import Request, Spider
from scrapy.selector import Selector

SIZE_RE = re.compile(r"\b(\d{3})/(\d{2,3})\s*R(\d{2}(?:\.\d+)?)\b", re.I)
LOAD_SPEED_RE = re.compile(r"\b\d{2,3}(?:/\d{2,3})?[A-Z]\b", re.I)
YEAR_RE = re.compile(r"\((\d{4})\)")


class GCCOScraper(Spider):
    name = "gcco"

    SITEMAP_URL = "https://gcco.ae/sitemap.xml"

    base_dir = os.path.dirname(os.path.abspath(__file__))
    today = datetime.now().strftime("%d-%m-%Y")
    output_file = os.path.join(base_dir, f"gcco_data_{today}.xlsx")

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
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    }

    async def start(self):
        yield Request(self.SITEMAP_URL, headers=self.headers, callback=self.parse_sitemap,
                      errback=self.handle_error)

    def handle_error(self, failure):
        response = getattr(failure.value, "response", None)
        if response is not None:
            self.logger.error("REQUEST ERROR: status=%s url=%s", response.status, response.url)
        else:
            self.logger.error("REQUEST ERROR: %s (%s)", failure.request.url, failure.value)

    def parse_sitemap(self, response):
        urls = Selector(text=response.text).css("loc::text").getall()
        product_urls = [u.strip() for u in urls if u and "/product/" in u]
        self.logger.info("Found %s product URLs in sitemap", len(product_urls))

        for url in product_urls:
            yield response.follow(url, headers=self.headers, callback=self.parse_detail,
                                  errback=self.handle_error)

    def parse_detail(self, response):
        product = self._product_ld_json(response)
        if not product:
            self.logger.warning("No Product JSON-LD found on %s", response.url)
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
