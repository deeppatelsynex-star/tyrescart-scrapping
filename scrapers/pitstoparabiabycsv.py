# MUST be first

# asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# from twisted.internet import asyncioreactor
# asyncioreactor.install()

import re
import os
import sys
import csv
from datetime import datetime
from collections import OrderedDict

from scrapy import Spider, Request, Selector # type: ignore


class TyreScraper(Spider):
    name = "pitstoparabia"

    # =========================
    # OUTPUT FILE
    # =========================
    # A per-run output path can be passed as the first CLI arg so concurrent
    # runs (one per user session) don't overwrite each other's file.
    # This script lives in scrapers/, but its default output/CSV paths stay
    # anchored to the project root (one level up) to match where app.py and
    # testurls.csv actually live.
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    today = datetime.now().strftime("%d-%m-%Y")

    output_file = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        base_dir,
        f"pitstoparabia_data_{today}.xlsx"
    )

    # =========================
    # CSV FILE
    # =========================
    csv_file = sys.argv[2] if len(sys.argv) > 2 else os.path.join(
        base_dir,
        "testurls.csv"
    )

    # =========================
    # SETTINGS
    # =========================
    custom_settings = {

        # XLSX Export
        "FEED_EXPORTERS": {
            "xlsx": "scrapy_xlsx.XlsxItemExporter"
        },
        "COOKIES_ENABLED": True,
        "FEEDS": {
            output_file: {
                "format": "xlsx",
                "encoding": "utf8",
                "store_empty": False,
            }
        },

        "DOWNLOAD_DELAY": 0.5,
        "CONCURRENT_REQUESTS": 3,

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pending_requests = {}
        self.failed_sources = set()
        self.seen_listing_pages = set()
        self.seen_detail_urls = set()
        self.exported_product_urls = set()

    def emit_status(self, url, status, parent=None, url_type=None):
        print(f"URL_STATUS|{url}|{status}|{parent or ''}|{url_type or ''}")

    @staticmethod
    def normalise_url(url):
        """Use a consistent key while preserving meaningful query parameters."""
        return (url or '').split('#', 1)[0].rstrip('/')

    def source_url(self, response_or_failure):
        request = getattr(response_or_failure, 'request', response_or_failure)
        return request.meta.get('source_url', request.url)

    def display_url(self, response_or_failure):
        request = getattr(response_or_failure, 'request', response_or_failure)
        return request.meta.get('display_url', request.url)

    def make_tracked_request(self, url, source_url, callback):
        self.pending_requests[source_url] = self.pending_requests.get(source_url, 0) + 1
        headers = self.headers.copy()
        headers['Referer'] = source_url
        return Request(
            url=url,
            callback=callback,
            errback=self.request_failed,
            headers=headers,
            meta={'source_url': source_url, 'display_url': url},
            dont_filter=True,
            
        )

    def mark_source_running(self, source_url):
        self.emit_status(source_url, 'running')

    def finish_source_request(self, source_url):
        remaining = self.pending_requests.get(source_url, 1) - 1
        if remaining > 0:
            self.pending_requests[source_url] = remaining
            return

        self.pending_requests.pop(source_url, None)
        status = 'blocked' if source_url in self.failed_sources else 'done'
        self.emit_status(source_url, status)

    def request_failed(self, failure):
        source_url = self.source_url(failure)
        self.emit_status(self.display_url(failure), 'blocked')
        self.failed_sources.add(source_url)
        self.logger.error('Request failed for %s: %s', failure.request.url, failure.value)
        self.finish_source_request(source_url)

    # =========================
    # START
    # =========================
    async def start(self):
        submitted_urls = set()
        with open(self.csv_file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if not row:
                    continue
                source_url = row[0].strip()
                normalised_source_url = self.normalise_url(source_url)

                if not source_url.startswith("http") or normalised_source_url in submitted_urls:
                    continue

                submitted_urls.add(normalised_source_url)
                # An explicitly submitted product URL is already scheduled below,
                # so a listing page must not schedule it a second time.
                self.seen_detail_urls.add(normalised_source_url)
                self.emit_status(source_url, 'pending', url_type='root')

                yield self.make_tracked_request(source_url, source_url, self.parse_input_url)
    
    # async def start(self):

    #     # yield Request(
    #     #     "https://www.pitstoparabia.com/en/tyres/265-35-r18",
    #     #     callback=self.parse_listing,
    #     #     headers=self.headers,
    #     #     dont_filter=True,
    #     # )
    #     yield Request(
    #         url='https://www.pitstoparabia.com/en/tyres/265-35-r18',
    #         callback=self.parse_listing,
    #         headers=self.headers,
    #         dont_filter=True
        # )
    
    # =========================
    # PARSE INPUT URL
    # =========================
    def parse_input_url(self, response):
        is_product_page = bool(response.css(
            'h1[itemprop="name"], .product-info-price, #product-addtocart-button'
        ).get())

        if is_product_page:
            yield from self.parse_detail(response)
        else:
            yield from self.parse_listing(response)

    # =========================
    # PARSE LISTING PAGE
    # =========================
    def parse_listing(self, response):
        source_url = self.source_url(response)
        display_url = self.display_url(response)
        request_blocked = False
        self.emit_status(display_url, 'running')

        try:
            if response.status == 403:
                request_blocked = True
                self.failed_sources.add(source_url)
                self.logger.warning('Blocked listing URL %s', response.url)
                self.emit_status(display_url, 'blocked')
                return

            self.seen_listing_pages.add((source_url, self.normalise_url(response.url)))
            product_links = response.css('a.product-item-link::attr(href)').getall()
            self.logger.info('Found %s products for %s', len(product_links), source_url)

            for link in product_links:
                product_url = response.urljoin(link)
                product_key = self.normalise_url(product_url)
                if not product_key or product_key in self.seen_detail_urls:
                    continue

                self.seen_detail_urls.add(product_key)
                self.emit_status(product_url, 'pending', parent=source_url, url_type='product')
                yield self.make_tracked_request(product_url, source_url, self.parse_detail)

            next_page = response.css(
                'a.next::attr(href), .pages-item-next a::attr(href), a.action.next::attr(href)'
            ).get()
            if next_page:
                next_page_url = response.urljoin(next_page)
                page_key = (source_url, self.normalise_url(next_page_url))
                if page_key not in self.seen_listing_pages:
                    self.seen_listing_pages.add(page_key)
                    self.emit_status(next_page_url, 'pending', parent=source_url, url_type='listing')
                    yield self.make_tracked_request(next_page_url, source_url, self.parse_listing)
        finally:
            if display_url != source_url and not request_blocked:
                self.emit_status(display_url, 'done')
            self.finish_source_request(source_url)

    # =========================
    # PRODUCT DETAIL
    # =========================
    def parse_detail(self, response):
        source_url = self.source_url(response)
        display_url = self.display_url(response)
        request_blocked = False
        self.emit_status(display_url, 'running')

        try:
            if response.status == 403:
                request_blocked = True
                self.failed_sources.add(source_url)
                self.logger.warning('Blocked product URL %s', response.url)
                self.emit_status(display_url, 'blocked')
                return

            product_key = self.normalise_url(response.url)
            if product_key in self.exported_product_urls:
                return
            self.exported_product_urls.add(product_key)

            # If an Add to Cart button exists with id "product-addtocart-button" or a tocart/add-to-cart class, we assume in-stock.
            add_to_cart_btn = response.css('button#product-addtocart-button, div.actions.add-to-cart button, button.tocart, button.add-to-cart')
            out_of_stock_div = response.css('div.stock.unavailable, .stock.unavailable')

            if add_to_cart_btn:
                InStock = 'Yes'
            elif out_of_stock_div:
                InStock = 'No'
            else:
                # fallback: if there's a stock text containing "out of stock"
                txt = ' '.join(response.css('div.stock::text, .stock::text').getall()).lower()
                InStock = 'No' if 'out of stock' in txt or 'unavailable' in txt else ''

            if InStock != 'Yes':
                return

            brand_val = response.css('.brand a::attr(title)').get('').strip()
            item = OrderedDict()
            raw_name = response.css('h1[itemprop="name"]::text').get('').strip()
            item['Sku'] = response.css('.sku::text').get('').strip()
            item['Product Name'] = raw_name.replace(brand_val, '').replace('  ', '').strip()
            item['Brand'] = brand_val
            item['InStock'] = InStock
            item['Size'] = response.css('.size_block span:contains("Size:") + b::text').get('').strip().replace('  ', '').replace('/None', '')
            item['Serv. Desc'] = ''.join([t.strip() for t in response.css('span:contains("Serv. Desc")').xpath('parent::*/text()').getall() if t.strip()]).replace(' ', '')
            item['Year'] = response.css('[title="Year of manufacture"]::text').get('').strip()
            item['Country'] = ''.join([t.strip() for t in response.css('span:contains("Country")').xpath('parent::*/text()').getall() if t.strip()])
            item['Tyre Type'] = response.css('.detail_left .v_type::attr(alt)').get('').strip().replace('Run Flat', 'Runflat')
            item['Tyre Marking'] = response.css('[itemprop="name"] .part_no::text').get('').strip()
            item['Price'] = response.css('[class="product-info-price product_price"] .price::text').get('').strip().replace('AED ', '')
            item['Set Price'] = response.css('.set_price .price::text').get('').strip().replace('AED ', '')
            item['Promo Text'] = ' | '.join(self.get_sel_text(response.css('.offer_block_inner')))
            item['Promo Code'] = response.css('.promo_cnt b::text').get('').strip()
            item['Vehicle Type'] = response.css('.product_thumbnail_container .v_type::attr(alt)').get('').strip()
            item['Warranty'] = ' '.join(self.get_sel_text(response.css('.warranty span')))
            item['Sidewall Style'] = response.css('span:contains("Sidewall Style")').xpath('parent::li/text()').get('').strip()

            try:
                item['UTQG'] = ' '.join(self.get_sel_text(response.css('span:contains("UTQG")').xpath('parent::*/span/text()'))[1:])
            except Exception:
                item['UTQG'] = ' '.join([t.strip() for t in response.css('span:contains("UTQG")').xpath('parent::*/span/text()').getall()][1:])

            item['Fuel Efficiency Rating'] = (response.css('.tyres_labels .tyre_label::attr(title)').re_first('Fuel Efficiency Rating:(.+)') or '').strip()
            item['Wet Grip Rating'] = (response.css('.tyres_labels .tyre_label::attr(title)').re_first('Wet Grip Rating:(.+)') or '').strip()
            item['External Noise'] = (response.css('.tyres_labels .tyre_label::attr(title)').re_first('External Noise:(.+)') or '').strip()

            images = response.css('[property="og:image"]::attr(content)').getall()
            item['Image'] = images[-1] if images else ''
            item['Source'] = response.url

            yield item
        finally:
            if display_url != source_url and not request_blocked:
                self.emit_status(display_url, 'done')
            self.finish_source_request(source_url)

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
