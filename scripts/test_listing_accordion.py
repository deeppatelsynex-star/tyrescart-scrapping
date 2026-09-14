import sys
from playwright.sync_api import sync_playwright

def test_all():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1720, 'height': 1100})

        # 1. Test Car Tyres Listing
        page.goto('http://127.0.0.1:5049/car-tyres', wait_until='networkidle')
        visible_cards = page.locator('.tv-product-card:visible').count()
        info_text = page.locator('#pagination-info').text_content()
        heading_text = page.locator('#catalog-count-heading').text_content()
        page_buttons = page.locator('#pagination-controls .tv-page-btn').count()
        print(f"Listing Initial -> Visible cards: {visible_cards}, Info: {info_text.strip()}, Heading: {heading_text.strip()}, Page btns: {page_buttons}")

        # Check row 1 and row 2 card bounding boxes to verify 8 in a row
        first_row_tops = []
        cards = page.locator('.tv-product-card:visible').all()
        for c in cards[:8]:
            box = c.bounding_box()
            first_row_tops.append(round(box['y']))
        print(f"Row 1 Y-coordinates for first 8 cards: {first_row_tops}")
        all_same_row = len(set(first_row_tops)) == 1
        print(f"Are all 8 cards in the exact same single row? {all_same_row}")

        # Take screenshot of page 1
        page.screenshot(path='C:/Users/admin/.gemini/antigravity-cli/brain/9e6cd800-b678-4825-affb-5eb4b668756e/car_tyres_8_columns_page1.png', full_page=False)

        # 2. Test Pagination Click: Page 2
        btn2 = page.locator('#pagination-controls .tv-page-btn', has_text='2')
        btn2.click()
        page.wait_for_timeout(400)
        info_page2 = page.locator('#pagination-info').text_content()
        active_btn = page.locator('#pagination-controls .tv-page-btn.active').text_content()
        print(f"After clicking Page 2 -> Info: {info_page2.strip()}, Active button: {active_btn.strip()}")
        page.screenshot(path='C:/Users/admin/.gemini/antigravity-cli/brain/9e6cd800-b678-4825-affb-5eb4b668756e/car_tyres_8_columns_page2.png', full_page=False)

        # 3. Test Filter Accordion on Listing
        header_size = page.locator('.tv-filter-header', has_text='Tyre Size')
        header_size.click()
        page.wait_for_timeout(300)
        size_box_visible = page.locator('.tv-search-size-box').is_visible()
        print(f"After clicking Tyre Size accordion -> Size search box visible: {size_box_visible}")
        header_size.click()
        page.wait_for_timeout(300)
        print(f"After clicking Tyre Size accordion again -> Size search box visible: {page.locator('.tv-search-size-box').is_visible()}")

        # 4. Test FAQ Accordion on EV Tyres
        page.goto('http://127.0.0.1:5049/ev-tyres', wait_until='networkidle')
        faq_item1 = page.locator('.faq-item').nth(0)
        faq_item2 = page.locator('.faq-item').nth(1)
        print(f"EV Tyres FAQ Initial -> Item 1 active: {'active' in (faq_item1.get_attribute('class') or '')}, Item 2 active: {'active' in (faq_item2.get_attribute('class') or '')}")
        
        # Click FAQ Item 2
        faq_item2.locator('.faq-trigger').click()
        page.wait_for_timeout(400)
        print(f"EV Tyres FAQ After Click Item 2 -> Item 1 active: {'active' in (faq_item1.get_attribute('class') or '')}, Item 2 active: {'active' in (faq_item2.get_attribute('class') or '')}")

        browser.close()

if __name__ == '__main__':
    test_all()
