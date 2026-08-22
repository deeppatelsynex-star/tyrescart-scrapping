import glob
import math
import os
import re
import threading
import time
from datetime import datetime

import openpyxl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CACHE_LOCK = threading.Lock()
_CACHE_TIMESTAMP = 0
_CACHE_DATA = []
_CACHE_BY_SKU = {}
_CACHE_BRANDS = []
_CACHE_STATS = {}
CACHE_TTL_SECONDS = 60


def _clean_str(val):
    if val is None:
        return ''
    return str(val).strip()


def _parse_float(val, default=0.0):
    if val is None:
        return default
    if isinstance(val, (int, float)):
        return float(val)
    cleaned = re.sub(r'[^\d.]', '', str(val))
    try:
        return float(cleaned) if cleaned else default
    except ValueError:
        return default


def _parse_size_specs(size_str):
    width, profile, rim = None, None, None
    if not size_str:
        return width, profile, rim

    m = re.search(r'(\d{3})[/\s]*(\d{2,3})?\s*[R|r|Z|z|D|d]?\s*(\d{2})', size_str)
    if m:
        width = int(m.group(1)) if m.group(1) else None
        profile = int(m.group(2)) if m.group(2) else None
        rim = int(m.group(3)) if m.group(3) else None
    return width, profile, rim


def _load_all_products_from_disk():
    xlsx_files = sorted(
        glob.glob(os.path.join(BASE_DIR, '*.xlsx')),
        key=os.path.getmtime,
        reverse=True,
    )

    products_by_sku = {}
    total_loaded = 0

    for file_path in xlsx_files:
        filename = os.path.basename(file_path)
        if filename.startswith('~$') or 'job_' in filename:
            continue

        try:
            wb = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
            ws = wb.active
            if ws is None:
                continue

            rows = list(ws.iter_rows(values_only=True))
            if not rows or len(rows) < 2:
                continue

            headers = [str(h).strip().lower() if h is not None else '' for h in rows[0]]

            col_map = {}
            for idx, h in enumerate(headers):
                if 'sku' in h:
                    col_map['sku'] = idx
                elif 'brand' in h:
                    col_map['brand'] = idx
                elif 'product' in h and 'name' in h:
                    if 'product_name' not in col_map:
                        col_map['product_name'] = idx
                elif 'name' in h and 'product_name' not in col_map:
                    col_map['product_name'] = idx
                elif 'size' in h:
                    col_map['size'] = idx
                elif 'price' in h and 'set' not in h:
                    col_map['price'] = idx
                elif 'set' in h and 'price' in h:
                    col_map['set_price'] = idx
                elif 'stock' in h:
                    col_map['instock'] = idx
                elif 'image' in h:
                    col_map['image'] = idx
                elif 'source' in h or 'url' in h:
                    col_map['source'] = idx
                elif 'vehicle' in h:
                    col_map['vehicle_type'] = idx
                elif 'year' in h:
                    col_map['year'] = idx
                elif 'country' in h:
                    col_map['country'] = idx
                elif 'warranty' in h:
                    col_map['warranty'] = idx
                elif 'serv' in h or 'desc' in h:
                    col_map['serv_desc'] = idx
                elif 'fuel' in h:
                    col_map['fuel_efficiency'] = idx
                elif 'wet' in h:
                    col_map['wet_grip'] = idx
                elif 'noise' in h:
                    col_map['noise'] = idx
                elif 'utqg' in h:
                    col_map['utqg'] = idx

            for row in rows[1:]:
                if not row or not any(row):
                    continue

                sku = _clean_str(row[col_map['sku']]) if 'sku' in col_map and col_map['sku'] < len(row) else f'tc_{total_loaded + 1}'
                if not sku:
                    sku = f'tc_{total_loaded + 1}'

                if sku in products_by_sku:
                    continue

                brand = _clean_str(row[col_map['brand']]) if 'brand' in col_map and col_map['brand'] < len(row) else 'Generic'
                prod_name = _clean_str(row[col_map['product_name']]) if 'product_name' in col_map and col_map['product_name'] < len(row) else ''
                size_str = _clean_str(row[col_map['size']]) if 'size' in col_map and col_map['size'] < len(row) else ''
                price_num = _parse_float(row[col_map['price']]) if 'price' in col_map and col_map['price'] < len(row) else 0.0
                set_price_num = _parse_float(row[col_map['set_price']]) if 'set_price' in col_map and col_map['set_price'] < len(row) else (price_num * 4 if price_num else 0.0)
                instock_val = _clean_str(row[col_map['instock']]) if 'instock' in col_map and col_map['instock'] < len(row) else 'Yes'
                image_url = _clean_str(row[col_map['image']]) if 'image' in col_map and col_map['image'] < len(row) else ''
                source_url = _clean_str(row[col_map['source']]) if 'source' in col_map and col_map['source'] < len(row) else ''
                vehicle_type = _clean_str(row[col_map['vehicle_type']]) if 'vehicle_type' in col_map and col_map['vehicle_type'] < len(row) else 'Car / Passenger'
                year = _clean_str(row[col_map['year']]) if 'year' in col_map and col_map['year'] < len(row) else str(datetime.now().year)
                country = _clean_str(row[col_map['country']]) if 'country' in col_map and col_map['country'] < len(row) else ''
                warranty = _clean_str(row[col_map['warranty']]) if 'warranty' in col_map and col_map['warranty'] < len(row) else '1 Year Official Warranty'
                serv_desc = _clean_str(row[col_map['serv_desc']]) if 'serv_desc' in col_map and col_map['serv_desc'] < len(row) else ''
                fuel = _clean_str(row[col_map['fuel_efficiency']]) if 'fuel_efficiency' in col_map and col_map['fuel_efficiency'] < len(row) else ''
                wet = _clean_str(row[col_map['wet_grip']]) if 'wet_grip' in col_map and col_map['wet_grip'] < len(row) else ''
                noise = _clean_str(row[col_map['noise']]) if 'noise' in col_map and col_map['noise'] < len(row) else ''
                utqg = _clean_str(row[col_map['utqg']]) if 'utqg' in col_map and col_map['utqg'] < len(row) else ''

                width, profile, rim = _parse_size_specs(size_str)

                if not prod_name:
                    prod_name = f'{brand} {size_str}'.strip()

                full_title = f'{brand} {prod_name}'.strip() if not prod_name.lower().startswith(brand.lower()) else prod_name

                if not image_url or not image_url.startswith('http'):
                    image_url = 'https://images.unsplash.com/photo-1578844251758-2f71da64c96f?w=600&auto=format&fit=crop&q=80'

                is_in_stock = instock_val.lower() in ('yes', '1', 'true', 'in stock', 'instock')

                item = {
                    'id': total_loaded + 1,
                    'sku': sku,
                    'title': full_title,
                    'product_name': prod_name,
                    'brand': brand or 'Generic',
                    'size': size_str or 'Standard Size',
                    'width': width,
                    'profile': profile,
                    'rim': rim,
                    'price': price_num,
                    'formatted_price': f'AED {price_num:,.2f}' if price_num else 'Price on Request',
                    'set_price': set_price_num,
                    'formatted_set_price': f'AED {set_price_num:,.2f}' if set_price_num else None,
                    'instock': is_in_stock,
                    'stock_status': 'In Stock' if is_in_stock else 'Out of Stock',
                    'image': image_url,
                    'source': source_url,
                    'vehicle_type': vehicle_type or 'Car / SUV',
                    'year': year,
                    'country': country or 'Imported',
                    'warranty': warranty,
                    'serv_desc': serv_desc,
                    'fuel_efficiency': fuel or 'C',
                    'wet_grip': wet or 'B',
                    'noise': noise or '71 dB',
                    'utqg': utqg or '400 A A',
                    'file_source': filename,
                }

                products_by_sku[sku] = item
                total_loaded += 1

        except Exception:
            continue

    all_products = list(products_by_sku.values())

    brand_counts = {}
    for p in all_products:
        b = p['brand']
        brand_counts[b] = brand_counts.get(b, 0) + 1

    brands_list = [
        {
            'name': b,
            'count': count,
            'slug': b.lower().replace(' ', '-'),
        }
        for b, count in sorted(brand_counts.items(), key=lambda x: x[0].lower())
    ]

    stats = {
        'total_products': len(all_products),
        'total_brands': len(brands_list),
        'in_stock_count': sum(1 for p in all_products if p['instock']),
        'min_price': min((p['price'] for p in all_products if p['price'] > 0), default=0),
        'max_price': max((p['price'] for p in all_products if p['price'] > 0), default=0),
        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }

    return all_products, products_by_sku, brands_list, stats


def _ensure_cache():
    global _CACHE_DATA, _CACHE_BY_SKU, _CACHE_BRANDS, _CACHE_STATS, _CACHE_TIMESTAMP
    now = time.time()
    if not _CACHE_DATA or (now - _CACHE_TIMESTAMP > CACHE_TTL_SECONDS):
        with _CACHE_LOCK:
            if not _CACHE_DATA or (now - _CACHE_TIMESTAMP > CACHE_TTL_SECONDS):
                _CACHE_DATA, _CACHE_BY_SKU, _CACHE_BRANDS, _CACHE_STATS = _load_all_products_from_disk()
                _CACHE_TIMESTAMP = now


def get_all_products():
    _ensure_cache()
    return _CACHE_DATA


def get_product_by_sku(sku):
    _ensure_cache()
    if not sku:
        return None
    if sku in _CACHE_BY_SKU:
        return _CACHE_BY_SKU[sku]

    sku_lower = str(sku).strip().lower()
    for s, p in _CACHE_BY_SKU.items():
        if s.lower() == sku_lower or str(p.get('id')) == sku_lower:
            return p
    return None


def get_brands():
    _ensure_cache()
    return _CACHE_BRANDS


def get_stats():
    _ensure_cache()
    return _CACHE_STATS


def query_products(
    brand=None,
    width=None,
    profile=None,
    rim=None,
    vehicle_type=None,
    min_price=None,
    max_price=None,
    instock_only=False,
    query=None,
    sort='relevance',
    page=1,
    per_page=20,
):
    products = get_all_products()

    filtered = []
    brand_filter = brand.strip().lower() if brand else None
    vehicle_filter = vehicle_type.strip().lower() if vehicle_type else None
    query_terms = [t.lower() for t in query.strip().split()] if query else []

    try:
        width_val = int(width) if width else None
    except (ValueError, TypeError):
        width_val = None

    try:
        profile_val = int(profile) if profile else None
    except (ValueError, TypeError):
        profile_val = None

    try:
        rim_val = int(rim) if rim else None
    except (ValueError, TypeError):
        rim_val = None

    try:
        min_p = float(min_price) if min_price is not None else None
    except (ValueError, TypeError):
        min_p = None

    try:
        max_p = float(max_price) if max_price is not None else None
    except (ValueError, TypeError):
        max_p = None

    for p in products:
        if instock_only and not p['instock']:
            continue

        if brand_filter and p['brand'].lower() != brand_filter:
            continue

        if width_val is not None and p['width'] != width_val:
            continue

        if profile_val is not None and p['profile'] != profile_val:
            continue

        if rim_val is not None and p['rim'] != rim_val:
            continue

        if vehicle_filter and vehicle_filter not in p['vehicle_type'].lower():
            continue

        if min_p is not None and p['price'] < min_p:
            continue

        if max_p is not None and p['price'] > max_p:
            continue

        if query_terms:
            searchable = f"{p['brand']} {p['title']} {p['size']} {p['vehicle_type']} {p['sku']}".lower()
            if not all(term in searchable for term in query_terms):
                continue

        filtered.append(p)

    if sort == 'price_asc':
        filtered.sort(key=lambda x: x['price'] if x['price'] > 0 else float('inf'))
    elif sort == 'price_desc':
        filtered.sort(key=lambda x: x['price'], reverse=True)
    elif sort == 'brand_asc':
        filtered.sort(key=lambda x: x['brand'].lower())
    elif sort == 'name_asc':
        filtered.sort(key=lambda x: x['title'].lower())

    total = len(filtered)
    page = max(1, page)
    per_page = max(1, min(per_page, 100))
    total_pages = max(1, math.ceil(total / per_page))

    start = (page - 1) * per_page
    end = start + per_page
    paginated = filtered[start:end]

    return {
        'products': paginated,
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1,
    }
