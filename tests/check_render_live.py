import requests

base = 'https://tyrescart-scrapping.onrender.com'
print(f'Checking {base}...')

try:
    r = requests.get(f'{base}/login', timeout=20)
    print(f'1. GET /login: Status {r.status_code}, Length: {len(r.text)}')
except Exception as e:
    print(f'1. GET /login Error: {e}')

try:
    r_js = requests.get(f'{base}/static/script.js', timeout=20)
    print(f'2. GET /static/script.js: Status {r_js.status_code}, Length: {len(r_js.text)}')
    dup_count = r_js.text.count('const closeEventSource = () =>')
    print(f'   - duplicate closeEventSource count: {dup_count}')
    has_init = 'renderSummaryPills({})' in r_js.text
    print(f'   - Has immediate default render in initPage? {has_init}')
except Exception as e:
    print(f'2. GET /static/script.js Error: {e}')

try:
    r_page = requests.get(f'{base}/scraperpage?fileId=35', timeout=20, allow_redirects=False)
    print(f'3. GET /scraperpage?fileId=35: Status {r_page.status_code}, Location: {r_page.headers.get("Location")}')
except Exception as e:
    print(f'3. GET /scraperpage Error: {e}')
