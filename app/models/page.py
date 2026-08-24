"""
app/models/page.py - Page Model and Query Helpers
Table: pages (static content pages e.g. About Us, Terms and Conditions, Privacy Policy, Shipping Policy)
Mixins: SlugMixin, SoftDeleteMixin, SearchableMixin
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
        """Checks if a given slug is unique in the pages table."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT id FROM pages WHERE slug = %s AND deleted_at IS NULL"
                params = [slug]
                if exclude_id:
                    sql += " AND id != %s"
                    params.append(exclude_id)
                cursor.execute(sql, tuple(params))
                return cursor.fetchone() is None
        finally:
            conn.close()


class SoftDeleteMixin:
    """Provides soft-delete capabilities and deleted-record filters."""

    @classmethod
    def soft_delete(cls, page_id: int) -> bool:
        """Marks a page as deleted without removing its row from disk."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE pages SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s AND deleted_at IS NULL",
                    (page_id,)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def restore(cls, page_id: int) -> bool:
        """Restores a soft-deleted page."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE pages SET deleted_at = NULL WHERE id = %s AND deleted_at IS NOT NULL",
                    (page_id,)
                )
                return cursor.rowcount > 0
        finally:
            conn.close()


class SearchableMixin:
    """Provides fulltext/JSON search across title and content."""

    @classmethod
    def search(cls, query: str, locale: str = 'en', limit: int = 20):
        """Searches active published pages by title or content snippet."""
        if not query:
            return []
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                term = f"%{query.strip()}%"
                sql = """
                    SELECT * FROM pages 
                    WHERE deleted_at IS NULL 
                      AND status = 'published'
                      AND (published_at IS NULL OR published_at <= CURRENT_TIMESTAMP)
                      AND (
                        JSON_UNQUOTE(JSON_EXTRACT(title, %s)) LIKE %s
                        OR JSON_UNQUOTE(JSON_EXTRACT(content, %s)) LIKE %s
                      )
                    ORDER BY sort_order ASC, id DESC
                    LIMIT %s
                """
                loc_key = f"$.{locale}"
                cursor.execute(sql, (loc_key, term, loc_key, term, limit))
                rows = cursor.fetchall()
                return [cls(r) for r in rows]
        finally:
            conn.close()


# ============================================================================
# PAGE MODEL
# ============================================================================

class Page(SlugMixin, SoftDeleteMixin, SearchableMixin):
    """
    Page model for managing static content pages (About Us, Terms, Privacy Policy, etc.).
    Supports multi-locale JSON payloads for title, content, excerpt, and SEO meta tags.
    """

    TABLE = 'pages'
    COLUMNS = (
        'id', 'title', 'slug', 'content', 'excerpt', 'template',
        'featured_image', 'status', 'published_at', 'show_in_footer',
        'show_in_header', 'sort_order', 'meta_title', 'meta_desc',
        'canonical_url', 'created_by', 'created_at', 'updated_at', 'deleted_at'
    )

    def __init__(self, data: dict):
        self.id = data.get('id')
        self.title = self._parse_json(data.get('title'))
        self.slug = data.get('slug')
        self.content = self._parse_json(data.get('content'))
        self.excerpt = self._parse_json(data.get('excerpt'))
        self.template = data.get('template', 'default')
        self.featured_image = data.get('featured_image')
        self.status = data.get('status', 'draft')
        self.published_at = data.get('published_at')
        self.show_in_footer = bool(data.get('show_in_footer'))
        self.show_in_header = bool(data.get('show_in_header'))
        self.sort_order = int(data.get('sort_order') or 0)
        self.meta_title = self._parse_json(data.get('meta_title'))
        self.meta_desc = self._parse_json(data.get('meta_desc'))
        self.canonical_url = data.get('canonical_url')
        self.created_by = data.get('created_by')
        self.created_at = data.get('created_at')
        self.updated_at = data.get('updated_at')
        self.deleted_at = data.get('deleted_at')

    @staticmethod
    def _parse_json(val):
        if val is None:
            return {}
        if isinstance(val, (dict, list)):
            return val
        try:
            return json.loads(val)
        except Exception:
            return {"en": str(val)}

    @staticmethod
    def _dump_json(val):
        if val is None:
            return None
        if isinstance(val, str):
            return val
        return json.dumps(val, ensure_ascii=False)

    # -------------------------------------------------------------------------
    # Localized Property Accessors
    # -------------------------------------------------------------------------
    def get_title(self, locale: str = 'en') -> str:
        """Returns the localized title string (fallback to 'en' or first available)."""
        if isinstance(self.title, dict):
            return self.title.get(locale) or self.title.get('en') or next(iter(self.title.values()), "")
        return str(self.title or "")

    def get_content(self, locale: str = 'en') -> str:
        """Returns the localized HTML body content."""
        if isinstance(self.content, dict):
            return self.content.get(locale) or self.content.get('en') or next(iter(self.content.values()), "")
        return str(self.content or "")

    def get_excerpt(self, locale: str = 'en') -> str:
        """Returns the localized excerpt string."""
        if isinstance(self.excerpt, dict):
            return self.excerpt.get(locale) or self.excerpt.get('en') or ""
        return str(self.excerpt or "")

    def get_meta_title(self, locale: str = 'en') -> str:
        """Returns the localized meta title (defaults to title if not specified)."""
        if isinstance(self.meta_title, dict) and self.meta_title.get(locale):
            return self.meta_title.get(locale)
        return self.get_title(locale)

    def get_meta_desc(self, locale: str = 'en') -> str:
        """Returns the localized meta description."""
        if isinstance(self.meta_desc, dict):
            return self.meta_desc.get(locale) or self.meta_desc.get('en') or ""
        return str(self.meta_desc or "")

    def to_dict(self, locale: str = None) -> dict:
        """Serializes page record for API responses or template context."""
        base = {
            'id': self.id,
            'slug': self.slug,
            'template': self.template,
            'featured_image': self.featured_image,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'show_in_footer': self.show_in_footer,
            'show_in_header': self.show_in_header,
            'sort_order': self.sort_order,
            'canonical_url': self.canonical_url,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if locale:
            base.update({
                'title': self.get_title(locale),
                'content': self.get_content(locale),
                'excerpt': self.get_excerpt(locale),
                'meta_title': self.get_meta_title(locale),
                'meta_desc': self.get_meta_desc(locale),
            })
        else:
            base.update({
                'title': self.title,
                'content': self.content,
                'excerpt': self.excerpt,
                'meta_title': self.meta_title,
                'meta_desc': self.meta_desc,
            })
        return base

    # -------------------------------------------------------------------------
    # Query Helpers
    # -------------------------------------------------------------------------
    @classmethod
    def all(cls, include_deleted: bool = False):
        """Returns all pages ordered by sort_order and id."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM pages"
                if not include_deleted:
                    sql += " WHERE deleted_at IS NULL"
                sql += " ORDER BY sort_order ASC, id DESC"
                cursor.execute(sql)
                return [cls(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @classmethod
    def published(cls):
        """Returns all live, published, non-deleted pages ordered by sort_order."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT * FROM pages 
                    WHERE deleted_at IS NULL 
                      AND status = 'published'
                      AND (published_at IS NULL OR published_at <= CURRENT_TIMESTAMP)
                    ORDER BY sort_order ASC, id ASC
                """
                cursor.execute(sql)
                return [cls(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @classmethod
    def in_footer(cls):
        """Returns all published pages configured to display in footer navigation."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT * FROM pages 
                    WHERE deleted_at IS NULL 
                      AND status = 'published'
                      AND show_in_footer = 1
                      AND (published_at IS NULL OR published_at <= CURRENT_TIMESTAMP)
                    ORDER BY sort_order ASC, id ASC
                """
                cursor.execute(sql)
                return [cls(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @classmethod
    def in_header(cls):
        """Returns all published pages configured to display in header navigation."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    SELECT * FROM pages 
                    WHERE deleted_at IS NULL 
                      AND status = 'published'
                      AND show_in_header = 1
                      AND (published_at IS NULL OR published_at <= CURRENT_TIMESTAMP)
                    ORDER BY sort_order ASC, id ASC
                """
                cursor.execute(sql)
                return [cls(r) for r in cursor.fetchall()]
        finally:
            conn.close()

    @classmethod
    def find_by_slug(cls, slug: str, include_drafts: bool = False):
        """Finds an active page by unique slug string."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                if include_drafts:
                    sql = "SELECT * FROM pages WHERE slug = %s AND deleted_at IS NULL LIMIT 1"
                else:
                    sql = """
                        SELECT * FROM pages 
                        WHERE slug = %s 
                          AND deleted_at IS NULL 
                          AND status = 'published'
                          AND (published_at IS NULL OR published_at <= CURRENT_TIMESTAMP)
                        LIMIT 1
                    """
                cursor.execute(sql, (slug,))
                row = cursor.fetchone()
                return cls(row) if row else None
        finally:
            conn.close()

    @classmethod
    def find_by_id(cls, page_id: int):
        """Finds a page by primary key id."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM pages WHERE id = %s AND deleted_at IS NULL LIMIT 1", (page_id,))
                row = cursor.fetchone()
                return cls(row) if row else None
        finally:
            conn.close()

    @classmethod
    def create(cls, **kwargs):
        """Creates and inserts a new Page row into MySQL."""
        slug = kwargs.get('slug')
        if not slug and kwargs.get('title'):
            t = kwargs['title']
            raw_title = t.get('en') if isinstance(t, dict) else str(t)
            slug = cls.slugify(raw_title)

        title_json = cls._dump_json(kwargs.get('title', {"en": ""}))
        content_json = cls._dump_json(kwargs.get('content', {"en": ""}))
        excerpt_json = cls._dump_json(kwargs.get('excerpt'))
        meta_title_json = cls._dump_json(kwargs.get('meta_title'))
        meta_desc_json = cls._dump_json(kwargs.get('meta_desc'))

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO pages (
                        title, slug, content, excerpt, template,
                        featured_image, status, published_at, show_in_footer,
                        show_in_header, sort_order, meta_title, meta_desc,
                        canonical_url, created_by
                    ) VALUES (
                        %s, %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s
                    )
                """
                cursor.execute(sql, (
                    title_json,
                    slug,
                    content_json,
                    excerpt_json,
                    kwargs.get('template', 'default'),
                    kwargs.get('featured_image'),
                    kwargs.get('status', 'draft'),
                    kwargs.get('published_at'),
                    1 if kwargs.get('show_in_footer') else 0,
                    1 if kwargs.get('show_in_header') else 0,
                    kwargs.get('sort_order', 0),
                    meta_title_json,
                    meta_desc_json,
                    kwargs.get('canonical_url'),
                    kwargs.get('created_by')
                ))
                page_id = cursor.lastrowid
                return cls.find_by_id(page_id)
        finally:
            conn.close()

    def update(self, **kwargs) -> bool:
        """Updates fields of this Page instance in MySQL."""
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
        if 'excerpt' in kwargs:
            updates.append("excerpt = %s")
            params.append(self._dump_json(kwargs['excerpt']))
        if 'template' in kwargs:
            updates.append("template = %s")
            params.append(kwargs['template'])
        if 'featured_image' in kwargs:
            updates.append("featured_image = %s")
            params.append(kwargs['featured_image'])
        if 'status' in kwargs:
            updates.append("status = %s")
            params.append(kwargs['status'])
        if 'published_at' in kwargs:
            updates.append("published_at = %s")
            params.append(kwargs['published_at'])
        if 'show_in_footer' in kwargs:
            updates.append("show_in_footer = %s")
            params.append(1 if kwargs['show_in_footer'] else 0)
        if 'show_in_header' in kwargs:
            updates.append("show_in_header = %s")
            params.append(1 if kwargs['show_in_header'] else 0)
        if 'sort_order' in kwargs:
            updates.append("sort_order = %s")
            params.append(kwargs['sort_order'])
        if 'meta_title' in kwargs:
            updates.append("meta_title = %s")
            params.append(self._dump_json(kwargs['meta_title']))
        if 'meta_desc' in kwargs:
            updates.append("meta_desc = %s")
            params.append(self._dump_json(kwargs['meta_desc']))
        if 'canonical_url' in kwargs:
            updates.append("canonical_url = %s")
            params.append(kwargs['canonical_url'])

        if not updates:
            return False

        params.append(self.id)
        cols_clause = ", ".join(updates)
        sql = f"UPDATE pages SET {cols_clause} WHERE id = %s"

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(sql, tuple(params))
                return cursor.rowcount > 0
        finally:
            conn.close()
