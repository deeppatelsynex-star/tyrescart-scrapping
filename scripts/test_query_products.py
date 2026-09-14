import sys
import math
sys.path.insert(0, 'app')
import db

def query_products(page=1, per_page=32, brands=None, sizes=None, vehicles=None, types=None, max_price=None, sort_by='popular', search=None):
    conn = db.get_connection()
    try:
        with conn.cursor() as cur:
            where = ["p.deleted_at IS NULL", "p.status = 'active'"]
            params = []

            if brands:
                b_placeholders = ', '.join(['%s'] * len(brands))
                where.append(f"(LOWER(b.slug) IN ({b_placeholders}) OR LOWER(b.name) IN ({b_placeholders}))")
                params.extend([b.lower() for b in brands])
                params.extend([b.lower() for b in brands])

            if vehicles:
                v_terms = []
                for v in vehicles:
                    v_low = v.lower()
                    if v_low == 'suv':
                        v_terms.extend(['suv', '4x4', 'suv / 4x4'])
                    elif v_low == 'car':
                        v_terms.extend(['car', 'passenger car'])
                    elif v_low == 'van':
                        v_terms.extend(['van', 'light truck / van', 'commercial van'])
                    else:
                        v_terms.append(v_low)
                v_placeholders = ', '.join(['%s'] * len(v_terms))
                where.append(f"LOWER(p.vehicle_type) IN ({v_placeholders})")
                params.extend(v_terms)

            if sizes:
                s_placeholders = ', '.join(['%s'] * len(sizes))
                where.append(f"p.tire_size_label IN ({s_placeholders})")
                params.extend(sizes)

            if types:
                t_clauses = []
                t_terms = []
                for t in types:
                    t_low = t.lower()
                    if t_low == 'run_flat':
                        t_clauses.append("p.run_flat = 1")
                    else:
                        t_terms.append(t_low)
                if t_terms:
                    t_placeholders = ', '.join(['%s'] * len(t_terms))
                    t_clauses.append(f"LOWER(p.tire_type) IN ({t_placeholders})")
                    params.extend(t_terms)
                if t_clauses:
                    where.append("(" + " OR ".join(t_clauses) + ")")

            if max_price:
                where.append("p.price <= %s")
                params.append(float(max_price))

            if search:
                s_term = f"%{search.strip()}%"
                where.append("(p.sku LIKE %s OR p.display_name LIKE %s OR p.tire_size_label LIKE %s)")
                params.extend([s_term, s_term, s_term])

            where_sql = " AND ".join(where)

            # 1. Total matching count
            cur.execute(f"""
                SELECT COUNT(*) as total 
                FROM products p 
                LEFT JOIN brands b ON p.brand_id = b.id 
                WHERE {where_sql}
            """, params)
            total_count = cur.fetchone()['total']

            # 2. Sorting
            order_sql = "ORDER BY p.sort_order ASC, p.id ASC"
            if sort_by == 'price-asc':
                order_sql = "ORDER BY p.price ASC, p.id ASC"
            elif sort_by == 'price-desc':
                order_sql = "ORDER BY p.price DESC, p.id ASC"
            elif sort_by == 'newest':
                order_sql = "ORDER BY p.id DESC"

            # 3. Paging
            page = max(1, int(page))
            per_page = max(1, int(per_page))
            total_pages = max(1, math.ceil(total_count / per_page))
            if page > total_pages and total_count > 0:
                page = total_pages
            offset = (page - 1) * per_page

            fetch_params = list(params) + [per_page, offset]
            cur.execute(f"""
                SELECT p.*, b.name as brand_name, b.slug as brand_slug, b.logo as brand_logo
                FROM products p
                LEFT JOIN brands b ON p.brand_id = b.id
                WHERE {where_sql}
                {order_sql}
                LIMIT %s OFFSET %s
            """, fetch_params)
            rows = cur.fetchall()

            return {
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages,
                'count': len(rows),
                'first_item_sku': rows[0]['sku'] if rows else None,
                'first_item_brand': rows[0]['brand_name'] if rows else None
            }
    finally:
        conn.close()

if __name__ == '__main__':
    print("ALL PRODUCTS:", query_products(page=1, per_page=32))
    print("PIRELLI PRODUCTS:", query_products(page=1, per_page=32, brands=['pirelli']))
    print("MICHELIN PRODUCTS:", query_products(page=1, per_page=32, brands=['michelin']))
    print("PIRELLI + MICHELIN:", query_products(page=1, per_page=32, brands=['pirelli', 'michelin']))
    print("PAGE 2 OF ALL:", query_products(page=2, per_page=32))
