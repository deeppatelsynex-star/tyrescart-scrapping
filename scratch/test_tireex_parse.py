import requests
import json
import re
from parsel import Selector

url = 'https://tireex.com/product/continental-265-60-r18-110v-2025-2/'
jina_url = f'https://r.jina.ai/{url}'
headers = {'X-Return-Format': 'html'}

r = requests.get(jina_url, headers=headers, timeout=25)
sel = Selector(text=r.text)

title = (sel.css('h1.product_title::text').get() or sel.css('h1::text').get() or '').strip()
sku = (sel.css('.sku::text').get() or '').strip()
img = sel.xpath("//meta[@property='og:image']/@content").get() or sel.css('.woocommerce-product-gallery__image img::attr(src)').get() or ''

# Price parsing
price = (
    sel.css('.price ins .amount::text, .price ins bdi::text').get()
    or sel.css('.price .amount::text, .price bdi::text').get()
    or sel.css('span.woocommerce-Price-amount::text').get()
    or ''
).strip()

specs = {}
for row in sel.css('table.woocommerce-product-attributes tr, table.shop_attributes tr'):
    k = ''.join(row.css('th *::text, th::text').getall()).strip()
    v = ''.join(row.css('td *::text, td::text').getall()).strip()
    if k and v:
        specs[k] = v

print('Title:', title)
print('Price:', price)
print('SKU:', sku)
print('Image:', img)
print('Specs:', json.dumps(specs, indent=2, ensure_ascii=False))
