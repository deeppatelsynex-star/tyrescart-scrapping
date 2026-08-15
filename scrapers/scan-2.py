"""Scrape tyre catalogue from https://gcco.ae using curl_cffi for Cloudflare TLS bypass.
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

import openpyxl
from curl_cffi import requests as c_requests
from scrapy.selector import Selector

SIZE_RE = re.compile(r"\b(\d{3})/(\d{2,3})\s*R(\d{2}(?:\.\d+)?)\b", re.I)
LOAD_SPEED_RE = re.compile(r"\b\d{2,3}(?:/\d{2,3})?[A-Z]\b", re.I)
YEAR_RE = re.compile(r"\((\d{4})\)")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TODAY = datetime.now().strftime("%d-%m-%Y")

DEFAULT_SITEMAP_URL = "https://gcco.ae/sitemap.xml"

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/127.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Sec-Ch-Ua": '"Not)A;Brand";v="99", "Google Chrome";v="127", "Chromium";v="127"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "none",
    "Sec-Fetch-User": "?1",
    "Upgrade-Insecure-Requests": "1",
}

OUTPUT_FILE = (
    sys.argv[1]
    if len(sys.argv) > 1
    else os.path.join(BASE_DIR, f"gcco_data_{TODAY}.xlsx")
)

INPUT_CSV = sys.argv[2] if len(sys.argv) > 2 else None


def emit_status(url, status, parent=None, url_type=None):
    print(f"URL_STATUS|{url}|{status}|{parent or ''}|{url_type or ''}", flush=True)


def load_input_urls():
    if INPUT_CSV and os.path.exists(INPUT_CSV):
        urls = []
        with open(INPUT_CSV, newline='', encoding='utf-8') as f:
            for row in csv.reader(f):
                if row and row[0].strip():
                    urls.append(row[0].strip())
        if urls:
            return urls
    return [DEFAULT_SITEMAP_URL]


def robust_get(session, url, retries=3):
    impersonates = ["chrome124", "safari17_0", "chrome120"]
    for attempt in range(retries):
        imp = impersonates[attempt % len(impersonates)]
        try:
            r = session.get(
                url,
                headers=DEFAULT_HEADERS,
                impersonate=imp,
                timeout=35,
                allow_redirects=True,
            )
            if r.status_code == 200 and r.text:
                return r
            time.sleep(1 + attempt * 0.5)
        except Exception:
            time.sleep(1 + attempt * 0.5)
    return None


def extract_product_urls_from_sitemap(session, sitemap_url):
    emit_status(sitemap_url, 'running', url_type='sitemap')
    r = robust_get(session, sitemap_url, retries=4)
    if not r:
        emit_status(sitemap_url, 'blocked', url_type='sitemap')
        return []

    sel = Selector(text=r.text)
    urls = sel.css("loc::text").getall()
    if not urls:
        urls = sel.xpath("//*[local-name()='loc']/text()").getall()

    product_urls = [u.strip() for u in urls if u and "/product/" in u]
    for u in product_urls:
        emit_status(u, 'pending', parent=sitemap_url, url_type='product')

    emit_status(sitemap_url, 'done', url_type='sitemap')
    return product_urls


def parse_product_page(session, url, parent_url):
    emit_status(url, 'running', parent=parent_url, url_type='product')
    try:
        r = robust_get(session, url, retries=3)
        if not r or r.status_code != 200:
            emit_status(url, 'blocked', parent=parent_url, url_type='product')
            return None

        sel = Selector(text=r.text)
        product = None
        for script in sel.css('script[type="application/ld+json"]::text').getall():
            try:
                data = json.loads(script)
                if data.get("@type") == "Product":
                    product = data
                    break
            except Exception:
                continue

        if not product:
            emit_status(url, 'blocked', parent=parent_url, url_type='product')
            return None

        name = product.get("name", "").strip()
        offers = product.get("offers") or {}
        images = product.get("image") or []

        def in_stock(availability):
            availability = (availability or "").lower()
            if "outofstock" in availability or "discontinued" in availability:
                return "No"
            if "instock" in availability or "limitedavailability" in availability or "preorder" in availability:
                return "Yes"
            return "Unknown"

        item = OrderedDict()
        item["Name"] = name
        item["Brand"] = (product.get("brand") or {}).get("name", "")
        item["SKU"] = product.get("sku", "")

        size_m = SIZE_RE.search(name)
        item["Tire Size"] = size_m.group(0) if size_m else ""
        item["Width"] = size_m.group(1) if size_m else ""
        item["Aspect Ratio"] = size_m.group(2) if size_m else ""
        item["Rim Diameter"] = size_m.group(3) if size_m else ""

        speed_m = LOAD_SPEED_RE.search(name)
        item["Load/Speed Index"] = speed_m.group(0) if speed_m else ""

        year_m = YEAR_RE.search(name)
        item["Year"] = year_m.group(1) if year_m else ""

        item["Category"] = product.get("category", "")
        item["Price"] = offers.get("price", "")
        item["Currency"] = offers.get("priceCurrency", "")
        item["In Stock"] = in_stock(offers.get("availability", ""))
        item["Image URL"] = images[0] if images else ""
        item["Description"] = product.get("description", "")
        item["Source"] = url

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
            "Name", "Brand", "SKU", "Tire Size", "Width", "Aspect Ratio",
            "Rim Diameter", "Load/Speed Index", "Year", "Category",
            "Price", "Currency", "In Stock", "Image URL", "Description", "Source"
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
            if self.save_count % 5 == 0:
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

    for target in inputs:
        if "sitemap" in target.lower() or target.endswith(".xml"):
            prods = extract_product_urls_from_sitemap(session, target)
            for p in prods:
                product_queue.append((p, target))
        elif "/product/" in target.lower():
            emit_status(target, 'pending', parent='', url_type='product')
            product_queue.append((target, ''))
        else:
            prods = extract_product_urls_from_sitemap(session, target)
            if not prods:
                emit_status(target, 'pending', parent='', url_type='product')
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
        sess = get_thread_session()
        item = parse_product_page(sess, url, parent_url)
        if item:
            writer.write_row(item)
        return item

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(worker_task, url, parent) for url, parent in product_queue]
        for f in as_completed(futures):
            pass

    writer.close()


if __name__ == "__main__":
    main()
