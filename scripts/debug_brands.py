import sys
sys.path.insert(0, 'app')
import db

conn = db.get_connection()
with conn.cursor() as cur:
    cur.execute("SELECT id, name, slug FROM brands WHERE status='active' LIMIT 15")
    brands = cur.fetchall()
    print("BRANDS:")
    for b in brands:
        print(b)
        
    cur.execute("""
        SELECT p.id, p.name, p.brand_id, b.slug as b_slug, b.name as b_name 
        FROM products p 
        LEFT JOIN brands b ON p.brand_id = b.id 
        WHERE p.deleted_at IS NULL AND p.status='active' 
        LIMIT 15
    """)
    prods = cur.fetchall()
    print("\nPRODUCTS BRAND JOIN:")
    for p in prods:
        print(p)

    cur.execute("""
        SELECT b.id, b.name, b.slug, COUNT(p.id) as cnt
        FROM brands b
        LEFT JOIN products p ON p.brand_id = b.id AND p.deleted_at IS NULL AND p.status = 'active'
        WHERE b.status = 'active'
        GROUP BY b.id, b.name, b.slug
        HAVING cnt > 0
        ORDER BY cnt DESC
        LIMIT 15
    """)
    b_counts = cur.fetchall()
    print("\nBRANDS WITH ACTIVE PRODUCTS:")
    for bc in b_counts:
        print(bc)
conn.close()
