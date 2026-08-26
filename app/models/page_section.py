import json
from datetime import datetime, timezone
from db import get_connection

class PageSection:
    """
    PageSection Model for dynamically managing page sections (About Us, etc.)
    Table: page_sections
    """

    @staticmethod
    def _parse_json(val):
        if val is None:
            return {}
        if isinstance(val, (dict, list)):
            return val
        try:
            return json.loads(val)
        except Exception:
            return val

    @staticmethod
    def _dump_json(val):
        if val is None:
            return None
        if isinstance(val, str):
            return val
        return json.dumps(val, ensure_ascii=False)

    @classmethod
    def all_for_page(cls, page_slug: str = "about-us", include_inactive: bool = False):
        """Fetches all sections for a page ordered by sort_order ASC, id ASC."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM page_sections WHERE page_slug = %s AND deleted_at IS NULL"
                params = [page_slug]
                if not include_inactive:
                    sql += " AND is_active = 1"
                sql += " ORDER BY sort_order ASC, id ASC"
                cursor.execute(sql, tuple(params))
                rows = cursor.fetchall() or []
                return [cls._row_to_dict(r) for r in rows]
        finally:
            conn.close()

    @classmethod
    def find_by_id(cls, section_id: int):
        """Fetches a single section by id."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM page_sections WHERE id = %s AND deleted_at IS NULL", (section_id,))
                row = cursor.fetchone()
                return cls._row_to_dict(row) if row else None
        finally:
            conn.close()

    @classmethod
    def create(cls, data: dict):
        """Creates a new page section."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                page_slug = data.get("page_slug", "about-us")
                section_type = data.get("section_type", "hero")
                section_title = cls._dump_json(data.get("section_title", {}))
                section_subtitle = cls._dump_json(data.get("section_subtitle", {}))
                content = cls._dump_json(data.get("content", {}))
                image = data.get("image")
                image_position = data.get("image_position", "right")
                button_text = cls._dump_json(data.get("button_text", {}))
                button_url = data.get("button_url")
                section_data = cls._dump_json(data.get("section_data", {}))
                sort_order = int(data.get("sort_order", 0))
                is_active = 1 if data.get("is_active", True) in (1, "1", True, "true") else 0

                sql = """
                    INSERT INTO page_sections (
                        page_slug, section_type, section_title, section_subtitle,
                        content, image, image_position, button_text, button_url,
                        section_data, sort_order, is_active
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (
                    page_slug, section_type, section_title, section_subtitle,
                    content, image, image_position, button_text, button_url,
                    section_data, sort_order, is_active
                ))
                new_id = cursor.lastrowid
                conn.commit()
                return cls.find_by_id(new_id)
        finally:
            conn.close()

    @classmethod
    def update(cls, section_id: int, data: dict):
        """Updates an existing page section."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                fields = []
                params = []

                if "section_type" in data:
                    fields.append("section_type = %s")
                    params.append(data["section_type"])
                if "section_title" in data:
                    fields.append("section_title = %s")
                    params.append(cls._dump_json(data["section_title"]))
                if "section_subtitle" in data:
                    fields.append("section_subtitle = %s")
                    params.append(cls._dump_json(data["section_subtitle"]))
                if "content" in data:
                    fields.append("content = %s")
                    params.append(cls._dump_json(data["content"]))
                if "image" in data:
                    fields.append("image = %s")
                    params.append(data["image"])
                if "image_position" in data:
                    fields.append("image_position = %s")
                    params.append(data["image_position"])
                if "button_text" in data:
                    fields.append("button_text = %s")
                    params.append(cls._dump_json(data["button_text"]))
                if "button_url" in data:
                    fields.append("button_url = %s")
                    params.append(data["button_url"])
                if "section_data" in data:
                    fields.append("section_data = %s")
                    params.append(cls._dump_json(data["section_data"]))
                if "sort_order" in data:
                    fields.append("sort_order = %s")
                    params.append(int(data["sort_order"]))
                if "is_active" in data:
                    fields.append("is_active = %s")
                    params.append(1 if data["is_active"] in (1, "1", True, "true") else 0)

                if not fields:
                    return cls.find_by_id(section_id)

                sql = f"UPDATE page_sections SET {', '.join(fields)} WHERE id = %s AND deleted_at IS NULL"
                params.append(section_id)
                cursor.execute(sql, tuple(params))
                conn.commit()
                return cls.find_by_id(section_id)
        finally:
            conn.close()

    @classmethod
    def toggle_active(cls, section_id: int):
        """Toggles the is_active status of a section."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE page_sections SET is_active = NOT is_active WHERE id = %s AND deleted_at IS NULL",
                    (section_id,)
                )
                conn.commit()
                return cls.find_by_id(section_id)
        finally:
            conn.close()

    @classmethod
    def reorder(cls, ordered_ids: list):
        """Updates the sort_order of sections based on list order."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                for idx, sec_id in enumerate(ordered_ids, start=1):
                    cursor.execute(
                        "UPDATE page_sections SET sort_order = %s WHERE id = %s",
                        (idx, sec_id)
                    )
                conn.commit()
                return True
        finally:
            conn.close()

    @classmethod
    def soft_delete(cls, section_id: int):
        """Soft deletes a section."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE page_sections SET deleted_at = CURRENT_TIMESTAMP WHERE id = %s",
                    (section_id,)
                )
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @classmethod
    def _row_to_dict(cls, row):
        if not row:
            return None
        return {
            "id": row.get("id"),
            "page_slug": row.get("page_slug") or "about-us",
            "section_type": row.get("section_type") or "hero",
            "section_title": cls._parse_json(row.get("section_title")),
            "section_subtitle": cls._parse_json(row.get("section_subtitle")),
            "content": cls._parse_json(row.get("content")),
            "image": row.get("image"),
            "image_position": row.get("image_position") or "right",
            "button_text": cls._parse_json(row.get("button_text")),
            "button_url": row.get("button_url"),
            "section_data": cls._parse_json(row.get("section_data")),
            "sort_order": row.get("sort_order") if row.get("sort_order") is not None else 0,
            "is_active": bool(row.get("is_active")),
            "created_at": row.get("created_at").isoformat() if row.get("created_at") else None,
            "updated_at": row.get("updated_at").isoformat() if row.get("updated_at") else None,
        }

    @classmethod
    def to_localized_dict(cls, section: dict, locale: str = "en"):
        """Resolves bilingual JSON dictionaries into strings for the given locale."""
        if not section:
            return {}

        def get_loc(val):
            if val is None:
                return ""
            if isinstance(val, dict):
                return val.get(locale) or val.get("en") or val.get("ar") or ""
            return str(val)

        sec_data = section.get("section_data") or {}
        localized_data = {}
        if isinstance(sec_data, dict):
            # Localize nested features, cards, metrics, badges
            for k, v in sec_data.items():
                if isinstance(v, list):
                    localized_list = []
                    for item in v:
                        if isinstance(item, dict):
                            loc_item = {}
                            for sub_k, sub_v in item.items():
                                if isinstance(sub_v, dict) and ("en" in sub_v or "ar" in sub_v):
                                    loc_item[sub_k] = get_loc(sub_v)
                                else:
                                    loc_item[sub_k] = sub_v
                            localized_list.append(loc_item)
                        else:
                            localized_list.append(item)
                    localized_data[k] = localized_list
                elif isinstance(v, dict) and ("en" in v or "ar" in v):
                    localized_data[k] = get_loc(v)
                else:
                    localized_data[k] = v

        return {
            "id": section.get("id"),
            "page_slug": section.get("page_slug"),
            "section_type": section.get("section_type"),
            "section_title": get_loc(section.get("section_title")),
            "section_subtitle": get_loc(section.get("section_subtitle")),
            "content": get_loc(section.get("content")),
            "image": section.get("image"),
            "image_position": section.get("image_position") or "right",
            "button_text": get_loc(section.get("button_text")),
            "button_url": section.get("button_url"),
            "section_data": localized_data,
            "raw_title": section.get("section_title"),
            "raw_subtitle": section.get("section_subtitle"),
            "raw_content": section.get("content"),
            "raw_button_text": section.get("button_text"),
            "raw_section_data": section.get("section_data"),
            "sort_order": section.get("sort_order"),
            "is_active": section.get("is_active"),
        }
