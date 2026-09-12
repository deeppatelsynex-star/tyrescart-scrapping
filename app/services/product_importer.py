"""
app/services/product_importer.py - Dynamic Multi-Type Product & Category CSV Importer Service

Handles importing products of any type (Tyres, Batteries, Wheels, Accessories, etc.):
- Automatically detects or maps attribute sets (Tyres, Battery, Wheels, Default, etc.).
- Dynamically matches CSV columns to database attribute definitions rather than static code.
- Automatically handles option resolution and auto-creation for select/multiselect attributes.
- Preserves all CSV columns in attributes_json and syncs to EAV product_attribute_values.
- Parses hierarchical category paths under root ID 2 (Default Category) via CategoryImporter.
- Auto-creates any missing brands.
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
    text = str(text).lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')


# Common column aliases mapping user-friendly or legacy CSV column headers
# to canonical attribute codes defined in the attributes table.
ATTRIBUTE_ALIAS_MAP = {
    'tyre_size': 'tire_size',
    'tire_size_label': 'tire_size',
    'size': 'tire_size',
    'load_index': 'load_speed_index',
    'speed_rating': 'tire_speed_rating',
    'country': 'origin',
    'country_of_origin': 'origin',
    'country_of_manufacture': 'origin',
    'tax_class_name': 'tax_class',
    'tax_class_id': 'tax_class',
    'offers': 'promotion',
    'voltage': 'volts',
    'voltage_v': 'volts',
    'battery_capacity': 'mah',
    'capacity': 'mah',
    'cca_rating': 'cca',
    'cold_cranking_amps': 'cca',
    'warranty': 'warranty_period',
    'short_description': 'short_desc',
}


class ProductImporter:
    @classmethod
    def import_csv(cls, file_content, user_id: int = 1) -> dict:
        """
        Imports products of ANY type (Batteries, Wheels, Tyres, etc.) from CSV.
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

        # Step 1: Run CategoryImporter to ensure all category hierarchies exist
        cat_result = CategoryImporter.import_csv(text, user_id=user_id)

        # Step 2: Build category tree cache: (parent_id, name_en.lower()) -> category_id
        conn = get_connection()
        cat_tree = {}
        set_lookup = {}
        attr_map = {}
        try:
            with conn.cursor() as cur:
                # Cache categories
                cur.execute("SELECT id, parent_id, name FROM categories WHERE deleted_at IS NULL")
                for c in cur.fetchall():
                    nd = parse_json_dict(c['name'])
                    name_en = (nd.get('en') if isinstance(nd, dict) else str(c['name'])).strip().lower()
                    cat_tree[(c['parent_id'], name_en)] = c['id']

                # Cache attribute sets (name -> id, slug -> id, singular/plural)
                cur.execute("SELECT id, name, slug FROM attribute_sets WHERE deleted_at IS NULL")
                for s in cur.fetchall():
                    s_id = s['id']
                    s_name = str(s['name']).strip().lower()
                    s_slug = str(s['slug']).strip().lower() if s.get('slug') else s_name
                    set_lookup[s_name] = s_id
                    set_lookup[s_slug] = s_id
                    set_lookup[str(s_id)] = s_id
                    if s_name.endswith('s'):
                        set_lookup[s_name[:-1]] = s_id
                    else:
                        set_lookup[s_name + 's'] = s_id

                # Cache all attribute definitions from DB
                cur.execute("SELECT id, code, name, type FROM attributes WHERE deleted_at IS NULL")
                for a in cur.fetchall():
                    c_code = a['code'].strip().lower()
                    attr_map[c_code] = a
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
            b_val = (r.get('brand') or r.get('brand_name') or r.get('manufacturer') or '').strip()
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

        # Step 4: Import each product row dynamically
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
                name = (row.get('name') or row.get('product_name') or row.get('display_name') or sku).strip()
                display_name = (row.get('display_name') or row.get('pattern') or name).strip()
                
                raw_price = row.get('price') or '0'
                try:
                    price = float(raw_price)
                except (ValueError, TypeError):
                    price = 0.0

                raw_cost = row.get('cost') or row.get('cost_price') or None
                try:
                    cost_price = float(raw_cost) if raw_cost else None
                except (ValueError, TypeError):
                    cost_price = None

                b_str = (row.get('brand') or row.get('brand_name') or row.get('manufacturer') or '').strip()
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

                # Resolve Attribute Set dynamically
                raw_set_hint = (
                    row.get('attribute_set_code') or 
                    row.get('attribute_set') or 
                    row.get('attribute_set_name') or 
                    row.get('attribute_set_id') or 
                    row.get('parts_category') or ''
                ).strip().lower()

                resolved_set_id = set_lookup.get(raw_set_hint)
                if not resolved_set_id and raw_set_hint.isdigit():
                    resolved_set_id = int(raw_set_hint)

                if not resolved_set_id:
                    # Infer set based on column indicators present in this row
                    cols_present = {k.strip().lower() for k, v in row.items() if v is not None and str(v).strip() != ''}
                    if {'volts', 'voltage', 'cca', 'battery_type', 'mah', 'terminal_layout'} & cols_present:
                        resolved_set_id = set_lookup.get('battery') or 3
                    elif {'bolt_pattern_pcd', 'wheel_type', 'offset', 'hub_bore', 'back_space_inches'} & cols_present:
                        resolved_set_id = set_lookup.get('wheels') or 7
                    elif {'bike_tyre_type'} & cols_present:
                        resolved_set_id = set_lookup.get('motorcycle tyres') or set_lookup.get('motorcycle_tyres') or 4
                    elif {'color_finish'} & cols_present and 'wheel_type' not in cols_present and 'offset' not in cols_present:
                        resolved_set_id = set_lookup.get('rim protectors') or set_lookup.get('rim_protectors') or 5
                    elif {'tyre_size', 'tire_size', 'width', 'height', 'rim', 'load_index', 'speed_rating', 'pattern', 'oem_tyres', 'runflat', 'tyre_type'} & cols_present:
                        resolved_set_id = set_lookup.get('tyres') or 1
                    else:
                        resolved_set_id = set_lookup.get('default') or 2

                # Standard core fields
                status_raw = str(row.get('status') or '1').strip().lower()
                status = 'active' if status_raw in ('1', 'active', 'true', 'yes') else 'inactive'
                visibility = (row.get('visibility') or 'Catalog, Search').strip()
                base_image = (row.get('base_image') or row.get('image_path') or row.get('image') or '').strip()
                small_image = (row.get('small_image') or base_image).strip()
                url_key = (row.get('url_key') or slugify(name)).strip()

                raw_weight = row.get('weight')
                try:
                    weight = float(raw_weight) if raw_weight else None
                except (ValueError, TypeError):
                    weight = None

                raw_qty = row.get('qty') or row.get('stock_qty') or '10'
                try:
                    stock_qty = int(float(raw_qty))
                except (ValueError, TypeError):
                    stock_qty = 10
                stock_status = (row.get('stock_status') or ('in_stock' if stock_qty > 0 else 'out_of_stock')).strip()

                # Build dynamic attributes dictionary from ALL columns present in CSV
                dynamic_attrs = {}
                for raw_k, raw_v in row.items():
                    if raw_k is None or raw_v is None:
                        continue
                    clean_k = str(raw_k).strip()
                    if not clean_k:
                        continue

                    val_str = str(raw_v).strip()

                    # Ignore attribute set indicators from dynamic attributes as attribute_set_id is a core column
                    k_lower = clean_k.lower()
                    if k_lower in ('attribute_set_id', 'attribute_set', 'attribute_set_code', 'attribute_set_name'):
                        continue

                    # Keep raw column value
                    dynamic_attrs[clean_k] = val_str

                    # Match against database attributes table
                    k_lower = clean_k.lower()
                    attr_def = attr_map.get(k_lower)
                    if not attr_def and k_lower in ATTRIBUTE_ALIAS_MAP:
                        target_code = ATTRIBUTE_ALIAS_MAP[k_lower]
                        attr_def = attr_map.get(target_code)

                    if attr_def:
                        code = attr_def['code']
                        a_type = attr_def['type']
                        if a_type == 'boolean':
                            normalized_val = 'Yes' if val_str.lower() in ('1', 'true', 'yes', 'y') else 'No'
                        else:
                            normalized_val = val_str
                        dynamic_attrs[code] = normalized_val

                # Smart additive helpers for domain-specific attributes (only if relevant fields present)
                width = dynamic_attrs.get('width') or ''
                height = dynamic_attrs.get('height') or dynamic_attrs.get('aspect_ratio') or ''
                rim = dynamic_attrs.get('rim') or dynamic_attrs.get('rim_size') or ''
                if width and height and rim and not dynamic_attrs.get('tire_size'):
                    auto_size = f"{width}/{height} R{rim}"
                    dynamic_attrs['tire_size'] = auto_size
                    dynamic_attrs['tire_size_label'] = auto_size

                raw_load = dynamic_attrs.get('load_index') or dynamic_attrs.get('load_speed_index') or ''
                extracted_speed = dynamic_attrs.get('speed_rating') or dynamic_attrs.get('tire_speed_rating') or ''
                extracted_load = raw_load
                if raw_load:
                    m = re.match(r'^(\d{2,3})\s*([A-Za-z]+)$', raw_load)
                    if m:
                        extracted_load = m.group(1)
                        if not extracted_speed:
                            extracted_speed = m.group(2).upper()
                    dynamic_attrs['load_speed_index'] = raw_load
                    dynamic_attrs['load_index'] = extracted_load
                    dynamic_attrs['tire_load_index'] = extracted_load
                    if extracted_speed:
                        dynamic_attrs['tire_speed_rating'] = extracted_speed

                # Country / Origin normalization
                country_val = dynamic_attrs.get('country') or dynamic_attrs.get('country_of_origin') or dynamic_attrs.get('origin')
                if country_val:
                    dynamic_attrs['origin'] = country_val
                    dynamic_attrs['country'] = country_val
                    dynamic_attrs['country_of_origin'] = country_val

                # Tax class normalization
                tax_val = dynamic_attrs.get('tax_class') or dynamic_attrs.get('tax_class_name') or 'Taxable Goods'
                dynamic_attrs['tax_class'] = tax_val
                dynamic_attrs['tax_class_name'] = tax_val

                # Promotion normalization
                promo_val = dynamic_attrs.get('promotion') or dynamic_attrs.get('offers') or 'None'
                dynamic_attrs['promotion'] = promo_val

                # Boolean flags
                runflat_raw = str(dynamic_attrs.get('runflat') or '').strip().lower()
                run_flat = 1 if runflat_raw in ('yes', '1', 'true') else 0
                ev_raw = str(dynamic_attrs.get('ev_tyre') or '').strip().lower()
                ev_rated = 1 if ev_raw in ('yes', '1', 'true') else 0
                tabby_raw = str(dynamic_attrs.get('tabby_payment') or '').strip().lower()
                pay_later_eligible = 1 if tabby_raw in ('yes', '1', 'true') else 0

                parts_cat = (dynamic_attrs.get('parts_category') or row.get('attribute_set_code') or 'Tyres').strip()
                tyres_cat = dynamic_attrs.get('tyres_category')
                year_val = dynamic_attrs.get('year')
                price_included = (dynamic_attrs.get('price_included_text') or dynamic_attrs.get('price_included') or 'Fitted Price').strip()

                # Build universal product payload
                product_payload = {
                    'sku': sku,
                    'website_id': 1,
                    'website_ids': [1],
                    'item_code': item_code,
                    'parts_category': parts_cat,
                    'tyres_category': tyres_cat,
                    'year': year_val,
                    'price_included': price_included,
                    'small_image': small_image,
                    'small_image_alt': display_name,
                    'display_name': display_name,
                    'name_en': name,
                    'slug': url_key,
                    'attribute_set_id': resolved_set_id,
                    'brand_id': brand_id,
                    'category_id': primary_category_id,
                    'category_ids': assigned_category_ids,
                    'price': price,
                    'cost_price': cost_price,
                    'stock_qty': stock_qty,
                    'stock_status': stock_status,
                    'weight': weight,
                    'run_flat': run_flat,
                    'ev_rated': ev_rated,
                    'pay_later_eligible': pay_later_eligible,
                    'image_path': base_image,
                    'status': status,
                    'visibility': visibility,
                    'short_desc_en': (row.get('short_description') or '').strip(),
                    'description_en': (row.get('description') or '').strip(),
                    'meta_title_en': (row.get('meta_title') or '').strip(),
                    'meta_desc_en': (row.get('meta_description') or '').strip(),
                    'dynamic_attributes': dynamic_attrs,
                    'attributes_json': dynamic_attrs
                }

                # Direct columns for tyre attributes if present
                if dynamic_attrs.get('tire_size'):
                    product_payload['tire_size_label'] = dynamic_attrs['tire_size']
                if extracted_load:
                    product_payload['tire_load_index'] = extracted_load
                if extracted_speed:
                    product_payload['tire_speed_rating'] = extracted_speed
                if dynamic_attrs.get('pattern'):
                    product_payload['tire_pattern'] = dynamic_attrs['pattern']
                if dynamic_attrs.get('tyre_type'):
                    product_payload['tire_type'] = dynamic_attrs['tyre_type']
                if country_val:
                    product_payload['country_of_origin'] = country_val

                # Insert or Update product
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
