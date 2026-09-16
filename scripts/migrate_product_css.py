import os
import re

# 1. Read ProductListing.html
listing_path = r'templates/Client/ProductListing.html'
with open(listing_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Extract <style>...</style> block
match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if not match:
    print("ERROR: <style> tag not found in ProductListing.html")
    exit(1)

raw_css = match.group(1).strip()
print(f"Extracted {len(raw_css)} chars of CSS from ProductListing.html")

# Remove @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&display=swap'); from CSS body
# because it will be loaded via <link> in <head>
cleaned_css = re.sub(r"@import\s+url\(['\"]https://fonts\.googleapis\.com/css2\?family=Caveat[^'\"]+['\"]\);\s*", "", raw_css)

# Font-face and currency-dirham block as specified by user
font_and_currency_block = """
/* =============================================================================
   UAE DIRHAM CURRENCY FONT & SYMBOL SPECIFICATION
   ============================================================================= */
@font-face {
    font-family: UAEDirham;
    src: url(fonts/UAE-dirham.woff) format("woff"),
         url(../fonts/UAE-dirham.woff) format("woff"),
         url(/static/fonts/UAE-dirham.woff) format("woff"),
         url(fonts/UAE-dirham.ttf) format("truetype"),
         url(../fonts/UAE-dirham.ttf) format("truetype");
    font-weight: 400;
    font-style: normal;
}
.currency-dirham {
    font-family: UAEDirham, sans-serif;
    position: relative;
}
"""

# Append to static/css/client.css
client_css_path = r'static/css/client.css'
with open(client_css_path, 'r', encoding='utf-8') as f:
    client_css = f.read()

# Check if product listing CSS already appended
marker = "/* =============================================================================\n   ANTIGRAVITY DESIGN EXPERT: PRODUCT LISTING / CAR TYRES CATALOG"
if marker not in client_css:
    updated_client_css = client_css.rstrip() + "\n\n" + font_and_currency_block + "\n\n" + cleaned_css + "\n"
    with open(client_css_path, 'w', encoding='utf-8') as f:
        f.write(updated_client_css)
    print("Appended Product Listing CSS & UAE Dirham font-face to client.css!")
else:
    print("Product Listing CSS already present in client.css, ensuring font-face block is present...")
    if ".currency-dirham" not in client_css:
        updated_client_css = client_css.rstrip() + "\n\n" + font_and_currency_block + "\n"
        with open(client_css_path, 'w', encoding='utf-8') as f:
            f.write(updated_client_css)

# Replace <style>...</style> in ProductListing.html with <link> for Caveat font
new_extra_head = """<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Caveat:wght@600;700&display=swap">"""
updated_content = re.sub(r'<style>.*?</style>', new_extra_head, content, flags=re.DOTALL)

# Update currency symbols &#272; to currency-dirham &#xe900;
updated_content = updated_content.replace('tv-curr-glyph">&#272;</span>', 'currency-dirham tv-curr-glyph">&#xe900;</span>')
updated_content = updated_content.replace('tv-curr-glyph-sub">&#272;</span>', 'currency-dirham tv-curr-glyph-sub">&#xe900;</span>')

with open(listing_path, 'w', encoding='utf-8') as f:
    f.write(updated_content)
print("Updated ProductListing.html successfully (CSS moved, currency glyphs updated to UAE Dirham symbol)!")
