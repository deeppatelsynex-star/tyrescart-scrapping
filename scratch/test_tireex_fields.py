import requests
import json
from parsel import Selector

url = 'https://tireex.com/product/continental-265-60-r18-110v-2025-2/'
jina_url = f'https://r.jina.ai/{url}'
headers = {'X-Return-Format': 'html'}

r = requests.get(jina_url, headers=headers, timeout=25)
print('Status:', r.status_code, 'len:', len(r.text))

sel = Selector(text=r.text)
title = (sel.css('h1.product_title::text').get() or sel.css('h1::text').get() or '').strip()
price = sel.css('.price bdi::text, .price .amount::text, span.amount::text').getall()
sku = (sel.css('.sku::text').get() or '').strip()
img = sel.xpath('//meta[@property="og:image"]/@content').get() or sel.css('.woocommerce-product-gallery__image img::attr(src)').get() or ''

specs = {}
for row in sel.css('table.woocommerce-product-attributes tr, table.shop_attributes tr, tr'):
    k = ''.join(row.css('th *::text, th::text').getall()).strip()
    v = ''.join(row.css('td *::text, td::text').getall()).strip()
    if k and v:
        specs[k] = v

print('Title:', title)
print('Prices found:', price)
print('SKU:', sku)
print('Image:', img)
print('Specs:', json.dumps(specs, indent=2))
print('Snippet:', r.text[:600])
