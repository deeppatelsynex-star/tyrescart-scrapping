"""
app/models/category.py - Category Model & Database Operations
Table: categories
"""

import re
from datetime import datetime, timezone
from db import get_connection


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
    def all_active(cls):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, name_en, slug, parent_id, image, sort_order, status
                    FROM categories
                    WHERE deleted_at IS NULL AND status = 'active'
                    ORDER BY sort_order ASC, name_en ASC
                """)
                return cursor.fetchall() or []
        finally:
            conn.close()

    @classmethod
    def search_and_paginate(cls, query: str = None, status: str = None, parent_id: int = None, page: int = 1, per_page: int = 15):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                where_clauses = ["c.deleted_at IS NULL"]
                params = []

                if query and query.strip():
                    term = f"%{query.strip()}%"
                    where_clauses.append("(c.name_en LIKE %s OR c.slug LIKE %s)")
                    params.extend([term, term])

                if status and status.strip() and status != 'all':
                    where_clauses.append("c.status = %s")
                    params.append(status.strip())

                if parent_id is not None:
                    where_clauses.append("c.parent_id = %s")
                    params.append(parent_id)

                where_sql = " AND ".join(where_clauses)

                cursor.execute(f"SELECT COUNT(*) AS total FROM categories c WHERE {where_sql}", params)
                total = cursor.fetchone()['total']

                offset = (page - 1) * per_page
                query_params = list(params) + [per_page, offset]

                cursor.execute(f"""
                    SELECT c.*,
                           p_cat.name_en AS parent_name,
                           (SELECT COUNT(*) FROM products p WHERE p.category_id = c.id AND p.deleted_at IS NULL) AS product_count
                    FROM categories c
                    LEFT JOIN categories p_cat ON c.parent_id = p_cat.id
                    WHERE {where_sql}
                    ORDER BY c.sort_order ASC, c.name_en ASC
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
    def find_by_id(cls, cat_id: int):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT c.*,
                           p_cat.name_en AS parent_name,
                           (SELECT COUNT(*) FROM products p WHERE p.category_id = c.id AND p.deleted_at IS NULL) AS product_count
                    FROM categories c
                    LEFT JOIN categories p_cat ON c.parent_id = p_cat.id
                    WHERE c.id = %s AND c.deleted_at IS NULL
                """, (cat_id,))
                return cursor.fetchone()
        finally:
            conn.close()

    @classmethod
    def find_by_slug(cls, slug: str):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM categories
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
                name_en = (data.get('name_en') or data.get('name') or '').strip()
                slug = cls.slugify(data.get('slug') or name_en)
                parent_id = int(data.get('parent_id')) if data.get('parent_id') else None
                image = data.get('image') or None
                description_en = data.get('description_en') or None
                sort_order = int(data.get('sort_order') or 0)
                status = data.get('status') or 'active'
                meta_title_en = data.get('meta_title_en') or None
                meta_desc_en = data.get('meta_desc_en') or None
                now = datetime.now(timezone.utc)

                cursor.execute("""
                    INSERT INTO categories (
                        name_en, slug, parent_id, image, description_en, sort_order,
                        status, meta_title_en, meta_desc_en, created_by, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name_en, slug, parent_id, image, description_en, sort_order,
                    status, meta_title_en, meta_desc_en, user_id, now, now
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
                name_en = (data.get('name_en') or data.get('name') or '').strip()
                slug = cls.slugify(data.get('slug') or name_en)
                parent_id = int(data.get('parent_id')) if data.get('parent_id') else None
                image = data.get('image') or None
                description_en = data.get('description_en') or None
                sort_order = int(data.get('sort_order') or 0)
                status = data.get('status') or 'active'
                meta_title_en = data.get('meta_title_en') or None
                meta_desc_en = data.get('meta_desc_en') or None
                now = datetime.now(timezone.utc)

                cursor.execute("""
                    UPDATE categories SET
                        name_en = %s,
                        slug = %s,
                        parent_id = %s,
                        image = %s,
                        description_en = %s,
                        sort_order = %s,
                        status = %s,
                        meta_title_en = %s,
                        meta_desc_en = %s,
                        updated_by = %s,
                        updated_at = %s
                    WHERE id = %s AND deleted_at IS NULL
                """, (
                    name_en, slug, parent_id, image, description_en, sort_order,
                    status, meta_title_en, meta_desc_en, user_id, now, cat_id
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
