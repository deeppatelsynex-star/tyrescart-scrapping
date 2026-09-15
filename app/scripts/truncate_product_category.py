import sys
sys.path.insert(0, 'app')
from db import get_connection

def truncate_product_and_category():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute('SET FOREIGN_KEY_CHECKS = 0;')
            
            tables_to_clear = [
                'product_categories',
                'product_attribute_values',
                'product_websites',
                'product_inventories',
                'product_prices',
                'product_stores',
                'product_field_selections',
                'cart_items',
                'wishlist_items',
                'products',
                'categories'
            ]
            for t in tables_to_clear:
                try:
                    cur.execute(f'TRUNCATE TABLE `{t}`')
                    print(f'Truncated {t}')
                except Exception as e:
                    cur.execute(f'DELETE FROM `{t}`')
                    print(f'Deleted from {t}: {e}')
                    
            # Re-insert root category with id = 2 (Default Category)
            cur.execute("""
                INSERT INTO categories (
                    id, name, slug, parent_id, status, sort_order, 
                    is_anchor, include_in_menu, display_mode, created_at, updated_at
                ) VALUES (
                    2, '{"en": "Default Category"}', 'default-category', NULL, 'active', 1,
                    1, 1, 'PRODUCTS', NOW(), NOW()
                )
            """)
            print('Re-created root category ID 2: Default Category')
            
            cur.execute('SET FOREIGN_KEY_CHECKS = 1;')
            conn.commit()
    finally:
        conn.close()
    print('Truncate of product and category tables completed successfully.')

if __name__ == '__main__':
    truncate_product_and_category()
