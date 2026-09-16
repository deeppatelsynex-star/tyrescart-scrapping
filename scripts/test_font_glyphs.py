import os
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto('http://127.0.0.1:5049/car-tyres', wait_until='networkidle')
    
    page.evaluate("""() => {
        const style = document.createElement('style');
        style.textContent = `
          @font-face {
              font-family: UAEDirham;
              src: url(/static/fonts/UAE-dirham.woff) format("woff");
              font-weight: 400;
              font-style: normal;
          }
          .currency-dirham {
              font-family: UAEDirham, sans-serif;
              position: relative;
          }
        `;
        document.head.appendChild(style);

        const d = document.createElement('div');
        d.id = 'font-test-box';
        d.style = 'background:white; color:black; padding:20px; font-size:28px; z-index:99999; position:relative;';
        d.innerHTML = `
          <div>Test 1 (e900): <span class="currency-dirham">&#xe900;</span> 165</div>
          <div>Test 2 (AED): <span class="currency-dirham">AED</span> 165</div>
          <div>Test 3 (aed): <span class="currency-dirham">aed</span> 165</div>
          <div>Test 4 (UAE-dirham): <span class="currency-dirham">UAE-dirham</span> 165</div>
          <div>Test 5 (Dhs): <span class="currency-dirham">Dhs</span> 165</div>
          <div>Test 6 (&#272;): <span class="currency-dirham">&#272;</span> 165</div>
        `;
        document.body.prepend(d);
    }""")
    page.wait_for_timeout(1000)
    test_box = page.locator('#font-test-box')
    test_box.screenshot(path=r'C:\Users\admin\.gemini\antigravity-cli\brain\9e6cd800-b678-4825-affb-5eb4b668756e\font_test_results.png')
    browser.close()

print('Saved font_test_results.png')
