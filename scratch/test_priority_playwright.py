from playwright.sync_api import sync_playwright
import time
from parsel import Selector

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
            viewport={'width': 1366, 'height': 768},
            locale='en-US',
        )
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {} };
        """)
        
        page = context.new_page()

        # 1. Sitemap test
        sitemap_url = 'https://www.prioritytire.com/sitemap/sitemap-singleproducts-1.xml'
        print('1. Navigating to sitemap:', sitemap_url, flush=True)
        page.goto(sitemap_url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(2)
        print('   Final URL:', page.url, flush=True)
        print('   Title:', page.title(), flush=True)
        content = page.content()
        print('   Content length:', len(content), flush=True)
        sel = Selector(text=content)
        locs = sel.xpath("//*[local-name()='loc']/text()").getall() or sel.css("loc::text").getall()
        print('   Extracted product URLs count:', len(locs), flush=True)
        if locs:
            print('   Sample product URL:', locs[0], flush=True)

        # 2. Product page test
        product_url = 'https://www.prioritytire.com/by-brand/americus-tires/freight-pro-csd/295-75r22-5-144-141m-g-14-ply-360806'
        print('\n2. Navigating to product page:', product_url, flush=True)
        page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        time.sleep(3)
        print('   Final URL:', page.url, flush=True)
        print('   Title:', page.title(), flush=True)
        p_content = page.content()
        p_sel = Selector(text=p_content)
        next_data = p_sel.css('script#__NEXT_DATA__::text').get('')
        print('   Has __NEXT_DATA__:', bool(next_data), 'length:', len(next_data), flush=True)

        browser.close()

if __name__ == '__main__':
    main()
