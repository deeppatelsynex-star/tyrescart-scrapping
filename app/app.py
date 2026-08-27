import os
import sys

# Ensure app directory, submodules, and project root are always in sys.path
_app_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_app_dir)
_scraperapp_dir = os.path.join(_app_dir, 'scraperapp')
_visionadmin_dir = os.path.join(_app_dir, 'visionadmin')
_siteapp_dir = os.path.join(_app_dir, 'siteapp')
_models_dir = os.path.join(_app_dir, 'models')
_scrapers_dir = os.path.join(_root_dir, 'scrapers')
for _p in reversed([_app_dir, _root_dir, _scraperapp_dir, _visionadmin_dir, _siteapp_dir, _models_dir, _scrapers_dir]):
    if _p in sys.path:
        sys.path.remove(_p)
    sys.path.insert(0, _p)

from datetime import timedelta

from flask import Flask, jsonify, render_template, request, session

from scraperapp.tcsadmin import register_tcsadmin_routes
from visionadmin import register_visionadmin_routes
from siteapp import site_bp
from api import register_api_routes

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scrapers'))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)

# High-Performance HTTP Response Compression (Brotli + Gzip)
try:
    from flask_compress import Compress
    Compress(app)
    app.config['COMPRESS_ALGORITHM'] = ['brotli', 'gzip', 'deflate']
    app.config['COMPRESS_MIN_SIZE'] = 500
except ImportError:
    pass

# Flask-CKEditor Integration (Rich Text & Code Snippet / Source Editing)
from flask_ckeditor import CKEditor
app.config['CKEDITOR_PKG_TYPE'] = 'full-all'
app.config['CKEDITOR_SERVE_LOCAL'] = False
app.config['CKEDITOR_HEIGHT'] = 260
app.config['CKEDITOR_ENABLE_CODESNIPPET'] = True
app.config['CKEDITOR_CODE_THEME'] = 'monokai_sublime'
ckeditor = CKEditor(app)

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-insecure-key-set-FLASK_SECRET_KEY-in-production')
app.permanent_session_lifetime = timedelta(days=7)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800  # 7 days browser cache for static files


@app.context_processor
def inject_i18n():
    """Provides Flask-Babel style translation helper _() for EN and AR locales."""
    def _(text):
        locale = session.get('site_locale', request.args.get('locale', 'en'))
        if locale == 'ar':
            translations = {
                'Home': 'الرئيسية',
                'Blog': 'المدونة',
                'Breadcrumb': 'مسار التنقل',
                'Pagination': 'صفحات المقالات',
                'Explore Our Blog — Tyre Advice & Car Maintenance Tips': 'استكشف مدونتنا — نصائح الإطارات وصيانة السيارات',
                'Items': 'عناصر',
                'to': 'إلى',
                'of': 'من',
                'total': 'إجمالي',
                'Show': 'عرض',
                'Previous': 'السابق',
                'Next': 'التالي',
                'Read Guide': 'اقرأ الدليل',
                'Featured': 'مميز',
                'No Results': 'لا توجد نتائج',
                'No articles found matching your criteria': 'لم يتم العثور على مقالات مطابقة لبحثك',
                'Try browsing all categories or searching with different keywords.': 'جرّب تصفح جميع الفئات أو البحث بكلمات أخرى.',
                'View All Articles': 'عرض جميع المقالات'
            }
            return translations.get(text, text)
        return text
    return dict(_=_)


@app.after_request
def add_performance_headers(response):
    """Adds caching headers for static assets and enables keep-alive."""
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=604800, stale-while-revalidate=86400'
    return response


# ============================================================================
# REGISTER PAGE ROUTES + CENTRALIZED API LAYER
#
#   tcsadmin.py            -> /tcsadmin/*   page routes (scraper admin)
#   Visionadminroute.py    -> /visionadmin/* page routes (CMS)
#   clientroute.py         -> /             page routes (public storefront)
#   api.py                 -> /tcsadmin/api/*, /visionadmin/api/*, /api/*
# ============================================================================

register_tcsadmin_routes(app)
register_visionadmin_routes(app)
app.register_blueprint(site_bp)
register_api_routes(app)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def handle_404_error(e):
    """Gracefully handles unwanted page or API requests by serving custom 404."""
    if request.path.startswith('/tcsadmin/api/') or request.headers.get('Accept') == 'application/json':
        return jsonify({
            'error': 'The requested API resource was not found.',
            'status': 404,
            'path': request.path
        }), 404
    return render_template(
        '404.html',
        page='404',
        requested_path=request.path,
        user_name=session.get('name'),
        user_email=session.get('email'),
        user_role=session.get('role'),
        user_avatar=session.get('avatar'),
        unread_notifications=0,
        notifications=[]
    ), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8090))
    app.run(host="0.0.0.0", port=port, debug=True)
