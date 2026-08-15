"""Scrape tyre catalogue at https://www.prioritytire.com/
Conforms to TyresCart protocol (sys.argv[1]=output, sys.argv[2]=input_csv, URL_STATUS).
"""

import os
import sys
import csv
import json
import re
from collections import OrderedDict
from datetime import datetime
from urllib.parse import urlparse

from scrapy import Spider, Request
from scrapy.crawler import CrawlerProcess


class PriorityTireScraper(Spider):
    name = "prioritytire.com"
    allowed_domains = ["prioritytire.com", "www.prioritytire.com"]

    # ---- OUTPUT FILE with DATE (sys.argv[1]) ----
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.now().strftime("%d-%m-%Y")
    output_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        base_dir, f"prioritytire_data_{today}.xlsx"
    )

    # ---- INPUT CSV (sys.argv[2]) ----
    csv_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        base_dir, "testurls.csv"
    )

    DEFAULT_SITEMAPS = [
        "https://www.prioritytire.com/sitemap/sitemap-singleproducts-1.xml",
        "https://www.prioritytire.com/sitemap/sitemap-singleproducts-2.xml",
        "https://www.prioritytire.com/sitemap/sitemap-singleproducts-3.xml",
        "https://www.prioritytire.com/sitemap/sitemap-singleproducts-4.xml",
        "https://www.prioritytire.com/sitemap/sitemap-singleproducts-5.xml",
        "https://www.prioritytire.com/sitemap/sitemap-singleproducts-6.xml",
        "https://www.prioritytire.com/sitemap/sitemap-singleproducts-7.xml",
        "https://www.prioritytire.com/sitemap/sitemap-configurableproducts.xml",
    ]

    SKIP_URL_PREFIXES = ("/tire-sets/",)

    # ---- SETTINGS ----
    custom_settings = {
        "FEED_EXPORTERS": {"xlsx": "scrapy_xlsx.XlsxItemExporter"},
        "COOKIES_ENABLED": True,
        "FEEDS": {
            output_file: {"format": "xlsx", "encoding": "utf8", "store_empty": False}
        },
        "DOWNLOAD_DELAY": 0.8,
        "RANDOMIZE_DOWNLOAD_DELAY": True,
        "REQUEST_FINGERPRINTER_IMPLEMENTATION": "2.7",
        "ROBOTSTXT_OBEY": False,
        "RETRY_ENABLED": True,
        "RETRY_TIMES": 3,
        "RETRY_HTTP_CODES": [403, 429, 500, 502, 503, 504],
        "DOWNLOAD_TIMEOUT": 30,
        "CONCURRENT_REQUESTS": 4,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
        "LOG_LEVEL": "INFO",
    }

    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
        "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Cache-Control": "max-age=0",
    }

    xml_headers = {
        "Accept": "text/xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pending_requests = {}
        self.failed_sources = set()
        self.seen_detail_urls = set()

    # ---- TYRESCART PROTOCOL (KEEP) ----
    def emit_status(self, url, status, parent=None, url_type=None):
        print(f"URL_STATUS|{url}|{status}|{parent or ''}|{url_type or ''}")

    def make_tracked_request(self, url, source_url, callback, headers=None):
        self.pending_requests[source_url] = self.pending_requests.get(source_url, 0) + 1
        req_headers = headers if headers is not None else self.headers
        return Request(
            url=url,
            callback=callback,
            errback=self.request_failed,
            headers=req_headers,
            meta={"source_url": source_url, "display_url": url},
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
                    source_url, source_url, self.parse_sitemap, headers=self.xml_headers
                )
            else:
                yield self.make_tracked_request(
                    source_url, source_url, self.parse_input_url
                )

    # ---- ROUTING: sitemap vs detail vs listing ----
    def parse_input_url(self, response):
        raw = response.css("script#__NEXT_DATA__::text").get("")
        if raw and ('"SimpleProduct:' in raw or '"ConfigurableProduct:' in raw):
            yield from self.parse_detail(response)
        elif response.url.endswith(".xml") or "sitemap" in response.url:
            yield from self.parse_sitemap(response)
        else:
            yield from self.parse_listing(response)

    # ---- SITEMAP PARSER ----
    def parse_sitemap(self, response):
        source_url = response.meta.get("source_url", response.url)
        self.emit_status(response.url, "running")
        try:
            urls = response.xpath("//*[local-name()='loc']/text()").getall()
            skipped = 0
            for url in urls:
                url = url.strip()
                if not url:
                    continue
                path = urlparse(url).path
                if any(path.startswith(p) for p in self.SKIP_URL_PREFIXES):
                    skipped += 1
                    continue
                key = url.rstrip("/")
                if key in self.seen_detail_urls:
                    continue
                self.seen_detail_urls.add(key)
                self.emit_status(url, "pending", parent=source_url, url_type="product")
                yield self.make_tracked_request(url, source_url, self.parse_detail)
            self.logger.info(f"[sitemap] {response.url} -> {len(urls)} URLs ({skipped} skipped)")
        finally:
            self.emit_status(response.url, "done")
            self.finish_source_request(source_url)

    # ---- LISTING PARSER ----
    def parse_listing(self, response):
        source_url = response.meta.get("source_url", response.url)
        self.emit_status(response.url, "running")
        try:
            links = response.css("a[href*='/by-brand/']::attr(href), a[href*='/tire/']::attr(href)").getall()
            for link in links:
                product_url = response.urljoin(link)
                path = urlparse(product_url).path
                if any(path.startswith(p) for p in self.SKIP_URL_PREFIXES):
                    continue
                key = product_url.rstrip("/")
                if key in self.seen_detail_urls:
                    continue
                self.seen_detail_urls.add(key)
                self.emit_status(product_url, "pending", parent=source_url, url_type="product")
                yield self.make_tracked_request(product_url, source_url, self.parse_detail)
        finally:
            self.emit_status(response.url, "done")
            self.finish_source_request(source_url)

    # ---- DETAIL EXTRACTION ----
    def parse_detail(self, response):
        source_url = response.meta.get("source_url", response.url)
        self.emit_status(response.url, "running")
        try:
            raw = response.css("script#__NEXT_DATA__::text").get("")
            if not raw:
                self.logger.warning(f"No __NEXT_DATA__ at: {response.url}")
                return

            try:
                data = json.loads(raw)
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON error at {response.url}: {e}")
                return

            apollo = (
                data.get("props", {})
                    .get("pageProps", {})
                    .get("apolloState", {})
            )

            PRODUCT_TYPE_PREFIXES = (
                "SimpleProduct:",
                "ConfigurableProduct:",
                "BundleProduct:",
                "GroupedProduct:",
                "VirtualProduct:",
            )
            product = None
            for key, val in apollo.items():
                if (
                    isinstance(val, dict)
                    and "sku" in val
                    and "price_range" in val
                    and any(key.startswith(p) for p in PRODUCT_TYPE_PREFIXES)
                ):
                    product = val
                    break

            if not product:
                self.logger.warning(f"No product in Apollo state at: {response.url}")
                return

            yield self._build_item(product, response.url)
        finally:
            self.emit_status(response.url, "done")
            self.finish_source_request(source_url)

    def _build_item(self, p, url):
        attrs = {}
        for key, val in p.items():
            if "attribute_values" in key and isinstance(val, list):
                for attr in val:
                    code = attr.get("code", "")
                    values = attr.get("values", [])
                    label = values[0].get("label", "") if values else ""
                    attrs[code] = label
                break

        price_range = p.get("price_range", {})
        min_price = price_range.get("minimum_price", {})
        final_price = min_price.get("final_price", {}).get("value", "")
        regular_price = min_price.get("regular_price", {}).get("value", "")

        def fmt_price(v):
            try:
                return f"${float(v):.2f}"
            except (TypeError, ValueError):
                return str(v) if v else ""

        load_speed = " / ".join(filter(None, [
            attrs.get("load_index", ""),
            attrs.get("speed_rating", ""),
        ]))

        small_image = p.get("small_image", {})
        image_url = small_image.get("url", "") if isinstance(small_image, dict) else ""

        rating = p.get("productRating", {})
        rating_str = ""
        if isinstance(rating, dict) and rating.get("ratingValue"):
            rating_str = f"{rating['ratingValue']} ({rating.get('ratingCount', 0)} reviews)"

        promo_labels = p.get("promo_labels", []) or []
        promos = ", ".join(str(x) for x in promo_labels if x)

        item = OrderedDict()
        item["Scraped Date"]          = datetime.now().strftime("%d-%m-%Y")
        item["Product Name"]          = (p.get("name") or "").strip()
        item["Tyre Size"]             = attrs.get("size", "")
        item["SKU"]                   = (p.get("sku") or "").strip()
        item["Price"]                 = fmt_price(final_price)
        item["Set Price"]             = fmt_price(regular_price) if regular_price != final_price else ""
        item["Load / Speed Index"]    = load_speed
        item["Manufactory Year"]      = attrs.get("dot", "")
        item["Origin"]                = (p.get("country_of_origin") or "").strip()
        item["Description"]           = ""
        item["Warranty"]              = attrs.get("treadlife_warranty", "")
        item["Manufacturer Warranty"] = ""
        item["Display Name"]          = (p.get("name") or "").strip()
        item["Brand"]                 = attrs.get("brand", "")
        item["Model"]                 = attrs.get("model", "")
        item["Run Flat"]              = attrs.get("run_flat", "")
        item["Promotions and Offers"] = promos
        item["Parts Category"]        = attrs.get("performance", "")
        item["Auto Stock"]            = (p.get("stock_status") or "").replace("_", " ").title()
        item["Tabby Method"]          = ""
        item["Category Quality"]      = attrs.get("car_type", "")
        item["Per Item"]              = fmt_price(final_price)
        item["Season"]                = attrs.get("season", "")
        item["Load Range"]            = attrs.get("load_range", "")
        item["Sidewall"]              = attrs.get("sidewall_specifics", "")
        item["Tread Depth"]           = attrs.get("tread_depth", "")
        item["Section Width"]         = attrs.get("section_width", "")
        item["Aspect Ratio"]          = attrs.get("aspect_ratio", "")
        item["Rim Diameter"]          = attrs.get("rim_diameter", "")
        item["UTQG"]                  = (p.get("utqg") or "").strip()
        item["EAN"]                   = (p.get("ean") or "").strip()
        item["UPC"]                   = (p.get("upc_code") or "").strip()
        item["MPN"]                   = (p.get("mpn1") or "").strip()
        item["Overall Diameter"]      = (p.get("overall_diameter") or "").strip()
        item["Rating"]                = rating_str
        item["Petrol"]                = ""
        item["Cloud"]                 = ""
        item["Sound"]                 = ""
        item["Video"]                 = ""
        item["Image"]                 = image_url
        item["Product URL"]           = url
        return item


if __name__ == "__main__":
    process = CrawlerProcess(PriorityTireScraper.custom_settings)
    process.crawl(PriorityTireScraper)
    process.start()
