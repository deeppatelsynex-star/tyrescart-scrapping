import csv
import random
import re
import os
import sys
import json
import subprocess
from datetime import datetime
from collections import OrderedDict
from scrapy import Spider, Request, Selector # type: ignore
from scrapy.http import HtmlResponse
from curl_cffi import requests as cffi_requests
from lxml import etree


import threading

class TyreScraper(Spider):
    name = 'tireex'

    # scrapers/ folder itself -- needed to locate the sibling
    # _cf_cookie_fetcher.py bridge script regardless of where output goes.
    scrapers_dir = os.path.dirname(os.path.abspath(__file__))
    # This script lives in scrapers/, but its default output stays anchored
    # to the project root (one level up), same convention as the other
    # scrapers in this folder -- not the scrapers/ folder itself.
    base_dir = os.path.dirname(scrapers_dir)
    today = datetime.now().strftime("%d-%m-%Y")

    # An output path can be passed as the first CLI arg, same convention as
    # the other scraper scripts in this folder.
    output_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        base_dir, f"tireex_data_{today}.xlsx"
    )

    DEFAULT_SITEMAP_URL = 'https://tireex.com/product-sitemap.xml'

    custom_settings = {
        # --- Export to XLSX ---
        "FEED_EXPORTERS": {"xlsx": "scrapy_xlsx.XlsxItemExporter"},
        "FEEDS": {output_file: {"format": "xlsx", "encoding": "utf8", "store_empty": False}},
        "CONCURRENT_REQUESTS": 4,
        "DOWNLOAD_DELAY": 0.5,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bridge_lock = threading.Lock()

    @classmethod
    def _load_urls(cls):
        """A CSV with URLs (sitemap or direct product URLs) can be passed
        as the second CLI arg.
        """
        if len(sys.argv) > 2 and os.path.exists(sys.argv[2]):
            urls = []
            with open(sys.argv[2], newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if row and row[0].strip():
                        urls.append(row[0].strip())
            if urls:
                return urls
        return [cls.DEFAULT_SITEMAP_URL]

    def emit_status(self, url, status, parent=None, url_type=None):
        print(f"URL_STATUS|{url}|{status}|{parent or ''}|{url_type or ''}", flush=True)

    def _start_browser_bridge(self):
        """Launch the persistent Playwright challenge-solver subprocess.

        Must run out-of-process: Scrapy's Twisted asyncio reactor forces a
        SelectorEventLoop on Windows, which can't spawn subprocesses (and
        Playwright launches its browser as one). Kept alive for the whole
        crawl since solving the JS proof-of-work challenge takes ~20-40s.
        """
        fetcher_script = os.path.join(self.scrapers_dir, "_cf_cookie_fetcher.py")
        self._bridge_proc = subprocess.Popen(
            [sys.executable, fetcher_script],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
        )

    def _bridge_fetch(self, url, _retried=False):
        """Fetch a URL through the persistent browser, solving the
        Cloudflare/SG Security challenge if one is served.
        Protected by _bridge_lock for thread safety across Scrapy workers.
        """
        with self._bridge_lock:
            if self._bridge_proc.poll() is not None:
                self.logger.warning("Browser bridge subprocess had exited; restarting it.")
                self._start_browser_bridge()

            self._bridge_proc.stdin.write(json.dumps({"url": url}) + "\n")
            self._bridge_proc.stdin.flush()

            line = self._bridge_proc.stdout.readline()
            if not line:
                stderr = self._bridge_proc.stderr.read()
                if not _retried:
                    self.logger.warning("Browser bridge died mid-request; restarting and retrying once.")
                    self._start_browser_bridge()
                    return self._bridge_fetch(url, _retried=True)
                raise RuntimeError(f"Browser bridge died: {stderr}")

            data = json.loads(line)
            if "error" in data:
                raise RuntimeError(data["error"])
            return data

    def closed(self, reason):
        bridge = getattr(self, "_bridge_proc", None)
        if bridge and bridge.poll() is None:
            try:
                bridge.stdin.write(json.dumps({"cmd": "close"}) + "\n")
                bridge.stdin.flush()
                bridge.wait(timeout=10)
            except Exception:
                bridge.terminate()

    async def start(self):
        self._start_browser_bridge()

        self.session = cffi_requests.Session(
            impersonate="chrome",
            headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://tireex.com/"
            }
        )

        input_urls = self._load_urls()
        for input_url in input_urls:
            if input_url.endswith('.xml') or 'sitemap' in input_url.lower():
                sitemap_url = input_url
                self.emit_status(sitemap_url, 'running', url_type='sitemap')

                self.logger.info("Fetching product sitemap...")
                try:
                    sitemap = self._bridge_fetch(sitemap_url)
                except Exception as e:
                    self.logger.error(f"Failed to fetch sitemap: {e}")
                    self.emit_status(sitemap_url, 'blocked', url_type='sitemap')
                    continue

                if sitemap["status"] != 200:
                    self.logger.error(f"Failed to fetch sitemap: HTTP {sitemap['status']}")
                    self.emit_status(sitemap_url, 'blocked', url_type='sitemap')
                    continue

                # Seed the curl_cffi session with the resolved challenge cookies
                self.session.cookies.update(sitemap["cookies"])

                # Parse product URLs (supports raw XML and browser-rendered HTML sitemap tables)
                body_text = sitemap["body"]
                raw_urls = Selector(text=body_text).css("table#sitemap a::attr(href), a[href*='/product/']::attr(href), loc::text").getall()
                if not raw_urls:
                    raw_urls = re.findall(r'href=["\'](https?://[^"\']*/product/[^"\']*)["\']', body_text)
                if not raw_urls:
                    raw_urls = re.findall(r'<loc>\s*(https?://[^\s<]+/product/[^\s<]*)\s*</loc>', body_text)

                urls = list(dict.fromkeys(
                    u.strip() for u in raw_urls
                    if u and '/product/' in u
                    and not u.endswith(('.webp', '.jpg', '.png', '.svg', '.jpeg'))
                ))

                self.logger.info(f"Found {len(urls)} product URLs in sitemap")
                for url in urls:
                    if '/en/' not in url:
                        url = url.replace('tireex.com/product/', 'tireex.com/en/product/', 1)
                    self.emit_status(url, 'pending', parent=sitemap_url, url_type='product')
                    yield Request(url, self.parse_detail, dont_filter=True,
                                  meta={'source_url': sitemap_url, 'display_url': url, 'handle_httpstatus_list': [202, 403, 520]})
                self.emit_status(sitemap_url, 'done', url_type='sitemap')
            else:
                prod_url = input_url
                if '/en/' not in prod_url and '/product/' in prod_url:
                    prod_url = prod_url.replace('tireex.com/product/', 'tireex.com/en/product/', 1)
                self.emit_status(prod_url, 'pending', url_type='product')
                yield Request(prod_url, self.parse_detail, dont_filter=True,
                              meta={'source_url': prod_url, 'display_url': prod_url, 'handle_httpstatus_list': [202, 403, 520]})

    def parse_detail(self, response):
        url = response.url
        source_url = response.meta.get('source_url', url)
        display_url = response.meta.get('display_url', url)
        parent_url = source_url if source_url != display_url else None
        self.emit_status(display_url, 'running', parent=parent_url, url_type='product')

        # Fetch via curl_cffi first (fast); only some pages are challenged,
        # so fall back to the browser bridge when that happens.
        try:
            r = self.session.get(url, timeout=30)
            if r.status_code == 200:
                response = HtmlResponse(url=url, body=r.content, encoding='utf-8')
            else:
                self.logger.info(f"Got {r.status_code} for {url}, retrying via browser")
                bridged = self._bridge_fetch(url)
                if bridged["status"] != 200:
                    self.logger.warning(f"Browser also got {bridged['status']} for {url}")
                    self.emit_status(display_url, 'blocked', parent=parent_url, url_type='product')
                    return
                response = HtmlResponse(url=url, body=bridged["body"].encode("utf-8"), encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            self.emit_status(display_url, 'blocked', parent=parent_url, url_type='product')
            return

        # Skip non product pages
        if "/en/product/" not in response.url:
            self.emit_status(display_url, 'blocked', parent=parent_url, url_type='product')
            return

        title = response.css('.product-title-wrapper h1.product_title::text').get()
        if not title:
            self.emit_status(display_url, 'blocked', parent=parent_url, url_type='product')
            return

        stock_text = response.css('p.stock.in-stock span::text').get('').strip()

        item = OrderedDict()

        # Extract meta_title from <title> tag
        meta_title = response.css('title::text').get('').strip()
        item['meta_title'] = meta_title

        # Extract new_patern (text before " - " in meta_title)
        if ' - ' in meta_title:
            item['new_patern'] = meta_title.split(' - ')[0].strip()
        else:
            item['new_patern'] = ''

        item['Name'] = response.css('.product-title-wrapper h1.product_title::text').get('').strip()
        item['SKU'] = (
            response.css('div.sku-label::text')
            .getall()[-1]
            .strip()
        )

        warranty_text = response.css('div.warranty-label::text').getall()

        if warranty_text:
            item['Warranty'] = warranty_text[-1].strip()
        else:
            item['Warranty'] = ''

        base_price = response.css('p.price del bdi::text').get()
        offer_price = response.css('p.price ins bdi::text').get()

        # Case 1: Special offer exists
        if offer_price:
            item['Base Price'] = base_price.strip() if base_price else ''
            item['Offer Price'] = offer_price.strip()

        # Case 2: No offer → single price
        else:
            normal_price = response.css('p.price bdi::text').get()
            item['Base Price'] = normal_price.strip() if normal_price else ''
            item['Offer Price'] = ''

        if stock_text.strip().lower() == 'in stock':
            item['In Stock'] = 'Yes'
        else:
            item['In Stock'] = 'No'

        item['Origin'] = ''
        item['Year of Production'] = ''
        item['Pattern'] = ''

        for li in response.css('ul.product-specifications-list li'):
            key = li.css('p::text').get('')
            value = li.css('h6::text').getall()

            key = key.strip()
            value = ' '.join(v.strip() for v in value if v.strip())

            if key:
                item[key] = value

        # Extract image URL from product gallery
        image_url = response.css('figure.woocommerce-product-gallery__image img.wp-post-image::attr(src)').get('')
        item['Image URL'] = image_url.strip() if image_url else ''

        item['Source'] = response.url

        self.emit_status(display_url, 'done', parent=parent_url, url_type='product')
        yield item
from scrapy.crawler import CrawlerProcess
        
if __name__ == "__main__":
    process = CrawlerProcess(TyreScraper.custom_settings)
    process.crawl(TyreScraper)
    process.start()
    