from playwright.sync_api import sync_playwright
import time
from parsel import Selector

def wait_for_cloudflare(page, timeout=30):
    start = time.time()
    while time.time() - start < timeout:
        title = page.title()
        if "just a moment" not in title.lower() and "attention required" not in title.lower():
            return True
        page.wait_for_timeout(1000)
    return False

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,  # Test in non-headless or stealth mode
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

        # Product page test
        product_url = 'https://www.prioritytire.com/by-brand/americus-tires/freight-pro-csd/295-75r22-5-144-141m-g-14-ply-360806'
        print('Navigating to:', product_url, flush=True)
        page.goto(product_url, wait_until='domcontentloaded', timeout=30000)
        
        passed = wait_for_cloudflare(page, timeout=20)
        print('Passed challenge:', passed, 'Title:', page.title(), flush=True)
        
        cookies = context.cookies()
        print('Cookies count:', len(cookies), [c['name'] for c in cookies], flush=True)
        
        content = page.content()
        sel = Selector(text=content)
        next_data = sel.css('script#__NEXT_DATA__::text').get('')
        print('Has __NEXT_DATA__:', bool(next_data), 'length:', len(next_data), flush=True)

        browser.close()

if __name__ == '__main__':
    main()
