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

print("=" * 50)
print("scan.py loaded")
print("=" * 50)

class TyreScraper(Spider):
    name = 'tireex'
    print("TyreScraper class created")
    # Save XLSX in the same folder as this file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    today = datetime.now().strftime("%d-%m-%Y")
    output_file = os.path.join(base_dir, f"tireex_data_{today}.xlsx")

    custom_settings = {
        # --- Export to XLSX ---
        "FEED_EXPORTERS": {"xlsx": "scrapy_xlsx.XlsxItemExporter"},
        "FEEDS": {output_file: {"format": "xlsx", "encoding": "utf8", "store_empty": False}},
        "CONCURRENT_REQUESTS": 8,
        "DOWNLOAD_DELAY": 0.5,
        "LOG_LEVEL": "INFO",
    }


    def _start_browser_bridge(self):
        """Launch the persistent Playwright challenge-solver subprocess.

        Must run out-of-process: Scrapy's Twisted asyncio reactor forces a
        SelectorEventLoop on Windows, which can't spawn subprocesses (and
        Playwright launches its browser as one). Kept alive for the whole
        crawl since solving the JS proof-of-work challenge takes ~20-40s.
        """
        fetcher_script = os.path.join(self.base_dir, "_cf_cookie_fetcher.py")
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

        The bridge subprocess can die outright under rare, severe failures
        (e.g. its own Playwright driver connection dying -- see
        _cf_cookie_fetcher.py's in-process recovery, which handles page/
        browser-level crashes but can't recover from that). Without a
        restart here, one such death would silently fail every subsequent
        challenged product for the rest of the crawl instead of just this one.
        """
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
        print("sesson start")

        self._start_browser_bridge()

        self.session = cffi_requests.Session(
            impersonate="chrome",
            headers={
                "Accept-Language": "en-US,en;q=0.9",
                "Referer": "https://tireex.com/"
            }
        )

        # The sitemap route is always behind the JS challenge, so fetch it
        # straight through the browser bridge instead of curl_cffi.
        self.logger.info("Fetching product sitemap...")
        sitemap = self._bridge_fetch('https://tireex.com/product-sitemap.xml')

        print("STATUS:", sitemap["status"])
        print("BODY:")
        print(sitemap["body"][:1000])
        if sitemap["status"] != 200:
            self.logger.error(f"Failed to fetch sitemap: HTTP {sitemap['status']}")
            return

        # Seed the curl_cffi session with the resolved challenge cookies
        self.session.cookies.update(sitemap["cookies"])

        # Parse XML and extract product URLs
        root = etree.fromstring(sitemap["body"].encode("utf-8"))
        ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
        urls = [loc.text for loc in root.findall('.//ns:url/ns:loc', ns)
                if loc.text and '/product/' in loc.text
                and not loc.text.endswith(('.webp', '.jpg', '.png'))]

        self.logger.info(f"Found {len(urls)} product URLs in sitemap")

        for url in urls:
            # Insert /en/ if not already present, to get English content
            if '/en/' not in url:
                url = url.replace('tireex.com/product/', 'tireex.com/en/product/', 1)
            yield Request(url, self.parse_detail, dont_filter=True,
                          meta={'handle_httpstatus_list': [520]})

    def parse_detail(self, response):
        url = response.url

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
                    return
                response = HtmlResponse(url=url, body=bridged["body"].encode("utf-8"), encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Failed to fetch {url}: {e}")
            return

        # Skip non product pages
        if "/en/product/" not in response.url:
            return

        title = response.css('.product-title-wrapper h1.product_title::text').get()
        if not title:
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

        yield item
from scrapy.crawler import CrawlerProcess
        
if __name__ == "__main__":
    process = CrawlerProcess(TyreScraper.custom_settings)
    process.crawl(TyreScraper)
    process.start()
    