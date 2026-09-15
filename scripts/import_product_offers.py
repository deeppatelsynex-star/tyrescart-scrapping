"""
scripts/import_product_offers.py
Imports 'offers' from 'C:\\Users\\admin\\Downloads\\product-tyres-14-09 1(1).csv'
into products table (attributes_json) and product_attribute_values table for
both 'promotion' (attr 57) and 'offers' (attr 97).
"""

import os
import sys
import csv
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

from db import get_connection

CSV_PATH = r"C:\Users\admin\Downloads\product-tyres-14-09 1(1).csv"

def import_offers():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Ensure 'Top Savings' rule exists in cart_price_rules
            cur.execute("SELECT id FROM cart_price_rules WHERE label_default = 'TOP SAVINGS' OR name = 'Top Savings Promotion'")
            top_rule = cur.fetchone()
            if not top_rule:
                cur.execute("""
                    INSERT INTO cart_price_rules (
                        name, label_default, description, is_active, coupon_type,
                        priority, discount_type, discount_amount, free_shipping, created_at, updated_at
                    )
                    VALUES (
                        'Top Savings Promotion', 'TOP SAVINGS',
                        'Special savings promotion on selected high-demand tyres.',
                        1, 'NO_COUPON', 3, 'percent_of_original', 10.00, 'no', NOW(), NOW()
                    )
                """)
                new_rule_id = cur.lastrowid
                cur.execute("INSERT IGNORE INTO cart_price_rule_websites (cart_price_rule_id, website_id) VALUES (%s, 1)", (new_rule_id,))
                print(f"Added 'TOP SAVINGS' rule to cart_price_rules (ID: {new_rule_id})")

            # 2. Get attribute IDs for promotion and offers
            cur.execute("SELECT id, code FROM attributes WHERE code IN ('promotion', 'offers')")
            attr_map = {r['code']: r['id'] for r in cur.fetchall()}
            promo_attr_id = attr_map.get('promotion', 57)
            offers_attr_id = attr_map.get('offers', 97)
            print(f"Attribute IDs -> promotion: {promo_attr_id}, offers: {offers_attr_id}")

            # 3. Load existing products into lookup dictionaries
            cur.execute("SELECT id, name, display_name, sku, attributes_json FROM products")
            prods = cur.fetchall()
            print(f"Loaded {len(prods)} products from database.")

            prod_by_name = {}
            prod_by_sku = {}
            for p in prods:
                pid = p['id']
                dn = (p.get('display_name') or '').strip().lower()
                if dn:
                    prod_by_name[dn] = p
                sk = (p.get('sku') or '').strip().lower()
                if sk:
                    prod_by_sku[sk] = p
                
                raw_n = p.get('name') or ''
                if raw_n.startswith('{'):
                    try:
                        n_dict = json.loads(raw_n)
                        en_n = (n_dict.get('en') or '').strip().lower()
                        if en_n:
                            prod_by_name[en_n] = p
                    except Exception:
                        pass
                elif raw_n:
                    prod_by_name[raw_n.strip().lower()] = p

            # 4. Read CSV and apply offers
            with open(CSV_PATH, 'r', encoding='utf-8', errors='ignore') as f:
                reader = csv.DictReader(f)
                updated_count = 0
                cleared_count = 0
                missing_count = 0

                for r in reader:
                    name_key = (r.get('name') or '').strip().lower()
                    sku_key = (r.get('\ufeffsku') or r.get('sku') or '').strip().lower()
                    raw_offer = (r.get('offers') or '').strip()

                    # Find product
                    prod = prod_by_name.get(name_key) or prod_by_sku.get(sku_key)
                    if not prod:
                        missing_count += 1
                        continue

                    pid = prod['id']
                    normalized_offer = raw_offer
                    if normalized_offer in ('0', ''):
                        normalized_offer = 'None'

                    # A. Update attributes_json
                    attr_j = prod.get('attributes_json') or {}
                    if isinstance(attr_j, str):
                        try:
                            attr_j = json.loads(attr_j)
                        except Exception:
                            attr_j = {}
                    elif not isinstance(attr_j, dict):
                        attr_j = {}

                    attr_j['offers'] = normalized_offer
                    attr_j['promotion'] = normalized_offer
                    if normalized_offer and normalized_offer != 'None':
                        attr_j['badge'] = normalized_offer
                        attr_j['badge_class'] = 'badge-blue'
                    else:
                        if 'badge' in attr_j and attr_j['badge'] in ('Free Wheel Alignment', 'Buy 3 Get 1 Free', 'Top Savings'):
                            attr_j['badge'] = ''

                    new_attr_json_str = json.dumps(attr_j, ensure_ascii=False)
                    cur.execute("UPDATE products SET attributes_json = %s WHERE id = %s", (new_attr_json_str, pid))

                    # B. Update product_attribute_values for promotion & offers
                    for aid in (promo_attr_id, offers_attr_id):
                        if not aid:
                            continue
                        cur.execute("""
                            INSERT INTO product_attribute_values (
                                product_id, attribute_id, website_id, store_id, store_view_id,
                                value_text, created_at, updated_at
                            )
                            VALUES (%s, %s, 1, 1, 1, %s, NOW(), NOW())
                            ON DUPLICATE KEY UPDATE value_text = VALUES(value_text), updated_at = NOW()
                        """, (pid, aid, normalized_offer))

                    if normalized_offer != 'None':
                        updated_count += 1
                    else:
                        cleared_count += 1

            conn.commit()
            print("=================================================================")
            print(f"Offers import completed successfully!")
            print(f"Products with active promotional offers: {updated_count}")
            print(f"Products with no offer ('None' / '0'): {cleared_count}")
            print(f"Unmatched rows: {missing_count}")
            print("=================================================================")
    finally:
        conn.close()

if __name__ == '__main__':
    import_offers()
