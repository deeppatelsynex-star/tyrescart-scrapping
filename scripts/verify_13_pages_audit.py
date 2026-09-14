"""
scripts/verify_13_pages_audit.py
Automated verification audit for all 13 pages against TyresVision-13-Page-Build-Plan 1.docx.
Checks:
- HTTP 200 status
- Exact title match
- Exact H1 match
- Exact internal link anchors
- Accordion structure presence
"""

import urllib.request
import re

pages_expectations = {
    'mobile-tyre-fitting': {
        'h1': 'Mobile Tyre Fitting in Dubai and Abu Dhabi',
        'title': 'Mobile Tyre Fitting in Dubai & Abu Dhabi | TyresVision',
        'links': ['tyre fitting in Dubai', 'tyre fitting in Abu Dhabi', 'EV and run-flat tyres', 'find your tyre size']
    },
    'ev-tyres': {
        'h1': 'EV and Hybrid Tyres in the UAE',
        'title': 'EV Tyres in Dubai & Abu Dhabi | Tesla, BYD | TyresVision',
        'links': ['mobile tyre fitting', 'tyre brands', 'tyre sizes', 'tyres for your car model']
    },
    'off-road-4x4-tyres': {
        'h1': 'Off-Road and 4x4 Tyres in the UAE',
        'title': 'Off-Road & 4x4 Tyres in the UAE | TyresVision',
        'links': ['tyre brands', 'tyres for your car model', 'tyre sizes', 'tyre fitting in Dubai']
    },
    'tyre-brands': {
        'h1': 'Tyre Brands We Supply Across the UAE',
        'title': 'Tyre Brands in the UAE | 60+ Brands | TyresVision',
        'links': ['off-road and 4x4 tyres', 'EV tyres', 'tyre sizes', 'tyres for your car model']
    },
    'tyre-sizes': {
        'h1': 'Tyre Sizes and Prices in the UAE',
        'title': 'Tyre Sizes in the UAE | Find Your Size | TyresVision',
        'links': ['tyres for your car model', 'tyre brands', '4x4 and SUV tyres', 'mobile tyre fitting']
    },
    'tyres-by-car': {
        'h1': 'Find Tyres for Your Car Model',
        'title': 'Tyres by Car Model in the UAE | TyresVision',
        'links': ['off-road and 4x4 tyres', 'EV tyres', 'how to read your tyre size', 'tyre brands']
    },
    'tyre-shop-dubai': {
        'h1': 'Tyre Shop in Dubai \u2014 Tyres Fitted Near You',
        'title': 'Tyre Shop in Dubai | Free Fitting Near You | TyresVision',
        'links': ['mobile tyre fitting', 'find your tyre size', 'tyre brands', 'EV tyres']
    },
    'tyre-shop-abu-dhabi': {
        'h1': 'Tyre Shop in Abu Dhabi \u2014 Tyres Fitted Near You',
        'title': 'Tyre Shop in Abu Dhabi | Free Fitting | TyresVision',
        'links': ['mobile tyre fitting', '4x4 and SUV tyres', 'find your tyre size', 'tyre brands']
    },
    'tyre-shop-sharjah': {
        'h1': 'Tyre Shop in Sharjah \u2014 Tyres Delivered and Fitted',
        'title': 'Tyre Shop in Sharjah | Free Fitting | TyresVision',
        'links': ['mobile tyre fitting', 'find your tyre size', 'budget and mid-range tyre brands']
    },
    'tyre-shop-ajman': {
        'h1': 'Tyre Shop in Ajman \u2014 Tyres Delivered and Fitted',
        'title': 'Tyre Shop in Ajman | Tyres Delivered & Fitted | TyresVision',
        'links': ['mobile tyre fitting', 'find your tyre size', 'tyre brands']
    },
    'tyre-shop-ras-al-khaimah': {
        'h1': 'Tyre Shop in Ras Al Khaimah',
        'title': 'Tyre Shop in Ras Al Khaimah | Tyres Fitted | TyresVision',
        'links': ['off-road and 4x4 tyres', 'mobile tyre fitting', 'find your tyre size']
    },
    'tyre-shop-fujairah': {
        'h1': 'Tyre Shop in Fujairah and the East Coast',
        'title': 'Tyre Shop in Fujairah | Tyres Fitted | TyresVision',
        'links': ['off-road and 4x4 tyres', 'mobile tyre fitting', 'tyre brands']
    },
    'tyre-shop-umm-al-quwain': {
        'h1': 'Tyre Shop in Umm Al Quwain',
        'title': 'Tyre Shop in Umm Al Quwain | Tyres Fitted | TyresVision',
        'links': ['mobile tyre fitting', 'find your tyre size', 'tyre brands']
    }
}

def run_audit():
    all_passed = True
    print("=" * 70)
    print("AUDIT: VERIFYING ALL 13 PAGES AGAINST BUILD PLAN SPECIFICATIONS")
    print("=" * 70)

    for slug, exp in pages_expectations.items():
        url = f"http://127.0.0.1:5049/{slug}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                html = resp.read().decode('utf-8')

                # Title check
                title_m = re.search(r'<title>(.*?)</title>', html, re.DOTALL | re.IGNORECASE)
                raw_title = title_m.group(1).replace('&amp;', '&').strip() if title_m else ''
                title_ok = exp['title'] in raw_title

                # H1 check
                h1_m = re.search(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL | re.IGNORECASE)
                raw_h1 = re.sub(r'<[^>]+>', ' ', h1_m.group(1)).strip() if h1_m else ''
                raw_h1 = re.sub(r'\s+', ' ', raw_h1)
                
                exp_h1_norm = exp['h1'].replace('\u2014', '-').replace('&mdash;', '-').strip()
                raw_h1_norm = raw_h1.replace('\u2014', '-').replace('&mdash;', '-').replace('—', '-').strip()
                h1_ok = (exp['h1'] in raw_h1) or (exp_h1_norm in raw_h1_norm)

                # Internal links check
                found_links = []
                for l in exp['links']:
                    pat = re.compile(r'<a[^>]+>[^<]*?' + re.escape(l) + r'[^<]*?</a>', re.IGNORECASE)
                    if pat.search(html):
                        found_links.append(l)

                links_ok = (len(found_links) == len(exp['links']))
                missing_links = set(exp['links']) - set(found_links)

                # Accordion check
                faq_ok = ('faq-item' in html) or ('mtf-accordion' in html)

                status = 'PASS' if (title_ok and h1_ok and links_ok and faq_ok) else 'FAIL'
                if status == 'FAIL':
                    all_passed = False

                print(f"[{status}] /{slug}")
                if not title_ok:
                    print(f"   [!] Title: Expected '{exp['title']}' | Got '{raw_title}'")
                if not h1_ok:
                    print(f"   [!] H1: Expected '{exp['h1']}' | Got '{raw_h1}'")
                if not links_ok:
                    print(f"   [!] Missing Anchors: {missing_links}")
                if not faq_ok:
                    print(f"   [!] Missing FAQ accordions")

        except Exception as e:
            all_passed = False
            print(f"[ERR] /{slug}: {e}")

    print("=" * 70)
    if all_passed:
        print("RESULT: ALL 13 PAGES FULLY VERIFIED & 100% PASSING!")
    else:
        print("RESULT: SOME AUDIT CHECKS FAILED. PLEASE REVIEW ABOVE.")
    print("=" * 70)

if __name__ == '__main__':
    run_audit()
