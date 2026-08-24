"""
vison_api.py - CMS REST API endpoints for /visonadmin
Handles pages, sections, media library, and site settings for the TyresVision storefront.
"""

from flask import jsonify, request, session
from auth import login_required_api, require_csrf

DEFAULT_PAGES = [
    {
        "id": "home",
        "title": "Home Page",
        "slug": "/",
        "status": "Published",
        "last_edited": "24 Aug 2026",
        "sections": [
            {"id": "hero", "name": "Hero Section", "badge": "Dubai • Abu Dhabi • Sharjah • Ajman", "headline": "Buy tyres online. Fitted locally across the UAE.", "cta_text": "WhatsApp for a quote"},
            {"id": "stats", "name": "Key Metrics Bar", "stats": ["60+ Tyre brands", "7,000+ Products", "25+ Locations", "10+ Mobile Vans"]},
            {"id": "why", "name": "Why Us (6 Feature Cards)", "count": 6},
            {"id": "services", "name": "Full Car Care Services Grid", "count": 16},
            {"id": "how", "name": "How It Works (4 Steps)", "count": 4},
            {"id": "brands", "name": "60+ Brands Logo List", "count": 21},
            {"id": "faq", "name": "Frequently Asked Questions", "count": 6}
        ]
    },
    {
        "id": "about",
        "title": "About Us",
        "slug": "/about",
        "status": "Draft",
        "last_edited": "22 Aug 2026",
        "sections": []
    },
    {
        "id": "contact",
        "title": "Contact & Locations",
        "slug": "/contact",
        "status": "Draft",
        "last_edited": "20 Aug 2026",
        "sections": []
    }
]

DEFAULT_MEDIA = [
    {"id": "m1", "name": "online-tyres-shop-dubai.png", "url": "/static/assets/images/favicon-color.webp", "type": "image/png", "size": "124 KB", "uploaded": "24 Aug 2026"},
    {"id": "m2", "name": "tyresvision-hero-banner.jpg", "url": "/static/assets/images/favicon-color.webp", "type": "image/jpeg", "size": "340 KB", "uploaded": "23 Aug 2026"},
    {"id": "m3", "name": "mobile-fitting-van.jpg", "url": "/static/assets/images/favicon-color.webp", "type": "image/jpeg", "size": "210 KB", "uploaded": "22 Aug 2026"},
    {"id": "m4", "name": "brand-logos-strip.svg", "url": "/static/assets/images/favicon-color.webp", "type": "image/svg+xml", "size": "45 KB", "uploaded": "20 Aug 2026"}
]

DEFAULT_SETTINGS = {
    "site_name": "TyresVision",
    "tagline": "Buy Tyres Online in Dubai, Abu Dhabi & Sharjah",
    "meta_title": "Buy Tyres Online in Dubai, Abu Dhabi & Sharjah | TyresVision",
    "meta_description": "Buy tyres online from 60+ brands, fitted free at 350+ centres across the UAE or at your door by mobile van. WhatsApp your tyre size for a price in minutes.",
    "whatsapp_number": "+971505069575",
    "phone_number": "+971505069575",
    "contact_email": "support@tyresvision.com",
    "gtm_id": "GTM-MNN5FHT2",
    "primary_color": "#58B31B",
    "dark_color": "#0E1108"
}


def register_vison_api_routes(app):
    """Registers all /visonadmin/api/* endpoints on the Flask application."""

    @app.route('/visonadmin/api/dashboard-stats', methods=['GET'])
    @login_required_api
    def vison_dashboard_stats():
        return jsonify({
            "totalPages": len(DEFAULT_PAGES),
            "publishedPages": len([p for p in DEFAULT_PAGES if p['status'] == 'Published']),
            "totalMedia": len(DEFAULT_MEDIA),
            "siteName": DEFAULT_SETTINGS.get('site_name'),
            "recentPages": DEFAULT_PAGES,
            "recentMedia": DEFAULT_MEDIA[:3]
        })

    @app.route('/visonadmin/api/pages', methods=['GET'])
    @login_required_api
    def vison_get_pages():
        return jsonify({"pages": DEFAULT_PAGES})

    @app.route('/visonadmin/api/pages/<page_id>', methods=['GET'])
    @login_required_api
    def vison_get_page(page_id):
        page = next((p for p in DEFAULT_PAGES if p['id'] == page_id), None)
        if not page:
            return jsonify({"error": "Page not found"}), 404
        return jsonify({"page": page})

    @app.route('/visonadmin/api/pages', methods=['POST'])
    @login_required_api
    @require_csrf
    def vison_create_page():
        data = request.get_json(silent=True) or {}
        title = (data.get('title') or '').strip()
        slug = (data.get('slug') or '').strip()
        if not title or not slug:
            return jsonify({"error": "Title and slug are required."}), 400

        new_page = {
            "id": slug.strip('/').replace('/', '-').lower() or "page",
            "title": title,
            "slug": slug if slug.startswith('/') else f"/{slug}",
            "status": "Draft",
            "last_edited": "Just now",
            "sections": []
        }
        DEFAULT_PAGES.append(new_page)
        return jsonify({"page": new_page, "message": "Page created successfully."}), 201

    @app.route('/visonadmin/api/pages/<page_id>', methods=['PUT'])
    @login_required_api
    @require_csrf
    def vison_update_page(page_id):
        page = next((p for p in DEFAULT_PAGES if p['id'] == page_id), None)
        if not page:
            return jsonify({"error": "Page not found"}), 404

        data = request.get_json(silent=True) or {}
        if 'title' in data:
            page['title'] = data['title']
        if 'status' in data:
            page['status'] = data['status']
        if 'sections' in data:
            page['sections'] = data['sections']
        page['last_edited'] = "Just now"

        return jsonify({"page": page, "message": "Page updated successfully."})

    @app.route('/visonadmin/api/pages/<page_id>', methods=['DELETE'])
    @login_required_api
    @require_csrf
    def vison_delete_page(page_id):
        if page_id == 'home':
            return jsonify({"error": "Cannot delete the default homepage."}), 400
        global DEFAULT_PAGES
        DEFAULT_PAGES = [p for p in DEFAULT_PAGES if p['id'] != page_id]
        return jsonify({"message": "Page deleted successfully."})

    @app.route('/visonadmin/api/media', methods=['GET'])
    @login_required_api
    def vison_get_media():
        return jsonify({"media": DEFAULT_MEDIA})

    @app.route('/visonadmin/api/media', methods=['POST'])
    @login_required_api
    @require_csrf
    def vison_upload_media():
        file = request.files.get('file')
        if not file:
            return jsonify({"error": "No file uploaded."}), 400
        
        new_media = {
            "id": f"m{len(DEFAULT_MEDIA) + 1}",
            "name": file.filename or "upload.png",
            "url": f"/static/assets/images/{file.filename or 'favicon-color.webp'}",
            "type": file.content_type or "image/png",
            "size": "150 KB",
            "uploaded": "Just now"
        }
        DEFAULT_MEDIA.insert(0, new_media)
        return jsonify({"media": new_media, "message": "Media uploaded successfully."}), 201

    @app.route('/visonadmin/api/media/<media_id>', methods=['DELETE'])
    @login_required_api
    @require_csrf
    def vison_delete_media(media_id):
        global DEFAULT_MEDIA
        DEFAULT_MEDIA = [m for m in DEFAULT_MEDIA if m['id'] != media_id]
        return jsonify({"message": "Media asset deleted."})

    @app.route('/visonadmin/api/settings', methods=['GET'])
    @login_required_api
    def vison_get_settings():
        return jsonify({"settings": DEFAULT_SETTINGS})

    @app.route('/visonadmin/api/settings', methods=['PUT'])
    @login_required_api
    @require_csrf
    def vison_update_settings():
        data = request.get_json(silent=True) or {}
        DEFAULT_SETTINGS.update(data)
        return jsonify({"settings": DEFAULT_SETTINGS, "message": "Settings updated successfully."})
