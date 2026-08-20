import requests
from parsel import Selector

BASE_URL = "https://tyrescart-scrapping.klever.ae"

def run_tests():
    print(f"=== Testing Live Site: {BASE_URL} ===\n")
    session = requests.Session()

    # 1. Root redirect
    r_root = session.get(BASE_URL, allow_redirects=False, timeout=15)
    print(f"1. Root URL ({BASE_URL}): HTTP {r_root.status_code}")
    if r_root.status_code in (301, 302):
        print(f"   -> Redirects to: {r_root.headers.get('Location')}")

    # 2. Login Page
    r_login = session.get(f"{BASE_URL}/login", timeout=15)
    print(f"\n2. Login Page ({BASE_URL}/login): HTTP {r_login.status_code}")
    sel_login = Selector(text=r_login.text)
    title = sel_login.css("title::text").get("").strip()
    print(f"   -> Page Title: {title}")
    has_form = bool(sel_login.css("form").get())
    has_email_input = bool(sel_login.css("input[name='email'], input[type='email']").get())
    has_pass_input = bool(sel_login.css("input[name='password'], input[type='password']").get())
    print(f"   -> Has Login Form: {has_form} (Email Input: {has_email_input}, Password Input: {has_pass_input})")

    # 3. Static Assets
    assets = [
        "/static/script.js",
        "/static/files.js",
        "/static/reports.js",
        "/static/users.js",
    ]
    print("\n3. Static Assets:")
    for asset in assets:
        r_asset = session.get(f"{BASE_URL}{asset}", timeout=15)
        print(f"   - {asset}: HTTP {r_asset.status_code} ({len(r_asset.content)} bytes)")

    # 4. HTTPS & Security Headers Check
    print("\n4. Security & Cloudflare Headers:")
    for h in ["Server", "x-frame-options", "x-content-type-options", "cf-cache-status"]:
        print(f"   - {h}: {r_login.headers.get(h, 'N/A')}")

    print("\n=== Live Site Tests Completed Successfully! ===")

if __name__ == "__main__":
    run_tests()
