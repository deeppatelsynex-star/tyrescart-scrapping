# app/siteapp/routes.py - TyresVision Customer Storefront Blueprint ('site')
from flask import Blueprint, render_template, request, session, abort, redirect, url_for
from models.page import Page

site_bp = Blueprint('site', __name__)


def _get_locale():
    req_locale = request.args.get('locale')
    if req_locale in ('en', 'ar'):
        session['site_locale'] = req_locale
        return req_locale
    return session.get('site_locale', 'en')


# ============================================================================
# 1. HOME & LANDING
# ============================================================================

@site_bp.route('/')
@site_bp.route('/home')
def home():
    """Client storefront home landing page."""
    return render_template('Client/Home.html')


# ============================================================================
# 2. STATIC CMS PAGES
# ============================================================================

@site_bp.route('/about-us')
def about_us():
    locale = _get_locale()
    page = Page.find_by_slug('about-us')
    if page:
        return render_template('Client/Page.html', page=page, locale=locale)
    return redirect(url_for('site.home', locale=locale))


@site_bp.route('/page/<slug>')
@site_bp.route('/<slug>')
def page_detail(slug):
    """Generic static CMS content page reader."""
    if slug in ('tcsadmin', 'visionadmin', 'visonadmin', 'admin', 'static', 'api', 'login', 'logout', 'forgot-password', 'reset-password', 'favicon.ico'):
        abort(404)

    locale = _get_locale()
    page = Page.find_by_slug(slug)
    if page:
        return render_template('Client/Page.html', page=page, locale=locale)

    abort(404)
