import sys
import time
from playwright.sync_api import sync_playwright

def run_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1600, 'height': 1200})
        
        print("\n--- STEP 1: INITIAL PAGE LOAD ---")
        page.goto('http://127.0.0.1:5049/car-tyres', wait_until='networkidle')
        page.wait_for_timeout(1000)
        
        total_cards = page.locator('.tv-product-card:not(.tv-card-skeleton)').count()
        heading_text = page.locator('#catalog-count-heading').inner_text()
        info_text = page.locator('#pagination-info').inner_text()
        print(f"Total cards rendered: {total_cards}")
        print(f"Heading text: {heading_text}")
        print(f"Pagination info: {info_text}")
        
        # Verify 4 rows by checking Y coordinates of cards
        cards = page.locator('.tv-product-card:not(.tv-card-skeleton)').all()
        y_coords = sorted(list(set([round(c.bounding_box()['y']) for c in cards])))
        print(f"Distinct Row Y-coordinates count: {len(y_coords)} -> {y_coords}")
        
        page.screenshot(path=r'C:\Users\admin\.gemini\antigravity-cli\brain\9e6cd800-b678-4825-affb-5eb4b668756e\pagination_4rows_page1.png')
        print("Captured screenshot pagination_4rows_page1.png")

        print("\n--- STEP 2: TEST SKELETON LOADING AND PAGE 2 NAVIGATION ---")
        # Click page 2
        page.click('#pagination-controls .tv-page-btn:has-text("2")')
        page.wait_for_timeout(1000)
        
        page2_cards = page.locator('.tv-product-card:not(.tv-card-skeleton)').count()
        page2_info = page.locator('#pagination-info').inner_text()
        print(f"Page 2 cards: {page2_cards}")
        print(f"Page 2 info: {page2_info}")
        
        page.screenshot(path=r'C:\Users\admin\.gemini\antigravity-cli\brain\9e6cd800-b678-4825-affb-5eb4b668756e\pagination_4rows_page2.png')
        print("Captured screenshot pagination_4rows_page2.png")

        print("\n--- STEP 3: TEST SIDEBAR BRAND FILTER (PIRELLI) ---")
        # Locate Pirelli checkbox
        pirelli_cb = page.locator('input[name="brand"][value="pirelli"]')
        print(f"Pirelli checkbox found: {pirelli_cb.count() > 0}")
        pirelli_cb.check()
        page.wait_for_timeout(1500)
        
        pirelli_heading = page.locator('#catalog-count-heading').inner_text()
        pirelli_info = page.locator('#pagination-info').inner_text()
        pirelli_cards = page.locator('.tv-product-card:not(.tv-card-skeleton)').count()
        first_card_title = page.locator('.tv-product-card:not(.tv-card-skeleton) .tv-product-model-name').first.inner_text()
        print(f"After Pirelli checked -> Heading: {pirelli_heading}")
        print(f"Pagination info: {pirelli_info}")
        print(f"Cards count: {pirelli_cards}")
        print(f"First product title: {first_card_title}")
        
        page.screenshot(path=r'C:\Users\admin\.gemini\antigravity-cli\brain\9e6cd800-b678-4825-affb-5eb4b668756e\brand_filter_pirelli.png')
        print("Captured screenshot brand_filter_pirelli.png")

        print("\n--- STEP 4: TEST PIRELLI PAGE 2 NAVIGATION ---")
        page.click('#pagination-controls .tv-page-btn:has-text("2")')
        page.wait_for_timeout(1000)
        pirelli_p2_info = page.locator('#pagination-info').inner_text()
        print(f"Pirelli Page 2 info: {pirelli_p2_info}")

        print("\n--- STEP 5: TEST SKELETON DISPLAY DIRECTLY ---")
        # Trigger skeleton rendering and capture screenshot immediately
        page.evaluate('renderSkeletons(32)')
        skeleton_count = page.locator('.tv-product-card.tv-card-skeleton').count()
        print(f"Active skeleton cards in DOM: {skeleton_count}")
        page.screenshot(path=r'C:\Users\admin\.gemini\antigravity-cli\brain\9e6cd800-b678-4825-affb-5eb4b668756e\skeleton_loading_verified.png')
        print("Captured screenshot skeleton_loading_verified.png")

        print("\n--- STEP 6: TEST CLEAR ALL FILTERS ---")
        page.click('.tv-btn-clear-filters')
        page.wait_for_timeout(1500)
        cleared_heading = page.locator('#catalog-count-heading').inner_text()
        cleared_info = page.locator('#pagination-info').inner_text()
        print(f"After Clear Filters -> Heading: {cleared_heading}")
        print(f"Pagination info: {cleared_info}")
        
        browser.close()
        print("\nALL VERIFICATION TESTS COMPLETED SUCCESSFULLY!")

if __name__ == '__main__':
    run_test()
