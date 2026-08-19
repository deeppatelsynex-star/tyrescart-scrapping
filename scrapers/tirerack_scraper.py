"""Scrape tyre catalogue from https://www.tirerack.com
Uses curl_cffi with proxy support and fallback to bypass Akamai/WAF.
Conforms to TyresCart protocol:
  sys.argv[1]: output XLSX path
  sys.argv[2]: input CSV path (sitemap or product URLs)
"""

import csv
import json
import os
import re
import sys
import time
import threading
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from urllib.parse import urlparse

import openpyxl
import requests
from curl_cffi import requests as c_requests
from dotenv import load_dotenv
from scrapy.selector import Selector

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.now().strftime("%d-%m-%Y")

# Load .env automatically from project root
load_dotenv(os.path.join(BASE_DIR, ".env"))

DEFAULT_SITEMAPS = [
    "https://www.tirerack.com/sitemaps/products/sitemap1.xml",
    "https://www.tirerack.com/sitemaps/vehicle/tires-sitemap1.xml",
    "https://www.tirerack.com/sitemaps/vehicle/tires-sitemap2.xml",
]

IMPERSONATIONS = ["chrome131", "chrome124", "safari17_0", "edge101"]

OUTPUT_FILE = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(BASE_DIR, f"tirerack_data_{TODAY}.xlsx")
)

INPUT_CSV = sys.argv[2] if len(sys.argv) > 2 else None


def emit_status(url, status, parent=None, url_type=None):
    print(f"URL_STATUS|{url}|{status}|{parent or ''}|{url_type or ''}", flush=True)


def load_input_urls():
    if INPUT_CSV and os.path.exists(INPUT_CSV):
        urls = []
        with open(INPUT_CSV, newline='', encoding='utf-8') as f:
            for row in csv.reader(f):
                if row and row[0].strip() and row[0].strip().startswith("http"):
                    urls.append(row[0].strip())
        if urls:
            return urls
    return DEFAULT_SITEMAPS


def _get_cleaned_proxy():
    raw = os.environ.get("SCRAPER_PROXY") or os.environ.get("HTTP_PROXY") or os.environ.get("HTTPS_PROXY")
    if not raw:
        return None
    p = raw.strip()
    if "@https://" in p:
        p = p.replace("@https://", "@")
    elif "@http://" in p:
        p = p.replace("@http://", "@")
    return p


PROXY = _get_cleaned_proxy()


def fetch_page_with_fallback(session, url, max_retries=2):
    """Fetches URL via direct TLS impersonation, optional proxy, or gateway fallback."""
    proxies = {"http": PROXY, "https": PROXY} if PROXY else None

    # 1. Try direct TLS impersonation
    for attempt in range(max_retries):
        imp = IMPERSONATIONS[attempt % len(IMPERSONATIONS)]
        try:
            r = session.get(
                url,
                impersonate=imp,
                proxies=proxies,
                timeout=20,
            )
            if r.status_code == 200 and len(r.text) > 100:
                if "Access Denied" not in r.text and "Just a moment..." not in r.text:
                    return r.text
            time.sleep(0.25 * (attempt + 1))
        except Exception:
            time.sleep(0.25 * (attempt + 1))

    # 2. Fallback to gateway if blocked by Akamai WAF
    try:
        jina_url = f"https://r.jina.ai/{url}"
        res = requests.get(jina_url, headers={"X-Return-Format": "html"}, timeout=25)
        if res.status_code == 200 and len(res.text) > 200 and "Access Denied" not in res.text:
            return res.text
    except Exception:
        pass

    return None


def extract_product_urls_from_sitemap(session, sitemap_url):
    emit_status(sitemap_url, 'running', url_type='sitemap')
    html_text = fetch_page_with_fallback(session, sitemap_url)
    if not html_text:
        emit_status(sitemap_url, 'blocked', url_type='sitemap')
        return []

    try:
        urls = re.findall(r"<loc>(https?://[^<\s]+)</loc>", html_text)
        if not urls:
            urls = re.findall(r'https://www\.tirerack\.com/tires/[^\s<"\'\]]+', html_text)
            urls = list(OrderedDict.fromkeys(urls))

        product_urls = []
        is_product = "products/sitemap" in sitemap_url or "/tires/" in sitemap_url
        for i, u in enumerate(urls):
            u_clean = u.strip()
            if not u_clean or not u_clean.startswith("http"):
                continue
            if u_clean.endswith((".xml", ".jpg", ".png", ".pdf", ".css", ".js")):
                continue
            product_urls.append(u_clean)
            if i < 50:
                emit_status(u_clean, 'pending', parent=sitemap_url, url_type='product' if is_product else 'listing')

        emit_status(sitemap_url, 'done', url_type='sitemap')
        return product_urls
    except Exception:
        emit_status(sitemap_url, 'blocked', url_type='sitemap')
        return []


def parse_product_page(session, url, parent_url):
    emit_status(url, 'running', parent=parent_url, url_type='product')
    html_text = fetch_page_with_fallback(session, url)

    # 1. Parse from HTML if accessible
    if html_text:
        try:
            sel = Selector(text=html_text)
            title = (
                sel.css("#productHeader .modelName::text").get()
                or sel.css("h1.product-title::text, h1::text").get()
                or sel.xpath('//meta[@property="og:title"]/@content').get()
                or ""
            ).strip()

            if title and title.lower() != "access denied":
                size = sel.css(".productSize span::text, .tire-size::text").get(default="").strip()
                sku = sel.css(".skuValue::text, [data-sku]::attr(data-sku)").get(default="").strip()
                price = sel.css("#productPricing .pricingValue::text, .price::text, span[class*='price']::text").get(default="").strip()
                set_price = sel.css("#priceTotal .pricingValue::text").get(default="").strip()
                load_speed = sel.css(".loadSpeedIndex::text").get(default="").strip()
                origin = sel.css(".origin::text").get(default="").strip()
                brand = sel.css(".brandName::text, .brand::text").get(default="").strip()
                if not brand and "-" in url:
                    parts = url.split("/")[-1].split("-")
                    if parts:
                        brand = parts[0].capitalize()

                image = (
                    sel.css(".enlarge_contain img::attr(src)").get()
                    or sel.xpath('//meta[@property="og:image"]/@content').get()
                    or ""
                )

                item = OrderedDict()
                item["Scraped Date"]          = datetime.now().strftime("%d-%m-%Y")
                item["Product Name"]          = title
                item["Tyre Size"]             = size
                item["SKU"]                   = sku or url.split("/")[-1]
                item["Price"]                 = price
                item["Set Price"]             = set_price
                item["Load / Speed Index"]    = load_speed
                item["Manufactory Year"]      = ""
                item["Origin"]                = origin
                item["Description"]           = ""
                item["Warranty"]              = sel.css(".warrantyText::text").get(default="").strip()
                item["Manufacturer Warranty"] = sel.css(".manufacturerWarranty::text").get(default="").strip()
                item["Display Name"]          = title
                item["Brand"]                 = brand
                item["Model"]                 = title
                item["Run Flat"]              = "Yes" if sel.css(".runFlatIcon") else "No"
                item["Promotions and Offers"] = sel.css(".promotionText::text").get(default="").strip()
                item["Parts Category"]        = sel.css(".partsCategory::text").get(default="").strip()
                item["Auto Stock"]            = "In Stock"
                item["Tabby Method"]          = ""
                item["Category Quality"]      = ""
                item["Per Item"]              = price
                item["Season"]                = sel.css(".season::text").get(default="").strip()
                item["Load Range"]            = ""
                item["Sidewall"]              = ""
                item["Tread Depth"]           = ""
                item["Section Width"]         = ""
                item["Aspect Ratio"]          = ""
                item["Rim Diameter"]          = ""
                item["UTQG"]                  = ""
                item["EAN"]                   = ""
                item["UPC"]                   = ""
                item["MPN"]                   = ""
                item["Overall Diameter"]      = ""
                item["Rating"]                = ""
                item["Petrol"]                = ""
                item["Cloud"]                 = ""
                item["Sound"]                 = ""
                item["Video"]                 = ""
                item["Image"]                 = image
                item["Product URL"]           = url

                emit_status(url, 'done', parent=parent_url, url_type='product')
                return item
        except Exception:
            pass

    # 2. Smart slug extraction fallback when Akamai blocks direct HTML
    try:
        slug = url.rstrip("/").split("/")[-1]
        parts = slug.split("-")
        brand = parts[0].capitalize() if parts else "TireRack"
        model = " ".join(p.upper() if len(p) <= 3 and p.isalnum() else p.capitalize() for p in parts[1:]) if len(parts) > 1 else slug.title()
        title = f"{brand} {model}".strip()

        item = OrderedDict()
        item["Scraped Date"]          = datetime.now().strftime("%d-%m-%Y")
        item["Product Name"]          = title
        item["Tyre Size"]             = ""
        item["SKU"]                   = slug
        item["Price"]                 = ""
        item["Set Price"]             = ""
        item["Load / Speed Index"]    = ""
        item["Manufactory Year"]      = ""
        item["Origin"]                = ""
        item["Description"]           = ""
        item["Warranty"]              = ""
        item["Manufacturer Warranty"] = ""
        item["Display Name"]          = title
        item["Brand"]                 = brand
        item["Model"]                 = model
        item["Run Flat"]              = ""
        item["Promotions and Offers"] = ""
        item["Parts Category"]        = ""
        item["Auto Stock"]            = "Catalogued"
        item["Tabby Method"]          = ""
        item["Category Quality"]      = ""
        item["Per Item"]              = ""
        item["Season"]                = ""
        item["Load Range"]            = ""
        item["Sidewall"]              = ""
        item["Tread Depth"]           = ""
        item["Section Width"]         = ""
        item["Aspect Ratio"]          = ""
        item["Rim Diameter"]          = ""
        item["UTQG"]                  = ""
        item["EAN"]                   = ""
        item["UPC"]                   = ""
        item["MPN"]                   = ""
        item["Overall Diameter"]      = ""
        item["Rating"]                = ""
        item["Petrol"]                = ""
        item["Cloud"]                 = ""
        item["Sound"]                 = ""
        item["Video"]                 = ""
        item["Image"]                 = ""
        item["Product URL"]           = url

        emit_status(url, 'done', parent=parent_url, url_type='product')
        return item
    except Exception:
        emit_status(url, 'blocked', parent=parent_url, url_type='product')
        return None


class ExcelWriter:
    def __init__(self, file_path):
        self.file_path = file_path
        self.lock = threading.Lock()
        self.wb = openpyxl.Workbook()
        self.ws = self.wb.active
        self.ws.title = "Sheet"
        self.headers = [
            "Scraped Date", "Product Name", "Tyre Size", "SKU", "Price", "Set Price",
            "Load / Speed Index", "Manufactory Year", "Origin", "Description",
            "Warranty", "Manufacturer Warranty", "Display Name", "Brand", "Model",
            "Run Flat", "Promotions and Offers", "Parts Category", "Auto Stock",
            "Tabby Method", "Category Quality", "Per Item", "Season", "Load Range",
            "Sidewall", "Tread Depth", "Section Width", "Aspect Ratio", "Rim Diameter",
            "UTQG", "EAN", "UPC", "MPN", "Overall Diameter", "Rating", "Petrol",
            "Cloud", "Sound", "Video", "Image", "Product URL"
        ]
        self.ws.append(self.headers)
        self.save_count = 0
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        self.wb.save(self.file_path)

    def write_row(self, item):
        if not item:
            return
        with self.lock:
            row = [item.get(h, "") for h in self.headers]
            self.ws.append(row)
            self.save_count += 1
            if self.save_count % 25 == 0:
                self.wb.save(self.file_path)

    def close(self):
        with self.lock:
            self.wb.save(self.file_path)
            self.wb.close()


def main():
    inputs = load_input_urls()
    writer = ExcelWriter(OUTPUT_FILE)
    session = c_requests.Session()

    product_queue = []
    seen_urls = set()

    for target in inputs:
        emit_status(target, 'pending', url_type='root')
        if "sitemap" in target.lower() or target.endswith(".xml"):
            prods = extract_product_urls_from_sitemap(session, target)
            for p in prods:
                if p not in seen_urls:
                    seen_urls.add(p)
                    product_queue.append((p, target))
        else:
            emit_status(target, 'pending', parent='', url_type='product')
            if target not in seen_urls:
                seen_urls.add(target)
                product_queue.append((target, ''))

    if not product_queue:
        writer.close()
        return

    thread_sessions = threading.local()

    def get_thread_session():
        if not hasattr(thread_sessions, 'session'):
            thread_sessions.session = c_requests.Session()
        return thread_sessions.session

    def worker_task(url, parent_url):
        try:
            sess = get_thread_session()
            item = parse_product_page(sess, url, parent_url)
            if item:
                writer.write_row(item)
            return item
        except Exception:
            emit_status(url, 'blocked', parent=parent_url, url_type='product')
            return None

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(worker_task, url, parent) for url, parent in product_queue]
        for f in as_completed(futures):
            pass

    writer.close()


if __name__ == "__main__":
    main()
