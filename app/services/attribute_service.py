import json
import logging
import re
from db import get_connection

logger = logging.getLogger(__name__)

class AttributeService:
    """
    Dynamic Hybrid EAV + JSON Schema Engine with Scoped Fallbacks:
    Store View Locale -> Store Override -> Website Override -> Global Master Default.
    """

    @staticmethod
    def get_all_attributes(include_inactive=False):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM attributes WHERE deleted_at IS NULL ORDER BY sort_order ASC, id ASC"
                cursor.execute(sql)
                attrs = cursor.fetchall()
                for a in attrs:
                    if a.get('name') and isinstance(a['name'], str):
                        try:
                            a['name'] = json.loads(a['name'])
                        except Exception:
                            pass
                    
                    if isinstance(a.get('name'), dict):
                        a['name_en'] = a['name'].get('en') or a['name'].get('ar') or ''
                        a['name_ar'] = a['name'].get('ar') or ''
                    elif isinstance(a.get('name'), str):
                        a['name_en'] = a['name']
                        a['name_ar'] = ''

                    if a.get('validation_rules') and isinstance(a['validation_rules'], str):
                        try:
                            a['validation_rules'] = json.loads(a['validation_rules'])
                        except Exception:
                            pass
                return attrs
        finally:
            conn.close()

    @staticmethod
    def get_trash_attributes():
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                sql = "SELECT * FROM attributes WHERE deleted_at IS NOT NULL ORDER BY deleted_at DESC"
                cursor.execute(sql)
                attrs = cursor.fetchall()
                for a in attrs:
                    if a.get('name') and isinstance(a['name'], str):
                        try:
                            a['name'] = json.loads(a['name'])
                        except Exception:
                            pass
                    
                    if isinstance(a.get('name'), dict):
                        a['name_en'] = a['name'].get('en') or a['name'].get('ar') or ''
                        a['name_ar'] = a['name'].get('ar') or ''
                    elif isinstance(a.get('name'), str):
                        a['name_en'] = a['name']
                        a['name_ar'] = ''
                return attrs
        finally:
            conn.close()

    @staticmethod
    def restore_attribute(attr_id, user_id=None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE attributes SET deleted_at = NULL, deleted_by = NULL, updated_by = %s WHERE id = %s", (user_id, attr_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def purge_attribute(attr_id):
        """Hard deletes an attribute and its associated options and group mappings from the database."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, code, is_required, is_system FROM attributes WHERE id = %s", (attr_id,))
                attr = cursor.fetchone()
                if not attr:
                    return False
                if attr.get('is_required') or attr.get('is_system') or attr.get('code') in ('sku', 'price', 'name', 'product_name', 'status', 'display_name', 'tire_size_label', 'load_index', 'speed_rating'):
                    raise ValueError(f"Required attribute '{attr['code']}' cannot be deleted or purged.")

                cursor.execute("DELETE FROM attribute_options WHERE attribute_id = %s", (attr_id,))
                cursor.execute("DELETE FROM attribute_group_attributes WHERE attribute_id = %s", (attr_id,))
                cursor.execute("DELETE FROM product_attribute_values WHERE attribute_id = %s", (attr_id,))
                cursor.execute("DELETE FROM attributes WHERE id = %s", (attr_id,))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def get_attribute_options(attribute_id):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, attribute_id, value, label, swatch_value, sort_order, is_default
                    FROM attribute_options
                    WHERE attribute_id = %s
                    ORDER BY sort_order ASC, id ASC
                """, (attribute_id,))
                options = cursor.fetchall()
                for o in options:
                    if o.get('label') and isinstance(o['label'], str):
                        try:
                            o['label'] = json.loads(o['label'])
                        except Exception:
                            pass
                return options
        finally:
            conn.close()

    @staticmethod
    def get_attribute_sets():
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT s.id, s.name, s.slug, s.description, s.is_system, s.sort_order, s.created_at, s.updated_at,
                           COUNT(DISTINCT g.id) AS groups_count
                    FROM attribute_sets s
                    LEFT JOIN attribute_groups g ON s.id = g.attribute_set_id
                    WHERE s.deleted_at IS NULL
                    GROUP BY s.id, s.name, s.slug, s.description, s.is_system, s.sort_order, s.created_at, s.updated_at
                    ORDER BY s.sort_order ASC, s.id ASC
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_trash_attribute_sets():
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT s.id, s.name, s.slug, s.description, s.is_system, s.sort_order, s.created_at, s.updated_at, s.deleted_at,
                           COUNT(DISTINCT g.id) AS groups_count
                    FROM attribute_sets s
                    LEFT JOIN attribute_groups g ON s.id = g.attribute_set_id
                    WHERE s.deleted_at IS NOT NULL
                    GROUP BY s.id, s.name, s.slug, s.description, s.is_system, s.sort_order, s.created_at, s.updated_at, s.deleted_at
                    ORDER BY s.deleted_at DESC
                """)
                return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def get_attribute_set_with_groups(attribute_set_id):
        """Fetches full set hierarchy with groups and assigned attributes with options."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Fetch set
                cursor.execute("SELECT * FROM attribute_sets WHERE id = %s AND deleted_at IS NULL", (attribute_set_id,))
                attr_set = cursor.fetchone()
                if not attr_set:
                    return None

                # 2. Fetch groups
                cursor.execute("""
                    SELECT id, attribute_set_id, name, code, sort_order
                    FROM attribute_groups
                    WHERE attribute_set_id = %s
                    ORDER BY sort_order ASC, id ASC
                """, (attribute_set_id,))
                groups = cursor.fetchall()

                for g in groups:
                    if g.get('name') and isinstance(g['name'], str):
                        try:
                            g['name'] = json.loads(g['name'])
                        except Exception:
                            pass

                    # 3. Fetch attributes in this group
                    cursor.execute("""
                        SELECT a.*, aga.sort_order AS group_sort_order
                        FROM attribute_group_attributes aga
                        JOIN attributes a ON aga.attribute_id = a.id
                        WHERE aga.attribute_group_id = %s AND a.deleted_at IS NULL
                        ORDER BY aga.sort_order ASC, a.sort_order ASC
                    """, (g['id'],))
                    attrs = cursor.fetchall()

                    for a in attrs:
                        if a.get('name') and isinstance(a['name'], str):
                            try:
                                a['name'] = json.loads(a['name'])
                            except Exception:
                                pass
                        if a.get('validation_rules') and isinstance(a['validation_rules'], str):
                            try:
                                a['validation_rules'] = json.loads(a['validation_rules'])
                            except Exception:
                                pass

                        # Attach options for select/multiselect
                        if a.get('type') in ('select', 'multiselect'):
                            a['options'] = AttributeService.get_attribute_options(a['id'])
                        else:
                            a['options'] = []

                    g['attributes'] = attrs

                # Ensure core attributes (product_name, sku, price, etc.) exist in every set
                all_assigned_codes = set()
                for g in groups:
                    for a in g.get('attributes', []):
                        all_assigned_codes.add(a.get('code'))

                if 'sku' not in all_assigned_codes or 'product_name' not in all_assigned_codes:
                    cursor.execute("""
                        SELECT * FROM attributes
                        WHERE code IN ('attribute_set_id', 'status', 'product_name', 'sku', 'price', 'categories', 'tax_class', 'visibility', 'tabby_payment')
                          AND deleted_at IS NULL
                        ORDER BY FIELD(code, 'attribute_set_id', 'status', 'product_name', 'sku', 'price', 'categories', 'tax_class', 'visibility', 'tabby_payment')
                    """)
                    core_attrs = cursor.fetchall()
                    for a in core_attrs:
                        if a.get('name') and isinstance(a['name'], str):
                            try:
                                a['name'] = json.loads(a['name'])
                            except Exception:
                                pass
                        if a.get('type') in ('select', 'multiselect'):
                            a['options'] = AttributeService.get_attribute_options(a['id'])
                        else:
                            a['options'] = []

                    general_group = {
                        'id': f"general_{attribute_set_id}",
                        'attribute_set_id': attribute_set_id,
                        'name': {'en': 'General Attributes', 'ar': 'الخصائص العامة'},
                        'code': 'general',
                        'sort_order': 0,
                        'attributes': [a for a in core_attrs if a['code'] not in all_assigned_codes]
                    }
                    groups.insert(0, general_group)

                attr_set['groups'] = groups
                return attr_set
        finally:
            conn.close()

    @staticmethod
    def _normalize_group_name_json(name):
        if isinstance(name, dict):
            return json.dumps(name)
        if isinstance(name, str):
            trimmed = name.strip()
            if (trimmed.startswith('{') and trimmed.endswith('}')) or (trimmed.startswith('"') and trimmed.endswith('"')):
                try:
                    json.loads(trimmed)
                    return trimmed
                except Exception:
                    pass
            return json.dumps({'en': name})
        return json.dumps({'en': str(name or 'Group')})

    @staticmethod
    def add_group_to_set(attribute_set_id, name, code=None, sort_order=10, user_id=None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                if not code:
                    clean_code = re.sub(r'[^a-z0-9_]+', '_', (name.get('en') if isinstance(name, dict) else str(name)).lower()).strip('_')
                else:
                    clean_code = code
                name_val = AttributeService._normalize_group_name_json(name)
                cursor.execute("""
                    INSERT INTO attribute_groups (attribute_set_id, name, code, sort_order, created_by, updated_by)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (attribute_set_id, name_val, clean_code, sort_order, user_id, user_id))
                conn.commit()
                return cursor.lastrowid
        finally:
            conn.close()

    @staticmethod
    def add_attribute_to_group(group_id, attribute_id, sort_order=10, user_id=None):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO attribute_group_attributes (attribute_group_id, attribute_id, sort_order, created_by, updated_by)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE sort_order = VALUES(sort_order), updated_by = VALUES(updated_by)
                """, (group_id, attribute_id, sort_order, user_id, user_id))
                conn.commit()
                return True
        finally:
            conn.close()

    @staticmethod
    def remove_attribute_from_group(group_id, attribute_id):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM attribute_group_attributes 
                    WHERE attribute_group_id = %s AND attribute_id = %s
                """, (group_id, attribute_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def remove_group_from_set(group_id):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM attribute_group_attributes WHERE attribute_group_id = %s", (group_id,))
                cursor.execute("DELETE FROM attribute_groups WHERE id = %s", (group_id,))
                conn.commit()
                return True
        finally:
            conn.close()

    @staticmethod
    def rename_group(group_id, name, user_id=None):
        """Renames an attribute group."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                name_val = AttributeService._normalize_group_name_json(name)
                cursor.execute("""
                    UPDATE attribute_groups
                    SET name = %s, updated_by = %s, updated_at = NOW()
                    WHERE id = %s
                """, (name_val, user_id, group_id))
                conn.commit()
                return cursor.rowcount > 0
        finally:
            conn.close()

    @staticmethod
    def save_full_set_schema(attribute_set_id, set_name, groups_data, user_id=None):
        """
        Atomically saves:
        - Attribute set name
        - Groups (create new, rename existing, delete removed non-system groups)
        - Group attribute mappings (with sort order, preventing deletion of required attributes!)
        """
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Update set name
                if set_name:
                    cursor.execute("""
                        UPDATE attribute_sets SET name = %s, updated_by = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (set_name.strip(), user_id, attribute_set_id))

                # 2. Get existing groups for this set
                cursor.execute("SELECT id, name FROM attribute_groups WHERE attribute_set_id = %s", (attribute_set_id,))
                existing_groups = {row['id']: row for row in cursor.fetchall()}

                # 3. Get all required attributes across the system
                cursor.execute("SELECT id, code FROM attributes WHERE is_required = 1 OR is_system = 1 OR code IN ('sku', 'name', 'price', 'status', 'product_name')")
                required_attrs = {row['id']: row['code'] for row in cursor.fetchall()}

                # Process groups in groups_data
                seen_group_ids = set()
                first_group_id = None

                for g_idx, g in enumerate(groups_data):
                    g_id = g.get('id')
                    g_name = g.get('name') or 'General'
                    g_name_val = AttributeService._normalize_group_name_json(g_name)
                    clean_str = g_name.get('en') if isinstance(g_name, dict) else str(g_name)
                    g_code = re.sub(r'[^a-z0-9_]+', '_', clean_str.lower()).strip('_') or f"group_{g_idx+1}"

                    if g_id and g_id in existing_groups:
                        # Update group name and sort order
                        cursor.execute("""
                            UPDATE attribute_groups SET name = %s, sort_order = %s, updated_by = %s
                            WHERE id = %s
                        """, (g_name_val, g_idx * 10, user_id, g_id))
                        target_group_id = g_id
                    else:
                        # Insert new group
                        cursor.execute("""
                            INSERT INTO attribute_groups (attribute_set_id, name, code, sort_order, created_by, updated_by)
                            VALUES (%s, %s, %s, %s, %s, %s)
                        """, (attribute_set_id, g_name_val, g_code, g_idx * 10, user_id, user_id))
                        target_group_id = cursor.lastrowid

                    seen_group_ids.add(target_group_id)
                    if first_group_id is None:
                        first_group_id = target_group_id

                    # Clear existing mappings for this group to replace with new order
                    cursor.execute("DELETE FROM attribute_group_attributes WHERE attribute_group_id = %s", (target_group_id,))

                    # Re-insert attributes for this group
                    attrs = g.get('attributes') or []
                    for a_idx, attr in enumerate(attrs):
                        attr_id = attr.get('id') if isinstance(attr, dict) else attr
                        if attr_id:
                            cursor.execute("""
                                INSERT INTO attribute_group_attributes (attribute_group_id, attribute_id, sort_order, created_by, updated_by)
                                VALUES (%s, %s, %s, %s, %s)
                            """, (target_group_id, attr_id, a_idx * 10, user_id, user_id))

                # Delete groups that were removed (not in seen_group_ids)
                for old_gid in existing_groups.keys():
                    if old_gid not in seen_group_ids:
                        cursor.execute("DELETE FROM attribute_group_attributes WHERE attribute_group_id = %s", (old_gid,))
                        cursor.execute("DELETE FROM attribute_groups WHERE id = %s", (old_gid,))

                # 4. Critical requirement check: ensure all required attributes are preserved in the set!
                cursor.execute("""
                    SELECT DISTINCT attribute_id FROM attribute_group_attributes aga
                    JOIN attribute_groups ag ON aga.attribute_group_id = ag.id
                    WHERE ag.attribute_set_id = %s
                """, (attribute_set_id,))
                assigned_attr_ids = {row['attribute_id'] for row in cursor.fetchall()}

                if first_group_id:
                    for req_id in required_attrs.keys():
                        if req_id not in assigned_attr_ids:
                            cursor.execute("""
                                INSERT INTO attribute_group_attributes (attribute_group_id, attribute_id, sort_order, created_by, updated_by)
                                VALUES (%s, %s, 999, %s, %s)
                            """, (first_group_id, req_id, user_id, user_id))

                conn.commit()
                return True
        finally:
            conn.close()


    @staticmethod
    def get_product_scoped_attributes(product_id, website_id=None, store_id=None, store_view_id=None):
        """
        Resolves product attribute values with 4-tier fallback:
        Store View -> Store -> Website -> Global Default.
        Returns dict keyed by attribute code:
        {
          'code': {
            'value': ...,
            'option_id': ...,
            'scope_level': 'store' | 'website' | 'global',
            'is_inherited': True | False
          }
        }
        """
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # Fetch all values for this product across all scopes
                cursor.execute("""
                    SELECT pav.*, a.code AS attr_code, a.type AS attr_type
                    FROM product_attribute_values pav
                    JOIN attributes a ON pav.attribute_id = a.id
                    WHERE pav.product_id = %s
                """, (product_id,))
                rows = cursor.fetchall()

                # Group by attribute_id
                values_by_attr = {}
                for r in rows:
                    attr_code = r['attr_code']
                    values_by_attr.setdefault(attr_code, []).append(r)

                resolved = {}
                for attr_code, entries in values_by_attr.items():
                    # 1. Check Store View
                    match = None
                    scope_level = 'global'
                    is_inherited = False

                    if store_view_id:
                        for e in entries:
                            if e.get('store_view_id') == store_view_id:
                                match = e
                                scope_level = 'store_view'
                                break

                    # 2. Check Store
                    if not match and store_id:
                        for e in entries:
                            if e.get('store_id') == store_id and e.get('store_view_id') is None:
                                match = e
                                scope_level = 'store'
                                break

                    # 3. Check Website
                    if not match and website_id:
                        for e in entries:
                            if e.get('website_id') == website_id and e.get('store_id') is None and e.get('store_view_id') is None:
                                match = e
                                scope_level = 'website'
                                break

                    # 4. Fallback to Global Default
                    if not match:
                        for e in entries:
                            if e.get('website_id') is None and e.get('store_id') is None and e.get('store_view_id') is None:
                                match = e
                                scope_level = 'global'
                                break

                    if match:
                        # Determine if this value was inherited from a higher scope
                        requested_scope = 'store' if store_id else ('website' if website_id else 'global')
                        if requested_scope == 'store' and scope_level != 'store':
                            is_inherited = True
                        elif requested_scope == 'website' and scope_level != 'website':
                            is_inherited = True

                        # Extract typed value
                        raw_val = match.get('value_text')
                        if match.get('value_number') is not None:
                            raw_val = float(match['value_number']) if '.' in str(match['value_number']) else int(match['value_number'])
                        elif match.get('value_boolean') is not None:
                            raw_val = bool(match['value_boolean'])
                        elif match.get('value_json') is not None:
                            raw_val = match['value_json'] if isinstance(match['value_json'], (dict, list)) else json.loads(match['value_json'])

                        resolved[attr_code] = {
                            'id': match.get('id'),
                            'attribute_id': match.get('attribute_id'),
                            'value': raw_val,
                            'option_id': match.get('option_id'),
                            'scope_level': scope_level,
                            'is_inherited': is_inherited
                        }

                return resolved
        finally:
            conn.close()

    @staticmethod
    def save_product_scoped_attribute(
        product_id,
        attribute_id,
        value,
        website_id=None,
        store_id=None,
        store_view_id=None,
        option_id=None,
        user_id=None
    ):
        """Upserts a typed EAV record for a specific product and scope level."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Fetch attribute definition
                cursor.execute("SELECT type, scope FROM attributes WHERE id = %s", (attribute_id,))
                attr_def = cursor.fetchone()
                if not attr_def:
                    return False

                attr_type = attr_def['type']
                val_text = None
                val_number = None
                val_boolean = None
                val_date = None
                val_json = None

                if attr_type in ('number', 'decimal') and value not in (None, ''):
                    val_number = float(value)
                elif attr_type == 'boolean' and value not in (None, ''):
                    val_boolean = 1 if str(value).strip().lower() in ('true', '1', 'yes', 'y') or value is True else 0
                elif attr_type == 'date' and value not in (None, ''):
                    val_date = str(value)
                elif attr_type in ('json', 'multiselect') and value not in (None, ''):
                    val_json = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
                elif value is not None:
                    val_text = str(value)

                if attr_type == 'select' and option_id is None and value not in (None, ''):
                    clean_opt_val = str(value).strip()
                    if clean_opt_val:
                        cursor.execute("""
                            SELECT id FROM attribute_options 
                            WHERE attribute_id = %s AND (LOWER(value) = LOWER(%s) OR JSON_UNQUOTE(JSON_EXTRACT(label, '$.en')) = %s)
                            LIMIT 1
                        """, (attribute_id, clean_opt_val, clean_opt_val))
                        opt_row = cursor.fetchone()
                        if opt_row:
                            option_id = opt_row['id']
                        else:
                            lbl_json = json.dumps({'en': clean_opt_val, 'ar': clean_opt_val}, ensure_ascii=False)
                            cursor.execute("""
                                INSERT INTO attribute_options (attribute_id, value, label, created_by, updated_by, created_at, updated_at)
                                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
                            """, (attribute_id, clean_opt_val, lbl_json, user_id, user_id))
                            option_id = cursor.lastrowid

                # Scoped match condition
                scope_cond = "website_id IS NULL AND store_id IS NULL AND store_view_id IS NULL"
                scope_params = [product_id, attribute_id]

                if store_view_id:
                    scope_cond = "store_view_id = %s"
                    scope_params.append(store_view_id)
                elif store_id:
                    scope_cond = "store_id = %s AND store_view_id IS NULL"
                    scope_params.append(store_id)
                elif website_id:
                    scope_cond = "website_id = %s AND store_id IS NULL AND store_view_id IS NULL"
                    scope_params.append(website_id)

                check_sql = f"SELECT id FROM product_attribute_values WHERE product_id = %s AND attribute_id = %s AND {scope_cond}"
                cursor.execute(check_sql, tuple(scope_params))
                existing = cursor.fetchone()

                if existing:
                    cursor.execute("""
                        UPDATE product_attribute_values
                        SET value_text = %s, value_number = %s, value_boolean = %s,
                            value_date = %s, value_json = %s, option_id = %s,
                            updated_by = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (
                        val_text, val_number, val_boolean, val_date, val_json,
                        option_id, user_id, existing['id']
                    ))
                else:
                    cursor.execute("""
                        INSERT INTO product_attribute_values (
                            product_id, attribute_id, website_id, store_id, store_view_id,
                            value_text, value_number, value_boolean, value_date, value_json,
                            option_id, created_by, updated_by, created_at, updated_at
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                    """, (
                        product_id, attribute_id, website_id, store_id, store_view_id,
                        val_text, val_number, val_boolean, val_date, val_json,
                        option_id, user_id, user_id
                    ))

                conn.commit()
                return True
        finally:
            conn.close()

    @staticmethod
    def get_dynamic_form_schema(attribute_set_id, product_id=None, website_id=None, store_id=None):
        """
        Generates Alpine.js reactive form schema for the product edit interface.
        Injects current values, fallback indicators, and option lists.
        """
        attr_set = AttributeService.get_attribute_set_with_groups(attribute_set_id)
        if not attr_set:
            return {'groups': []}

        saved_values = {}
        prod_data = {}
        if product_id:
            saved_values = AttributeService.get_product_scoped_attributes(product_id, website_id, store_id)
            conn = get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
                    prow = cursor.fetchone()
                    if prow:
                        prod_data = dict(prow)
                        if prod_data.get('attributes_json') and isinstance(prod_data['attributes_json'], str):
                            try:
                                prod_data['attributes_json'] = json.loads(prod_data['attributes_json'])
                            except Exception:
                                prod_data['attributes_json'] = {}
            except Exception as e:
                logger.error(f"Error fetching product in get_dynamic_form_schema: {e}")
            finally:
                conn.close()

        for group in attr_set.get('groups', []):
            for attr in group.get('attributes', []):
                code = attr['code']
                val_info = saved_values.get(code, {})
                c_val = val_info.get('value')

                # Fallback to products.attributes_json
                if (c_val is None or c_val == '') and prod_data.get('attributes_json') and isinstance(prod_data['attributes_json'], dict):
                    attrs_j = prod_data['attributes_json']
                    c_val = attrs_j.get(code)
                    if c_val is None or c_val == '':
                        if code == 'tire_size':
                            c_val = attrs_j.get('tyre_size') or attrs_j.get('tire_size_label')
                        elif code == 'load_speed_index':
                            c_val = attrs_j.get('load_speed_index') or attrs_j.get('load_index')
                            sr = attrs_j.get('tire_speed_rating') or prod_data.get('tire_speed_rating')
                            if c_val and sr and not any(ch.isalpha() for ch in str(c_val)):
                                c_val = f"{c_val}{sr}".strip()
                        elif code == 'origin':
                            c_val = attrs_j.get('country') or attrs_j.get('country_of_origin')
                        elif code == 'tax_class':
                            c_val = attrs_j.get('tax_class_name')
                        elif code == 'promotion':
                            c_val = attrs_j.get('offers') or 'None'

                # Fallback to direct columns in products table
                if (c_val is None or c_val == '') and prod_data:
                    if code == 'url_key':
                        c_val = prod_data.get('slug')
                    elif code == 'attribute_set_id':
                        c_val = prod_data.get('attribute_set_id') or attribute_set_id
                    elif code == 'status':
                        c_val = prod_data.get('status', 'active')
                    elif code == 'brand' and prod_data.get('brand_id'):
                        c_val = prod_data.get('brand_id')
                    elif code == 'price_per_item':
                        c_val = prod_data.get('price')
                    elif code == 'tabby_payment':
                        c_val = bool(prod_data.get('pay_later_eligible', True))
                    elif code in ('product_name', 'name'):
                        c_val = prod_data.get('display_name') or prod_data.get('name')
                    elif code == 'display_name':
                        c_val = prod_data.get('display_name')
                    elif code == 'tire_size':
                        c_val = prod_data.get('tire_size_label')
                    elif code == 'origin':
                        c_val = prod_data.get('country_of_origin')
                    elif code == 'load_speed_index':
                        li = prod_data.get('tire_load_index') or ''
                        sr = prod_data.get('tire_speed_rating') or ''
                        c_val = f"{li}{sr}".strip() or None
                    elif code == 'promotion':
                        c_val = 'None'
                    elif code in prod_data and prod_data.get(code) is not None:
                        c_val = prod_data.get(code)

                # Format numeric strings for select options like width/height/rim (e.g. 185.0 -> 185)
                if code in ('width', 'height', 'rim') and c_val is not None:
                    try:
                        f_val = float(c_val)
                        if f_val.is_integer():
                            c_val = str(int(f_val))
                        else:
                            c_val = str(f_val)
                    except Exception:
                        c_val = str(c_val)

                if c_val is None:
                    c_val = attr.get('default_value')

                attr['current_value'] = c_val
                attr['current_option_id'] = val_info.get('option_id')
                attr['scope_level'] = val_info.get('scope_level', 'global')
                attr['is_inherited'] = val_info.get('is_inherited', False)

        return attr_set
