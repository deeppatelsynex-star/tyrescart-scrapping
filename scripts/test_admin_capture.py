import sys
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={'width': 1600, 'height': 1000})
    
    print("Navigating to login...")
    page.goto('http://127.0.0.1:5049/visionadmin/login', wait_until='networkidle')
    
    page.fill('#email', 'admin@tyresvision.com')
    page.fill('#password', 'admin123')
    
    with page.expect_response(lambda r: '/visionadmin/login' in r.url) as response_info:
        page.click('#btn-submit')
    
    page.wait_for_timeout(1500)
    
    print("Navigating to products page...")
    page.goto('http://127.0.0.1:5049/visionadmin/products', wait_until='networkidle')
    page.wait_for_timeout(3000)
    
    out_path = r'C:\Users\admin\.gemini\antigravity-cli\brain\9e6cd800-b678-4825-affb-5eb4b668756e\admin_products_verified.png'
    page.screenshot(path=out_path)
    print(f"Captured main table screenshot to {out_path}")

    # Now search for Maxzez to verify No Image Available placeholder
    print("Searching for Maxzez...")
    search_input = page.locator('input[placeholder*="Search SKU, name, specs"]')
    search_input.fill('Maxzez')
    page.wait_for_timeout(2000)
    
    no_img_path = r'C:\Users\admin\.gemini\antigravity-cli\brain\9e6cd800-b678-4825-affb-5eb4b668756e\admin_no_image_verified.png'
    page.screenshot(path=no_img_path)
    print(f"Captured no-image search screenshot to {no_img_path}")

    # Now search for Sailun to verify Sailun product from user's screenshot
    print("Searching for Sailun 750...")
    search_input.fill('Sailun 750')
    page.wait_for_timeout(2000)

    sailun_path = r'C:\Users\admin\.gemini\antigravity-cli\brain\9e6cd800-b678-4825-affb-5eb4b668756e\admin_sailun_verified.png'
    page.screenshot(path=sailun_path)
    print(f"Captured Sailun product screenshot to {sailun_path}")

    browser.close()
