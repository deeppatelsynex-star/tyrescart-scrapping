import os
from playwright.sync_api import sync_playwright

html = """<!DOCTYPE html>
<html>
<head>
<style>
@font-face {
    font-family: UAEDirham;
    src: url(http://127.0.0.1:5049/static/fonts/UAE-dirham.woff) format("woff");
    font-weight: 400;
    font-style: normal;
}
.currency-dirham {
    font-family: UAEDirham, sans-serif;
    position: relative;
    font-size: 32px;
}
</style>
</head>
<body style="background: white; padding: 40px; font-family: sans-serif;">
  <div>1. Plain AED: <span class="currency-dirham">AED</span> 165</div>
  <div>2. Lower aed: <span class="currency-dirham">aed</span> 165</div>
  <div>3. Dhs: <span class="currency-dirham">Dhs</span> 165</div>
  <div>4. DH: <span class="currency-dirham">DH</span> 165</div>
  <div>5. Arabic: <span class="currency-dirham">&#1583;.&#1573;</span> 165</div>
  <div>6. Single letters A E D: <span class="currency-dirham">A</span> <span class="currency-dirham">E</span> <span class="currency-dirham">D</span></div>
</body>
</html>"""

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.set_content(html)
    page.wait_for_timeout(1000)
    page.screenshot(path=r"C:\Users\admin\.gemini\antigravity-cli\brain\9e6cd800-b678-4825-affb-5eb4b668756e\test_uae_dirham.png")
    browser.close()
print("Screenshot saved!")
