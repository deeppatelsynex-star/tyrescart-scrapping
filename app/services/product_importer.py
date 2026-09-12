"""
app/services/product_importer.py - Product & Category CSV Importer Service

Handles importing products along with Magento category hierarchy paths and brands.
- Parses categories column into hierarchical tree under root ID 2 (Default Category).
- Auto-creates any missing brands.
- Creates products with all tyre attributes, inventories, website assignments.
- Maps leaf category IDs into product_categories table and product.category_id.
"""

import csv
import io
import re
from datetime import datetime, timezone
from db import get_connection
from i18n import dump_json_dict, parse_json_dict
from models.brand import Brand
from models.category import Category
from models.product import Product
from services.category_importer import CategoryImporter, parse_category_paths


def slugify(text: str) -> str:
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')


class ProductImporter:
    @classmethod
    def import_csv(cls, file_content, user_id: int = 1) -> dict:
        """
        Imports products and their category hierarchies from CSV.
        Supports bytes, str, or file-like stream.
        """
        if isinstance(file_content, bytes):
            text = file_content.decode('utf-8-sig', errors='replace')
        elif isinstance(file_content, str):
            text = file_content
        elif hasattr(file_content, 'read'):
            raw = file_content.read()
            if isinstance(raw, bytes):
                text = raw.decode('utf-8-sig', errors='replace')
            else:
                text = str(raw)
        else:
            return {'success': False, 'error': 'Invalid file stream.', 'imported': 0}

        # Step 1: Run CategoryImporter to ensure category tree hierarchy exists
        cat_result = CategoryImporter.import_csv(text, user_id=user_id)

        # Step 2: Build category tree cache: (parent_id, name_en.lower()) -> category_id
        conn = get_connection()
        cat_tree = {}
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, parent_id, name FROM categories WHERE deleted_at IS NULL")
                for c in cur.fetchall():
                    nd = parse_json_dict(c['name'])
                    name_en = (nd.get('en') if isinstance(nd, dict) else str(c['name'])).strip().lower()
                    cat_tree[(c['parent_id'], name_en)] = c['id']
        finally:
            conn.close()

        def resolve_leaf_category_id(path_segments: list):
            if not path_segments:
                return None
            curr_id = 2  # Root Default Category
            segs = path_segments[1:] if path_segments[0].strip().lower() == 'default category' else path_segments
            for s in segs:
                norm_s = s.strip().lower()
                key = (curr_id, norm_s)
                if key in cat_tree:
                    curr_id = cat_tree[key]
                else:
                    return None
            return curr_id

        # Step 3: Ensure brands exist and build brand_map
        stream = io.StringIO(text)
        reader = csv.DictReader(stream)
        rows = list(reader)
        if not rows:
            return {'success': False, 'error': 'CSV is empty.', 'imported': 0}

        distinct_brands = set()
        for r in rows:
            b_val = (r.get('brand') or r.get('brand_name') or '').strip()
            if b_val:
                distinct_brands.add(b_val)

        brand_map = {}
        for b_name in distinct_brands:
            b_slug = Brand.slugify(b_name)
            existing_b = Brand.find_by_slug(b_slug)
            if existing_b:
                brand_map[b_name.lower()] = existing_b['id']
            else:
                new_b_id = Brand.create({
                    'name': b_name,
                    'slug': b_slug,
                    'status': 'active'
                }, user_id=user_id)
                brand_map[b_name.lower()] = new_b_id

        # Step 4: Import each product
        imported = 0
        updated = 0
        errors = []

        for idx, row in enumerate(rows, start=2):
            try:
                sku = (row.get('sku') or '').strip().upper()
                if not sku:
                    errors.append(f"Row {idx}: Missing SKU, skipped.")
                    continue

                item_code = (row.get('item_code') or sku).strip()
                name = (row.get('name') or row.get('display_name') or sku).strip()
                display_name = (row.get('display_name') or row.get('pattern') or name).strip()
                raw_price = row.get('price') or '0'
                try:
                    price = float(raw_price)
                except ValueError:
                    price = 0.0

                raw_cost = row.get('cost') or None
                try:
                    cost_price = float(raw_cost) if raw_cost else None
                except ValueError:
                    cost_price = None

                b_str = (row.get('brand') or '').strip()
                brand_id = brand_map.get(b_str.lower())

                # Resolve category paths
                cat_cell = row.get('categories') or ''
                parsed_paths = parse_category_paths(cat_cell)
                assigned_category_ids = []
                for p in parsed_paths:
                    leaf_id = resolve_leaf_category_id(p)
                    if leaf_id and leaf_id not in assigned_category_ids:
                        assigned_category_ids.append(leaf_id)

                primary_category_id = assigned_category_ids[0] if assigned_category_ids else None

                # Dimensions and specs
                width = (row.get('width') or '').strip()
                height = (row.get('height') or '').strip()
                rim = (row.get('rim') or '').strip()
                tyre_size = (row.get('tyre_size') or '').strip()
                if not tyre_size and width and height and rim:
                    tyre_size = f"{width}/{height} R{rim}"

                raw_load_index = (row.get('load_index') or '').strip()
                load_index = raw_load_index
                speed_rating = (row.get('speed_rating') or row.get('tire_speed_rating') or '').strip()
                if raw_load_index:
                    import re
                    m = re.match(r'^(\d{2,3})\s*([A-Za-z]+)$', raw_load_index)
                    if m:
                        load_index = m.group(1)
                        if not speed_rating:
                            speed_rating = m.group(2).upper()

                pattern = (row.get('pattern') or '').strip()
                country = (row.get('country') or '').strip()
                year = (row.get('year') or '').strip()
                warranty_period = (row.get('warranty_period') or '').strip()
                parts_category = (row.get('parts_category') or 'Tyres').strip()
                tyres_category = (row.get('tyres_category') or 'Premium').strip()
                price_included = (row.get('price_included_text') or row.get('price_included') or 'Fitted Price').strip()
                runflat_raw = (row.get('runflat') or '').strip().lower()
                run_flat = 1 if runflat_raw in ('yes', '1', 'true') else 0
                ev_raw = (row.get('ev_tyre') or '').strip().lower()
                ev_rated = 1 if ev_raw in ('yes', '1', 'true') else 0
                tabby_raw = (row.get('tabby_payment') or '').strip().lower()
                pay_later_eligible = 1 if tabby_raw in ('yes', '1', 'true') else 0

                base_image = (row.get('base_image') or '').strip()
                small_image = (row.get('small_image') or base_image).strip()
                url_key = (row.get('url_key') or slugify(name)).strip()
                raw_weight = row.get('weight')
                try:
                    weight = float(raw_weight) if raw_weight else None
                except (ValueError, TypeError):
                    weight = None

                # Dynamic attributes dictionary matching Magento fields
                dynamic_attrs = {
                    'sku': sku,
                    'item_code': item_code,
                    'price': str(price),
                    'price_per_item': row.get('price_per_item') or str(price),
                    'brand': b_str,
                    'pattern': pattern,
                    'display_name': display_name,
                    'product_name': name,
                    'tyre_marking': (row.get('tyre_marking') or '').strip(),
                    'oem_tyres': (row.get('oem_tyres') or '').strip(),
                    'ev_tyre': 'Yes' if ev_rated else 'No',
                    'tyre_size': tyre_size,
                    'tire_size': tyre_size,
                    'tire_size_label': tyre_size,
                    'width': width,
                    'height': height,
                    'aspect_ratio': height,
                    'rim': rim,
                    'rim_size': rim,
                    'load_index': load_index,
                    'load_speed_index': raw_load_index or f"{load_index}{speed_rating}".strip(),
                    'tire_load_index': load_index,
                    'tire_speed_rating': speed_rating,
                    'year': year,
                    'runflat': 'Yes' if run_flat else 'No',
                    'country': country,
                    'country_of_origin': country,
                    'origin': country,
                    'parts_category': parts_category,
                    'tyre_type': (row.get('tyre_type') or 'Car').strip(),
                    'warranty_period': warranty_period,
                    'tyres_category': tyres_category,
                    'tabby_payment': 'Yes' if pay_later_eligible else 'No',
                    'price_included_text': price_included,
                    'tax_class': (row.get('tax_class_name') or row.get('tax_class') or 'Taxable Goods').strip(),
                    'tax_class_name': (row.get('tax_class_name') or row.get('tax_class') or 'Taxable Goods').strip(),
                    'promotion': (row.get('offers') or row.get('promotion') or 'None').strip(),
                    'offers': (row.get('offers') or row.get('promotion') or '').strip(),
                    'visibility': (row.get('visibility') or 'Catalog, Search').strip()
                }

                product_payload = {
                    'sku': sku,
                    'website_id': 1,
                    'item_code': item_code,
                    'parts_category': parts_category,
                    'tyres_category': tyres_category,
                    'year': year,
                    'price_included': price_included,
                    'small_image': small_image,
                    'small_image_alt': display_name,
                    'display_name': display_name,
                    'name_en': name,
                    'slug': url_key,
                    'attribute_set_id': 1,  # Tyres
                    'brand_id': brand_id,
                    'category_id': primary_category_id,
                    'category_ids': assigned_category_ids,
                    'website_ids': [1],
                    'price': price,
                    'cost_price': cost_price,
                    'stock_qty': 10,
                    'stock_status': 'in_stock',
                    'vehicle_type': 'car',
                    'tire_type': 'summer',
                    'width': width,
                    'aspect_ratio': height,
                    'rim_size': rim,
                    'tire_size_label': tyre_size,
                    'tire_speed_rating': speed_rating,
                    'tire_load_index': load_index,
                    'tire_pattern': pattern,
                    'country_of_origin': country,
                    'warranty_months': 12,
                    'weight': weight,
                    'run_flat': run_flat,
                    'ev_rated': ev_rated,
                    'pay_later_eligible': pay_later_eligible,
                    'image_path': base_image,
                    'status': 'active',
                    'visibility': 'visible',
                    'short_desc_en': (row.get('short_description') or '').strip(),
                    'description_en': (row.get('description') or '').strip(),
                    'meta_title_en': (row.get('meta_title') or '').strip(),
                    'meta_desc_en': (row.get('meta_description') or '').strip(),
                    'dynamic_attributes': dynamic_attrs,
                    'attributes_json': dynamic_attrs
                }

                existing_p = Product.find_by_sku(sku)
                if existing_p:
                    Product.update(existing_p['id'], product_payload, user_id=user_id)
                    updated += 1
                else:
                    Product.create(product_payload, user_id=user_id)
                    imported += 1

            except Exception as ex:
                errors.append(f"Row {idx} ({row.get('sku')}): {str(ex)}")

        return {
            'success': True,
            'total_rows': len(rows),
            'imported': imported,
            'updated': updated,
            'category_result': cat_result,
            'errors': errors
        }
