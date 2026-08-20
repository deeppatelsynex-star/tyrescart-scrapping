import requests
from parsel import Selector

p_url = 'https://www.tirerack.com/tires/advanta-atx-850'
jina_url = f'https://r.jina.ai/{p_url}'
r = requests.get(jina_url, headers={'X-Return-Format': 'html'}, timeout=25)
print('Jina product status:', r.status_code, 'len:', len(r.text))

sel = Selector(text=r.text)
title = sel.css('h1::text').get() or sel.css('title::text').get()
meta_title = sel.xpath('//meta[@property="og:title"]/@content').get()
desc = sel.xpath('//meta[@name="description"]/@content').get()

print('Title:', title)
print('OG Title:', meta_title)
print('Description:', desc)
print('Body snippet:', r.text[:800])
