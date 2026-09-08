# app/siteapp/clientroute.py - TyresVision Customer Storefront Blueprint ('site')
#
# Serves the public client-facing HTML pages only (home, blog listing/detail,
# About Us, generic CMS pages). The public JSON API endpoints that used to
# live in this file (/api/blogs, /api/blogs/<slug>) now live in the unified
# app/api.py alongside the tcsadmin and visionadmin APIs.
import json
import os
from datetime import datetime, timedelta
from flask import Blueprint, current_app, render_template, request, session, abort, redirect, make_response, send_from_directory
from models.blog import Blog
from models.page import Page
from models.page_section import PageSection
from models.setting import Setting

from i18n import (
    get_locale as _get_locale,
    is_rtl,
    localize_value,
    translate,
    get_supported_locales,
)

site_bp = Blueprint('site', __name__)

# This file is app/siteapp/clientroute.py, so the project root (where
# robots.txt/sitemap.xml live, alongside app/, scrapers/, templates/) is
# two directories up (siteapp -> app -> root).
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# --- SEO: robots.txt / sitemap.xml ---
# These are plain files sitting at the project root (not under static/), so
# without an explicit route the catch-all page_detail('/<slug>') route below
# intercepts /robots.txt and /sitemap.xml first, finds no matching CMS page
# or blog, and 404s -- even though the files exist on disk.
@site_bp.route('/robots.txt')
def robots_txt():
    return send_from_directory(BASE_DIR, 'robots.txt', mimetype='text/plain')


@site_bp.route('/sitemap.xml')
def sitemap_xml():
    return send_from_directory(BASE_DIR, 'sitemap.xml', mimetype='application/xml')


# ============================================================================
# CLIENT STOREFRONT (HOME, BLOG, STATIC CMS PAGES WITH DYNAMIC MULTI-LOCALE)
# ============================================================================

# --- HOME ROUTES ---
def _get_home_sections(locale: str = None):
    """Helper to fetch and localize all active home page sections from DB."""
    try:
        from models.page_section import PageSection
        loc = locale or _get_locale()
        raw_sections = PageSection.all_for_page('home', include_inactive=False)
        return [PageSection.to_localized_dict(s, locale=loc) for s in raw_sections]
    except Exception as err:
        current_app.logger.warning(f"Error fetching home page sections from DB: {err}")
        return []


@site_bp.route('/')
@site_bp.route('/home')
def home():
    """Client storefront home landing page with dynamic locale support."""
    locale = _get_locale()
    sections = _get_home_sections(locale)
    resp = make_response(render_template('Client/Home.html', sections=sections, locale=locale))
    resp.set_cookie('site_locale', locale, max_age=31536000, path='/')
    return resp


@site_bp.route('/<string(length=2):lang_code>')
@site_bp.route('/<string(length=2):lang_code>/')
@site_bp.route('/<string(length=2):lang_code>/home')
def home_locale(lang_code):
    """Directly render storefront home for any dynamic locale (e.g. /ar, /de)."""
    code = lang_code.lower()
    page_match = Page.find_by_slug(code)
    if page_match:
        return render_template('Client/AboutUs.html', page=page_match, slug=code, locale=code)
    session['site_locale'] = code
    sections = _get_home_sections(code)
    resp = make_response(render_template('Client/Home.html', sections=sections, locale=code))
    resp.set_cookie('site_locale', code, max_age=31536000, path='/')
    return resp


# --- BLOG LISTING ROUTES ---
@site_bp.route('/<string(length=2):lang_code>/blog')
@site_bp.route('/<string(length=2):lang_code>/blog/')
@site_bp.route('/<string(length=2):lang_code>/blogs')
@site_bp.route('/<string(length=2):lang_code>/blogs/')
def blog_locale(lang_code):
    """Directly render blog listing for any dynamic locale (e.g. /ar/blog, /de/blog)."""
    code = lang_code.lower()
    session['site_locale'] = code
    categories = Blog.distinct_categories(locale=code)
    selected_category = (request.args.get('category') or '').strip()
    resp = make_response(render_template('Client/Blog.html', locale=code, categories=categories, selected_category=selected_category))
    resp.set_cookie('site_locale', code, max_age=31536000, path='/')
    return resp


# --- BLOG DETAIL ROUTES ---
@site_bp.route('/<string(length=2):lang_code>/blog/<slug>')
@site_bp.route('/<string(length=2):lang_code>/blogs/<slug>')
def blog_detail_locale(lang_code, slug):
    """Directly render blog detail for any dynamic locale (e.g. /ar/blog/<slug>)."""
    code = lang_code.lower()
    session['site_locale'] = code
    return _render_blog_detail(slug, code)


@site_bp.route('/blog/<slug>')
@site_bp.route('/blogs/<slug>')
def blog_detail_default(slug):
    """Default single blog detail route."""
    locale = _get_locale()
    return _render_blog_detail(slug, locale)


def _render_blog_detail(slug, locale):
    blog = Blog.find_by_slug(slug)
    if not blog:
        abort(404)

    all_published = Blog.published() or []
    other_blogs = [b for b in all_published if b.slug != slug]

    # Find prev and next blogs
    prev_post = None
    next_post = None
    for idx, b in enumerate(all_published):
        if b.slug == slug:
            if idx > 0:
                prev_post = {
                    'title': all_published[idx - 1].get_title(locale),
                    'slug': all_published[idx - 1].slug,
                    'cover_image_url': all_published[idx - 1].image or '/static/assets/images/online-tyres-shop-dubai.png',
                    'url': f"/blog/{all_published[idx - 1].slug}"
                }
            if idx < len(all_published) - 1:
                next_post = {
                    'title': all_published[idx + 1].get_title(locale),
                    'slug': all_published[idx + 1].slug,
                    'cover_image_url': all_published[idx + 1].image or '/static/assets/images/online-tyres-shop-dubai.png',
                    'url': f"/blog/{all_published[idx + 1].slug}"
                }
            break

    # If no other blogs in DB, create fallback prev/next
    if not prev_post and other_blogs:
        prev_post = {
            'title': other_blogs[0].get_title(locale),
            'slug': other_blogs[0].slug,
            'cover_image_url': other_blogs[0].image or '/static/assets/images/online-tyres-shop-dubai.png',
            'url': f"/blog/{other_blogs[0].slug}"
        }

    # Related posts for sidebar
    related_posts = []
    for b in other_blogs[:5]:
        related_posts.append({
            'title': b.get_title(locale),
            'slug': b.slug,
            'cover_image_url': b.image or '/static/assets/images/online-tyres-shop-dubai.png',
            'published_at': b.published_at.strftime('%d-%m-%Y') if b.published_at else '24-08-2026',
            'url': f"/blog/{b.slug}"
        })

    # Dynamic Sidebar categories from DB
    distinct_cats = Blog.distinct_categories()
    categories = []
    for cat in distinct_cats:
        count = len([b for b in all_published if (b.category_name or '').strip() == cat.strip()])
        categories.append({
            'name': cat,
            'slug': Blog.slugify(cat),
            'count': count
        })

    cat_name = blog.get_category_name(locale) or translate('Blog', locale)

    pub_dt = blog.published_at or blog.created_at
    if pub_dt:
        published_str = pub_dt.strftime('%d-%m-%Y')
        reviewed_str = (pub_dt - timedelta(days=2)).strftime('%d-%m-%Y')
    else:
        published_str = '26-08-2026'
        reviewed_str = '24-08-2026'

    blog_data = {
        'id': blog.id,
        'slug': blog.slug,
        'title': blog.get_title(locale),
        'content': blog.get_content(locale),
        'short_description': blog.get_short_desc(locale),
        'category': cat_name,
        'cover_image_url': blog.image or '/static/assets/images/online-tyres-shop-dubai.png',
        'published_at': published_str,
        'reviewed_at': reviewed_str,
        'read_time': translate('5 min read', locale),
        'faqs': blog.get_faqs(locale),
        'author': {
            'name': translate('Admin', locale),
            'role': translate('Tyre Specialist, TyresVision', locale),
            'avatar_initials': 'TV'
        }
    }

    reviewer_info = Setting.get_reviewer_settings(locale)

    resp = make_response(render_template(
        'Client/BlogDetail.html',
        post=blog_data,
        related_posts=related_posts,
        categories=categories,
        prev_post=prev_post,
        next_post=next_post,
        reviewer=reviewer_info,
        locale=locale
    ))
    resp.set_cookie('site_locale', locale, max_age=31536000, path='/')
    return resp


# --- ABOUT US & CMS PAGES ---
def _build_about_us_context(page, locale=None):
    """
    Constructs a complete dynamic data dictionary for every section of the About Us page,
    supporting localized overrides from the database (Page model / content JSON)
    with robust defaults matching the design specification.
    """
    loc = locale or _get_locale()
    page_title = page.get_title(loc) if page else None
    page_meta = page.get_meta_desc(loc) if page else None
    page_banner = page.banner_image if (page and page.banner_image) else None
    page_content = page.get_content(loc) if page else None

    parsed_json = {}
    if page and isinstance(page.content, dict):
        loc_content = page.content.get(loc) or page.content
        if isinstance(loc_content, dict):
            parsed_json = loc_content
        elif isinstance(loc_content, str) and loc_content.strip().startswith('{'):
            try:
                parsed_json = json.loads(loc_content)
            except Exception:
                pass

    # HERO SECTION
    hero = {
        'breadcrumb_home': translate('Home', loc),
        'breadcrumb_current': page_title or translate('About Us', loc),
        'eyebrow': localize_value(parsed_json.get('hero_eyebrow'), loc) or translate('About Us', loc),
        'title': page_title or localize_value(parsed_json.get('hero_title'), loc) or translate('Genuine Tyres, Honest Service — Built for UAE Drivers', loc),
        'lead': page_meta or localize_value(parsed_json.get('hero_lead'), loc) or translate(
            'We are committed to providing genuine certified tyres, transparent upfront pricing, and effortless mobile doorstep fitting or workshop installation across the UAE.',
            loc
        ),
        'cta_text': localize_value(parsed_json.get('hero_cta_text'), loc) or translate('Our Journey & Story', loc),
        'cta_link': parsed_json.get('hero_cta_link') or '#our-story',
        'image': page_banner or parsed_json.get('hero_image') or '/static/assets/images/online-tyres-shop-dubai.png'
    }

    # STORY SECTION
    story = {
        'eyebrow': localize_value(parsed_json.get('story_eyebrow'), loc) or translate('Our Story', loc),
        'title': localize_value(parsed_json.get('story_title'), loc) or translate('Driven by Transparency & Road Safety', loc),
        'badge_title': localize_value(parsed_json.get('story_badge_title'), loc) or translate('100% Genuine Tyres', loc),
        'badge_sub': localize_value(parsed_json.get('story_badge_sub'), loc) or translate('Official Warranty & GCC Spec', loc),
        'image': parsed_json.get('story_image') or '/static/assets/images/online-tyres-shop-dubai.png',
        'content_html': page_content if (page_content and len(page_content) > 60) else None,
        'p1': localize_value(parsed_json.get('story_p1'), loc) or translate(
            'Our journey began with a simple belief — buying and replacing tyres in the UAE should be transparent, effortless, and dependable, without the hassle of driving to industrial areas or comparing confusing quotes in person.',
            loc
        ),
        'p2': localize_value(parsed_json.get('story_p2'), loc) or translate(
            'What started as a digital tyre platform has quickly expanded into a nationwide network connecting motorists directly with over 60 global manufacturers, mobile van fitting at your door, and 350+ certified garage partners across all 7 Emirates.',
            loc
        ),
        'cta_text': localize_value(parsed_json.get('story_cta_text'), loc) or translate('Learn More About Us', loc),
        'cta_link': parsed_json.get('story_cta_link') or '/#why'
    }

    # VALUES SECTION (5 Cards)
    default_values = [
        {
            'icon': 'shield',
            'title': translate('100% Genuine', loc),
            'desc': translate('Directly sourced with fresh production dates and official GCC warranty.', loc)
        },
        {
            'icon': 'van',
            'title': translate('Mobile Doorstep Van', loc),
            'desc': translate('Fully equipped vans fitting and balancing tyres at your home or workplace.', loc)
        },
        {
            'icon': 'heart',
            'title': translate('Customer First', loc),
            'desc': translate('Honest recommendations focused on your safety, budget, and driving habits.', loc)
        },
        {
            'icon': 'tag',
            'title': translate('Full Transparency', loc),
            'desc': translate('All-inclusive pricing with zero hidden fees — delivery, fitting, and VAT included.', loc)
        },
        {
            'icon': 'network',
            'title': translate('350+ Garage Network', loc),
            'desc': translate('Partner fitting garages across Dubai, Abu Dhabi, Sharjah, and Northern Emirates.', loc)
        }
    ]
    values = {
        'eyebrow': localize_value(parsed_json.get('values_eyebrow'), loc) or translate('Our Values', loc),
        'title': localize_value(parsed_json.get('values_title'), loc) or translate('What Drives Us', loc),
        'cards': parsed_json.get('values_cards') or parsed_json.get('values_items') or default_values
    }

    # STATS SECTION (4 Metrics)
    default_stats = [
        {
            'icon': 'brand',
            'num': '60+',
            'label': translate('Global Tyre Brands', loc),
            'sub': translate('Michelin, Continental, Bridgestone & more', loc)
        },
        {
            'icon': 'garage',
            'num': '350+',
            'label': translate('Partner Fitting Centres', loc),
            'sub': translate('Across all 7 UAE Emirates', loc)
        },
        {
            'icon': 'drivers',
            'num': '10,000+',
            'label': translate('Satisfied Motorists', loc),
            'sub': translate('Trusted roadside & home installation', loc)
        },
        {
            'icon': 'shield',
            'num': '100%',
            'label': translate('Certified Genuine Quality', loc),
            'sub': translate('Official manufacturer warranty', loc)
        }
    ]
    stats = {
        'metrics': parsed_json.get('stats_metrics') or parsed_json.get('stats_items') or default_stats
    }

    # TEAM SECTION
    team = {
        'eyebrow': localize_value(parsed_json.get('team_eyebrow'), loc) or translate('Our Team', loc),
        'title': localize_value(parsed_json.get('team_title'), loc) or translate('Passionate Specialists, Purposeful Work', loc),
        'desc': localize_value(parsed_json.get('team_desc'), loc) or translate(
            'Our team is made up of certified automotive technicians, master fitters, logistics coordinators, and tyre specialists dedicated to delivering seamless tyre replacement right to your doorstep.',
            loc
        ),
        'cta_text': localize_value(parsed_json.get('team_cta_text'), loc) or translate('Meet Our Team', loc),
        'cta_link': parsed_json.get('team_cta_link') or 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20would%20like%20to%20connect%20with%20your%20team.',
        'image': parsed_json.get('team_image') or '/static/assets/images/online-tyres-shop-dubai.png'
    }

    # ACTION CALLOUT BANNER
    cta_banner = {
        'title': localize_value(parsed_json.get('banner_title'), loc) or translate("Let's Drive a Safer Tomorrow Together", loc),
        'desc': localize_value(parsed_json.get('banner_desc'), loc) or translate(
            'Message our specialists on WhatsApp for instant sizing assistance and price quotes across 60+ brands.',
            loc
        ),
        'cta_text': localize_value(parsed_json.get('banner_cta_text'), loc) or translate('Get In Touch →', loc),
        'cta_link': parsed_json.get('banner_cta_link') or 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20would%20like%20a%20tyre%20quote.'
    }

    return {
        'hero': hero,
        'story': story,
        'values': values,
        'stats': stats,
        'team': team,
        'cta_banner': cta_banner
    }


@site_bp.route('/about-us')
def about_us():
    locale = _get_locale()
    page = Page.find_by_slug('about-us')
    resp = make_response(render_template('Client/AboutUs.html', page=page, slug='about-us', locale=locale))
    resp.set_cookie('site_locale', locale, max_age=31536000, path='/')
    return resp


@site_bp.route('/<string(length=2):lang_code>/about-us')
def about_us_locale(lang_code):
    """Directly render About Us page for any dynamic locale (e.g. /ar/about-us, /de/about-us)."""
    code = lang_code.lower()
    session['site_locale'] = code
    page = Page.find_by_slug('about-us')
    resp = make_response(render_template('Client/AboutUs.html', page=page, slug='about-us', locale=code))
    resp.set_cookie('site_locale', code, max_age=31536000, path='/')
    return resp


@site_bp.route('/<string(length=2):lang_code>/page/<slug>')
@site_bp.route('/<string(length=2):lang_code>/<slug>')
def page_detail_locale(lang_code, slug):
    """Directly render CMS page or blog for dynamic locale (e.g. /ar/terms, /de/privacy)."""
    code = lang_code.lower()
    session['site_locale'] = code
    if slug in ('blog', 'blogs'):
        return blog_locale(code)
    elif slug == 'about-us':
        return about_us_locale(code)

    page = Page.find_by_slug(slug)
    if page:
        resp = make_response(render_template('Client/AboutUs.html', page=page, slug=slug, locale=code))
        resp.set_cookie('site_locale', code, max_age=31536000, path='/')
        return resp
    blog = Blog.find_by_slug(slug)
    if blog:
        return _render_blog_detail(slug, code)
    abort(404)


@site_bp.route('/page/<slug>')
@site_bp.route('/<slug>')
def page_detail(slug):
    """Generic static CMS content page reader with dynamic sections support."""
    if slug in ('tcsadmin', 'visionadmin', 'visonadmin', 'admin', 'static', 'api', 'login', 'logout', 'forgot-password', 'reset-password', 'favicon.ico'):
        abort(404)
    locale = _get_locale()
    page = Page.find_by_slug(slug)
    if page:
        return render_template('Client/AboutUs.html', page=page, slug=slug, locale=locale)
    blog = Blog.find_by_slug(slug)
    if blog:
        return redirect(f'/blog/{slug}')
    abort(404)
