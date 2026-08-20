import requests
import re
from parsel import Selector

sitemap_url = 'https://www.prioritytire.com/sitemap/sitemap-singleproducts-1.xml'
r = requests.get(f'https://r.jina.ai/{sitemap_url}', headers={'X-Return-Format': 'html'}, timeout=25)
print('Jina sitemap status:', r.status_code, 'len:', len(r.text))

sel = Selector(text=r.text)
locs = sel.xpath("//*[local-name()='loc']/text()").getall() or sel.css("loc::text").getall()
print('Found locs count:', len(locs))

if not locs:
    urls = re.findall(r'https://www\.prioritytire\.com/[^\s<"\'\]]+', r.text)
    print('Found regex urls:', len(urls), urls[:3] if urls else [])
