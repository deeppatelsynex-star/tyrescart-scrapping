"""
app/models/blog.py - Blog Model & ORM Layer
Table: blogs
Schema:
  - id: bigint UNSIGNED PRIMARY KEY AUTO_INCREMENT
  - title: json NOT NULL
  - slug: varchar(255) NOT NULL UNIQUE
  - content: json NOT NULL
  - short_description: json DEFAULT NULL
  - image: varchar(255) DEFAULT NULL
  - blog_category_id: bigint UNSIGNED DEFAULT NULL
  - author_id: bigint UNSIGNED DEFAULT NULL
  - status: enum('draft','published','archived') NOT NULL DEFAULT 'draft'
  - published_at: timestamp NULL DEFAULT NULL
  - meta_title: json DEFAULT NULL
  - meta_desc: json DEFAULT NULL
  - created_at: timestamp NULL DEFAULT CURRENT_TIMESTAMP
  - updated_at: timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
  - deleted_at: timestamp NULL DEFAULT NULL
  - created_by: bigint UNSIGNED DEFAULT NULL
  - updated_by: bigint UNSIGNED DEFAULT NULL
"""

import json
import re
from datetime import datetime, timezone
from db import get_connection


# ============================================================================
# MIXINS
# ============================================================================

class SlugMixin:
    """Provides slug generation, normalization, and uniqueness checking."""
    
    @staticmethod
    def slugify(text: str) -> str:
        """Converts a raw string into a clean URL slug."""
        if not text:
            return ""
        text = text.lower().strip()
        text = re.sub(r'[^\w\s-]', '', text)
        text = re.sub(r'[\s_-]+', '-', text)
        return text.strip('-')

    @classmethod
    def is_slug_available(cls, slug: str, exclude_id: int = None) -> bool:
        """Checks if a given slug is unique in the blogs table."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT id FROM blogs WHERE slug = %s"
                params = [slug]
                if exclude_id:
                    sql += " AND id != %s"
                    params.append(exclude_id)
                cursor.execute(sql, tuple(params))
                return cursor.fetchone() is None
        finally:
            conn.close()


class SoftDeleteMixin:
    """Provides soft-delete capabilities and unique slug collision handling."""

    @classmethod
    def soft_delete(cls, blog_id: int) -> bool:
        """Marks a blog as deleted and prefixes slug to free it for reuse."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT slug FROM blogs WHERE id = %s AND deleted_at IS NULL", (blog_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                old_slug = row.get('slug') or ''
                ts = int(datetime.now(timezone.utc).timestamp())
                new_slug = f"__del_{blog_id}_{ts}_{old_slug}"[:250]
                cursor.execute(
                    "UPDATE blogs SET deleted_at = CURRENT_TIMESTAMP, slug = %s WHERE id = %s",
                    (new_slug, blog_id)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def restore(cls, blog_id: int) -> bool:
        """Restores a soft-deleted blog, reclaiming original slug if available."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT slug FROM blogs WHERE id = %s AND deleted_at IS NOT NULL", (blog_id,))
                row = cursor.fetchone()
                if not row:
                    return False
                cur_slug = row.get('slug') or ''
                clean_slug = re.sub(r'^__del_\d+_\d+_', '', cur_slug)
                target_slug = clean_slug

                cursor.execute("SELECT id FROM blogs WHERE slug = %s AND id != %s", (target_slug, blog_id))
                if cursor.fetchone() is not None:
                    target_slug = f"{clean_slug}-restored-{blog_id}"

                cursor.execute(
                    "UPDATE blogs SET deleted_at = NULL, slug = %s WHERE id = %s",
                    (target_slug, blog_id)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def hard_delete(cls, blog_id: int) -> bool:
        """Permanently deletes a blog record from the MySQL database."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM blogs WHERE id = %s", (blog_id,))
                return cursor.rowcount > 0
        finally:
            conn.close()


class SearchableMixin:
    """Provides fulltext/JSON search across title, short_description, and content."""

    @classmethod
    def search(cls, query: str, locale: str = 'en', limit: int = 20):
        """Searches active published blogs by title or content snippet."""
        if not query:
            return []
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                term = f"%{query.strip()}%"
                sql = """
                    SELECT * FROM blogs 
                    WHERE deleted_at IS NULL 
                      AND status = 'published'
                      AND (
                        JSON_UNQUOTE(JSON_EXTRACT(title, %s)) LIKE %s
                        OR JSON_UNQUOTE(JSON_EXTRACT(content, %s)) LIKE %s
                        OR JSON_UNQUOTE(JSON_EXTRACT(short_description, %s)) LIKE %s
                      )
                    ORDER BY published_at DESC, id DESC
                    LIMIT %s
                """
                loc_key = f"$.{locale}"
                cursor.execute(sql, (loc_key, term, loc_key, term, loc_key, term, limit))
                rows = cursor.fetchall()
                return [cls(r) for r in rows]
        finally:
            conn.close()


# ============================================================================
# BLOG MODEL
# ============================================================================

class Blog(SlugMixin, SoftDeleteMixin, SearchableMixin):
    """
    Blog ORM model for managing articles, posts, and announcements.
    Supports localized JSON payloads for title, content, short_description, meta_title, and meta_desc.
    """

    TABLE = 'blogs'
    COLUMNS = (
        'id', 'title', 'slug', 'content', 'short_description', 'image',
        'category_name', 'blog_category_id', 'author_id', 'status', 'published_at',
        'meta_title', 'meta_desc', 'created_at', 'updated_at', 'deleted_at',
        'created_by', 'updated_by'
    )

    VALID_STATUSES = ('draft', 'published', 'archived')

    def __init__(self, data: dict):
        self.id = data.get('id')
        self.title = self._parse_json(data.get('title'))
        
        # Display clean slug for soft-deleted items
        raw_slug = data.get('slug') or ''
        self.raw_slug = raw_slug
        self.slug = re.sub(r'^__del_\d+_\d+_', '', raw_slug)

        self.content = self._parse_json(data.get('content'))
        self.short_description = self._parse_json(data.get('short_description'))
        self.image = data.get('image')
        self.category_name = data.get('category_name') or ''
        self.blog_category_id = data.get('blog_category_id')
        self.author_id = data.get('author_id')
        self.status = data.get('status') or 'draft'
        self.published_at = data.get('published_at')
        self.meta_title = self._parse_json(data.get('meta_title'))
        self.meta_desc = self._parse_json(data.get('meta_desc'))
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.deleted_at = data.get('deleted_at')
        self.created_by = data.get('created_by')
        self.updated_by = data.get('updated_by')

    @staticmethod
    def _parse_json(val):
        if val is None:
            return {}
        if isinstance(val, (dict, list)):
            return val
        if isinstance(val, str):
            val_str = val.strip()
            if val_str.startswith('{') or val_str.startswith('['):
                try:
                    res = json.loads(val_str)
                    return res if isinstance(res, (dict, list)) else {'en': str(res)}
                except Exception:
                    pass
            return {'en': val}
        return {'en': str(val)}

    @staticmethod
    def _dump_json(val):
        if val is None:
            return None
        if isinstance(val, (dict, list)):
            return json.dumps(val, ensure_ascii=False)
        if isinstance(val, str):
            val_strip = val.strip()
            if val_strip.startswith('{') or val_strip.startswith('['):
                try:
                    json.loads(val_strip)
                    return val_strip
                except Exception:
                    pass
            return json.dumps({'en': val}, ensure_ascii=False)
        return json.dumps(val, ensure_ascii=False)

    # -------------------------------------------------------------------------
    # Localized Property Accessors
    # -------------------------------------------------------------------------
    def get_title(self, locale: str = 'en') -> str:
        """Returns the localized title string."""
        if isinstance(self.title, dict):
            return self.title.get(locale) or self.title.get('en') or next(iter(self.title.values()), "")
        return str(self.title or "")

    def get_content(self, locale: str = 'en') -> str:
        """Returns the localized HTML body content."""
        if isinstance(self.content, dict):
            return self.content.get(locale) or self.content.get('en') or next(iter(self.content.values()), "")
        return str(self.content or "")

    def get_short_desc(self, locale: str = 'en') -> str:
        """Returns the localized short summary description."""
        if isinstance(self.short_description, dict):
            return self.short_description.get(locale) or self.short_description.get('en') or ""
        return str(self.short_description or "")

    def get_meta_title(self, locale: str = 'en') -> str:
        """Returns the localized meta title (fallback to title)."""
        if isinstance(self.meta_title, dict) and self.meta_title.get(locale):
            return self.meta_title.get(locale)
        return self.get_title(locale)

    def get_meta_desc(self, locale: str = 'en') -> str:
        """Returns the localized meta description (fallback to short_description)."""
        if isinstance(self.meta_desc, dict) and self.meta_desc.get(locale):
            return self.meta_desc.get(locale)
        return self.get_short_desc(locale)

    @property
    def is_published(self) -> bool:
        """Checks if blog post is published and not deleted."""
        return self.status == 'published' and self.deleted_at is None

    def to_dict(self, locale: str = None) -> dict:
        """Serializes blog record for API responses or template rendering."""
        base = {
            'id': self.id,
            'slug': self.slug,
            'image': self.image,
            'category_name': self.category_name or '',
            'blog_category_id': self.blog_category_id,
            'author_id': self.author_id,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'created_by': self.created_by,
            'updated_by': self.updated_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'deleted_at': self.deleted_at.isoformat() if self.deleted_at else None,
        }
        if locale:
            base.update({
                'title': self.get_title(locale),
                'content': self.get_content(locale),
                'short_description': self.get_short_desc(locale),
                'meta_title': self.get_meta_title(locale),
                'meta_desc': self.get_meta_desc(locale),
            })
        else:
            base.update({
                'title': self.title,
                'content': self.content,
                'short_description': self.short_description,
                'meta_title': self.meta_title,
                'meta_desc': self.meta_desc,
            })
        return base

    # -------------------------------------------------------------------------
    # Query Helpers
    # -------------------------------------------------------------------------
    @classmethod
    def distinct_categories(cls) -> list:
        """Returns distinct category names currently stored in blogs table."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT category_name 
                    FROM blogs 
                    WHERE category_name IS NOT NULL 
                      AND category_name != '' 
                      AND deleted_at IS NULL
                    ORDER BY category_name ASC
                """)
                rows = cursor.fetchall()
                found = [r['category_name'].strip() for r in rows if r.get('category_name') and r['category_name'].strip()]
                # Pre-populate sensible defaults if table has few
                defaults = ['Tyre Buying Guide', 'Tyre Maintenance', 'Mobile Tyre Fitting', 'Wheel Alignment', 'GCC Specifications', 'Car Battery & Service']
                combined = []
                for cat in found + defaults:
                    if cat not in combined:
                        combined.append(cat)
                return combined
        finally:
            conn.close()
    @classmethod
    def all(cls, include_deleted: bool = False, status: str = None):
        """Returns all blogs with optional status/trash filtering."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM blogs WHERE 1=1"
                params = []
                if not include_deleted:
                    sql += " AND deleted_at IS NULL"
                if status:
                    sql += " AND status = %s"
                    params.append(status)
                sql += " ORDER BY id DESC"
                cursor.execute(sql, tuple(params))
                return [cls(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @classmethod
    def published(cls, limit: int = None):
        """Returns all published non-deleted blogs ordered by published_at DESC."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT * FROM blogs 
                    WHERE deleted_at IS NULL 
                      AND status = 'published' 
                    ORDER BY COALESCE(published_at, created_at) DESC, id DESC
                """
                if limit:
                    sql += f" LIMIT {int(limit)}"
                cursor.execute(sql)
                return [cls(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @classmethod
    def find_by_slug(cls, slug: str, include_drafts: bool = False):
        """Finds a blog post by unique slug string."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                if include_drafts:
                    sql = "SELECT * FROM blogs WHERE slug = %s AND deleted_at IS NULL LIMIT 1"
                else:
                    sql = "SELECT * FROM blogs WHERE slug = %s AND deleted_at IS NULL AND status = 'published' LIMIT 1"
                cursor.execute(sql, (slug,))
                row = cursor.fetchone()
                return cls(row) if row else None
        finally:
            conn.close()

    @classmethod
    def find_by_id(cls, blog_id: int):
        """Finds a blog post by primary key id."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM blogs WHERE id = %s LIMIT 1", (blog_id,))
                row = cursor.fetchone()
                return cls(row) if row else None
        finally:
            conn.close()

    @classmethod
    def create(cls, **kwargs):
        """Creates and inserts a new Blog row into MySQL."""
        slug = kwargs.get('slug')
        if not slug and kwargs.get('title'):
            t = kwargs['title']
            raw_title = t.get('en') if isinstance(t, dict) else str(t)
            slug = cls.slugify(raw_title)

        title_json = cls._dump_json(kwargs.get('title', {"en": ""}))
        content_json = cls._dump_json(kwargs.get('content', {"en": "", "ar": ""}))
        short_desc_json = cls._dump_json(kwargs.get('short_description'))
        meta_title_json = cls._dump_json(kwargs.get('meta_title'))
        meta_desc_json = cls._dump_json(kwargs.get('meta_desc'))
        status = kwargs.get('status', 'draft')
        if status not in cls.VALID_STATUSES:
            status = 'draft'

        published_at = kwargs.get('published_at')
        if status == 'published' and not published_at:
            published_at = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO blogs (
                        title, slug, content, short_description, image,
                        category_name, blog_category_id, author_id, status, published_at,
                        meta_title, meta_desc, created_by, updated_by
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )
                """
                cursor.execute(sql, (
                    title_json,
                    slug,
                    content_json,
                    short_desc_json,
                    kwargs.get('image'),
                    kwargs.get('category_name'),
                    kwargs.get('blog_category_id'),
                    kwargs.get('author_id', 1),
                    status,
                    published_at,
                    meta_title_json,
                    meta_desc_json,
                    kwargs.get('created_by'),
                    kwargs.get('updated_by')
                ))
                blog_id = cursor.lastrowid
                return cls.find_by_id(blog_id)
        finally:
            conn.close()

    def update(self, **kwargs) -> bool:
        """Updates fields of this Blog instance in MySQL."""
        updates = []
        params = []

        if 'title' in kwargs:
            updates.append("title = %s")
            params.append(self._dump_json(kwargs['title']))
        if 'slug' in kwargs:
            updates.append("slug = %s")
            params.append(kwargs['slug'])
        if 'content' in kwargs:
            updates.append("content = %s")
            params.append(self._dump_json(kwargs['content']))
        if 'short_description' in kwargs:
            updates.append("short_description = %s")
            params.append(self._dump_json(kwargs['short_description']))
        if 'image' in kwargs:
            updates.append("image = %s")
            params.append(kwargs['image'])
        if 'category_name' in kwargs:
            updates.append("category_name = %s")
            params.append(kwargs['category_name'])
        if 'blog_category_id' in kwargs:
            updates.append("blog_category_id = %s")
            params.append(kwargs['blog_category_id'])
        if 'author_id' in kwargs:
            updates.append("author_id = %s")
            params.append(kwargs['author_id'])
        if 'status' in kwargs:
            new_status = kwargs['status']
            if new_status in self.VALID_STATUSES:
                updates.append("status = %s")
                params.append(new_status)
        if 'published_at' in kwargs:
            updates.append("published_at = %s")
            params.append(kwargs['published_at'])
        if 'meta_title' in kwargs:
            updates.append("meta_title = %s")
            params.append(self._dump_json(kwargs['meta_title']))
        if 'meta_desc' in kwargs:
            updates.append("meta_desc = %s")
            params.append(self._dump_json(kwargs['meta_desc']))
        if 'updated_by' in kwargs:
            updates.append("updated_by = %s")
            params.append(kwargs['updated_by'])

        if not updates:
            return False

        params.append(self.id)
        cols_clause = ", ".join(updates)
        sql = f"UPDATE blogs SET {cols_clause} WHERE id = %s"

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, tuple(params))
                return cursor.rowcount > 0
        finally:
            conn.close()
