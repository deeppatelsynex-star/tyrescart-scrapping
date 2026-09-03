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
    def find_by_id(cls, brand_id: int):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM brands
                    WHERE id = %s AND deleted_at IS NULL
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
                now = datetime.now(timezone.utc)

                cursor.execute("""
                    INSERT INTO brands (
                        name, slug, logo, description_en, country, sort_order,
                        is_featured, status, created_by, created_at, updated_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    name, slug, logo, description_en, country, sort_order,
                    is_featured, status, user_id, now, now
                ))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()
