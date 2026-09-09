"""
app/models/brand.py - Brand Model & Database Operations
Table: brands
"""

import re
from datetime import datetime, timezone
from db import get_connection


from i18n import localize_value, dump_json_dict, parse_json_dict


class Brand:
    @staticmethod
    def slugify(text: str) -> str:
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        return text.strip('-')

    @classmethod
    def _normalize_brand_row(cls, r: dict, locale: str = None) -> dict:
        if not r:
            return r
        r['description'] = parse_json_dict(r.get('description'))
        r['meta_title'] = parse_json_dict(r.get('meta_title'))
        r['meta_desc'] = parse_json_dict(r.get('meta_desc'))
        r['description_en'] = localize_value(r['description'], 'en') or localize_value(r['description'], locale)
        r['description_ar'] = localize_value(r['description'], 'ar')
        r['meta_title_en'] = localize_value(r['meta_title'], 'en') or localize_value(r['meta_title'], locale)
        r['meta_desc_en'] = localize_value(r['meta_desc'], 'en') or localize_value(r['meta_desc'], locale)
        return r

    @classmethod
    def all_active(cls, locale: str = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, slug, logo, country, is_featured, sort_order, status
                    FROM brands
                    WHERE deleted_at IS NULL AND status = 'active'
                    ORDER BY sort_order ASC, name ASC
                """)
                rows = cursor.fetchall() or []
                return [cls._normalize_brand_row(r, locale) for r in rows]
        finally:
            conn.close()

    @classmethod
    def search_and_paginate(cls, query: str = None, status: str = None, page: int = 1, per_page: int = 15, locale: str = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                where_clauses = ["b.deleted_at IS NULL"]
                params = []

                if query and query.strip():
                    term = f"%{query.strip()}%"
                    where_clauses.append("(b.name LIKE %s OR b.slug LIKE %s OR b.country LIKE %s)")
                    params.extend([term, term, term])

                if status and status.strip() and status != 'all':
                    where_clauses.append("b.status = %s")
                    params.append(status.strip())

                where_sql = " AND ".join(where_clauses)

                cursor.execute(f"SELECT COUNT(*) AS total FROM brands b WHERE {where_sql}", params)
                total = cursor.fetchone()['total']

                offset = (page - 1) * per_page
                query_params = list(params) + [per_page, offset]

                cursor.execute(f"""
                    SELECT b.*,
                           (SELECT COUNT(*) FROM products p WHERE p.brand_id = b.id AND p.deleted_at IS NULL) AS product_count
                    FROM brands b
                    WHERE {where_sql}
                    ORDER BY b.sort_order ASC, b.name ASC
                    LIMIT %s OFFSET %s
                """, query_params)
                items = cursor.fetchall() or []

                total_pages = max(1, (total + per_page - 1) // per_page)
                return {
                    'items': [cls._normalize_brand_row(it, locale) for it in items],
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages
                }
        finally:
            conn.close()

    @classmethod
    def find_by_id(cls, brand_id: int, locale: str = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT b.*,
                           (SELECT COUNT(*) FROM products p WHERE p.brand_id = b.id AND p.deleted_at IS NULL) AS product_count
                    FROM brands b
                    WHERE b.id = %s AND b.deleted_at IS NULL
                """, (brand_id,))
                row = cursor.fetchone()
                return cls._normalize_brand_row(row, locale) if row else None
        finally:
            conn.close()

    @classmethod
    def find_by_slug(cls, slug: str, locale: str = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM brands
                    WHERE slug = %s AND deleted_at IS NULL
                """, (slug,))
                row = cursor.fetchone()
                return cls._normalize_brand_row(row, locale) if row else None
        finally:
            conn.close()

    @classmethod
    def create(cls, data: dict, user_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                name = (data.get('name') or '').strip()
                slug = cls.slugify(data.get('slug') or name)
                logo = data.get('logo') or None
                country = data.get('country') or None
                sort_order = int(data.get('sort_order') or 0)
                is_featured = 1 if data.get('is_featured') else 0
                status = data.get('status') or 'active'

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

                now = datetime.now(timezone.utc)

                cursor.execute("""
                    INSERT INTO brands (
                        name, slug, logo, description, country, sort_order,
                        is_featured, status, meta_title, meta_desc,
                        created_by, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name, slug, logo, desc_json, country, sort_order,
                    is_featured, status, meta_t_json, meta_d_json,
                    user_id, now, now
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @classmethod
    def update(cls, brand_id: int, data: dict, user_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM brands WHERE id = %s AND deleted_at IS NULL", (brand_id,))
                existing = cursor.fetchone()
                if not existing:
                    return False

                name = (data.get('name') or existing.get('name') or '').strip()
                slug = cls.slugify(data.get('slug') or name)
                logo = data.get('logo') if 'logo' in data else existing.get('logo')
                country = data.get('country') if 'country' in data else existing.get('country')
                sort_order = int(data.get('sort_order', existing.get('sort_order') or 0))
                is_featured = 1 if data.get('is_featured') else (0 if 'is_featured' in data else existing.get('is_featured', 0))
                status = data.get('status') or existing.get('status') or 'active'

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

                now = datetime.now(timezone.utc)

                cursor.execute("""
                    UPDATE brands SET
                        name = %s,
                        slug = %s,
                        logo = %s,
                        description = %s,
                        country = %s,
                        sort_order = %s,
                        is_featured = %s,
                        status = %s,
                        meta_title = %s,
                        meta_desc = %s,
                        updated_by = %s,
                        updated_at = %s
                    WHERE id = %s AND deleted_at IS NULL
                """, (
                    name, slug, logo, desc_json, country, sort_order,
                    is_featured, status, meta_t_json, meta_d_json,
                    user_id, now, brand_id
                ))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def delete(cls, brand_id: int, user_id: int = None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                now = datetime.now(timezone.utc)
                cursor.execute("""
                    UPDATE brands SET
                        deleted_at = %s,
                        deleted_by = %s
                    WHERE id = %s AND deleted_at IS NULL
                """, (now, user_id, brand_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()
