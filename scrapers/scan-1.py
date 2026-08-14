import csv
import re
import os
import sys
from datetime import datetime
from collections import OrderedDict
from scrapy import Spider, Request, Selector # type: ignore
from scrapy.exceptions import CloseSpider
from tqdm import tqdm

class TyreScraper(Spider):
    name = 'kafaratplus'
    count = 0
    limit = 640
    pbar = None

    # This script lives in scrapers/, but its default output stays anchored
    # to the project root (one level up), same convention as the other
    # scrapers in this folder -- not the scrapers/ folder itself.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.now().strftime("%d-%m-%Y")

    # An output path can be passed as the first CLI arg, same convention as
    # the other scraper scripts in this folder.
    output_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        base_dir, f"kafaratplus_data_{today}.xlsx"
    )

    custom_settings = {
        # --- Export to XLSX ---
        "FEED_EXPORTERS": {"xlsx": "scrapy_xlsx.XlsxItemExporter"},
        "FEEDS": {output_file: {"format": "xlsx", "encoding": "utf8", "store_empty": False}},
        # Keep console clean so the progress bar is readable
        "LOG_LEVEL": "WARNING",
    }

    DEFAULT_URL = 'https://kafaratplus.com/sitemap/en/sitemap_products.xml'

    @classmethod
    def _load_url(cls):
        """A CSV with a single sitemap URL (same one-per-line format the
        other scrapers in this folder read) can be passed as the second CLI
        arg to override the hardcoded default above.
        """
        if len(sys.argv) > 2:
            with open(sys.argv[2], newline='', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if row and row[0].strip():
                        return row[0].strip()
        return cls.DEFAULT_URL

    headers = {
        'Accept': 'text/html, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
                      ' (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'sec-ch-ua': '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"macOS"'
    }

    seen = []

    def emit_status(self, url, status, parent=None, url_type=None):
        print(f"URL_STATUS|{url}|{status}|{parent or ''}|{url_type or ''}", flush=True)

    def start_requests(self):
        target_url = self._load_url()
        self.emit_status(target_url, 'running', url_type='sitemap')
        yield Request(target_url, self.parse_brands, errback=self.parse_error,
                      meta={'dont_merge_cookies': True, 'source_url': target_url},
                      headers=self.headers)

    async def start(self):
        for request in self.start_requests():
            yield request

    def parse_brands(self, response):
        source_url = response.meta.get('source_url', response.url)
        urls = [
            url.strip() for url in Selector(text=response.text).css('loc::text').getall()
            if url and "/PCR-SUV-Tires/" in url
        ]
        self.pbar = tqdm(total=len(urls), desc="Scraping products", unit="page") if tqdm else None
        for url in urls:
            self.emit_status(url, 'pending', parent=source_url, url_type='product')
            yield response.follow(
                url, self.parse_detail, errback=self.parse_error,
                meta={**response.meta, 'source_url': source_url, 'display_url': url},
                headers=self.headers,
            )
        self.emit_status(source_url, 'done', url_type='sitemap')

    def parse_error(self, failure):
        # Shared errback for both the initial sitemap request and every
        # per-product request -- report root or product as blocked.
        source_url = failure.request.meta.get('source_url')
        display_url = failure.request.meta.get('display_url', failure.request.url)
        if source_url and failure.request.url == source_url:
            self.emit_status(source_url, 'blocked', url_type='sitemap')
        else:
            self.emit_status(display_url, 'blocked', parent=source_url, url_type='product')
        if self.pbar is not None:
            self.pbar.update(1)

    def closed(self, reason):
        if self.pbar is not None:
            self.pbar.close()

    def parse_detail(self, response):
        source_url = response.meta.get('source_url', response.url)
        display_url = response.meta.get('display_url', response.url)
        self.emit_status(display_url, 'running', parent=source_url, url_type='product')
        if self.pbar is not None:
            self.pbar.update(1)

        try:
            # detect buttons ONLY inside product-infor

            notify_btn = response.xpath(
                "//div[contains(@class,'product-infor')]//button//span[contains(text(),'Notify Me')]"
            )

            quote_btn = response.xpath(
                "//div[contains(@class,'product-infor')]//button//span[contains(text(),'Request Quotation')]"
            )

            # --- LOGIC ---
            if notify_btn or quote_btn:
                ooStock = 'Yes'
            else:
                txt = ' '.join(response.css('div.stock::text, .stock::text').getall()).lower()
                if 'out of stock' in txt or 'unavailable' in txt:
                    ooStock = 'Yes'
                else:
                    ooStock = 'No'
                    
            item = OrderedDict()
            item['Name'] = response.css('h2.product-title::text').get('').strip()
            item['Category'] = response.css('.product-category span::text').get('').strip()
            item['Warranty'] = (
                                    response.xpath(
                                    "//div[contains(@class,'manufacturer-warranty')]//span[contains(text(),'Warranty')]/text()"
                                )
                                .get('')
                                .replace('Warranty:', '')
                                .strip()
                            )
            item['Offer Price'] = response.css('span[itemprop="price"]::text').get('').strip()
            item['Price'] = response.css('.product-origin-price span::text').get('').strip()
            item['Out of stock'] = ooStock
            item['Offer Image'] = response.css('.main-gallery-section img[alt="offer logo"]::attr(src)').get()
            item['Width'] = ''
            item['Height'] = ''
            item['Rim'] = ''

            for spec in response.css('div[itemprop="additionalProperty"]'):
                key = spec.css('[itemprop="name"]::text').get('')
                value = spec.css('[itemprop="value"]::text').get('')

                if not key or not value:
                    continue

                key = key.strip().lower()
                value = value.strip()

                if key == 'width':
                    item['Width'] = value
                elif key == 'height':
                    item['Height'] = value
                elif key == 'rim':
                    item['Rim'] = value

            item['Tire Size'] = ''
            item['Model'] = ''
            item['Brand'] = ''
            item['Speed/Load Index'] = ''
            item['Country of Origin'] = ''
            item['Year'] = ''
            item['Heat Resistance'] = ''

            # Extract Year and Country from product-meta div
            model_text = response.css('span[itemprop="model"]::text').get('')
            year_match = re.search(r'\b(20\d{2})\b', model_text)
            if year_match:
                item['Year'] = year_match.group(1)

            country_from_meta = response.css('span[itemprop="countryOfOrigin"]::text').get('')
            if country_from_meta:
                item['Country of Origin'] = country_from_meta.strip()
            item['Usage Type'] = ''
            item['Compliance'] = ''
            item['Technologies'] = ''
            
            KEY_MAP = {
                'tire size': 'Tire Size',
                'tyre size': 'Tire Size',
                'size': 'Tire Size',
                'model': 'Model',
                'brand': 'Brand',
                'speed/load index': 'Speed/Load Index',
                'load/speed index': 'Speed/Load Index',
                'country of origin': 'Country of Origin',
                'country': 'Country of Origin',
                'origin': 'Country of Origin',
                'heat resistance': 'Heat Resistance',
                'usage type': 'Usage Type',
                'compliance': 'Compliance',
                'technologies': 'Technologies',
            }

            for row in response.css('table.tire-specs-table-en tbody tr, table.tire-specs-table tbody tr'):
                raw_key = row.css('td:nth-child(1)::text').get('')
                value = row.css('td:nth-child(2)::text, td:nth-child(2) strong::text').get('')

                raw_key = raw_key.lower()

                if raw_key in KEY_MAP:
                    item[KEY_MAP[raw_key]] = value

            item['Source'] = response.url
            yield item
        finally:
            self.emit_status(display_url, 'done', parent=source_url, url_type='product')

    def get_sel_text(self, selector, dont_skip=None):
        dont_skip = dont_skip or []
        assert isinstance(dont_skip, list), "'dont_skip' must be a 'list' or None type"

        required_tags = ['a', 'i', 'u', 'strong', 'b', 'em', 'span', 'sup', 'sub', 'font']
        required_tags.extend(dont_skip)

        results = []
        for text in selector.getall():
            for tag in required_tags:
                text = re.sub(r'<\s*%s>' % tag, '', text)
                text = re.sub(r'</\s*%s>' % tag, '', text)
                text = re.sub(r'<\s*%s[^\w][^>]*>' % tag, '', text)
                text = re.sub(r'</\s*%s[^\w]\s*>' % tag, '', text)

            text = text.replace('\r\n', ' ')
            text = re.sub(r'<!--.*?-->', '', text, re.S)
            sel = Selector(text=text)

            all_texts = sel.xpath(''.join([
                'descendant::text()/parent::*[name()!="td"]',
                '[name()!="script"][name()!="style"]/text()'
            ])).getall()
            all_texts = [x.strip() for x in all_texts]
            results += all_texts

        results = list(filter(None, results))
        return results
from scrapy.crawler import CrawlerProcess
        
if __name__ == "__main__":
    process = CrawlerProcess(TyreScraper.custom_settings)
    process.crawl(TyreScraper)
    process.start()