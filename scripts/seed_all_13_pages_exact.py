"""
scripts/seed_all_13_pages_exact.py
Seeds all 13 CMS pages in the MySQL `pages` table with exact specifications,
metadata, headings, vehicle tables, local angles, and internal link anchors
from 'TyresVision-13-Page-Build-Plan 1.docx'.
"""

import os
import sys
import json

# Setup paths
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from db import get_connection

from page_builders_mobile import build_page_mobile
from page_builders_ev import build_page_ev
from build_4x4_page_clean import build_page_off_road_4x4
from page_builders_brands import build_page_brands
from page_builders_sizes import build_page_sizes
from page_builders_cars import build_page_cars
from page_builders_locations import (
    build_page_dubai,
    build_page_abu_dhabi,
    build_page_sharjah,
    build_page_ajman,
    build_page_rak,
    build_page_fujairah,
    build_page_uaq
)

DEFAULT_HERO_BG = "/static/uploads/pages/banner_1788954653_64dd43ed.png"

PAGES_SPECS = [
    # 1. Mobile Tyre Fitting
    {
        'slug': 'mobile-tyre-fitting',
        'title': {'en': 'Mobile Tyre Fitting in Dubai and Abu Dhabi'},
        'seo_title': {'en': 'Mobile Tyre Fitting in Dubai & Abu Dhabi | TyresVision'},
        'meta_description': {'en': 'Mobile tyre fitting at your home, office or car park across Dubai and Abu Dhabi. Send your tyre size and location on WhatsApp for a price in minutes.'},
        'generator': build_page_mobile
    },
    # 2. EV Tyres
    {
        'slug': 'ev-tyres',
        'title': {'en': 'EV and Hybrid Tyres in the UAE'},
        'seo_title': {'en': 'EV Tyres in Dubai & Abu Dhabi | Tesla, BYD | TyresVision'},
        'meta_description': {'en': 'Tyres for Tesla, BYD, hybrid and electric cars in the UAE. Correct load rating and low rolling resistance, fitted free at a centre near you.'},
        'generator': build_page_ev
    },
    # 3. Off-Road & 4x4 Tyres
    {
        'slug': 'off-road-4x4-tyres',
        'title': {'en': 'Off-Road and 4x4 Tyres in the UAE'},
        'seo_title': {'en': 'Off-Road & 4x4 Tyres in the UAE | TyresVision'},
        'meta_description': {'en': 'Off-road, all-terrain and highway 4x4 tyres for Patrol, Land Cruiser and Prado. Honest advice on desert versus tarmac, fitted free across the UAE.'},
        'generator': build_page_off_road_4x4
    },
    # 4. Tyre Brands
    {
        'slug': 'tyre-brands',
        'title': {'en': 'Tyre Brands We Supply Across the UAE'},
        'seo_title': {'en': 'Tyre Brands in the UAE | 60+ Brands | TyresVision'},
        'meta_description': {'en': 'Compare 60+ tyre brands available in the UAE. Premium, mid-range and budget explained, with honest advice on which suits UAE heat and your mileage.'},
        'generator': build_page_brands
    },
    # 5. Tyre Sizes
    {
        'slug': 'tyre-sizes',
        'title': {'en': 'Tyre Sizes and Prices in the UAE'},
        'seo_title': {'en': 'Tyre Sizes in the UAE | Find Your Size | TyresVision'},
        'meta_description': {'en': 'Find your tyre size and see UAE prices. Popular sizes from 195/65 R15 to 305/40 R22, what each number means, and which cars use them.'},
        'generator': build_page_sizes
    },
    # 6. Tyres by Car Model
    {
        'slug': 'tyres-by-car',
        'title': {'en': 'Find Tyres for Your Car Model'},
        'seo_title': {'en': 'Tyres by Car Model in the UAE | TyresVision'},
        'meta_description': {'en': 'Find the right tyre size for your car. Land Cruiser, Patrol, Corolla, Camry, Civic, Tesla and more, with UAE prices and free fitting near you.'},
        'generator': build_page_cars
    },
    # 7. Tyre Shop Dubai
    {
        'slug': 'tyre-shop-dubai',
        'title': {'en': 'Tyre Shop in Dubai — Tyres Fitted Near You'},
        'seo_title': {'en': 'Tyre Shop in Dubai | Free Fitting Near You | TyresVision'},
        'meta_description': {'en': 'Looking for a tyre shop in Dubai? 60+ brands delivered and fitted free at a centre near you, from Al Quoz to Deira. Send your size on WhatsApp.'},
        'generator': build_page_dubai
    },
    # 8. Tyre Shop Abu Dhabi
    {
        'slug': 'tyre-shop-abu-dhabi',
        'title': {'en': 'Tyre Shop in Abu Dhabi — Tyres Fitted Near You'},
        'seo_title': {'en': 'Tyre Shop in Abu Dhabi | Free Fitting | TyresVision'},
        'meta_description': {'en': 'Looking for a tyre shop in Abu Dhabi? 60+ brands delivered and fitted free at a centre near you, from Musaffah to Khalifa City. WhatsApp your size.'},
        'generator': build_page_abu_dhabi
    },
    # 9. Tyre Shop Sharjah
    {
        'slug': 'tyre-shop-sharjah',
        'title': {'en': 'Tyre Shop in Sharjah — Tyres Delivered and Fitted'},
        'seo_title': {'en': 'Tyre Shop in Sharjah | Free Fitting | TyresVision'},
        'meta_description': {'en': 'Tyre shop serving Sharjah. 60+ brands delivered free to a fitting centre near you in Al Nahda, Al Majaz or Muwaileh. WhatsApp your tyre size.'},
        'generator': build_page_sharjah
    },
    # 10. Tyre Shop Ajman
    {
        'slug': 'tyre-shop-ajman',
        'title': {'en': 'Tyre Shop in Ajman — Tyres Delivered and Fitted'},
        'seo_title': {'en': 'Tyre Shop in Ajman | Tyres Delivered & Fitted | TyresVision'},
        'meta_description': {'en': 'Tyre shop serving Ajman. 60+ brands delivered free to a fitting centre near you in Al Nuaimiya, Al Jurf or Ajman city. WhatsApp your tyre size.'},
        'generator': build_page_ajman
    },
    # 11. Tyre Shop Ras Al Khaimah
    {
        'slug': 'tyre-shop-ras-al-khaimah',
        'title': {'en': 'Tyre Shop in Ras Al Khaimah'},
        'seo_title': {'en': 'Tyre Shop in Ras Al Khaimah | Tyres Fitted | TyresVision'},
        'meta_description': {'en': 'Tyre shop serving Ras Al Khaimah. 60+ brands delivered free to a fitting centre near you, from Al Nakheel to Al Hamra. WhatsApp your tyre size.'},
        'generator': build_page_rak
    },
    # 12. Tyre Shop Fujairah
    {
        'slug': 'tyre-shop-fujairah',
        'title': {'en': 'Tyre Shop in Fujairah and the East Coast'},
        'seo_title': {'en': 'Tyre Shop in Fujairah | Tyres Fitted | TyresVision'},
        'meta_description': {'en': 'Tyre shop serving Fujairah and the east coast. 60+ brands delivered free to a fitting centre near you. Send your tyre size on WhatsApp.'},
        'generator': build_page_fujairah
    },
    # 13. Tyre Shop Umm Al Quwain
    {
        'slug': 'tyre-shop-umm-al-quwain',
        'title': {'en': 'Tyre Shop in Umm Al Quwain'},
        'seo_title': {'en': 'Tyre Shop in Umm Al Quwain | Tyres Fitted | TyresVision'},
        'meta_description': {'en': 'Tyre shop serving Umm Al Quwain. 60+ brands delivered free to a fitting centre near you, with mobile fitting on request. WhatsApp your size.'},
        'generator': build_page_uaq
    }
]

def seed_all_pages():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("=================================================================")
            print("Seeding all 13 CMS pages matching TyresVision-13-Page-Build-Plan")
            print("=================================================================")

            for spec in PAGES_SPECS:
                slug = spec['slug']
                title_json = json.dumps(spec['title'], ensure_ascii=False)
                seo_title_json = json.dumps(spec['seo_title'], ensure_ascii=False)
                meta_desc_json = json.dumps(spec['meta_description'], ensure_ascii=False)

                # Generate content
                html_body = spec['generator']()
                content_json = json.dumps({'en': html_body}, ensure_ascii=False)

                # Check if exists
                cur.execute("SELECT id FROM pages WHERE slug = %s", (slug,))
                row = cur.fetchone()

                if row:
                    cur.execute("""
                        UPDATE pages
                        SET title = %s,
                            seo_title = %s,
                            meta_description = %s,
                            content = %s,
                            banner_image = %s,
                            is_active = 1,
                            deleted_at = NULL,
                            updated_at = NOW()
                        WHERE slug = %s
                    """, (title_json, seo_title_json, meta_desc_json, content_json, DEFAULT_HERO_BG, slug))
                    print(f"  [UPDATED]  /{slug} (ID: {row['id']})")
                else:
                    cur.execute("""
                        INSERT INTO pages (
                            slug, title, seo_title, meta_description, content,
                            banner_image, is_active, created_at, updated_at
                        ) VALUES (
                            %s, %s, %s, %s, %s,
                            %s, 1, NOW(), NOW()
                        )
                    """, (slug, title_json, seo_title_json, meta_desc_json, content_json, DEFAULT_HERO_BG))
                    print(f"  [INSERTED] /{slug}")

            conn.commit()
            print("=================================================================")
            print("All 13 pages successfully synchronized into MySQL `pages` table!")
            print("=================================================================")
    finally:
        conn.close()

if __name__ == '__main__':
    seed_all_pages()
