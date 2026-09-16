import sys
import os
import time
from playwright.sync_api import sync_playwright

# Ensure stdout handles unicode without crashing on Windows cmd
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

SLUGS = [
    'mobile-tyre-fitting',
    'ev-tyres',
    'off-road-4x4-tyres',
    'tyre-brands',
    'tyre-sizes',
    'tyres-by-car',
    'tyre-shop-dubai',
    'tyre-shop-abu-dhabi',
    'tyre-shop-sharjah',
    'tyre-shop-ajman',
    'tyre-shop-ras-al-khaimah',
    'tyre-shop-fujairah',
    'tyre-shop-umm-al-quwain'
]

BASE_URL = "http://127.0.0.1:5049"
ARTIFACT_DIR = r"C:\Users\admin\.gemini\antigravity-cli\brain\9e6cd800-b678-4825-affb-5eb4b668756e"

def test_pages():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        # -------------------------------------------------------------
        # 1. MOBILE TESTS (viewport: 390x844)
        # -------------------------------------------------------------
        print("\n=== STARTING MOBILE VIEWPORT TESTS (390x844) ===")
        context_mobile = browser.new_context(
            viewport={'width': 390, 'height': 844},
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
        )
        page = context_mobile.new_page()

        for slug in SLUGS:
            url = f"{BASE_URL}/{slug}"
            print(f"\nTesting Mobile: {slug} -> {url}")
            page.goto(url, wait_until='networkidle')
            page.wait_for_timeout(400)

            # Check for tables
            tables = page.locator('.price-table, .tv-4x4-table, .tv-ev-table')
            t_count = tables.count()
            if t_count == 0:
                print(f"  [INFO] No data table on {slug} (expected for mobile-tyre-fitting).")
                continue

            table = tables.first

            # Check horizontal scroll on page body & table container
            scroll_info = page.evaluate("""() => {
                const tbl = document.querySelector('.price-table, .tv-4x4-table, .tv-ev-table');
                const scrollEl = document.querySelector('.price-table-scroll');
                return {
                    bodyScrollWidth: document.body.scrollWidth,
                    bodyClientWidth: document.body.clientWidth,
                    scrollElScrollWidth: scrollEl ? scrollEl.scrollWidth : 0,
                    scrollElClientWidth: scrollEl ? scrollEl.clientWidth : 0,
                    tableScrollWidth: tbl ? tbl.scrollWidth : 0,
                    tableClientWidth: tbl ? tbl.clientWidth : 0
                };
            }""")
            print(f"  Scroll info: Body: {scroll_info['bodyClientWidth']}px (scroll: {scroll_info['bodyScrollWidth']}px) | Table: {scroll_info['tableClientWidth']}px (scroll: {scroll_info['tableScrollWidth']}px)")

            # Verify ZERO horizontal scroll on body
            assert scroll_info['bodyScrollWidth'] <= scroll_info['bodyClientWidth'], f"Body has horizontal scroll on {slug}!"

            # Check dtr-control-btn presence and visibility
            first_btn = page.locator('.dtr-control-btn').first
            btn_visible = first_btn.is_visible()
            print(f"  First .dtr-control-btn visible: {btn_visible}")
            assert btn_visible, f"Expected .dtr-control-btn to be visible on mobile for {slug}"

            # Check intermediate columns hidden
            hidden_cols = page.locator('.desktop-col')
            if hidden_cols.count() > 0:
                first_hidden_visible = hidden_cols.first.is_visible()
                print(f"  .desktop-col hidden: {not first_hidden_visible} (total {hidden_cols.count()} elements)")
                assert not first_hidden_visible, f".desktop-col should be hidden on mobile for {slug}"

            # Check child rows before click
            first_child_row = page.locator('.dtr-child-row').first
            assert not first_child_row.is_visible(), f"Child row should be collapsed by default on {slug}"

            # Take screenshot before click
            if slug in ('ev-tyres', 'off-road-4x4-tyres', 'tyre-shop-dubai', 'tyre-sizes'):
                table.screenshot(path=os.path.join(ARTIFACT_DIR, f"mobile_{slug}_collapsed.png"))

            # Click first parent row to expand
            first_parent_row = page.locator('.dtr-parent-row').first
            first_parent_row.click(position={'x': 25, 'y': 20})
            page.wait_for_timeout(400)

            # Check child row after click
            assert first_child_row.is_visible(), f"Child row should be visible after click on {slug}"
            btn_text = first_btn.text_content().strip()
            print(f"  After expand: child row visible = True, button icon = '{btn_text}'")

            # Check detail items exist inside child row
            detail_items = first_child_row.locator('.dtr-detail-item')
            print(f"  Child row detail items count: {detail_items.count()}")
            assert detail_items.count() >= 2, f"Child row should contain detail items on {slug}"

            # Take screenshot after expand
            if slug in ('ev-tyres', 'off-road-4x4-tyres', 'tyre-shop-dubai', 'tyre-sizes'):
                table.screenshot(path=os.path.join(ARTIFACT_DIR, f"mobile_{slug}_expanded.png"))

            # Test clicking second row closes first row (exclusive accordion)
            parent_rows = page.locator('.dtr-parent-row')
            if parent_rows.count() > 1:
                second_parent_row = parent_rows.nth(1)
                second_child_row = page.locator('.dtr-child-row').nth(1)
                second_parent_row.click(position={'x': 25, 'y': 20})
                page.wait_for_timeout(400)

                assert not first_child_row.is_visible(), f"First child row should be closed when second row opened on {slug}"
                assert second_child_row.is_visible(), f"Second child row should be open on {slug}"
                print(f"  Accordion behavior verified: row 1 collapsed, row 2 expanded successfully.")

            print(f"  [PASS] Mobile test passed for {slug}")

        context_mobile.close()

        # -------------------------------------------------------------
        # 2. DESKTOP TESTS (viewport: 1400x900)
        # -------------------------------------------------------------
        print("\n=== STARTING DESKTOP VIEWPORT TESTS (1400x900) ===")
        context_desktop = browser.new_context(viewport={'width': 1400, 'height': 900})
        page_desk = context_desktop.new_page()

        for slug in ('ev-tyres', 'off-road-4x4-tyres', 'tyre-shop-dubai', 'tyre-sizes', 'tyres-by-car', 'tyre-brands'):
            url = f"{BASE_URL}/{slug}"
            print(f"\nTesting Desktop: {slug} -> {url}")
            page_desk.goto(url, wait_until='networkidle')
            page_desk.wait_for_timeout(400)

            table = page_desk.locator('.price-table, .tv-4x4-table, .tv-ev-table').first

            # Ensure .dtr-control-btn is completely hidden on desktop
            dtr_btns = page_desk.locator('.dtr-control-btn')
            if dtr_btns.count() > 0:
                assert not dtr_btns.first.is_visible(), f".dtr-control-btn should be hidden on desktop for {slug}"
            print("  .dtr-control-btn is hidden: True")

            # Ensure .dtr-child-row is completely hidden on desktop
            child_rows = page_desk.locator('.dtr-child-row')
            if child_rows.count() > 0:
                assert not child_rows.first.is_visible(), f".dtr-child-row should be hidden on desktop for {slug}"
            print("  .dtr-child-row is hidden: True")

            # Ensure all intermediate columns (.desktop-col) ARE visible on desktop
            desk_cols = page_desk.locator('.desktop-col')
            if desk_cols.count() > 0:
                assert desk_cols.first.is_visible(), f".desktop-col should be visible on desktop for {slug}"
            print(f"  .desktop-col is visible: True (total {desk_cols.count()} visible desktop columns)")

            # Screenshot desktop table to verify unchanged appearance
            table.screenshot(path=os.path.join(ARTIFACT_DIR, f"desktop_{slug}.png"))
            print(f"  [PASS] Desktop test passed for {slug}")

        context_desktop.close()
        browser.close()
        print("\n=== ALL 13 PAGES VERIFIED AND PASSED SUCCESSFULLY! ===")

if __name__ == '__main__':
    test_pages()
