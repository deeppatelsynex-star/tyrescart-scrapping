"""
scripts/seed_listing_products.py
Seeds the 16 exact products and all 14 brands shown in ChatGPT Image Sep 14, 2026, 02_44_06 PM.png
into the MySQL database (`brands` and `products` tables).
"""

import sys
import os
import json
from decimal import Decimal

# Add app directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from db import get_connection

brands_data = [
    {"name": "Michelin", "slug": "michelin", "logo": "/static/assets/images/brands/michelin.svg"},
    {"name": "Bridgestone", "slug": "bridgestone", "logo": "/static/assets/images/brands/bridgestone.svg"},
    {"name": "Continental", "slug": "continental", "logo": "/static/assets/images/brands/continental.svg"},
    {"name": "Goodyear", "slug": "goodyear", "logo": "/static/assets/images/brands/goodyear.svg"},
    {"name": "Pirelli", "slug": "pirelli", "logo": "/static/assets/images/brands/pirelli.svg"},
    {"name": "Yokohama", "slug": "yokohama", "logo": "/static/assets/images/brands/yokohama.svg"},
    {"name": "Hankook", "slug": "hankook", "logo": "/static/assets/images/brands/hankook.svg"},
    {"name": "Toyo Tires", "slug": "toyo", "logo": "/static/assets/images/brands/toyo.svg"},
    {"name": "Falken", "slug": "falken", "logo": "/static/assets/images/brands/falken.svg"},
    {"name": "Dunlop", "slug": "dunlop", "logo": "/static/assets/images/brands/dunlop.svg"},
    {"name": "Kumho Tire", "slug": "kumho", "logo": "/static/assets/images/brands/kumho.svg"},
    {"name": "Nexen", "slug": "nexen", "logo": "/static/assets/images/brands/nexen.svg"},
    {"name": "Apollo", "slug": "apollo", "logo": "/static/assets/images/brands/apollo.svg"},
    {"name": "CEAT", "slug": "ceat", "logo": "/static/assets/images/brands/ceat.svg"},
]

products_data = [
    # ROW 1 (Cards 1 - 8)
    {
        "model": "Primacy 4",
        "brand": "Michelin",
        "size": "205/55 R16 91V",
        "price": 420.00,
        "list_price": None,
        "rating": 4.8,
        "reviews": 128,
        "badge": "Best Seller",
        "badge_class": "badge-blue",
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_1.jpg",
        "sort_order": 1
    },
    {
        "model": "Turanza T005",
        "brand": "Bridgestone",
        "size": "205/55 R16 91V",
        "price": 380.00,
        "list_price": 475.00,
        "rating": 4.7,
        "reviews": 96,
        "badge": "20% OFF",
        "badge_class": "badge-red",
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_2.jpg",
        "sort_order": 2
    },
    {
        "model": "PremiumContact 6",
        "brand": "Continental",
        "size": "225/55 R17 94Y",
        "price": 450.00,
        "list_price": None,
        "rating": 4.7,
        "reviews": 94,
        "badge": None,
        "badge_class": None,
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_3.jpg",
        "sort_order": 3
    },
    {
        "model": "EfficientGrip Performance",
        "brand": "Goodyear",
        "size": "205/55 R16 91V",
        "price": 400.00,
        "list_price": None,
        "rating": 4.7,
        "reviews": 73,
        "badge": None,
        "badge_class": None,
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_1.jpg",
        "sort_order": 4
    },
    {
        "model": "Cinturato P7",
        "brand": "Pirelli",
        "size": "205/55 R16 91V",
        "price": 410.00,
        "list_price": None,
        "rating": 4.6,
        "reviews": 68,
        "badge": "New",
        "badge_class": "badge-green",
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_2.jpg",
        "sort_order": 5
    },
    {
        "model": "BluEarth AE50",
        "brand": "Yokohama",
        "size": "205/55 R16 91V",
        "price": 395.00,
        "list_price": None,
        "rating": 4.4,
        "reviews": 52,
        "badge": None,
        "badge_class": None,
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_3.jpg",
        "sort_order": 6
    },
    {
        "model": "Pilot Sport 5",
        "brand": "Michelin",
        "size": "225/40 R18 92Y",
        "price": 620.00,
        "list_price": None,
        "rating": 4.8,
        "reviews": 110,
        "badge": "Special Offer",
        "badge_class": "badge-orange",
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_1.jpg",
        "sort_order": 7
    },
    {
        "model": "Potenza Sport",
        "brand": "Bridgestone",
        "size": "225/45 R17 94Y",
        "price": 520.00,
        "list_price": 600.00,
        "rating": 4.7,
        "reviews": 92,
        "badge": None,
        "badge_class": None,
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_2.jpg",
        "sort_order": 8
    },

    # ROW 2 (Cards 9 - 16)
    {
        "model": "Ventus Prime4",
        "brand": "Hankook",
        "size": "205/55 R16 91V",
        "price": 390.00,
        "list_price": None,
        "rating": 4.4,
        "reviews": 61,
        "badge": None,
        "badge_class": None,
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_3.jpg",
        "sort_order": 9
    },
    {
        "model": "Proxes Comfort",
        "brand": "Toyo Tires",
        "size": "205/55 R16 91V",
        "price": 420.00,
        "list_price": None,
        "rating": 4.5,
        "reviews": 58,
        "badge": "Popular",
        "badge_class": "badge-blue",
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_1.jpg",
        "sort_order": 10
    },
    {
        "model": "Ziex ZE310",
        "brand": "Falken",
        "size": "205/55 R16 91V",
        "price": 360.00,
        "list_price": None,
        "rating": 4.3,
        "reviews": 40,
        "badge": None,
        "badge_class": None,
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_2.jpg",
        "sort_order": 11
    },
    {
        "model": "Sport BluResponse",
        "brand": "Dunlop",
        "size": "205/55 R16 91V",
        "price": 370.00,
        "list_price": None,
        "rating": 4.4,
        "reviews": 46,
        "badge": None,
        "badge_class": None,
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_3.jpg",
        "sort_order": 12
    },
    {
        "model": "Ecsta HS52",
        "brand": "Kumho Tire",
        "size": "205/55 R16 91V",
        "price": 360.00,
        "list_price": None,
        "rating": 4.3,
        "reviews": 38,
        "badge": "New",
        "badge_class": "badge-green",
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_1.jpg",
        "sort_order": 13
    },
    {
        "model": "N'Fera SU1",
        "brand": "Nexen",
        "size": "205/55 R16 91V",
        "price": 340.00,
        "list_price": None,
        "rating": 4.2,
        "reviews": 35,
        "badge": None,
        "badge_class": None,
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_2.jpg",
        "sort_order": 14
    },
    {
        "model": "Alnac 4G",
        "brand": "Apollo",
        "size": "205/55 R16 91V",
        "price": 330.00,
        "list_price": None,
        "rating": 4.2,
        "reviews": 32,
        "badge": "Eco Choice",
        "badge_class": "badge-green",
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_3.jpg",
        "sort_order": 15
    },
    {
        "model": "SecuraDrive",
        "brand": "CEAT",
        "size": "205/55 R16 91V",
        "price": 320.00,
        "list_price": None,
        "rating": 4.1,
        "reviews": 28,
        "badge": None,
        "badge_class": None,
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_1.jpg",
        "sort_order": 16
    },

    # Additional popular sizes for pagination and filters
    {
        "model": "CrossClimate 2",
        "brand": "Michelin",
        "size": "225/50 R17 98V",
        "price": 540.00,
        "list_price": None,
        "rating": 4.9,
        "reviews": 84,
        "badge": "All Weather",
        "badge_class": "badge-blue",
        "vehicle_type": "car",
        "tire_type": "all_season",
        "image": "/static/assets/images/products/tyre_2.jpg",
        "sort_order": 17
    },
    {
        "model": "Scorpion Verde All Season",
        "brand": "Pirelli",
        "size": "235/50 R18 97V",
        "price": 590.00,
        "list_price": None,
        "rating": 4.6,
        "reviews": 56,
        "badge": "Popular",
        "badge_class": "badge-blue",
        "vehicle_type": "suv",
        "tire_type": "all_season",
        "image": "/static/assets/images/products/tyre_3.jpg",
        "sort_order": 18
    },
    {
        "model": "Eagle F1 Asymmetric 6",
        "brand": "Goodyear",
        "size": "225/45 R17 94Y",
        "price": 480.00,
        "list_price": 540.00,
        "rating": 4.8,
        "reviews": 77,
        "badge": "Special Offer",
        "badge_class": "badge-orange",
        "vehicle_type": "car",
        "tire_type": "summer",
        "image": "/static/assets/images/products/tyre_1.jpg",
        "sort_order": 19
    },
    {
        "model": "Dynapro AT2 RF11",
        "brand": "Hankook",
        "size": "265/65 R17 112T",
        "price": 510.00,
        "list_price": None,
        "rating": 4.7,
        "reviews": 65,
        "badge": None,
        "badge_class": None,
        "vehicle_type": "4x4",
        "tire_type": "all_season",
        "image": "/static/assets/images/products/tyre_2.jpg",
        "sort_order": 20
    }
]

def seed_listing():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Upsert brands
            brand_map = {}
            for b in brands_data:
                cur.execute("SELECT id FROM brands WHERE LOWER(name) = LOWER(%s) OR slug = %s", (b['name'], b['slug']))
                row = cur.fetchone()
                if row:
                    b_id = row['id']
                    cur.execute("UPDATE brands SET logo = %s, status = 'active' WHERE id = %s", (b['logo'], b_id))
                else:
                    cur.execute(
                        "INSERT INTO brands (name, slug, logo, status) VALUES (%s, %s, %s, 'active')",
                        (b['name'], b['slug'], b['logo'])
                    )
                    b_id = cur.lastrowid
                brand_map[b['name'].lower()] = b_id
                brand_map[b['slug'].lower()] = b_id

            print(f"Synchronized {len(brands_data)} brands!")

            # 2. Upsert products
            for idx, p in enumerate(products_data):
                b_name = p['brand']
                b_id = brand_map.get(b_name.lower(), 1)
                full_name = f"{b_name} {p['model']} {p['size']}"
                slug = p['model'].lower().replace(' ', '-').replace("'", '') + '-' + p['size'].lower().replace('/', '-').replace(' ', '-')
                sku = f"TV-{p['brand'][:3].upper()}-{idx+1:03d}"

                attr_json = {
                    'rating': p['rating'],
                    'reviews': p['reviews'],
                    'badge': p['badge'],
                    'badge_class': p['badge_class'],
                    'tire_size': p['size'],
                    'season': 'Summer' if p['tire_type'] == 'summer' else 'All Season',
                    'category': 'Car',
                    'brand_logo': f"/static/assets/images/brands/{p['brand'].lower().replace(' tires', '').replace(' tire', '')}.svg"
                }

                name_json = json.dumps({"en": full_name})
                desc_json = json.dumps({"en": f"{full_name} available at TyresVision with free mobile fitting in UAE."})
                attr_str = json.dumps(attr_json)

                cur.execute("SELECT id FROM products WHERE sku = %s OR slug = %s", (sku, slug))
                existing = cur.fetchone()

                if existing:
                    cur.execute("""
                        UPDATE products SET
                            display_name = %s,
                            name = %s,
                            description = %s,
                            price = %s,
                            list_price = %s,
                            brand_id = %s,
                            tire_size_label = %s,
                            vehicle_type = %s,
                            tire_type = %s,
                            image_path = %s,
                            attributes_json = %s,
                            sort_order = %s,
                            status = 'active',
                            stock_status = 'in_stock'
                        WHERE id = %s
                    """, (
                        p['model'],
                        name_json,
                        desc_json,
                        p['price'],
                        p['list_price'],
                        b_id,
                        p['size'],
                        p['vehicle_type'],
                        p['tire_type'],
                        p['image'],
                        attr_str,
                        p['sort_order'],
                        existing['id']
                    ))
                else:
                    cur.execute("""
                        INSERT INTO products (
                            website_id, attribute_set_id, sku, display_name, slug, name, description,
                            price, list_price, currency, stock_qty, stock_status,
                            tire_size_label, vehicle_type, tire_type, brand_id, image_path,
                            attributes_json, sort_order, status, visibility
                        ) VALUES (
                            1, 1, %s, %s, %s, %s, %s,
                            %s, %s, 'AED', 50, 'in_stock',
                            %s, %s, %s, %s, %s,
                            %s, %s, 'active', 'visible'
                        )
                    """, (
                        sku,
                        p['model'],
                        slug,
                        name_json,
                        desc_json,
                        p['price'],
                        p['list_price'],
                        p['size'],
                        p['vehicle_type'],
                        p['tire_type'],
                        b_id,
                        p['image'],
                        attr_str,
                        p['sort_order']
                    ))

            conn.commit()
            print(f"Successfully seeded {len(products_data)} catalog products!")

    finally:
        conn.close()

if __name__ == '__main__':
    seed_listing()
