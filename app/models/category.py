"""
app/models/category.py - Category Model & Database Operations
Table: categories
"""

import re
from datetime import datetime, timezone
from db import get_connection


from i18n import localize_value, dump_json_dict, parse_json_dict, DEFAULT_LOCALE


class Category:
    @staticmethod
    def slugify(text: str) -> str:
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        return text.strip('-')

    @classmethod
    def _normalize_category_row(cls, r: dict, locale: str = None) -> dict:
        if not r:
            return r
        from services.store_context import StoreContext
        from i18n import get_translated_value
        loc = locale or StoreContext.get_current_language()
        r['name'] = parse_json_dict(r.get('name'))
        r['description'] = parse_json_dict(r.get('description'))
        r['meta_title'] = parse_json_dict(r.get('meta_title'))
        r['meta_desc'] = parse_json_dict(r.get('meta_desc'))
        r['display_name'] = get_translated_value(r['name'], loc)
        # Compatibility aliases for templates / legacy UI
        r['name_en'] = get_translated_value(r['name'], 'en') or r.get('display_name')
        r['name_ar'] = get_translated_value(r['name'], 'ar')
        r['description_en'] = get_translated_value(r['description'], 'en')
        r['description_ar'] = get_translated_value(r['description'], 'ar')
        r['meta_title_en'] = get_translated_value(r['meta_title'], 'en')
        r['meta_title_ar'] = get_translated_value(r['meta_title'], 'ar')
        r['meta_desc_en'] = get_translated_value(r['meta_desc'], 'en')
        r['default_attribute_set_id'] = r.get('default_attribute_set_id')
        r['include_in_menu'] = bool(r.get('include_in_menu', 1)) if r.get('include_in_menu') is not None else True
        r['is_anchor'] = bool(r.get('is_anchor', 1)) if r.get('is_anchor') is not None else True
        r['display_mode'] = r.get('display_mode') or 'PRODUCTS'
        r['use_in_search'] = bool(r.get('use_in_search', 1)) if r.get('use_in_search') is not None else True
        r['display_in_autocomplete'] = bool(r.get('display_in_autocomplete', 1)) if r.get('display_in_autocomplete') is not None else True
        return r

    @classmethod
    def all_active(cls, locale: str = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, slug, parent_id, image, sort_order, status, default_attribute_set_id
                    FROM categories
                    WHERE deleted_at IS NULL AND status = 'active'
                    ORDER BY sort_order ASC, id ASC
                """)
                rows = cursor.fetchall() or []
                return [cls._normalize_category_row(r, locale) for r in rows]
        finally:
            conn.close()

    @classmethod
    def search_and_paginate(cls, query: str = None, status: str = None, parent_id: int = None, page: int = 1, per_page: int = 15, locale: str = None, trash: bool = False):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                is_trash = bool(trash) or (status and str(status).strip().lower() == 'trash')
                if is_trash:
                    where_clauses = ["c.deleted_at IS NOT NULL"]
                else:
                    where_clauses = ["c.deleted_at IS NULL"]
                params = []

                if query and query.strip():
                    term = f"%{query.strip()}%"
                    where_clauses.append("(c.name LIKE %s OR c.slug LIKE %s)")
                    params.extend([term, term])

                if status and status.strip() and status not in ('all', 'trash'):
                    where_clauses.append("c.status = %s")
                    params.append(status.strip())

                if parent_id is not None:
                    where_clauses.append("c.parent_id = %s")
                    params.append(parent_id)

                where_sql = " AND ".join(where_clauses)

                cursor.execute(f"SELECT COUNT(*) AS total FROM categories c WHERE {where_sql}", params)
                total = cursor.fetchone()['total']

                cursor.execute("SELECT COUNT(*) AS trash_count FROM categories WHERE deleted_at IS NOT NULL")
                trash_count = cursor.fetchone().get('trash_count', 0)

                offset = (page - 1) * per_page
                query_params = list(params) + [per_page, offset]

                cursor.execute(f"""
                    SELECT c.*,
                           p_cat.name AS parent_name,
                           (SELECT COUNT(*) FROM products p WHERE p.category_id = c.id AND p.deleted_at IS NULL) AS product_count
                    FROM categories c
                    LEFT JOIN categories p_cat ON c.parent_id = p_cat.id
                    WHERE {where_sql}
                    ORDER BY c.sort_order ASC, c.id ASC
                    LIMIT %s OFFSET %s
                """, query_params)
                items = cursor.fetchall() or []
                normalized_items = []
                for item in items:
                    item = cls._normalize_category_row(item, locale)
                    if item.get('parent_name'):
                        p_name_dict = parse_json_dict(item['parent_name'])
                        item['parent_name'] = localize_value(p_name_dict, locale) or localize_value(p_name_dict, 'en')
                    normalized_items.append(item)

                total_pages = max(1, (total + per_page - 1) // per_page)
                return {
                    'items': normalized_items,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages,
                    'trash_count': trash_count
                }
        finally:
            conn.close()

    @classmethod
    def find_by_id(cls, cat_id: int, locale: str = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*,
                           p_cat.name AS parent_name,
                           (SELECT COUNT(*) FROM products p WHERE p.category_id = c.id AND p.deleted_at IS NULL) AS product_count
                    FROM categories c
                    LEFT JOIN categories p_cat ON c.parent_id = p_cat.id
                    WHERE c.id = %s AND c.deleted_at IS NULL
                """, (cat_id,))
                row = cursor.fetchone()
                if row:
                    row = cls._normalize_category_row(row, locale)
                    if row.get('parent_name'):
                        p_name_dict = parse_json_dict(row['parent_name'])
                        row['parent_name'] = localize_value(p_name_dict, locale) or localize_value(p_name_dict, 'en')
                return row
        finally:
            conn.close()

    @classmethod
    def find_by_slug(cls, slug: str, locale: str = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM categories
                    WHERE slug = %s AND deleted_at IS NULL
                """, (slug,))
                row = cursor.fetchone()
                return cls._normalize_category_row(row, locale) if row else None
        finally:
            conn.close()

    @classmethod
    def create(cls, data: dict, user_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                name_input = data.get('name') or data.get('name_en') or ''
                name_dict = name_input if isinstance(name_input, dict) else parse_json_dict(name_input)
                if not isinstance(name_dict, dict) or not name_dict:
                    name_dict = {DEFAULT_LOCALE: str(name_input).strip()}
                if data.get('name_en'):
                    name_dict['en'] = data['name_en'].strip()
                if data.get('name_ar'):
                    name_dict['ar'] = data['name_ar'].strip()
                name_json = dump_json_dict(name_dict)

                slug_seed = name_dict.get('en') or next(iter(name_dict.values()), '')
                slug = cls.slugify(data.get('slug') or slug_seed)
                parent_id = int(data.get('parent_id')) if data.get('parent_id') else None
                image = data.get('image') or None

                desc_input = data.get('description') or data.get('description_en')
                desc_dict = desc_input if isinstance(desc_input, dict) else parse_json_dict(desc_input)
                if not isinstance(desc_dict, dict) or not desc_dict:
                    desc_dict = {DEFAULT_LOCALE: str(desc_input).strip()} if desc_input else {}
                if data.get('description_en'):
                    desc_dict['en'] = str(data['description_en']).strip()
                if data.get('description_ar'):
                    desc_dict['ar'] = str(data['description_ar']).strip()
                desc_dict = {k: v for k, v in desc_dict.items() if v}
                desc_json = dump_json_dict(desc_dict) if desc_dict else None

                meta_t_input = data.get('meta_title') or data.get('meta_title_en')
                meta_t_dict = meta_t_input if isinstance(meta_t_input, dict) else parse_json_dict(meta_t_input)
                if not isinstance(meta_t_dict, dict) or not meta_t_dict:
                    meta_t_dict = {DEFAULT_LOCALE: str(meta_t_input).strip()} if meta_t_input else {}
                if data.get('meta_title_en'):
                    meta_t_dict['en'] = str(data['meta_title_en']).strip()
                if data.get('meta_title_ar'):
                    meta_t_dict['ar'] = str(data['meta_title_ar']).strip()
                meta_t_dict = {k: v for k, v in meta_t_dict.items() if v}
                meta_t_json = dump_json_dict(meta_t_dict) if meta_t_dict else None

                meta_d_input = data.get('meta_desc') or data.get('meta_desc_en')
                meta_d_dict = meta_d_input if isinstance(meta_d_input, dict) else parse_json_dict(meta_d_input)
                if not isinstance(meta_d_dict, dict) or not meta_d_dict:
                    meta_d_dict = {DEFAULT_LOCALE: str(meta_d_input).strip()} if meta_d_input else {}
                if data.get('meta_desc_en'):
                    meta_d_dict['en'] = str(data['meta_desc_en']).strip()
                if data.get('meta_desc_ar'):
                    meta_d_dict['ar'] = str(data['meta_desc_ar']).strip()
                meta_d_dict = {k: v for k, v in meta_d_dict.items() if v}
                meta_d_json = dump_json_dict(meta_d_dict) if meta_d_dict else None

                sort_order = int(data.get('sort_order') or 0)
                status = data.get('status') or 'active'
                default_attr_set_id = int(data.get('default_attribute_set_id')) if data.get('default_attribute_set_id') else None
                include_in_menu = 1 if data.get('include_in_menu', True) else 0
                is_anchor = 1 if data.get('is_anchor', True) else 0
                display_mode = str(data.get('display_mode') or 'PRODUCTS')
                use_in_search = 1 if data.get('use_in_search', True) else 0
                display_in_autocomplete = 1 if data.get('display_in_autocomplete', True) else 0
                now = datetime.now(timezone.utc)

                cursor.execute("""
                    INSERT INTO categories (
                        name, slug, parent_id, image, description, sort_order,
                        status, meta_title, meta_desc, default_attribute_set_id,
                        include_in_menu, is_anchor, display_mode, use_in_search, display_in_autocomplete,
                        created_by, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name_json, slug, parent_id, image, desc_json, sort_order,
                    status, meta_t_json, meta_d_json, default_attr_set_id,
                    include_in_menu, is_anchor, display_mode, use_in_search, display_in_autocomplete,
                    user_id, now, now
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @classmethod
    def update(cls, cat_id: int, data: dict, user_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM categories WHERE id = %s AND deleted_at IS NULL", (cat_id,))
                existing = cursor.fetchone()
                if not existing:
                    return False

                from services.store_context import StoreContext
                curr_lang = StoreContext.get_current_language()

                name_input = data.get('name') or data.get('name_en')
                if name_input is not None:
                    name_dict = parse_json_dict(existing.get('name')) if existing.get('name') else {}
                    if not isinstance(name_dict, dict):
                        name_dict = {}
                    if isinstance(name_input, dict):
                        name_dict.update(name_input)
                    elif isinstance(name_input, str):
                        s = name_input.strip()
                        if s.startswith('{'):
                            try:
                                p = json.loads(s)
                                if isinstance(p, dict):
                                    name_dict.update(p)
                                else:
                                    name_dict[curr_lang] = s
                            except Exception:
                                name_dict[curr_lang] = s
                        else:
                            name_dict[curr_lang] = s
                    if data.get('name_en'):
                        name_dict['en'] = str(data['name_en']).strip()
                    if data.get('name_ar'):
                        name_dict['ar'] = str(data['name_ar']).strip()
                    name_json = dump_json_dict(name_dict)
                    slug_seed = name_dict.get('en') or next(iter(name_dict.values()), '')
                    slug = cls.slugify(data.get('slug') or slug_seed)
                else:
                    name_json = existing.get('name')
                    slug = data.get('slug') or existing.get('slug')

                parent_id = int(data.get('parent_id')) if data.get('parent_id') else None
                image = data.get('image') if 'image' in data else existing.get('image')

                desc_input = data.get('description') or data.get('description_en')
                if desc_input is not None or 'description' in data or 'description_en' in data or 'description_ar' in data:
                    base_dict = parse_json_dict(existing.get('description')) if existing.get('description') else {}
                    if not isinstance(base_dict, dict):
                        base_dict = {}
                    if desc_input is not None:
                        new_dict = desc_input if isinstance(desc_input, dict) else parse_json_dict(desc_input)
                        if isinstance(new_dict, dict):
                            base_dict.update(new_dict)
                        elif str(desc_input).strip():
                            base_dict[curr_lang] = str(desc_input).strip()
                    if data.get('description_en') is not None:
                        val_en = str(data['description_en']).strip()
                        if val_en:
                            base_dict['en'] = val_en
                        else:
                            base_dict.pop('en', None)
                    if data.get('description_ar') is not None:
                        val_ar = str(data['description_ar']).strip()
                        if val_ar:
                            base_dict['ar'] = val_ar
                        else:
                            base_dict.pop('ar', None)
                    clean_dict = {k: v for k, v in base_dict.items() if v}
                    desc_json = dump_json_dict(clean_dict) if clean_dict else None
                else:
                    desc_json = existing.get('description')

                meta_t_input = data.get('meta_title') or data.get('meta_title_en')
                if meta_t_input is not None or 'meta_title' in data or 'meta_title_en' in data or 'meta_title_ar' in data:
                    base_mt = parse_json_dict(existing.get('meta_title')) if existing.get('meta_title') else {}
                    if not isinstance(base_mt, dict):
                        base_mt = {}
                    if meta_t_input is not None:
                        new_mt = meta_t_input if isinstance(meta_t_input, dict) else parse_json_dict(meta_t_input)
                        if isinstance(new_mt, dict):
                            base_mt.update(new_mt)
                        elif str(meta_t_input).strip():
                            base_mt[curr_lang] = str(meta_t_input).strip()
                    if data.get('meta_title_en') is not None:
                        val = str(data['meta_title_en']).strip()
                        if val:
                            base_mt['en'] = val
                        else:
                            base_mt.pop('en', None)
                    if data.get('meta_title_ar') is not None:
                        val = str(data['meta_title_ar']).strip()
                        if val:
                            base_mt['ar'] = val
                        else:
                            base_mt.pop('ar', None)
                    clean_mt = {k: v for k, v in base_mt.items() if v}
                    meta_t_json = dump_json_dict(clean_mt) if clean_mt else None
                else:
                    meta_t_json = existing.get('meta_title')

                meta_d_input = data.get('meta_desc') or data.get('meta_desc_en')
                if meta_d_input is not None or 'meta_desc' in data or 'meta_desc_en' in data or 'meta_desc_ar' in data:
                    base_md = parse_json_dict(existing.get('meta_desc')) if existing.get('meta_desc') else {}
                    if not isinstance(base_md, dict):
                        base_md = {}
                    if meta_d_input is not None:
                        new_md = meta_d_input if isinstance(meta_d_input, dict) else parse_json_dict(meta_d_input)
                        if isinstance(new_md, dict):
                            base_md.update(new_md)
                        elif str(meta_d_input).strip():
                            base_md[curr_lang] = str(meta_d_input).strip()
                    if data.get('meta_desc_en') is not None:
                        val = str(data['meta_desc_en']).strip()
                        if val:
                            base_md['en'] = val
                        else:
                            base_md.pop('en', None)
                    if data.get('meta_desc_ar') is not None:
                        val = str(data['meta_desc_ar']).strip()
                        if val:
                            base_md['ar'] = val
                        else:
                            base_md.pop('ar', None)
                    clean_md = {k: v for k, v in base_md.items() if v}
                    meta_d_json = dump_json_dict(clean_md) if clean_md else None
                else:
                    meta_d_json = existing.get('meta_desc')

                sort_order = int(data.get('sort_order', existing.get('sort_order') or 0))
                status = data.get('status') or existing.get('status') or 'active'
                if 'default_attribute_set_id' in data:
                    val_as = data.get('default_attribute_set_id')
                    default_attr_set_id = int(val_as) if val_as else None
                else:
                    default_attr_set_id = existing.get('default_attribute_set_id')

                include_in_menu = 1 if data.get('include_in_menu', existing.get('include_in_menu') if existing.get('include_in_menu') is not None else True) else 0
                is_anchor = 1 if data.get('is_anchor', existing.get('is_anchor') if existing.get('is_anchor') is not None else True) else 0
                display_mode = str(data.get('display_mode') or existing.get('display_mode') or 'PRODUCTS')
                use_in_search = 1 if data.get('use_in_search', existing.get('use_in_search') if existing.get('use_in_search') is not None else True) else 0
                display_in_autocomplete = 1 if data.get('display_in_autocomplete', existing.get('display_in_autocomplete') if existing.get('display_in_autocomplete') is not None else True) else 0

                now = datetime.now(timezone.utc)

                cursor.execute("""
                    UPDATE categories SET
                        name = %s,
                        slug = %s,
                        parent_id = %s,
                        image = %s,
                        description = %s,
                        sort_order = %s,
                        status = %s,
                        meta_title = %s,
                        meta_desc = %s,
                        default_attribute_set_id = %s,
                        include_in_menu = %s,
                        is_anchor = %s,
                        display_mode = %s,
                        use_in_search = %s,
                        display_in_autocomplete = %s,
                        updated_by = %s,
                        updated_at = %s
                    WHERE id = %s AND deleted_at IS NULL
                """, (
                    name_json, slug, parent_id, image, desc_json, sort_order,
                    status, meta_t_json, meta_d_json, default_attr_set_id,
                    include_in_menu, is_anchor, display_mode, use_in_search, display_in_autocomplete,
                    user_id, now, cat_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def delete(cls, cat_id: int, user_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                now = datetime.now(timezone.utc)
                cursor.execute("""
                    UPDATE categories SET
                        deleted_at = %s,
                        deleted_by = %s
                    WHERE id = %s AND deleted_at IS NULL
                """, (now, user_id, cat_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def restore(cls, cat_id: int, user_id: int = None):
        """Restores a soft-deleted category back to active."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                now = datetime.now(timezone.utc)
                cursor.execute("""
                    UPDATE categories SET
                        deleted_at = NULL,
                        deleted_by = NULL,
                        updated_by = %s,
                        updated_at = %s
                    WHERE id = %s AND deleted_at IS NOT NULL
                """, (user_id, now, cat_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def purge(cls, cat_id: int):
        """Hard deletes a category permanently from the database."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # Disconnect child categories and products before permanent delete
                cursor.execute("UPDATE categories SET parent_id = NULL WHERE parent_id = %s", (cat_id,))
                cursor.execute("UPDATE products SET category_id = NULL WHERE category_id = %s", (cat_id,))
                cursor.execute("DELETE FROM categories WHERE id = %s", (cat_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def get_category_tree(cls, locale: str = None):
        """Returns the full hierarchical category tree with accurate rolled-up product counts."""
        from collections import defaultdict
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*
                    FROM categories c
                    WHERE c.deleted_at IS NULL
                    ORDER BY c.sort_order ASC, c.id ASC
                """)
                rows = cursor.fetchall() or []
                items = [cls._normalize_category_row(r, locale) for r in rows]

                # Fetch all active product-to-category associations in a single query
                cursor.execute("""
                    SELECT DISTINCT product_id, category_id 
                    FROM (
                        SELECT id AS product_id, category_id FROM products WHERE category_id IS NOT NULL AND deleted_at IS NULL
                        UNION ALL
                        SELECT pc.product_id, pc.category_id 
                        FROM product_categories pc
                        JOIN products p ON p.id = pc.product_id AND p.deleted_at IS NULL
                    ) AS all_pc
                """)
                pc_rows = cursor.fetchall() or []
                direct_prods_by_cat = defaultdict(set)
                for pr in pc_rows:
                    direct_prods_by_cat[pr['category_id']].add(pr['product_id'])

                by_id = {item['id']: {**item, 'children': []} for item in items}
                tree = []
                for item in items:
                    pid = item.get('parent_id')
                    node = by_id[item['id']]
                    if pid and pid in by_id:
                        by_id[pid]['children'].append(node)
                    else:
                        tree.append(node)

                # Recursively calculate rolled-up subtree product counts and assign depths
                def calc_subtree(node, depth=0, path=None):
                    if path is None:
                        path = []
                    curr_path = path + [node['id']]
                    node['depth'] = depth
                    node['path'] = curr_path

                    all_prods = set(direct_prods_by_cat.get(node['id'], set()))
                    node['direct_product_count'] = len(all_prods)

                    for child in node['children']:
                        child_prods = calc_subtree(child, depth + 1, curr_path)
                        all_prods.update(child_prods)

                    node['product_count'] = len(all_prods)
                    node['has_children'] = len(node['children']) > 0
                    return all_prods

                for root_node in tree:
                    calc_subtree(root_node, 0)

                # Pre-order flattened list for recursive arbitrary depth display in UI
                flat_ordered = []
                def flatten_node(node):
                    flat_ordered.append({
                        'id': node['id'],
                        'name': node.get('name_en') or node.get('display_name') or node.get('name') or '',
                        'name_en': node.get('name_en') or node.get('display_name') or '',
                        'slug': node.get('slug'),
                        'parent_id': node.get('parent_id'),
                        'depth': node.get('depth', 0),
                        'product_count': node.get('product_count', 0),
                        'direct_product_count': node.get('direct_product_count', 0),
                        'has_children': node.get('has_children', False),
                        'status': node.get('status', 'active'),
                        'sort_order': node.get('sort_order', 0),
                        'path': node.get('path', []),
                        '_expanded': True
                    })
                    for child in node['children']:
                        flatten_node(child)

                for root_node in tree:
                    flatten_node(root_node)

                return {'tree': tree, 'flat': flat_ordered, 'raw_flat': items}
        finally:
            conn.close()

    @classmethod
    def get_category_products(cls, cat_id: int, search: str = None, assigned: str = 'all', page: int = 1, per_page: int = 20, stock_status: str = None, locale: str = None):
        """Returns products with assignment status and position for a category."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # Total assigned count for category
                cursor.execute("""
                    SELECT COUNT(*) AS assigned_count
                    FROM products p
                    WHERE p.deleted_at IS NULL AND (
                        p.category_id = %s OR EXISTS (
                            SELECT 1 FROM product_categories pc WHERE pc.product_id = p.id AND pc.category_id = %s
                        )
                    )
                """, (cat_id, cat_id))
                assigned_count = cursor.fetchone().get('assigned_count', 0)

                where_clauses = ["p.deleted_at IS NULL"]
                params = {
                    'cat_id': cat_id,
                    'limit': per_page,
                    'offset': (page - 1) * per_page
                }

                if assigned in ('1', 'assigned', 'true'):
                    where_clauses.append("(p.category_id = %(cat_id)s OR EXISTS (SELECT 1 FROM product_categories pc WHERE pc.product_id = p.id AND pc.category_id = %(cat_id)s))")
                elif assigned in ('0', 'unassigned', 'false'):
                    where_clauses.append("NOT (p.category_id = %(cat_id)s OR EXISTS (SELECT 1 FROM product_categories pc WHERE pc.product_id = p.id AND pc.category_id = %(cat_id)s))")

                if search and search.strip():
                    term = f"%{search.strip()}%"
                    params['search_term'] = term
                    where_clauses.append("(p.sku LIKE %(search_term)s OR p.display_name LIKE %(search_term)s OR p.tire_size_label LIKE %(search_term)s OR b.name LIKE %(search_term)s)")

                if stock_status and stock_status in ('in_stock', 'out_of_stock', 'backorder'):
                    params['stock_status'] = stock_status
                    where_clauses.append("p.stock_status = %(stock_status)s")

                where_sql = " AND ".join(where_clauses)

                cursor.execute(f"""
                    SELECT COUNT(*) AS total
                    FROM products p
                    LEFT JOIN brands b ON p.brand_id = b.id
                    WHERE {where_sql}
                """, params)
                total = cursor.fetchone().get('total', 0)

                cursor.execute(f"""
                    SELECT p.id, p.sku, p.item_code, p.display_name, p.name, p.price, p.stock_qty, p.stock_status,
                           p.tire_size_label, p.tire_speed_rating, p.tire_type, p.image_path, p.small_image,
                           b.name AS brand_name,
                           CASE WHEN (p.category_id = %(cat_id)s OR EXISTS (
                               SELECT 1 FROM product_categories pc WHERE pc.product_id = p.id AND pc.category_id = %(cat_id)s
                           )) THEN 1 ELSE 0 END AS is_assigned,
                           COALESCE((
                               SELECT pc.position FROM product_categories pc WHERE pc.product_id = p.id AND pc.category_id = %(cat_id)s LIMIT 1
                           ), 0) AS position
                    FROM products p
                    LEFT JOIN brands b ON p.brand_id = b.id
                    WHERE {where_sql}
                    ORDER BY is_assigned DESC, position ASC, p.id ASC
                    LIMIT %(limit)s OFFSET %(offset)s
                """, params)
                products = cursor.fetchall() or []

                from services.store_context import StoreContext
                from i18n import get_translated_value
                loc = locale or StoreContext.get_current_language()

                for prod in products:
                    name_dict = parse_json_dict(prod.get('name'))
                    prod['name_localized'] = get_translated_value(name_dict, loc) or prod.get('display_name') or ''
                    if prod.get('price') is not None:
                        prod['price_formatted'] = f"{float(prod['price']):.2f}"
                    else:
                        prod['price_formatted'] = '0.00'
                    prod['thumbnail'] = prod.get('small_image') or prod.get('image_path') or '/static/images/placeholder-tyre.png'

                total_pages = max(1, (total + per_page - 1) // per_page)
                return {
                    'products': products,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages,
                    'assigned_count': assigned_count
                }
        finally:
            conn.close()

    @classmethod
    def save_category_products(cls, cat_id: int, assignments: list):
        """Saves product category assignments and positions."""
        if not cat_id:
            return False
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                for item in assignments:
                    pid = int(item['product_id'])
                    assigned = bool(item.get('assigned', True))
                    pos = int(item.get('position', 0))
                    if assigned:
                        cursor.execute("""
                            INSERT INTO product_categories (product_id, category_id, position)
                            VALUES (%s, %s, %s)
                            ON DUPLICATE KEY UPDATE position = VALUES(position)
                        """, (pid, cat_id, pos))
                        cursor.execute("""
                            UPDATE products SET category_id = %s WHERE id = %s AND (category_id IS NULL OR category_id = %s)
                        """, (cat_id, pid, cat_id))
                    else:
                        cursor.execute("""
                            DELETE FROM product_categories WHERE category_id = %s AND product_id = %s
                        """, (cat_id, pid))
                        cursor.execute("""
                            UPDATE products SET category_id = NULL WHERE id = %s AND category_id = %s
                        """, (pid, cat_id))
                conn.commit()
                return True
        finally:
            conn.close()

