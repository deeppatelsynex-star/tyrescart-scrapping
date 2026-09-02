import json
import sys
import os
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.insert(0, os.path.dirname(__file__))
from db import get_connection

def seed_phase1_data():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            print("🌱 Seeding Phase 1 Master Data...")

            # 1. Seed Websites
            cursor.execute("SELECT id FROM websites WHERE code = 'tyresvision_uae'")
            row = cursor.fetchone()
            if not row:
                cursor.execute("""
                    INSERT INTO websites (code, name, domain, is_default, status, sort_order)
                    VALUES ('tyresvision_uae', 'TyresVision UAE', 'www.tyresvision.com', 1, 'active', 1)
                """)
                website_id_tv = cursor.lastrowid
            else:
                website_id_tv = row['id']

            cursor.execute("SELECT id FROM websites WHERE code = 'tyrescart_b2b'")
            row = cursor.fetchone()
            if not row:
                cursor.execute("""
                    INSERT INTO websites (code, name, domain, is_default, status, sort_order)
                    VALUES ('tyrescart_b2b', 'TyresCart Global B2B', 'b2b.tyresvision.com', 0, 'active', 2)
                """)
                website_id_b2b = cursor.lastrowid
            else:
                website_id_b2b = row['id']

            # 2. Seed Stores
            default_stores = [
                ('dubai_hub', {'en': 'Dubai Central Fitting & Retail Hub', 'ar': 'مركز دبي الرئيسي لتركيب وبيع الإطارات'}, 'Dubai', '+971505069575', 'dubai@tyresvision.com', 1, 1),
                ('abu_dhabi_hub', {'en': 'Abu Dhabi Service Centre', 'ar': 'مركز خدمة أبوظبي'}, 'Abu Dhabi', '+971505069575', 'abudhabi@tyresvision.com', 1, 2),
                ('mobile_vans', {'en': 'UAE Mobile Van Fitting Fleet', 'ar': 'أسطول سيارات التركيب المتنقلة في الإمارات'}, 'All Emirates', '+971505069575', 'mobile@tyresvision.com', 1, 3),
            ]

            store_ids_map = {}
            for code, name_json, emirate, phone, email, is_act, order in default_stores:
                cursor.execute("SELECT id FROM stores WHERE code = %s", (code,))
                r = cursor.fetchone()
                if not r:
                    cursor.execute("""
                        INSERT INTO stores (website_id, code, name, emirate, phone, email, is_active, sort_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (website_id_tv, code, json.dumps(name_json), emirate, phone, email, is_act, order))
                    store_ids_map[code] = cursor.lastrowid
                else:
                    store_ids_map[code] = r['id']

            dubai_store_id = store_ids_map.get('dubai_hub', 1)

            # Update website default_store_id
            cursor.execute("UPDATE websites SET default_store_id = %s WHERE id = %s", (dubai_store_id, website_id_tv))

            # 3. Seed Store Views
            cursor.execute("SELECT id FROM store_views WHERE code = 'dubai_en'")
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO store_views (store_id, website_id, code, name, locale, currency_code, is_active, sort_order)
                    VALUES (%s, %s, 'dubai_en', 'English Storefront', 'en', 'AED', 1, 1)
                """, (dubai_store_id, website_id_tv))

            cursor.execute("SELECT id FROM store_views WHERE code = 'dubai_ar'")
            if not cursor.fetchone():
                cursor.execute("""
                    INSERT INTO store_views (store_id, website_id, code, name, locale, currency_code, is_active, sort_order)
                    VALUES (%s, %s, 'dubai_ar', 'Arabic Storefront (العربية)', 'ar', 'AED', 1, 2)
                """, (dubai_store_id, website_id_tv))

            # 3. Seed Attribute Sets
            attr_sets = [
                ('Passenger Car Tyres', 'passenger_tyres', 'Standard and performance passenger car tyres', 1, 1),
                ('SUV & 4x4 Tyres', 'suv_4x4_tyres', 'All-terrain, highway terrain, and mud-terrain 4x4 tyres', 1, 2),
                ('Commercial Van Tyres', 'commercial_van_tyres', 'Heavy-duty commercial and delivery van tyres', 1, 3),
                ('Alloy Wheels & Rims', 'alloy_wheels', 'Custom passenger and SUV alloy wheels', 0, 4),
                ('Car Batteries', 'car_batteries', 'Automotive starting batteries and AGM batteries', 0, 5),
                ('Car Care Services', 'car_services', 'Fitting, balancing, alignment and maintenance packages', 0, 6)
            ]

            set_ids = {}
            for name, slug, desc, is_sys, order in attr_sets:
                cursor.execute("SELECT id FROM attribute_sets WHERE slug = %s", (slug,))
                r = cursor.fetchone()
                if not r:
                    cursor.execute("""
                        INSERT INTO attribute_sets (name, slug, description, is_system, sort_order)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (name, slug, desc, is_sys, order))
                    set_ids[slug] = cursor.lastrowid
                else:
                    set_ids[slug] = r['id']

            passenger_set_id = set_ids.get('passenger_tyres')

            # 4. Seed Attribute Groups for Passenger Car Tyres
            groups = [
                ('dimensions', {'en': 'Dimensions & Sizing', 'ar': 'الأبعاد والمقاسات'}, 1),
                ('performance', {'en': 'Performance & Ratings', 'ar': 'الأداء والمواصفات'}, 2),
                ('eu_label', {'en': 'EU Tyre Label Grades', 'ar': 'بطاقة كفاءة الطاقة الأوروبية'}, 3),
                ('warranty_origin', {'en': 'Origin, DOT & Warranty', 'ar': 'المنشأ وسنة الصنع والضمان'}, 4)
            ]

            group_ids = {}
            for code, name_json, order in groups:
                cursor.execute("SELECT id FROM attribute_groups WHERE attribute_set_id = %s AND code = %s", (passenger_set_id, code))
                r = cursor.fetchone()
                if not r:
                    cursor.execute("""
                        INSERT INTO attribute_groups (attribute_set_id, name, code, sort_order)
                        VALUES (%s, %s, %s, %s)
                    """, (passenger_set_id, json.dumps(name_json), code, order))
                    group_ids[code] = cursor.lastrowid
                else:
                    group_ids[code] = r['id']

            # 5. Seed Core Attributes
            attributes_data = [
                # (code, name_json, type, scope, unit, is_req, is_filt, is_search, group_code, sort_order)
                ('width', {'en': 'Width', 'ar': 'العرض'}, 'select', 'global', 'mm', 1, 1, 1, 'dimensions', 1),
                ('aspect_ratio', {'en': 'Profile / Aspect Ratio', 'ar': 'نسبة الارتفاع'}, 'select', 'global', '%', 1, 1, 1, 'dimensions', 2),
                ('rim_size', {'en': 'Rim Size', 'ar': 'مقاس الجنط'}, 'select', 'global', 'inch', 1, 1, 1, 'dimensions', 3),
                ('speed_index', {'en': 'Speed Rating', 'ar': 'مؤشر السرعة'}, 'select', 'global', 'km/h', 1, 1, 1, 'performance', 1),
                ('load_index', {'en': 'Load Index', 'ar': 'مؤشر الحمولة'}, 'select', 'global', 'kg', 1, 1, 1, 'performance', 2),
                ('run_flat', {'en': 'Run-Flat Technology', 'ar': 'إطار مقاوم للثقوب (Run-Flat)'}, 'boolean', 'global', None, 0, 1, 0, 'performance', 3),
                ('wet_grip', {'en': 'Wet Grip Class', 'ar': 'التماسك على الأسطح الرطبة'}, 'select', 'global', None, 0, 1, 0, 'eu_label', 1),
                ('fuel_efficiency', {'en': 'Fuel Efficiency Class', 'ar': 'كفاءة استهلاك الوقود'}, 'select', 'global', None, 0, 1, 0, 'eu_label', 2),
                ('noise_db', {'en': 'Noise Level', 'ar': 'مستوى الضوضاء'}, 'number', 'global', 'dB', 0, 1, 0, 'eu_label', 3),
                ('manufacturing_year', {'en': 'DOT / Production Year', 'ar': 'سنة الصنع (DOT)'}, 'select', 'store', 'year', 0, 1, 0, 'warranty_origin', 1),
                ('country_of_origin', {'en': 'Country of Origin', 'ar': 'بلد المنشأ'}, 'select', 'global', None, 0, 1, 1, 'warranty_origin', 2),
                ('warranty_years', {'en': 'Official Warranty', 'ar': 'الضمان الرسمي'}, 'number', 'store', 'years', 0, 0, 0, 'warranty_origin', 3),
                ('homologation', {'en': 'OEM Approval Mark', 'ar': 'اعتماد الشركة المصنعة'}, 'text', 'global', None, 0, 1, 1, 'performance', 4),
            ]

            attr_ids = {}
            for code, name_json, attr_type, scope, unit, is_req, is_filt, is_search, grp_code, order in attributes_data:
                cursor.execute("SELECT id FROM attributes WHERE code = %s", (code,))
                r = cursor.fetchone()
                if not r:
                    cursor.execute("""
                        INSERT INTO attributes (code, name, type, scope, unit, is_required, is_filterable, is_searchable, is_system, sort_order)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 1, %s)
                    """, (code, json.dumps(name_json), attr_type, scope, unit, is_req, is_filt, is_search, order))
                    attr_id = cursor.lastrowid
                else:
                    attr_id = r['id']
                attr_ids[code] = attr_id

                # Link to group
                grp_id = group_ids.get(grp_code)
                if grp_id:
                    cursor.execute("SELECT id FROM attribute_group_attributes WHERE attribute_group_id = %s AND attribute_id = %s", (grp_id, attr_id))
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO attribute_group_attributes (attribute_group_id, attribute_id, sort_order)
                            VALUES (%s, %s, %s)
                        """, (grp_id, attr_id, order))

            # 6. Seed Options for Select Attributes
            options_map = {
                'width': [str(w) for w in [155, 165, 175, 185, 195, 205, 215, 225, 235, 245, 255, 265, 275, 285, 295, 305, 315]],
                'aspect_ratio': [str(a) for a in [30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85]],
                'rim_size': [str(r) for r in [13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24]],
                'speed_index': [
                    ('T', {'en': 'T (Up to 190 km/h)', 'ar': 'T (حتى 190 كم/س)'}),
                    ('H', {'en': 'H (Up to 210 km/h)', 'ar': 'H (حتى 210 كم/س)'}),
                    ('V', {'en': 'V (Up to 240 km/h)', 'ar': 'V (حتى 240 كم/س)'}),
                    ('W', {'en': 'W (Up to 270 km/h)', 'ar': 'W (حتى 270 كم/س)'}),
                    ('Y', {'en': 'Y (Up to 300 km/h)', 'ar': 'Y (حتى 300 كم/س)'}),
                    ('(Y)', {'en': '(Y) (Over 300 km/h)', 'ar': '(Y) (أكثر من 300 كم/س)'})
                ],
                'load_index': [str(l) for l in [82, 84, 88, 91, 92, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 107, 108, 110, 112, 114, 116]],
                'wet_grip': [
                    ('A', {'en': 'Class A (Best in wet)', 'ar': 'الفئة A (الأفضل في الثبات)'}),
                    ('B', {'en': 'Class B', 'ar': 'الفئة B'}),
                    ('C', {'en': 'Class C', 'ar': 'الفئة C'}),
                    ('D', {'en': 'Class D', 'ar': 'الفئة D'}),
                    ('E', {'en': 'Class E', 'ar': 'الفئة E'})
                ],
                'fuel_efficiency': [
                    ('A', {'en': 'Class A (Highest efficiency)', 'ar': 'الفئة A (الأعلى كفاءة)'}),
                    ('B', {'en': 'Class B', 'ar': 'الفئة B'}),
                    ('C', {'en': 'Class C', 'ar': 'الفئة C'}),
                    ('D', {'en': 'Class D', 'ar': 'الفئة D'}),
                    ('E', {'en': 'Class E', 'ar': 'الفئة E'})
                ],
                'manufacturing_year': [('2024', {'en': '2024', 'ar': '2024'}), ('2025', {'en': '2025', 'ar': '2025'}), ('2026', {'en': '2026', 'ar': '2026'})],
                'country_of_origin': [
                    ('Japan', {'en': 'Japan', 'ar': 'اليابان'}),
                    ('Germany', {'en': 'Germany', 'ar': 'ألمانيا'}),
                    ('France', {'en': 'France', 'ar': 'فرنسا'}),
                    ('USA', {'en': 'United States', 'ar': 'الولايات المتحدة'}),
                    ('Italy', {'en': 'Italy', 'ar': 'إيطاليا'}),
                    ('South Korea', {'en': 'South Korea', 'ar': 'كوريا الجنوبية'}),
                    ('Thailand', {'en': 'Thailand', 'ar': 'تايلاند'}),
                    ('Indonesia', {'en': 'Indonesia', 'ar': 'إندونيسيا'}),
                    ('Turkey', {'en': 'Turkey', 'ar': 'تركيا'}),
                    ('Poland', {'en': 'Poland', 'ar': 'بولندا'}),
                    ('China', {'en': 'China', 'ar': 'الصين'})
                ]
            }

            for attr_code, opts in options_map.items():
                attr_id = attr_ids.get(attr_code)
                if not attr_id:
                    continue
                for idx, opt in enumerate(opts, start=1):
                    if isinstance(opt, tuple):
                        val, label_json = opt
                    else:
                        val = str(opt)
                        label_json = {'en': str(opt), 'ar': str(opt)}

                    cursor.execute("SELECT id FROM attribute_options WHERE attribute_id = %s AND value = %s", (attr_id, val))
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO attribute_options (attribute_id, value, label, sort_order)
                            VALUES (%s, %s, %s, %s)
                        """, (attr_id, val, json.dumps(label_json), idx))

            conn.commit()
            print("✅ Phase 1 master data seeded successfully!")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_phase1_data()
