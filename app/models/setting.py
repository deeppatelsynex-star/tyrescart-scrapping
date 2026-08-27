import json
from db import get_connection

DEFAULT_REVIEWER_SETTINGS = {
    "enabled": True,
    "name": {
        "en": "Sharvil Kumar",
        "ar": "شارفيل كومار"
    },
    "initials": "SK",
    "role": {
        "en": "Tyre Selection Specialist, TyresCart",
        "ar": "أخصائي اختيار الإطارات، تايرز كارت"
    },
    "bio": {
        "en": "Sharvil Kumar oversees operations at TyresCart, helping customers find tyres that match their vehicle and budget. He ensures a smooth purchasing experience and trusted installation support.",
        "ar": "يشرف شارفيل كومار على العمليات في تايرز كارت، لمساعدة العملاء في العثور على الإطارات المثالية التي تتطابق مع سياراتهم وميزانيتهم، مع ضمان تجربة شراء سلسة وخدمة تركيب معتمدة وموثوقة."
    }
}

class Setting:
    TABLE = "settings"

    @staticmethod
    def _parse_val(raw):
        if raw is None:
            return None
        if isinstance(raw, (dict, list)):
            return raw
        if isinstance(raw, str):
            s = raw.strip()
            if s.startswith("{") or s.startswith("["):
                try:
                    return json.loads(s)
                except Exception:
                    pass
            return raw
        return raw

    @staticmethod
    def _dump_val(val):
        if val is None:
            return None
        if isinstance(val, (dict, list)):
            return json.dumps(val, ensure_ascii=False)
        return str(val)

    @classmethod
    def get(cls, key: str, default=None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT value FROM settings WHERE `key` = %s LIMIT 1", (key,))
                row = cursor.fetchone()
                if not row or row.get("value") is None:
                    return default
                return cls._parse_val(row.get("value"))
        finally:
            conn.close()

    @classmethod
    def set(cls, key: str, value, group: str = "general") -> bool:
        dumped = cls._dump_val(value)
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = """
                    INSERT INTO settings (`key`, `value`, `group`, created_at, updated_at)
                    VALUES (%s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    ON DUPLICATE KEY UPDATE
                        `value` = VALUES(`value`),
                        `group` = VALUES(`group`),
                        updated_at = CURRENT_TIMESTAMP
                """
                cursor.execute(sql, (key, dumped, group))
                conn.commit()
                return True
        finally:
            conn.close()

    @classmethod
    def get_reviewer_settings(cls, locale: str = None) -> dict:
        data = cls.get("reviewer_settings", DEFAULT_REVIEWER_SETTINGS)
        if not isinstance(data, dict):
            data = DEFAULT_REVIEWER_SETTINGS.copy()

        enabled_val = data.get("enabled", True)
        if isinstance(enabled_val, str):
            enabled = enabled_val.strip().lower() in ("true", "1", "yes")
        else:
            enabled = bool(enabled_val)

        name_val = data.get("name") or DEFAULT_REVIEWER_SETTINGS["name"]
        initials = str(data.get("initials") or DEFAULT_REVIEWER_SETTINGS["initials"]).strip()
        role_val = data.get("role") or DEFAULT_REVIEWER_SETTINGS["role"]
        bio_val = data.get("bio") or data.get("description") or DEFAULT_REVIEWER_SETTINGS["bio"]

        if locale:
            name_str = (name_val.get(locale) or name_val.get("en") or next(iter(name_val.values()), "")) if isinstance(name_val, dict) else str(name_val)
            role_str = (role_val.get(locale) or role_val.get("en") or next(iter(role_val.values()), "")) if isinstance(role_val, dict) else str(role_val)
            bio_str = (bio_val.get(locale) or bio_val.get("en") or next(iter(bio_val.values()), "")) if isinstance(bio_val, dict) else str(bio_val)

            return {
                "enabled": enabled,
                "name": name_str,
                "initials": initials,
                "role": role_str,
                "bio": bio_str
            }

        return {
            "enabled": enabled,
            "name": name_val if isinstance(name_val, dict) else {"en": str(name_val), "ar": str(name_val)},
            "initials": initials,
            "role": role_val if isinstance(role_val, dict) else {"en": str(role_val), "ar": str(role_val)},
            "bio": bio_val if isinstance(bio_val, dict) else {"en": str(bio_val), "ar": str(bio_val)}
        }
