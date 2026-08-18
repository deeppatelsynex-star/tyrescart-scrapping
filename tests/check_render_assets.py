import requests

base = 'https://tyrescart-scrapping.onrender.com'
assets = [
    '/static/style.css',
    '/static/internal.css',
    '/static/idb_storage.js',
    '/static/script.js',
    '/static/files.js',
    '/static/reports.js',
    '/static/admin.js',
    '/static/profile.js',
    '/static/trash.js',
    '/static/assets/images/favicon-color.webp',
    '/login'
]

print(f"=== Auditing Live Assets on {base} ===")
for asset in assets:
    url = f"{base}{asset}"
    try:
        r = requests.get(url, timeout=10)
        status = r.status_code
        size = len(r.content)
        ct = r.headers.get('Content-Type', '')
        print(f"[OK] [{status}] {asset:<35} Size: {size:>7} bytes | Type: {ct}")
    except Exception as e:
        print(f"[FAIL] {asset:<35} Error: {e}")
