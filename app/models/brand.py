"""
app/models/brand.py - Brand Model & Database Operations
Table: brands
"""

import re
from datetime import datetime, timezone
from db import get_connection


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
    def all_active(cls):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name, slug, logo, country, is_featured, sort_order, status
                    FROM brands
                    WHERE deleted_at IS NULL AND status = 'active'
                    ORDER BY sort_order ASC, name ASC
                """)
                return cursor.fetchall() or []
        finally:
            conn.close()

    @classmethod
    def search_and_paginate(cls, query: str = None, status: str = None, page: int = 1, per_page: int = 15):
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

                # Total count
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
                    'items': items,
                    'total': total,
                    'page': page,
                    'per_page': per_page,
                    'total_pages': total_pages
                }
        finally:
            conn.close()

    @classmethod
    def find_by_id(cls, brand_id: int):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT b.*,
                           (SELECT COUNT(*) FROM products p WHERE p.brand_id = b.id AND p.deleted_at IS NULL) AS product_count
                    FROM brands b
                    WHERE b.id = %s AND b.deleted_at IS NULL
                """, (brand_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @classmethod
    def find_by_slug(cls, slug: str):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM brands
                    WHERE slug = %s AND deleted_at IS NULL
                """, (slug,))
                return cursor.fetchone()
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
                description_en = data.get('description_en') or None
                country = data.get('country') or None
                sort_order = int(data.get('sort_order') or 0)
                is_featured = 1 if data.get('is_featured') else 0
                status = data.get('status') or 'active'
                meta_title_en = data.get('meta_title_en') or None
                meta_desc_en = data.get('meta_desc_en') or None
                now = datetime.now(timezone.utc)

                cursor.execute("""
                    INSERT INTO brands (
                        name, slug, logo, description_en, country, sort_order,
                        is_featured, status, meta_title_en, meta_desc_en,
                        created_by, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name, slug, logo, description_en, country, sort_order,
                    is_featured, status, meta_title_en, meta_desc_en,
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
                name = (data.get('name') or '').strip()
                slug = cls.slugify(data.get('slug') or name)
                logo = data.get('logo') or None
                description_en = data.get('description_en') or None
                country = data.get('country') or None
                sort_order = int(data.get('sort_order') or 0)
                is_featured = 1 if data.get('is_featured') else 0
                status = data.get('status') or 'active'
                meta_title_en = data.get('meta_title_en') or None
                meta_desc_en = data.get('meta_desc_en') or None
                now = datetime.now(timezone.utc)

                cursor.execute("""
                    UPDATE brands SET
                        name = %s,
                        slug = %s,
                        logo = %s,
                        description_en = %s,
                        country = %s,
                        sort_order = %s,
                        is_featured = %s,
                        status = %s,
                        meta_title_en = %s,
                        meta_desc_en = %s,
                        updated_by = %s,
                        updated_at = %s
                    WHERE id = %s AND deleted_at IS NULL
                """, (
                    name, slug, logo, description_en, country, sort_order,
                    is_featured, status, meta_title_en, meta_desc_en,
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
