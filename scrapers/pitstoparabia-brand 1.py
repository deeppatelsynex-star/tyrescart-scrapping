import re
import datetime
from collections import OrderedDict
from scrapy import Spider, Request, Selector # type: ignore

try:
    from tqdm import tqdm
except ImportError:
    tqdm = None
    print("NOTE: tqdm is not installed, so no progress bar will be shown.")
    print("      Install it with:  py -m pip install tqdm")


# ---------------------------------------------------------------------------
# Paste/edit your brand URLs here. One per line.
# ---------------------------------------------------------------------------
BRAND_URLS = [
    'https://www.pitstoparabia.com/en/tyres/brands/accelera',
    'https://www.pitstoparabia.com/en/tyres/brands/acenda',
    'https://www.pitstoparabia.com/en/tyres/brands/achilles',
    'https://www.pitstoparabia.com/en/tyres/brands/apollo',
    'https://www.pitstoparabia.com/en/tyres/brands/Aptanytires',
    'https://www.pitstoparabia.com/en/tyres/brands/armstrong',
    'https://www.pitstoparabia.com/en/tyres/brands/arroyo',
    'https://www.pitstoparabia.com/en/tyres/brands/atlas',
    'https://www.pitstoparabia.com/en/tyres/brands/atturotyres',
    'https://www.pitstoparabia.com/en/tyres/brands/autogrip',
    'https://www.pitstoparabia.com/en/tyres/brands/barum',
    'https://www.pitstoparabia.com/en/tyres/brands/Bearway',
    'https://www.pitstoparabia.com/en/tyres/brands/bfgoodrich',
    'https://www.pitstoparabia.com/en/tyres/brands/bridgestone',
    'https://www.pitstoparabia.com/en/tyres/brands/continental',
    'https://www.pitstoparabia.com/en/tyres/brands/coopertires',
    'https://www.pitstoparabia.com/en/tyres/brands/davanti',
    'https://www.pitstoparabia.com/en/tyres/brands/deestone',
    'https://www.pitstoparabia.com/en/tyres/brands/Doublestar_tyres',
    'https://www.pitstoparabia.com/en/tyres/brands/dunlop',
    'https://www.pitstoparabia.com/en/tyres/brands/eternity',
    'https://www.pitstoparabia.com/en/tyres/brands/falken',
    'https://www.pitstoparabia.com/en/tyres/brands/firestone',
    'https://www.pitstoparabia.com/en/tyres/brands/Forceland',
    'https://www.pitstoparabia.com/en/tyres/brands/fortunetires',
    'https://www.pitstoparabia.com/en/tyres/brands/FRZTRAC',
    'https://www.pitstoparabia.com/en/tyres/brands/Fulda',
    'https://www.pitstoparabia.com/en/tyres/brands/FullRun',
    'https://www.pitstoparabia.com/en/tyres/brands/Galaxia',
    'https://www.pitstoparabia.com/en/tyres/brands/generaltires',
    'https://www.pitstoparabia.com/en/tyres/brands/Giti',
    'https://www.pitstoparabia.com/en/tyres/brands/goodride',
    'https://www.pitstoparabia.com/en/tyres/brands/Goodtrip',
    'https://www.pitstoparabia.com/en/tyres/brands/goodyear',
    'https://www.pitstoparabia.com/en/tyres/brands/Gripmaxtires',
    'https://www.pitstoparabia.com/en/tyres/brands/habilead',
    'https://www.pitstoparabia.com/en/tyres/brands/hankook',
    'https://www.pitstoparabia.com/en/tyres/brands/horizon',
    'https://www.pitstoparabia.com/en/tyres/brands/infinity',
    'https://www.pitstoparabia.com/en/tyres/brands/kenda',
    'https://www.pitstoparabia.com/en/tyres/brands/kumhotyre',
    'https://www.pitstoparabia.com/en/tyres/brands/Kustone',
    'https://www.pitstoparabia.com/en/tyres/brands/landsail',
    'https://www.pitstoparabia.com/en/tyres/brands/landspidertires',
    'https://www.pitstoparabia.com/en/tyres/brands/lassa',
    'https://www.pitstoparabia.com/en/tyres/brands/laufenn',
    'https://www.pitstoparabia.com/en/tyres/brands/leao_tyres',
    'https://www.pitstoparabia.com/en/tyres/brands/lexani',
    'https://www.pitstoparabia.com/en/tyres/brands/LingLong',
    'https://www.pitstoparabia.com/en/tyres/brands/marshal',
    'https://www.pitstoparabia.com/en/tyres/brands/mastercraft',
    'https://www.pitstoparabia.com/en/tyres/brands/Matraxtires',
    'https://www.pitstoparabia.com/en/tyres/brands/Maxen',
    'https://www.pitstoparabia.com/en/tyres/brands/maxxis',
    'https://www.pitstoparabia.com/en/tyres/brands/michelin',
    'https://www.pitstoparabia.com/en/tyres/brands/mickeythompson',
    'https://www.pitstoparabia.com/en/tyres/brands/nankang',
    'https://www.pitstoparabia.com/en/tyres/brands/neoterra',
    'https://www.pitstoparabia.com/en/tyres/brands/nexen',
    'https://www.pitstoparabia.com/en/tyres/brands/nitto',
    'https://www.pitstoparabia.com/en/tyres/brands/otani',
    'https://www.pitstoparabia.com/en/tyres/brands/ovation',
    'https://www.pitstoparabia.com/en/tyres/brands/pallyking',
    'https://www.pitstoparabia.com/en/tyres/brands/pearly',
    'https://www.pitstoparabia.com/en/tyres/brands/Petlas',
    'https://www.pitstoparabia.com/en/tyres/brands/pirelli',
    'https://www.pitstoparabia.com/en/tyres/brands/Radar',
    'https://www.pitstoparabia.com/en/tyres/brands/riken',
    'https://www.pitstoparabia.com/en/tyres/brands/roadmarch',
    'https://www.pitstoparabia.com/en/tyres/brands/roadcruza',
    'https://www.pitstoparabia.com/en/tyres/brands/roadstone',
    'https://www.pitstoparabia.com/en/tyres/brands/RoadX',
    'https://www.pitstoparabia.com/en/tyres/brands/rotalla',
    'https://www.pitstoparabia.com/en/tyres/brands/sailun_tyres',
    'https://www.pitstoparabia.com/en/tyres/brands/Sava',
    'https://www.pitstoparabia.com/en/tyres/brands/seamtyre',
    'https://www.pitstoparabia.com/en/tyres/brands/sportrak',
    'https://www.pitstoparabia.com/en/tyres/brands/sumitomo',
    'https://www.pitstoparabia.com/en/tyres/brands/tbb_Tires',
    'https://www.pitstoparabia.com/en/tyres/brands/thunderer',
    'https://www.pitstoparabia.com/en/tyres/brands/toyo',
    'https://www.pitstoparabia.com/en/tyres/brands/tracmaxtires',
    'https://www.pitstoparabia.com/en/tyres/brands/Triangle',
    'https://www.pitstoparabia.com/en/tyres/brands/VenomPower',
    'https://www.pitstoparabia.com/en/tyres/brands/vitourtire',
    'https://www.pitstoparabia.com/en/tyres/brands/Vredestein',
    'https://www.pitstoparabia.com/en/tyres/brands/Windforcetires',
    'https://www.pitstoparabia.com/en/tyres/brands/Winruntires',
    'https://www.pitstoparabia.com/en/tyres/brands/yokohama',
    'https://www.pitstoparabia.com/en/tyres/brands/zeetex',
    'https://www.pitstoparabia.com/en/tyres/brands/zelda',
    'https://www.pitstoparabia.com/en/tyres/brands/zeta_tyres',
]


class pitstoparabiabrands(Spider):
    name = 'pitstoparabiabrands'

    _timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

    custom_settings = {
        'FEED_EXPORTERS': {'xlsx': 'scrapy_xlsx.XlsxItemExporter'},
        'FEED_FORMAT': 'xlsx',
        'FEED_URI': f'pitstoparabia_brands_data_{_timestamp}.xlsx',
        'DOWNLOAD_DELAY': 0.3,
        'LOG_LEVEL': 'INFO',
    }

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.seen_products = set()   # dedupe product detail URLs
        self.seen_listings = set()   # dedupe brand/pagination listing URLs
        self.pbar = None
        if tqdm is not None:
            # total starts at 0 and grows as listing pages reveal more
            # products to scrape; current count = products scraped so far.
            self.pbar = tqdm(total=0, unit='product', desc='Scraping products',
                              dynamic_ncols=True)

    async def start(self):
        meta = {'dont_merge_cookies': True}
        for url in BRAND_URLS:
            yield Request(url.strip(), self.parse_listing, meta=meta, headers=self.headers)

    def parse_listing(self, response):
        if response.url in self.seen_listings:
            return
        self.seen_listings.add(response.url)

        try:
            sel = Selector(text=response.json()['products'])
        except Exception:
            sel = Selector(text=response.text)

        # --- products on this page ---
        product_urls = sel.css('.product-item-link::attr(href)').getall()
        for url in product_urls:
            url = (url or '').strip()
            if not url or url in self.seen_products:
                continue
            self.seen_products.add(url)

            if self.pbar is not None:
                self.pbar.total += 1
                self.pbar.refresh()

            yield response.follow(url, self.parse_detail,
                                  meta=response.meta, headers=self.headers)

        # --- follow pagination so no product on later pages is skipped ---
        next_url = (
            sel.css('link[rel="next"]::attr(href)').get()
            or sel.css('a.action.next::attr(href)').get()
            or sel.css('.pages-item-next a::attr(href)').get()
            or sel.css('a[title="Next"]::attr(href)').get()
        )
        if next_url:
            next_url = next_url.strip()
            if next_url and next_url not in self.seen_listings:
                yield response.follow(next_url, self.parse_listing,
                                      meta=response.meta, headers=self.headers)

    def parse_detail(self, response):
        add_to_cart_btn = response.css('button#product-addtocart-button, div.actions.add-to-cart button, button.tocart, button.add-to-cart')
        out_of_stock_div = response.css('div.stock.unavailable, .stock.unavailable')

        if add_to_cart_btn:
            InStock = 'Yes'
        elif out_of_stock_div:
            InStock = 'No'
        else:
            txt = ' '.join(response.css('div.stock::text, .stock::text').getall()).lower()
            if 'out of stock' in txt or 'unavailable' in txt:
                InStock = 'No'
            else:
                InStock = 'Unknown'
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

        if self.pbar is not None:
            self.pbar.update(1)
            self.pbar.set_postfix_str(f"pending={self.pbar.total - self.pbar.n}")

        yield item

    def closed(self, reason):
        if self.pbar is not None:
            self.pbar.close()

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