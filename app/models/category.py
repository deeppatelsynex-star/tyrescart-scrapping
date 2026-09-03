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
    def find_by_id(cls, cat_id: int):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM categories
                    WHERE id = %s AND deleted_at IS NULL
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
                parent_id = data.get('parent_id') or None
                image = data.get('image') or None
                description_en = data.get('description_en') or None
                sort_order = int(data.get('sort_order') or 0)
                status = data.get('status') or 'active'
                now = datetime.now(timezone.utc)

                cursor.execute("""
                    INSERT INTO categories (
                        name_en, slug, parent_id, image, description_en, sort_order,
                        status, created_by, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name_en, slug, parent_id, image, description_en, sort_order,
                    status, user_id, now, now
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()
