"""
app/models/product.py - Product Model & ORM Helpers
Table: products
Phase 2.1 & 3.1 & 6.4 Catalog Product Implementation
"""

import json
import re
from datetime import datetime, timezone
from decimal import Decimal
from db import get_connection


class Product:
    @staticmethod
    def slugify(text: str) -> str:
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        return text.strip('-')

    @staticmethod
    def _parse_json_field(val):
        if val is None:
            return None
        if isinstance(val, (dict, list)):
            return val
        if isinstance(val, str):
            val_str = val.strip()
            if (val_str.startswith('{') and val_str.endswith('}')) or (val_str.startswith('[') and val_str.endswith(']')):
                try:
                    return json.loads(val_str)
                except Exception:
                    pass
        return val

    @classmethod
    def to_dict(cls, row):
        if not row:
            return None
        d = dict(row)
        # Parse JSON fields safely
        for k in ['name', 'description', 'short_desc', 'meta_title', 'meta_desc', 'gallery_json', 'make_ids', 'price_included', 'attributes_json']:
            if k in d:
                d[k] = cls._parse_json_field(d[k])

        # Resolve display name string
        if isinstance(d.get('name'), dict):
            d['name_en'] = d['name'].get('en') or d.get('display_name') or ''
        elif isinstance(d.get('name'), str):
            d['name_en'] = d['name']
        else:
            d['name_en'] = d.get('display_name') or ''

        # Decimal / Float conversions for JSON serialization
        for k in ['price', 'list_price', 'sale_price', 'cost_price', 'weight']:
            if k in d and d[k] is not None:
                d[k] = float(d[k])

        # Date / Timestamp formatting
        for k in ['created_at', 'updated_at', 'deleted_at', 'sale_start_date', 'sale_end_date']:
            if k in d and d[k] is not None:
                d[k] = d[k].isoformat() if hasattr(d[k], 'isoformat') else str(d[k])

        return d

    @classmethod
    def get_counts(cls):
        """Returns statistics for product metrics cards."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT
                        COUNT(CASE WHEN deleted_at IS NULL THEN 1 END) as total_active,
                        COUNT(CASE WHEN deleted_at IS NULL AND stock_status = 'in_stock' THEN 1 END) as in_stock,
                        COUNT(CASE WHEN deleted_at IS NULL AND stock_status = 'out_of_stock' THEN 1 END) as out_of_stock,
                        COUNT(CASE WHEN deleted_at IS NULL AND status = 'inactive' THEN 1 END) as inactive,
                        COUNT(CASE WHEN deleted_at IS NOT NULL THEN 1 END) as trash_count
                    FROM products
                """)
                row = cursor.fetchone() or {}
                return {
                    'total': row.get('total_active', 0),
                    'in_stock': row.get('in_stock', 0),
                    'out_of_stock': row.get('out_of_stock', 0),
                    'inactive': row.get('inactive', 0),
                    'trash': row.get('trash_count', 0),
                }
        finally:
            conn.close()

    @classmethod
    def paginate(cls, page: int = 1, per_page: int = 25, search: str = None,
                 brand_id: int = None, category_id: int = None, status: str = None,
                 stock_status: str = None, vehicle_type: str = None, is_trash: bool = False,
                 sort_by: str = 'created_at', sort_dir: str = 'DESC'):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                where_clauses = []
                params = []

                if is_trash:
                    where_clauses.append("p.deleted_at IS NOT NULL")
                else:
                    where_clauses.append("p.deleted_at IS NULL")

                if search:
                    s = f"%{search.strip()}%"
                    where_clauses.append("(p.sku LIKE %s OR p.display_name LIKE %s OR p.tire_size_label LIKE %s OR p.slug LIKE %s)")
                    params.extend([s, s, s, s])

                if brand_id:
                    where_clauses.append("p.brand_id = %s")
                    params.append(brand_id)

                if category_id:
                    where_clauses.append("p.category_id = %s")
                    params.append(category_id)

                if status:
                    where_clauses.append("p.status = %s")
                    params.append(status)

                if stock_status:
                    where_clauses.append("p.stock_status = %s")
                    params.append(stock_status)

                if vehicle_type:
                    where_clauses.append("p.vehicle_type = %s")
                    params.append(vehicle_type)

                where_sql = " AND ".join(where_clauses)
                if where_sql:
                    where_sql = "WHERE " + where_sql

                # Allowed sort columns
                allowed_sorts = {
                    'id': 'p.id',
                    'sku': 'p.sku',
                    'display_name': 'p.display_name',
                    'price': 'p.price',
                    'stock_qty': 'p.stock_qty',
                    'created_at': 'p.created_at',
                    'status': 'p.status'
                }
                order_col = allowed_sorts.get(sort_by, 'p.id')
                direction = 'ASC' if str(sort_dir).upper() == 'ASC' else 'DESC'

                # Total count
                count_sql = f"SELECT COUNT(*) as cnt FROM products p {where_sql}"
                cursor.execute(count_sql, tuple(params))
                total_items = cursor.fetchone()['cnt']

                # Paginated items with brand and category names joined
                offset = max(0, (page - 1) * per_page)
                items_sql = f"""
                    SELECT p.*,
                           b.name as brand_name,
                           b.logo as brand_logo,
                           c.name_en as category_name
                    FROM products p
                    LEFT JOIN brands b ON b.id = p.brand_id
                    LEFT JOIN categories c ON c.id = p.category_id
                    {where_sql}
                    ORDER BY {order_col} {direction}
                    LIMIT %s OFFSET %s
                """
                page_params = list(params) + [per_page, offset]
                cursor.execute(items_sql, tuple(page_params))
                rows = cursor.fetchall() or []

                total_pages = max(1, (total_items + per_page - 1) // per_page)
                return {
                    'items': [cls.to_dict(r) for r in rows],
                    'total': total_items,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages,
                    'has_prev': page > 1,
                    'has_next': page < total_pages
                }
        finally:
            conn.close()

    @classmethod
    def find_by_id(cls, product_id: int, include_trash: bool = False):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT p.*,
                           b.name as brand_name,
                           b.logo as brand_logo,
                           c.name_en as category_name
                    FROM products p
                    LEFT JOIN brands b ON b.id = p.brand_id
                    LEFT JOIN categories c ON c.id = p.category_id
                    WHERE p.id = %s
                """
                if not include_trash:
                    sql += " AND p.deleted_at IS NULL"
                cursor.execute(sql, (product_id,))
                row = cursor.fetchone()
                return cls.to_dict(row) if row else None
        finally:
            conn.close()

    @classmethod
    def find_by_sku(cls, sku: str, exclude_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT id, sku FROM products WHERE sku = %s"
                params = [sku.strip()]
                if exclude_id:
                    sql += " AND id != %s"
                    params.append(exclude_id)
                cursor.execute(sql, tuple(params))
                return cursor.fetchone()
        finally:
            conn.close()

    @classmethod
    def find_by_slug(cls, slug: str, exclude_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT id, slug FROM products WHERE slug = %s"
                params = [slug.strip()]
                if exclude_id:
                    sql += " AND id != %s"
                    params.append(exclude_id)
                cursor.execute(sql, tuple(params))
                return cursor.fetchone()
        finally:
            conn.close()

    @classmethod
    def create(cls, data: dict, user_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sku = str(data.get('sku') or '').strip().upper()
                name_val = data.get('name') or data.get('name_en') or data.get('display_name') or ''
                if isinstance(name_val, dict):
                    name_json = name_val
                    display_name = name_val.get('en') or ''
                else:
                    name_str = str(name_val).strip()
                    name_json = {'en': name_str, 'ar': name_str}
                    display_name = name_str

                slug_candidate = data.get('slug') or display_name or sku
                slug = cls.slugify(slug_candidate)

                # Ensure slug uniqueness
                base_slug = slug
                counter = 1
                while cls.find_by_slug(slug):
                    slug = f"{base_slug}-{counter}"
                    counter += 1

                # Pricing
                price = Decimal(str(data.get('price') or 0))
                list_price = Decimal(str(data['list_price'])) if data.get('list_price') else None
                sale_price = Decimal(str(data['sale_price'])) if data.get('sale_price') else None
                cost_price = Decimal(str(data['cost_price'])) if data.get('cost_price') else None

                # Inventory
                stock_qty = int(data.get('stock_qty') or 0)
                stock_status = data.get('stock_status') or ('in_stock' if stock_qty > 0 else 'out_of_stock')
                manage_stock = 1 if data.get('manage_stock', True) else 0
                min_order_qty = int(data.get('min_order_qty') or 1)
                max_order_qty = int(data.get('max_order_qty') or 99)

                # Tyre size label auto-formatting if width/aspect/rim given
                tire_size_label = (data.get('tire_size_label') or '').strip()
                if not tire_size_label and data.get('width') and data.get('aspect_ratio') and data.get('rim_size'):
                    tire_size_label = f"{data.get('width')}/{data.get('aspect_ratio')}R{data.get('rim_size')}"

                tire_speed_rating = (data.get('tire_speed_rating') or '').strip() or None
                tire_load_index = (data.get('tire_load_index') or '').strip() or None
                tire_type = data.get('tire_type') or 'summer'
                tire_pattern = (data.get('tire_pattern') or '').strip() or None
                run_flat = 1 if data.get('run_flat') else 0
                ev_rated = 1 if data.get('ev_rated') else 0
                oem_approved = 1 if data.get('oem_approved') else 0
                oem_brand = (data.get('oem_brand') or '').strip() or None
                vehicle_type = data.get('vehicle_type') or 'car'

                brand_id = int(data['brand_id']) if data.get('brand_id') else None
                category_id = int(data['category_id']) if data.get('category_id') else None

                image_path = (data.get('image_path') or '').strip() or None
                image_alt = (data.get('image_alt') or display_name).strip() or None
                gallery_json = json.dumps(data.get('gallery_json') or [])

                description = json.dumps(data.get('description') or {'en': data.get('description_en', ''), 'ar': ''})
                short_desc = json.dumps(data.get('short_desc') or {'en': data.get('short_desc_en', ''), 'ar': ''})

                weight = Decimal(str(data['weight'])) if data.get('weight') else None
                country_of_origin = (data.get('country_of_origin') or '').strip() or None
                warranty_months = int(data['warranty_months']) if data.get('warranty_months') else None
                is_featured = 1 if data.get('is_featured') else 0
                is_new = 1 if data.get('is_new') else 0
                sort_order = int(data.get('sort_order') or 0)
                status = data.get('status') or 'active'
                visibility = data.get('visibility') or 'visible'
                pay_later_eligible = 1 if data.get('pay_later_eligible', True) else 0

                meta_title = json.dumps(data.get('meta_title') or {'en': data.get('meta_title_en', display_name), 'ar': ''})
                meta_desc = json.dumps(data.get('meta_desc') or {'en': data.get('meta_desc_en', ''), 'ar': ''})
                canonical_url = (data.get('canonical_url') or '').strip() or None

                now = datetime.now(timezone.utc)

                cursor.execute("""
                    INSERT INTO products (
                        sku, display_name, slug, name, description, short_desc,
                        price, list_price, sale_price, cost_price, currency,
                        stock_qty, stock_status, manage_stock, min_order_qty, max_order_qty,
                        tire_size_label, tire_speed_rating, tire_load_index, tire_type, tire_pattern,
                        run_flat, ev_rated, oem_approved, oem_brand, vehicle_type,
                        brand_id, category_id, image_path, image_alt, gallery_json,
                        weight, country_of_origin, warranty_months,
                        is_featured, is_new, sort_order, status, visibility, pay_later_eligible,
                        canonical_url, meta_title, meta_desc,
                        created_by, created_at, updated_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, %s,
                        %s, %s, %s
                    )
                """, (
                    sku, display_name, slug, json.dumps(name_json), description, short_desc,
                    price, list_price, sale_price, cost_price, 'AED',
                    stock_qty, stock_status, manage_stock, min_order_qty, max_order_qty,
                    tire_size_label, tire_speed_rating, tire_load_index, tire_type, tire_pattern,
                    run_flat, ev_rated, oem_approved, oem_brand, vehicle_type,
                    brand_id, category_id, image_path, image_alt, gallery_json,
                    weight, country_of_origin, warranty_months,
                    is_featured, is_new, sort_order, status, visibility, pay_later_eligible,
                    canonical_url, meta_title, meta_desc,
                    user_id, now, now
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @classmethod
    def update(cls, product_id: int, data: dict, user_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # Check existing
                cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                existing = cursor.fetchone()
                if not existing:
                    return False

                fields = []
                params = []

                if 'sku' in data:
                    fields.append("sku = %s")
                    params.append(str(data['sku']).strip().upper())

                if 'display_name' in data or 'name_en' in data or 'name' in data:
                    name_val = data.get('name') or data.get('name_en') or data.get('display_name')
                    if isinstance(name_val, dict):
                        display_name = name_val.get('en') or ''
                        name_json = name_val
                    else:
                        display_name = str(name_val).strip()
                        name_json = {'en': display_name, 'ar': display_name}
                    fields.extend(["display_name = %s", "name = %s"])
                    params.extend([display_name, json.dumps(name_json)])

                if 'slug' in data and data['slug']:
                    clean_slug = cls.slugify(data['slug'])
                    fields.append("slug = %s")
                    params.append(clean_slug)

                for price_col in ['price', 'list_price', 'sale_price', 'cost_price']:
                    if price_col in data:
                        val = Decimal(str(data[price_col])) if data[price_col] is not None and str(data[price_col]).strip() != '' else None
                        fields.append(f"{price_col} = %s")
                        params.append(val)

                if 'stock_qty' in data:
                    sq = int(data['stock_qty'] or 0)
                    fields.append("stock_qty = %s")
                    params.append(sq)
                    if 'stock_status' not in data:
                        fields.append("stock_status = %s")
                        params.append('in_stock' if sq > 0 else 'out_of_stock')

                if 'stock_status' in data:
                    fields.append("stock_status = %s")
                    params.append(data['stock_status'])

                if 'tire_size_label' in data:
                    fields.append("tire_size_label = %s")
                    params.append(data['tire_size_label'])

                for spec_col in ['tire_speed_rating', 'tire_load_index', 'tire_type', 'tire_pattern',
                                 'vehicle_type', 'oem_brand', 'country_of_origin']:
                    if spec_col in data:
                        fields.append(f"{spec_col} = %s")
                        params.append(data[spec_col] or None)

                for bool_col in ['run_flat', 'ev_rated', 'oem_approved', 'is_featured', 'is_new', 'manage_stock', 'pay_later_eligible']:
                    if bool_col in data:
                        fields.append(f"{bool_col} = %s")
                        params.append(1 if data[bool_col] else 0)

                for fk_col in ['brand_id', 'category_id', 'warranty_months', 'sort_order', 'min_order_qty', 'max_order_qty']:
                    if fk_col in data:
                        val = int(data[fk_col]) if data[fk_col] is not None and str(data[fk_col]).strip() != '' else None
                        fields.append(f"{fk_col} = %s")
                        params.append(val)

                for str_col in ['image_path', 'image_alt', 'status', 'visibility', 'canonical_url']:
                    if str_col in data:
                        fields.append(f"{str_col} = %s")
                        params.append(data[str_col] or None)

                if 'gallery_json' in data:
                    fields.append("gallery_json = %s")
                    params.append(json.dumps(data['gallery_json'] or []))

                if 'description' in data:
                    fields.append("description = %s")
                    params.append(json.dumps(data['description'] or {}))

                if 'short_desc' in data:
                    fields.append("short_desc = %s")
                    params.append(json.dumps(data['short_desc'] or {}))

                if 'meta_title' in data:
                    fields.append("meta_title = %s")
                    params.append(json.dumps(data['meta_title'] or {}))

                if 'meta_desc' in data:
                    fields.append("meta_desc = %s")
                    params.append(json.dumps(data['meta_desc'] or {}))

                now = datetime.now(timezone.utc)
                fields.extend(["updated_by = %s", "updated_at = %s"])
                params.extend([user_id, now])

                sql = f"UPDATE products SET {', '.join(fields)} WHERE id = %s"
                params.append(product_id)

                cursor.execute(sql, tuple(params))
                conn.commit()
                return True
        finally:
            conn.close()

    @classmethod
    def soft_delete(cls, product_id: int, user_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                now = datetime.now(timezone.utc)
                cursor.execute("""
                    UPDATE products
                    SET deleted_at = %s, deleted_by = %s
                    WHERE id = %s AND deleted_at IS NULL
                """, (now, user_id, product_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def restore(cls, product_id: int, user_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                now = datetime.now(timezone.utc)
                cursor.execute("""
                    UPDATE products
                    SET deleted_at = NULL, deleted_by = NULL, updated_at = %s, updated_by = %s
                    WHERE id = %s AND deleted_at IS NOT NULL
                """, (now, user_id, product_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def purge(cls, product_id: int):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def bulk_action(cls, action: str, ids: list, user_id: int = None):
        if not ids:
            return 0
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                now = datetime.now(timezone.utc)
                placeholders = ', '.join(['%s'] * len(ids))
                if action == 'delete':
                    sql = f"UPDATE products SET deleted_at = %s, deleted_by = %s WHERE id IN ({placeholders}) AND deleted_at IS NULL"
                    cursor.execute(sql, [now, user_id] + ids)
                elif action == 'restore':
                    sql = f"UPDATE products SET deleted_at = NULL, deleted_by = NULL, updated_at = %s WHERE id IN ({placeholders}) AND deleted_at IS NOT NULL"
                    cursor.execute(sql, [now] + ids)
                elif action == 'in_stock':
                    sql = f"UPDATE products SET stock_status = 'in_stock', updated_at = %s WHERE id IN ({placeholders})"
                    cursor.execute(sql, [now] + ids)
                elif action == 'out_of_stock':
                    sql = f"UPDATE products SET stock_status = 'out_of_stock', updated_at = %s WHERE id IN ({placeholders})"
                    cursor.execute(sql, [now] + ids)
                elif action == 'active':
                    sql = f"UPDATE products SET status = 'active', updated_at = %s WHERE id IN ({placeholders})"
                    cursor.execute(sql, [now] + ids)
                elif action == 'inactive':
                    sql = f"UPDATE products SET status = 'inactive', updated_at = %s WHERE id IN ({placeholders})"
                    cursor.execute(sql, [now] + ids)
                conn.commit()
                return cursor.rowcount
        finally:
            conn.close()
