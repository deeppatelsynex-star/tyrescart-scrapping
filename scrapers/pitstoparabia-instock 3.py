import re
from collections import OrderedDict
from scrapy import Spider, Request, Selector # type: ignore


class pitstoparabia(Spider):
    name = 'pitstoparabia'

    custom_settings = {
        'FEED_EXPORTERS': {'xlsx': 'scrapy_xlsx.XlsxItemExporter'},
        'FEED_FORMAT': 'xlsx',
        'FEED_URI': 'pitstoparabia_data.xlsx',
        'DOWNLOAD_DELAY': 0.3
    }

    url = 'https://www.pitstoparabia.com/en/sitemap/tyre_sizes'

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

    # Path fragments that are clearly not tyre category/product pages —
    # skip these to avoid wasting requests on nav/footer/account junk.
    JUNK_PATH_KEYWORDS = (
        '/contact', '/about', '/blog', '/cart', '/account', '/login',
        '/register', '/wishlist', '/compare', '/checkout', '/customer',
        '/terms', '/privacy', '/faq', '/careers', '/store-locator',
        '/facebook.com', '/instagram.com', '/twitter.com', '/x.com',
        '/youtube.com', '/linkedin.com', '/tiktok.com', '/wa.me',
        '/whatsapp.com', '/apple.com', '/google.com', '/play.google.com',
    )

    async def start(self):
        meta = {'dont_merge_cookies': True}
        yield Request(self.url, self.parse_brands, meta=meta, headers=self.headers)

    def parse_brands(self, response):
        sel = Selector(text=response.text)

        # Try XML sitemap format first (<loc>...</loc>)
        urls = sel.css('loc::text').getall()

        # Fall back to an HTML sitemap page (plain <a href="..."> links)
        if not urls:
            urls = sel.css('a::attr(href)').getall()

        seen_urls = set()
        for url in urls:
            url = (url or '').strip()

            if not url or url in seen_urls:
                continue
            if url.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                continue
            if any(kw in url.lower() for kw in self.JUNK_PATH_KEYWORDS):
                continue
            # Only follow same-site links (skip external domains entirely)
            if url.startswith('http') and 'pitstoparabia.com' not in url:
                continue

            seen_urls.add(url)
            print("URL: ========================")
            print(url)
            yield response.follow(url, self.parse_listing,
                                  meta=response.meta, headers=self.headers)

    def parse_listing(self, response):
        #print("Resoinse: ========================")
        #print(response.json())

        try:
            sel = Selector(text=response.json()['products'])
        except:
            sel = Selector(text=response.text)
            
        for url in sel.css('.product-item-link::attr(href)').getall():
            yield response.follow(url, self.parse_detail,
                                  meta=response.meta, headers=self.headers)

    def parse_detail(self, response):
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
            if 'out of stock' in txt or 'unavailable' in txt:
                InStock = 'No'
            else:
                InStock = ''
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
        except:
            item['UTQG'] = ' '.join([t.strip() for t in response.css('span:contains("UTQG")').xpath('parent::*/span/text()').getall()][1:])
        
        item['Fuel Efficiency Rating'] = (response.css('.tyres_labels .tyre_label::attr(title)').re_first('Fuel Efficiency Rating:(.+)') or '').strip()
        item['Wet Grip Rating'] = (response.css('.tyres_labels .tyre_label::attr(title)').re_first('Wet Grip Rating:(.+)') or '').strip()
        item['External Noise'] = (response.css('.tyres_labels .tyre_label::attr(title)').re_first('External Noise:(.+)') or '').strip()
        
        item['Image'] = response.css('[property="og:image"]::attr(content)').getall()[-1]
        item['Source'] = response.url
        yield item

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