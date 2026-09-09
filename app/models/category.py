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
        r['name'] = parse_json_dict(r.get('name'))
        r['description'] = parse_json_dict(r.get('description'))
        r['meta_title'] = parse_json_dict(r.get('meta_title'))
        r['meta_desc'] = parse_json_dict(r.get('meta_desc'))
        r['display_name'] = localize_value(r['name'], locale)
        # Compatibility aliases for templates / legacy UI
        r['name_en'] = localize_value(r['name'], 'en') or r.get('display_name')
        r['name_ar'] = localize_value(r['name'], 'ar')
        r['description_en'] = localize_value(r['description'], 'en')
        r['description_ar'] = localize_value(r['description'], 'ar')
        r['meta_title_en'] = localize_value(r['meta_title'], 'en')
        r['meta_desc_en'] = localize_value(r['meta_desc'], 'en')
        return r

    @classmethod
    def all_active(cls, locale: str = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, slug, parent_id, image, sort_order, status
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
                meta_t_json = dump_json_dict(meta_t_input) if meta_t_input else None

                meta_d_input = data.get('meta_desc') or data.get('meta_desc_en')
                meta_d_json = dump_json_dict(meta_d_input) if meta_d_input else None

                sort_order = int(data.get('sort_order') or 0)
                status = data.get('status') or 'active'
                now = datetime.now(timezone.utc)

                cursor.execute("""
                    INSERT INTO categories (
                        name, slug, parent_id, image, description, sort_order,
                        status, meta_title, meta_desc, created_by, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name_json, slug, parent_id, image, desc_json, sort_order,
                    status, meta_t_json, meta_d_json, user_id, now, now
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

                name_input = data.get('name') or data.get('name_en')
                if name_input:
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
                            base_dict[DEFAULT_LOCALE] = str(desc_input).strip()
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
                meta_t_json = dump_json_dict(meta_t_input) if meta_t_input else existing.get('meta_title')

                meta_d_input = data.get('meta_desc') or data.get('meta_desc_en')
                meta_d_json = dump_json_dict(meta_d_input) if meta_d_input else existing.get('meta_desc')

                sort_order = int(data.get('sort_order', existing.get('sort_order') or 0))
                status = data.get('status') or existing.get('status') or 'active'
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
                        updated_by = %s,
                        updated_at = %s
                    WHERE id = %s AND deleted_at IS NULL
                """, (
                    name_json, slug, parent_id, image, desc_json, sort_order,
                    status, meta_t_json, meta_d_json, user_id, now, cat_id
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
