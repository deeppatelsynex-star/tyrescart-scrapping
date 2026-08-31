import json
import logging
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
    def get_attribute_options(attribute_id):
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, attribute_id, value, label, swatch_value, sort_order
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
                    SELECT id, name, slug, description, is_system, sort_order, created_at, updated_at
                    FROM attribute_sets
                    WHERE deleted_at IS NULL
                    ORDER BY sort_order ASC, id ASC
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

                attr_set['groups'] = groups
                return attr_set
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
                    val_boolean = 1 if value in (True, 1, '1', 'true', 'True') else 0
                elif attr_type == 'date' and value not in (None, ''):
                    val_date = str(value)
                elif attr_type in ('json', 'multiselect') and value not in (None, ''):
                    val_json = json.dumps(value) if isinstance(value, (dict, list)) else str(value)
                elif value is not None:
                    val_text = str(value)

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
        if product_id:
            saved_values = AttributeService.get_product_scoped_attributes(product_id, website_id, store_id)

        for group in attr_set.get('groups', []):
            for attr in group.get('attributes', []):
                code = attr['code']
                val_info = saved_values.get(code, {})
                attr['current_value'] = val_info.get('value', attr.get('default_value'))
                attr['current_option_id'] = val_info.get('option_id')
                attr['scope_level'] = val_info.get('scope_level', 'global')
                attr['is_inherited'] = val_info.get('is_inherited', False)

        return attr_set
