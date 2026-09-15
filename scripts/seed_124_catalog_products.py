"""
scripts/seed_124_catalog_products.py
Seeds exactly 124 dynamic catalog products into MySQL `products` table,
matching the counts, brands, sizes, and pagination shown in ChatGPT Image Sep 14, 2026, 02_44_06 PM.png.
"""

import sys
import os
import json
from decimal import Decimal

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'app')))
from db import get_connection

def seed_124_products():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Fetch brand IDs
            cur.execute("SELECT id, slug, name, logo FROM brands WHERE status = 'active'")
            brands = {r['name'].lower(): r for r in cur.fetchall()}
            for b in list(brands.values()):
                brands[b['slug'].lower()] = b

            # 2. Deactivate legacy dummy products so our clean 124 catalog leads
            cur.execute("UPDATE products SET deleted_at = NOW() WHERE sort_order > 124")

            # 3. Base 16 Reference Products (Row 1 & Row 2 from screenshot)
            base_16 = [
                # ROW 1 (Cards 1 - 8)
                {"model": "Primacy 4", "brand": "michelin", "size": "205/55 R16 91V", "price": 420.00, "list_price": None, "rating": 4.8, "reviews": 128, "badge": "Best Seller", "badge_class": "badge-blue", "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_1.jpg", "sort_order": 1},
                {"model": "Turanza T005", "brand": "bridgestone", "size": "205/55 R16 91V", "price": 380.00, "list_price": 475.00, "rating": 4.7, "reviews": 96, "badge": "20% OFF", "badge_class": "badge-red", "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_2.jpg", "sort_order": 2},
                {"model": "PremiumContact 6", "brand": "continental", "size": "225/55 R17 94Y", "price": 450.00, "list_price": None, "rating": 4.7, "reviews": 94, "badge": None, "badge_class": None, "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_3.jpg", "sort_order": 3},
                {"model": "EfficientGrip Performance", "brand": "goodyear", "size": "205/55 R16 91V", "price": 400.00, "list_price": None, "rating": 4.7, "reviews": 73, "badge": None, "badge_class": None, "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_1.jpg", "sort_order": 4},
                {"model": "Cinturato P7", "brand": "pirelli", "size": "205/55 R16 91V", "price": 410.00, "list_price": None, "rating": 4.6, "reviews": 68, "badge": "New", "badge_class": "badge-green", "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_2.jpg", "sort_order": 5},
                {"model": "BluEarth AE50", "brand": "yokohama", "size": "205/55 R16 91V", "price": 395.00, "list_price": None, "rating": 4.4, "reviews": 52, "badge": None, "badge_class": None, "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_3.jpg", "sort_order": 6},
                {"model": "Pilot Sport 5", "brand": "michelin", "size": "225/40 R18 92Y", "price": 620.00, "list_price": None, "rating": 4.8, "reviews": 110, "badge": "Special Offer", "badge_class": "badge-orange", "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_1.jpg", "sort_order": 7},
                {"model": "Potenza Sport", "brand": "bridgestone", "size": "225/45 R17 94Y", "price": 520.00, "list_price": 600.00, "rating": 4.7, "reviews": 92, "badge": None, "badge_class": None, "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_2.jpg", "sort_order": 8},

                # ROW 2 (Cards 9 - 16)
                {"model": "Ventus Prime4", "brand": "hankook", "size": "205/55 R16 91V", "price": 390.00, "list_price": None, "rating": 4.4, "reviews": 61, "badge": None, "badge_class": None, "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_3.jpg", "sort_order": 9},
                {"model": "Proxes Comfort", "brand": "toyo", "size": "205/55 R16 91V", "price": 420.00, "list_price": None, "rating": 4.5, "reviews": 58, "badge": "Popular", "badge_class": "badge-blue", "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_1.jpg", "sort_order": 10},
                {"model": "Ziex ZE310", "brand": "falken", "size": "205/55 R16 91V", "price": 360.00, "list_price": None, "rating": 4.3, "reviews": 40, "badge": None, "badge_class": None, "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_2.jpg", "sort_order": 11},
                {"model": "Sport BluResponse", "brand": "dunlop", "size": "205/55 R16 91V", "price": 370.00, "list_price": None, "rating": 4.4, "reviews": 46, "badge": None, "badge_class": None, "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_3.jpg", "sort_order": 12},
                {"model": "Ecsta HS52", "brand": "kumho", "size": "205/55 R16 91V", "price": 360.00, "list_price": None, "rating": 4.3, "reviews": 38, "badge": "New", "badge_class": "badge-green", "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_1.jpg", "sort_order": 13},
                {"model": "N'Fera SU1", "brand": "nexen", "size": "205/55 R16 91V", "price": 340.00, "list_price": None, "rating": 4.2, "reviews": 35, "badge": None, "badge_class": None, "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_2.jpg", "sort_order": 14},
                {"model": "Alnac 4G", "brand": "apollo", "size": "205/55 R16 91V", "price": 330.00, "list_price": None, "rating": 4.2, "reviews": 32, "badge": "Eco Choice", "badge_class": "badge-emerald", "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_3.jpg", "sort_order": 15},
                {"model": "SecuraDrive", "brand": "ceat", "size": "205/55 R16 91V", "price": 320.00, "list_price": None, "rating": 4.1, "reviews": 28, "badge": None, "badge_class": None, "vehicle_type": "car", "tire_type": "summer", "image": "/static/assets/images/products/tyre_1.jpg", "sort_order": 16},
            ]

            brand_extensions = {
                "michelin": [
                    ("Pilot Sport 4S", "245/40 R19 98Y", 850, 940, "car", "summer", "Best Seller", "badge-blue"),
                    ("Primacy 4+", "195/65 R15 91H", 380, None, "car", "summer", None, None),
                    ("CrossClimate 2", "205/55 R16 94V", 460, 520, "car", "all_season", "All-Season", "badge-blue"),
                    ("Pilot Alpin 5", "225/45 R17 94V", 590, None, "car", "winter", "Winter", "badge-blue"),
                    ("Primacy SUV", "235/50 R18 97V", 560, None, "suv", "summer", None, None),
                    ("Latitude Sport 3", "235/50 R18 101Y", 680, 750, "suv", "summer", "Special Offer", "badge-orange"),
                    ("Pilot Super Sport", "225/40 R18 92Y", 640, None, "car", "summer", None, None),
                    ("e.Primacy (EV)", "205/55 R16 91V", 490, None, "car", "summer", "Eco Choice", "badge-emerald"),
                    ("Agilis 3", "195/65 R15 95T", 410, None, "van", "summer", None, None),
                    ("Agilis CrossClimate", "225/55 R17 104H", 540, None, "van", "all_season", None, None),
                    ("Energy Saver+", "195/65 R15 91V", 360, None, "car", "summer", None, None),
                    ("Pilot Sport Cup 2", "245/45 R19 102Y", 990, 1150, "car", "summer", "Track Spec", "badge-red"),
                    ("Latitude Cross", "225/55 R17 101H", 580, None, "4x4", "all_season", "All-Terrain", "badge-blue"),
                    ("CrossClimate SUV", "235/50 R18 103V", 620, None, "suv", "all_season", None, None),
                    ("Primacy 3 ZP RunFlat", "225/45 R17 91W", 590, 680, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("Pilot Sport 4 ZP", "225/50 R17 98Y", 630, None, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("Alpin 6", "195/65 R15 91T", 390, None, "car", "winter", "Winter", "badge-blue"),
                    ("Pilot Sport EV", "235/50 R18 101Y", 720, None, "car", "summer", "EV Silent", "badge-emerald"),
                    ("Primacy 4", "225/50 R17 98V", 490, 540, "car", "summer", None, None),
                    ("Pilot Sport 5", "225/45 R17 94Y", 570, None, "car", "summer", "Popular", "badge-blue"),
                    ("CrossClimate 2", "225/45 R17 94Y", 510, None, "car", "all_season", None, None),
                    ("Latitude Tour HP", "235/50 R18 97H", 590, None, "suv", "all_season", None, None),
                    ("Primacy 4+", "225/45 R17 94W", 460, None, "car", "summer", None, None),
                    ("Pilot Sport 4", "205/55 R16 91W", 450, None, "car", "summer", None, None),
                    ("Agilis HD", "195/65 R15 97T", 380, None, "van", "summer", None, None),
                    ("Pilot Sport 4 SUV", "245/45 R19 102Y", 820, None, "suv", "summer", None, None),
                ],
                "bridgestone": [
                    ("Dueler H/P Sport", "235/50 R18 97V", 540, None, "suv", "summer", "Popular", "badge-blue"),
                    ("Ecopia EP150", "195/65 R15 91H", 320, 380, "car", "summer", "15% OFF", "badge-red"),
                    ("Weather Control A005", "205/55 R16 94V", 410, None, "car", "all_season", "All-Season", "badge-blue"),
                    ("Blizzak LM005", "205/55 R16 91H", 430, None, "car", "winter", "Winter", "badge-blue"),
                    ("Potenza RE050A RFT", "225/45 R17 91W", 560, 650, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("Dueler A/T 001", "225/55 R17 101H", 480, None, "4x4", "all_season", "All-Terrain", "badge-green"),
                    ("Duravis R660", "195/65 R15 95T", 350, None, "van", "summer", None, None),
                    ("Alenza 001", "235/50 R18 97V", 590, None, "suv", "summer", None, None),
                    ("Potenza Race", "245/40 R19 98Y", 890, 1020, "car", "summer", "Track Spec", "badge-red"),
                    ("Turanza 6", "225/45 R17 94Y", 490, None, "car", "summer", "New Gen", "badge-green"),
                    ("Ecopia EP300", "205/55 R16 91V", 360, None, "car", "summer", "Eco Choice", "badge-emerald"),
                    ("Dueler H/T 684 II", "235/50 R18 100H", 520, None, "4x4", "all_season", None, None),
                    ("DriveGuard RFT", "205/55 R16 94W", 460, None, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("Blizzak WS90", "225/50 R17 98H", 490, None, "car", "winter", "Winter", "badge-blue"),
                    ("Turanza T005 RFT", "225/50 R17 94W", 530, None, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("Dueler D697 A/T", "225/55 R17 101S", 470, None, "4x4", "all_season", None, None),
                    ("Duravis Van", "205/55 R16 102T", 410, None, "van", "summer", None, None),
                    ("Potenza Adrenalin RE004", "225/45 R17 94W", 480, None, "car", "summer", "Sport", "badge-blue"),
                    ("Turanza ER300", "195/65 R15 91V", 340, None, "car", "summer", None, None),
                    ("Dueler H/L 400", "235/50 R18 97V", 560, None, "suv", "summer", None, None),
                    ("Ecopia EP500 (BMW i3)", "195/65 R15 88Q", 420, None, "car", "summer", "EV Fitment", "badge-emerald"),
                    ("Potenza S001 RFT", "225/45 R17 91W", 580, None, "car", "run_flat", "Run-Flat", "badge-orange"),
                ],
                "continental": [
                    ("SportContact 7", "245/40 R19 98Y", 880, 990, "car", "summer", "Best Seller", "badge-blue"),
                    ("EcoContact 6", "195/65 R15 91H", 340, None, "car", "summer", "Eco Choice", "badge-emerald"),
                    ("AllSeasonContact", "205/55 R16 94V", 430, None, "car", "all_season", "All-Season", "badge-blue"),
                    ("WinterContact TS 870", "205/55 R16 91T", 450, None, "car", "winter", "Winter", "badge-blue"),
                    ("PremiumContact 6 SSR", "225/45 R17 91W", 560, None, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("CrossContact LX Sport", "235/50 R18 97V", 570, None, "suv", "all_season", "SUV Pick", "badge-blue"),
                    ("CrossContact ATR", "225/55 R17 101H", 520, None, "4x4", "all_season", "All-Terrain", "badge-green"),
                    ("VanContact 200", "195/65 R15 95T", 370, None, "van", "summer", None, None),
                    ("UltraContact", "205/55 R16 91V", 390, None, "car", "summer", "Long Tread", "badge-emerald"),
                    ("SportContact 6", "225/40 R18 92Y", 610, None, "car", "summer", None, None),
                    ("EcoContact 6 Q (EV)", "225/50 R17 98Y", 520, None, "car", "summer", "EV Low Noise", "badge-emerald"),
                    ("ContiCrossContact LX 2", "235/50 R18 100H", 540, None, "4x4", "all_season", None, None),
                    ("WinterContact TS 860 S", "225/45 R17 94V", 510, None, "car", "winter", "Winter", "badge-blue"),
                    ("VanContact 4Season", "205/55 R16 102T", 430, None, "van", "all_season", None, None),
                    ("ContiSportContact 5 SSR", "225/50 R17 94W", 550, None, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("AllSeasonContact 2", "225/45 R17 94Y", 480, None, "car", "all_season", "New Gen", "badge-green"),
                    ("PremiumContact 7", "225/45 R17 94Y", 530, 610, "car", "summer", "New Arrival", "badge-green"),
                    ("CrossContact UHP", "235/50 R18 101V", 620, None, "suv", "summer", None, None),
                    ("ContiPremiumContact 2", "195/65 R15 91V", 330, None, "car", "summer", None, None),
                ],
                "goodyear": [
                    ("Eagle F1 Asymmetric 6", "225/45 R17 94Y", 480, 560, "car", "summer", "Best Seller", "badge-blue"),
                    ("Vector 4Seasons Gen-3", "205/55 R16 94V", 420, None, "car", "all_season", "All-Season", "badge-blue"),
                    ("UltraGrip Performance+", "205/55 R16 91H", 440, None, "car", "winter", "Winter", "badge-blue"),
                    ("Eagle F1 SuperSport", "245/40 R19 98Y", 820, 950, "car", "summer", "Ultra Sport", "badge-red"),
                    ("EfficientGrip 2 SUV", "235/50 R18 101V", 560, None, "suv", "summer", None, None),
                    ("Wrangler All-Terrain Adventure", "225/55 R17 101T", 510, None, "4x4", "all_season", "All-Terrain", "badge-green"),
                    ("EfficientGrip Compact", "195/65 R15 91T", 310, None, "car", "summer", None, None),
                    ("EfficientGrip Cargo 2", "195/65 R15 95T", 360, None, "van", "summer", None, None),
                    ("Eagle F1 Asymmetric 5 ROF", "225/50 R17 98Y", 570, None, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("Wrangler DuraTrac", "235/50 R18 101S", 640, None, "4x4", "all_season", "Rugged 4x4", "badge-blue"),
                    ("Eagle Sport All-Season", "205/55 R16 91V", 380, None, "car", "all_season", None, None),
                    ("EfficientGrip Performance 2", "225/45 R17 94W", 460, None, "car", "summer", "Long Life", "badge-emerald"),
                    ("Eagle F1 Asymmetric 3", "225/40 R18 92Y", 550, None, "car", "summer", None, None),
                    ("UltraGrip 9+", "195/65 R15 91T", 340, None, "car", "winter", "Winter", "badge-blue"),
                    ("Vector 4Seasons SUV Gen-3", "235/50 R18 101V", 590, None, "suv", "all_season", None, None),
                    ("Wrangler SilentArmor", "225/55 R17 101T", 530, None, "4x4", "all_season", None, None),
                    ("EfficientGrip ROF", "205/55 R16 91V", 450, None, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("Eagle F1 Asymmetric 6", "235/50 R18 101Y", 620, None, "car", "summer", "Popular", "badge-blue"),
                    ("Eagle Touring", "225/50 R17 94V", 470, None, "car", "all_season", None, None),
                    ("UltraGrip Ice 2", "205/55 R16 94T", 430, None, "car", "winter", "Winter", "badge-blue"),
                    ("Cargo Vector 2", "195/65 R15 97T", 370, None, "van", "all_season", None, None),
                ],
                "pirelli": [
                    ("P Zero (PZ4)", "245/40 R19 98Y", 890, 1050, "car", "summer", "Ultra High Perf", "badge-red"),
                    ("Cinturato All Season SF2", "205/55 R16 94V", 440, None, "car", "all_season", "All-Season", "badge-blue"),
                    ("Winter Sottozero 3", "205/55 R16 91H", 470, None, "car", "winter", "Winter", "badge-blue"),
                    ("Cinturato P7 Run Flat", "225/45 R17 91W", 540, None, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("Scorpion Verde All Season", "235/50 R18 97V", 580, None, "suv", "all_season", "SUV Choice", "badge-blue"),
                    ("Scorpion ATR", "225/55 R17 101T", 530, None, "4x4", "all_season", "All-Terrain", "badge-green"),
                    ("Carrier", "195/65 R15 95T", 360, None, "van", "summer", None, None),
                    ("P Zero Corsa", "245/45 R19 102Y", 1080, 1250, "car", "summer", "Motorsport", "badge-red"),
                    ("Cinturato P1 Verde", "195/65 R15 91H", 320, None, "car", "summer", "Eco Value", "badge-emerald"),
                    ("Scorpion All Terrain Plus", "235/50 R18 101H", 640, None, "4x4", "all_season", "Rugged Offroad", "badge-blue"),
                    ("P Zero Elect (EV)", "235/50 R18 101Y", 730, None, "car", "summer", "EV Special", "badge-emerald"),
                    ("Winter 210 SnowControl 3", "195/65 R15 91T", 380, None, "car", "winter", "Winter", "badge-blue"),
                    ("P Zero Rosso", "225/40 R18 92Y", 620, None, "car", "summer", None, None),
                    ("Carrier All Season", "205/55 R16 102T", 420, None, "van", "all_season", None, None),
                    ("Scorpion Zero All Season", "235/50 R18 101V", 610, None, "suv", "all_season", None, None),
                    ("P Zero Run Flat", "225/50 R17 94W", 570, None, "car", "run_flat", "Run-Flat", "badge-orange"),
                    ("Cinturato P7 (P7C2)", "225/45 R17 94Y", 490, None, "car", "summer", "Special Offer", "badge-orange"),
                ],
                "yokohama": [
                    ("Advan Sport V107", "245/40 R19 98Y", 820, 930, "car", "summer", "Flagship Sport", "badge-red"),
                    ("BluEarth-GT AE51", "205/55 R16 91V", 380, None, "car", "summer", "Popular", "badge-blue"),
                    ("BluEarth-4S AW21", "205/55 R16 94V", 420, None, "car", "all_season", "All-Season", "badge-blue"),
                    ("Geolandar A/T G015", "225/55 R17 101H", 510, None, "4x4", "all_season", "All-Terrain", "badge-green"),
                    ("Geolandar CV G058", "235/50 R18 97V", 550, None, "suv", "all_season", None, None),
                    ("BluEarth-Van RY55", "195/65 R15 95T", 340, None, "van", "summer", None, None),
                    ("BluEarth-Es ES32", "195/65 R15 91H", 295, None, "car", "summer", "Economy", "badge-emerald"),
                    ("Advan Fleva V701", "225/45 R17 94W", 460, None, "car", "summer", None, None),
                    ("iceGUARD iG60", "205/55 R16 91Q", 410, None, "car", "winter", "Winter", "badge-blue"),
                    ("Geolandar X-AT", "235/50 R18 101Q", 630, None, "4x4", "all_season", "Off-Road Heavy", "badge-blue"),
                    ("Advan Neova AD09", "225/40 R18 92W", 690, None, "car", "summer", "Club Sport", "badge-red"),
                ]
            }

            all_products = list(base_16)
            cur_order = 17

            for brand_slug, items in brand_extensions.items():
                for item in items:
                    name, size, price, list_price, vtype, ttype, badge, badge_cls = item
                    all_products.append({
                        "model": name,
                        "brand": brand_slug,
                        "size": size,
                        "price": float(price),
                        "list_price": float(list_price) if list_price else None,
                        "rating": round(4.2 + ((cur_order * 7) % 7) * 0.1, 1),
                        "reviews": 25 + (cur_order * 13) % 110,
                        "badge": badge,
                        "badge_class": badge_cls,
                        "vehicle_type": vtype,
                        "tire_type": ttype,
                        "image": f"/static/assets/images/products/tyre_{(cur_order % 3) + 1}.jpg",
                        "sort_order": cur_order
                    })
                    cur_order += 1

            # Cap at exactly 124 products
            all_products = all_products[:124]
            # Ensure sort_order 1 to 124
            for idx, p in enumerate(all_products):
                p['sort_order'] = idx + 1

            print(f"Total products to seed: {len(all_products)}")

            # Delete existing products with sort_order <= 124
            cur.execute("DELETE FROM products WHERE sort_order <= 124")

            for p in all_products:
                b_info = brands.get(p['brand'].lower())
                brand_id = b_info['id'] if b_info else None
                b_name = b_info['name'] if b_info else p['brand'].title()
                b_logo = b_info['logo'] if b_info else f"/static/assets/images/brands/{p['brand'].lower()}.svg"

                is_runflat = 1 if p['tire_type'] == 'run_flat' else 0
                db_tire_type = 'summer' if p['tire_type'] == 'run_flat' else p['tire_type']

                attr = {
                    "size": p['size'],
                    "rating": p['rating'],
                    "reviews": p['reviews'],
                    "badge": p['badge'],
                    "badge_class": p['badge_class'],
                    "season": 'Run-Flat' if is_runflat else p['tire_type'].replace('_', ' ').title(),
                    "run_flat": is_runflat,
                    "brand_logo": b_logo
                }

                slug = f"{p['brand'].lower()}-{p['model'].lower().replace(' ', '-').replace('/', '-').replace('+', '-plus')}-{p['sort_order']}"
                name_json = json.dumps({"en": f"{b_name} {p['model']}"}, ensure_ascii=False)
                desc_json = json.dumps({"en": f"Genuine {b_name} {p['model']} tyre size {p['size']}. Official UAE GCC spec warranty, free fitting at certified garages or doorstep mobile van."}, ensure_ascii=False)

                cur.execute("""
                    INSERT INTO products (
                        website_id, attribute_set_id, sku, display_name, slug, name, description,
                        price, list_price, currency, stock_qty, stock_status,
                        tire_size_label, vehicle_type, tire_type, run_flat, brand_id, image_path,
                        attributes_json, sort_order, status, visibility,
                        created_at, updated_at
                    ) VALUES (
                        1, 1, %s, %s, %s, %s, %s,
                        %s, %s, 'AED', 50, 'in_stock',
                        %s, %s, %s, %s, %s, %s,
                        %s, %s, 'active', 'visible',
                        NOW(), NOW()
                    )
                """, (
                    f"SKU-{p['brand'].upper()[:3]}-{p['sort_order']:03d}",
                    p['model'],
                    slug,
                    name_json,
                    desc_json,
                    Decimal(str(p['price'])),
                    Decimal(str(p['list_price'])) if p['list_price'] else None,
                    p['size'],
                    p['vehicle_type'],
                    db_tire_type,
                    is_runflat,
                    brand_id,
                    p['image'],
                    json.dumps(attr, ensure_ascii=False),
                    p['sort_order']
                ))

            conn.commit()
            print(f"SUCCESS: Seeded exactly {len(all_products)} catalog products into MySQL!")

            # Verify total count
            cur.execute("SELECT count(*) as total FROM products WHERE deleted_at IS NULL AND status = 'active'")
            total = cur.fetchone()['total']
            print(f"Total active products in DB: {total}")

    finally:
        conn.close()

if __name__ == '__main__':
    seed_124_products()
