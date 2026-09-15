# app/siteapp/clientroute.py - TyresVision Customer Storefront Blueprint ('site')
#
# Serves the public client-facing HTML pages only (home, blog listing/detail,
# About Us, generic CMS pages). The public JSON API endpoints that used to
# live in this file (/api/blogs, /api/blogs/<slug>) now live in the unified
# app/api.py alongside the tcsadmin and visionadmin APIs.
import json
import os
import math
import re
from datetime import datetime, timedelta
from flask import Blueprint, current_app, render_template, request, session, abort, redirect, make_response, send_from_directory, jsonify
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
@site_bp.route('/blog')
@site_bp.route('/blog/')
@site_bp.route('/blogs')
@site_bp.route('/blogs/')
def blog_default():
    """Directly render blog listing using active site locale."""
    code = _get_locale()
    session['site_locale'] = code
    categories = Blog.distinct_categories(locale=code)
    selected_category = (request.args.get('category') or '').strip()
    resp = make_response(render_template('Client/Blog.html', locale=code, categories=categories, selected_category=selected_category))
    resp.set_cookie('site_locale', code, max_age=31536000, path='/')
    return resp


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


@site_bp.route('/mobile-tyre-fitting')
def mobile_tyre_fitting():
    """Dedicated high-fidelity Mobile Tyre Fitting landing page."""
    locale = _get_locale()
    page = Page.find_by_slug('mobile-tyre-fitting')
    resp = make_response(render_template('Client/MobileTyreFitting.html', page=page, slug='mobile-tyre-fitting', locale=locale))
    resp.set_cookie('site_locale', locale, max_age=31536000, path='/')
    return resp


@site_bp.route('/<string(length=2):lang_code>/mobile-tyre-fitting')
def mobile_tyre_fitting_locale(lang_code):
    """Directly render Mobile Tyre Fitting page for dynamic locale."""
    code = lang_code.lower()
    session['site_locale'] = code
    page = Page.find_by_slug('mobile-tyre-fitting')
    resp = make_response(render_template('Client/MobileTyreFitting.html', page=page, slug='mobile-tyre-fitting', locale=code))
    resp.set_cookie('site_locale', code, max_age=31536000, path='/')
    return resp


def _format_product_for_client(p, locale='en'):
    p_dict = dict(p)
    attr = p_dict.get('attributes_json')
    if isinstance(attr, str):
        try:
            attr = json.loads(attr)
        except Exception:
            attr = {}
    elif not isinstance(attr, dict):
        attr = {}
    p_dict['attr'] = attr
    p_dict['rating'] = float(attr.get('rating', 4.5))

    # Top Offer Banner (e.g. FREE WHEEL ALIGNMENT / BUY 3 GET 1 FREE / TOP SAVINGS)
    raw_offer = attr.get('offers') or attr.get('promotion') or attr.get('badge') or ''
    if not raw_offer or str(raw_offer).strip().lower() in ('none', '0', '', 'null'):
        offer_banner = 'FREE WHEEL ALIGNMENT'
    else:
        offer_banner = str(raw_offer).strip().upper()
    p_dict['offer_banner'] = offer_banner
    p_dict['badge'] = offer_banner
    p_dict['badge_class'] = attr.get('badge_class', 'badge-blue')

    # Warranty
    warranty_val = str(attr.get('warranty_period') or attr.get('warranty') or '3 Years Warranty').strip()
    if not warranty_val or warranty_val.lower() in ('none', '0', 'null'):
        warranty_val = '3 Years Warranty'
    p_dict['warranty'] = warranty_val

    # Vehicle type normalization ('car', 'suv', 'van')
    raw_veh = str(p_dict.get('vehicle_type') or attr.get('tyre_type') or 'car').strip().lower()
    if any(k in raw_veh for k in ('suv', '4x4', '4wd', 'crossover')):
        veh_type = 'suv'
    elif any(k in raw_veh for k in ('van', 'truck', 'commercial')):
        veh_type = 'van'
    else:
        veh_type = 'car'
    p_dict['vehicle_type'] = veh_type

    p_dict['season'] = attr.get('season') or p_dict.get('tire_type') or 'Summer'
    
    b_slug = p_dict.get('brand_slug') or (p_dict.get('brand_name') or 'michelin').lower().replace(' ', '')
    p_dict['brand_slug'] = b_slug
    p_dict['brand_name'] = p_dict.get('brand_name') or b_slug.capitalize()
    p_dict['brand_logo'] = p_dict.get('brand_logo') or f"/static/assets/images/brands/{b_slug}.svg"
    
    # Normalize image_path:
    raw_img = p_dict.get('image_path') or p_dict.get('small_image') or attr.get('image')
    if raw_img and str(raw_img).strip():
        img_s = str(raw_img).strip().replace('\\', '/')
        if not (img_s.startswith('http://') or img_s.startswith('https://') or img_s.startswith('data:')):
            if not img_s.startswith('/'):
                img_s = '/' + img_s
        p_dict['image_path'] = img_s
    else:
        p_dict['image_path'] = '/static/assets/images/no-image-available.svg'

    # Price conversions
    price_val = float(p_dict.get('price') or 0)
    p_dict['price'] = price_val
    p_dict['price_formatted'] = f"{price_val:.2f}"
    p_dict['price_set_of_4'] = f"{price_val * 4:.2f}"
    p_dict['list_price'] = float(p_dict['list_price']) if p_dict.get('list_price') else None

    # Ensure display_name is readable
    if not p_dict.get('display_name'):
        name_raw = p_dict.get('name')
        if isinstance(name_raw, dict):
            p_dict['display_name'] = name_raw.get(locale) or name_raw.get('en') or list(name_raw.values())[0] if name_raw else p_dict.get('sku')
        elif isinstance(name_raw, str) and name_raw.strip().startswith('{'):
            try:
                n_json = json.loads(name_raw)
                p_dict['display_name'] = n_json.get(locale) or n_json.get('en') or list(n_json.values())[0]
            except Exception:
                p_dict['display_name'] = name_raw
        else:
            p_dict['display_name'] = name_raw or p_dict.get('sku')

    # Pattern / Model Name (e.g. "Atrezzo Eco")
    pat = str(attr.get('pattern') or attr.get('pattern.1') or '').strip()
    if not pat or pat.lower() in ('none', 'null', '0'):
        pat = p_dict.get('display_name') or ''
        b_name = p_dict.get('brand_name') or ''
        if b_name and pat.lower().startswith(b_name.lower()):
            pat = pat[len(b_name):].strip()
    p_dict['pattern_name'] = pat or p_dict.get('display_name') or 'Tyre'

    # Size spec with load/speed index (e.g. "165/65 R14 79T")
    base_size = str(p_dict.get('tire_size_label') or attr.get('tire_size') or attr.get('tyre_size') or '').strip()
    if not base_size:
        w = attr.get('width')
        h = attr.get('height')
        r = attr.get('rim')
        if w and r:
            base_size = f"{w}/{h} R{r}" if h else f"{w} R{r}"
    
    load_speed = str(attr.get('load_speed_index') or '').strip()
    if not load_speed:
        l_idx = str(attr.get('tire_load_index') or attr.get('load_index') or '').strip()
        s_rat = str(attr.get('tire_speed_rating') or '').strip()
        if l_idx or s_rat:
            load_speed = f"{l_idx}{s_rat}".strip()

    if load_speed and load_speed.lower() not in base_size.lower():
        full_size = f"{base_size} {load_speed}".strip()
    else:
        full_size = base_size

    p_dict['tire_size_label'] = base_size
    p_dict['full_size_spec'] = full_size or base_size or 'Standard Fit'

    # Year (e.g. 2024 / 2025 / 2026)
    yr_val = str(attr.get('year') or attr.get('dot') or '').strip()
    if not yr_val or yr_val.lower() in ('none', 'null', '0'):
        m_yr = re.search(r'\b(202[3-7])\b', str(p_dict.get('name') or '') + ' ' + str(p_dict.get('display_name') or ''))
        yr_val = m_yr.group(1) if m_yr else '2024'
    p_dict['year'] = yr_val

    # Country of Origin (e.g. "China", "Japan", "Germany")
    origin_val = str(attr.get('country_of_origin') or attr.get('origin') or attr.get('country') or '').strip()
    if not origin_val or origin_val.lower() in ('none', 'null', '0'):
        origin_val = 'China'
    p_dict['country_of_origin'] = origin_val.title()

    p_dict['fitted_text'] = attr.get('price_included_text') or 'Fitted Price'

    return p_dict


def _fetch_catalog_products(args, locale='en'):
    """Queries products with dynamic filters, pagination, and sorting for client catalog."""
    from db import get_connection
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            where = ["p.deleted_at IS NULL", "p.status = 'active'"]
            params = []

            # 1. Brands filter (supports ?brand=pirelli,michelin or ?brand=pirelli&brand=michelin)
            raw_brands = args.getlist('brand') or args.getlist('brands')
            brands = []
            for b_entry in raw_brands:
                for b_part in b_entry.split(','):
                    bp = b_part.strip().lower()
                    if bp and bp not in brands:
                        brands.append(bp)

            if brands:
                b_placeholders = ', '.join(['%s'] * len(brands))
                where.append(f"(LOWER(b.slug) IN ({b_placeholders}) OR LOWER(b.name) IN ({b_placeholders}))")
                params.extend(brands)
                params.extend(brands)

            # 2. Vehicle Types filter
            raw_vehicles = args.getlist('vehicle') or args.getlist('vehicle_type') or args.getlist('vehicles')
            vehicles = []
            for v_entry in raw_vehicles:
                for v_part in v_entry.split(','):
                    vp = v_part.strip().lower()
                    if vp and vp not in vehicles:
                        vehicles.append(vp)

            if vehicles:
                v_terms = []
                for v in vehicles:
                    if v == 'suv':
                        v_terms.extend(['suv', '4x4', 'suv / 4x4'])
                    elif v == 'car':
                        v_terms.extend(['car', 'passenger car'])
                    elif v == 'van':
                        v_terms.extend(['van', 'light truck / van', 'commercial van'])
                    else:
                        v_terms.append(v)
                v_placeholders = ', '.join(['%s'] * len(v_terms))
                where.append(f"LOWER(p.vehicle_type) IN ({v_placeholders})")
                params.extend(v_terms)

            # 3. Sizes filter
            raw_sizes = args.getlist('size') or args.getlist('sizes')
            sizes = []
            for s_entry in raw_sizes:
                for s_part in s_entry.split(','):
                    sp = s_part.strip()
                    if sp and sp not in sizes:
                        sizes.append(sp)

            if sizes:
                s_clauses = []
                s_params = []
                for sz in sizes:
                    sz_clean = sz.strip()
                    sz_hyphen = sz_clean.replace('/', '-').replace(' ', '-')
                    s_clauses.append("(p.tire_size_label = %s OR REPLACE(REPLACE(p.tire_size_label, '/', '-'), ' ', '-') = %s)")
                    s_params.extend([sz_clean, sz_hyphen])
                where.append("(" + " OR ".join(s_clauses) + ")")
                params.extend(s_params)

            # 4. Tyre Types / Seasons
            raw_types = args.getlist('type') or args.getlist('tire_type') or args.getlist('types')
            types = []
            for t_entry in raw_types:
                for t_part in t_entry.split(','):
                    tp = t_part.strip().lower()
                    if tp and tp not in types:
                        types.append(tp)

            if types:
                t_clauses = []
                t_terms = []
                for t in types:
                    if t == 'run_flat':
                        t_clauses.append("p.run_flat = 1")
                    else:
                        t_terms.append(t)
                if t_terms:
                    t_placeholders = ', '.join(['%s'] * len(t_terms))
                    t_clauses.append(f"LOWER(p.tire_type) IN ({t_placeholders})")
                    params.extend(t_terms)
                if t_clauses:
                    where.append("(" + " OR ".join(t_clauses) + ")")

            # 5. Price filter
            max_price = args.get('max_price')
            if max_price:
                try:
                    where.append("p.price <= %s")
                    params.append(float(max_price))
                except (ValueError, TypeError):
                    pass

            min_price = args.get('min_price')
            if min_price:
                try:
                    where.append("p.price >= %s")
                    params.append(float(min_price))
                except (ValueError, TypeError):
                    pass

            # 6. Search query
            search = args.get('search') or args.get('q')
            if search and search.strip():
                s_term = f"%{search.strip()}%"
                where.append("(p.sku LIKE %s OR p.display_name LIKE %s OR p.tire_size_label LIKE %s)")
                params.extend([s_term, s_term, s_term])

            where_sql = " AND ".join(where)

            # Total matching count
            cur.execute(f"""
                SELECT COUNT(*) as total
                FROM products p
                LEFT JOIN brands b ON p.brand_id = b.id
                WHERE {where_sql}
            """, params)
            c_row = cur.fetchone()
            total_count = c_row['total'] if c_row else 0

            # Sorting
            sort_by = args.get('sort') or args.get('sort_by') or 'popular'
            if sort_by == 'price-asc':
                order_sql = "ORDER BY p.price ASC, p.id ASC"
            elif sort_by == 'price-desc':
                order_sql = "ORDER BY p.price DESC, p.id ASC"
            elif sort_by == 'newest':
                order_sql = "ORDER BY p.id DESC"
            elif sort_by == 'rating':
                order_sql = "ORDER BY p.sort_order ASC, p.id ASC"
            else:
                order_sql = "ORDER BY p.sort_order ASC, p.id ASC"

            # Pagination (default 16 for 4 rows of 4 cards on desktop)
            try:
                page = max(1, int(args.get('page', 1)))
            except (ValueError, TypeError):
                page = 1

            try:
                per_page = max(1, min(100, int(args.get('per_page', 16))))
            except (ValueError, TypeError):
                per_page = 16

            total_pages = max(1, math.ceil(total_count / per_page)) if total_count > 0 else 1
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
            raw_products = cur.fetchall()

            products = [_format_product_for_client(p, locale) for p in raw_products]
            return {
                'products': products,
                'total': total_count,
                'page': page,
                'per_page': per_page,
                'total_pages': total_pages
            }
    finally:
        conn.close()


# # --- PRODUCT CATALOG / CAR TYRES LISTING ---
def _parse_filter_path(filter_path):
    """Parses clean SEO slug filter segments (e.g. /page-2-16/brand-pirelli/size-225-40-R18/max_price-5693) into request args."""
    from werkzeug.datastructures import MultiDict
    import re
    args = MultiDict()
    if not filter_path:
        return args

    segments = [s.strip() for s in filter_path.split('/') if s.strip()]
    for seg in segments:
        m_page = re.match(r'^page-(\d+)(?:-(\d+))?$', seg, re.IGNORECASE)
        if m_page:
            args.setlistdefault('page', []).append(m_page.group(1))
            if m_page.group(2):
                args.setlistdefault('per_page', []).append(m_page.group(2))
            continue

        m_brand = re.match(r'^brand-(.+)$', seg, re.IGNORECASE)
        if m_brand:
            for b in m_brand.group(1).split(','):
                if b.strip():
                    args.add('brand', b.strip())
            continue

        m_size = re.match(r'^size-(.+)$', seg, re.IGNORECASE)
        if m_size:
            for s in m_size.group(1).split(','):
                if s.strip():
                    args.add('size', s.strip())
            continue

        m_veh = re.match(r'^vehicle-(.+)$', seg, re.IGNORECASE)
        if m_veh:
            for v in m_veh.group(1).split(','):
                if v.strip():
                    args.add('vehicle', v.strip())
            continue

        m_type = re.match(r'^type-(.+)$', seg, re.IGNORECASE)
        if m_type:
            for t in m_type.group(1).split(','):
                if t.strip():
                    args.add('type', t.strip())
            continue

        m_max_p = re.match(r'^max_price-(\d+(?:\.\d+)?)$', seg, re.IGNORECASE)
        if m_max_p:
            args.setlistdefault('max_price', []).append(m_max_p.group(1))
            continue

        m_min_p = re.match(r'^min_price-(\d+(?:\.\d+)?)$', seg, re.IGNORECASE)
        if m_min_p:
            args.setlistdefault('min_price', []).append(m_min_p.group(1))
            continue

        m_sort = re.match(r'^sort-(.+)$', seg, re.IGNORECASE)
        if m_sort:
            args.setlistdefault('sort', []).append(m_sort.group(1))
            continue

        m_q = re.match(r'^(?:search|q)-(.+)$', seg, re.IGNORECASE)
        if m_q:
            args.setlistdefault('search', []).append(m_q.group(1))
            continue

    return args


def _render_product_listing(locale, filter_path=None):
    """Renders the dedicated product listing catalog with data and sidebar filters from MySQL database."""
    from werkzeug.datastructures import MultiDict
    combined_args = MultiDict()
    if filter_path:
        combined_args.update(_parse_filter_path(filter_path))
    for k, vals in request.args.lists():
        combined_args.setlist(k, vals)

    # Check if client requested JSON via query param or header
    if combined_args.get('format') == 'json' or request.headers.get('Accept') == 'application/json':
        data = _fetch_catalog_products(combined_args, locale)
        return jsonify(data)

    catalog_data = _fetch_catalog_products(combined_args, locale)
    products = catalog_data['products']
    total_count = catalog_data['total']
    current_page = catalog_data['page']
    per_page = catalog_data['per_page']
    total_pages = catalog_data['total_pages']

    active_brands = [b.lower() for b in (combined_args.getlist('brand') or combined_args.getlist('brands'))]
    active_vehicles = [v.lower() for v in (combined_args.getlist('vehicle') or combined_args.getlist('vehicle_type'))]
    active_sizes = []
    for s in (combined_args.getlist('size') or combined_args.getlist('sizes')):
        active_sizes.append(s.strip())
        active_sizes.append(s.strip().replace('/', '-').replace(' ', '-'))
    active_types = [t.lower() for t in (combined_args.getlist('type') or combined_args.getlist('tire_type'))]
    active_max_price = combined_args.get('max_price')
    active_min_price = combined_args.get('min_price')
    active_sort = combined_args.get('sort') or 'popular'

    from db import get_connection
    conn = get_connection()
    try:
        with conn.cursor() as cur:

            # 2. Sidebar: Brands from DB (active brands + product counts)
            cur.execute("""
                SELECT b.id, b.name, b.slug, b.logo, COUNT(p.id) as cnt
                FROM brands b
                LEFT JOIN products p ON p.brand_id = b.id AND p.deleted_at IS NULL AND p.status = 'active'
                WHERE b.status = 'active'
                GROUP BY b.id, b.name, b.slug, b.logo
                ORDER BY cnt DESC, b.name ASC
            """)
            filter_brands = []
            for b in cur.fetchall():
                b_slug = b.get('slug') or (b.get('name') or '').lower().replace(' ', '')
                b_logo = b.get('logo') or f"/static/assets/images/brands/{b_slug}.svg"
                filter_brands.append({
                    'id': b['id'],
                    'name': b['name'],
                    'slug': b_slug,
                    'logo': b_logo,
                    'count': b.get('cnt', 0)
                })

            # 3. Sidebar: Tyre Sizes from DB (from active products + attribute_options)
            cur.execute("""
                SELECT tire_size_label as size, COUNT(*) as cnt
                FROM products
                WHERE deleted_at IS NULL AND status = 'active' 
                  AND tire_size_label IS NOT NULL AND tire_size_label != ''
                GROUP BY tire_size_label
                ORDER BY cnt DESC, tire_size_label ASC
            """)
            filter_sizes = []
            seen_sizes = set()
            for r in cur.fetchall():
                sz = r['size'].strip() if r.get('size') else ''
                if sz and sz not in seen_sizes:
                    seen_sizes.add(sz)
                    filter_sizes.append({'size': sz, 'count': r['cnt']})

            # Supplement from attribute_options (attributes.code = 'tire_size')
            cur.execute("""
                SELECT ao.value as size, COUNT(p.id) as cnt
                FROM attribute_options ao
                JOIN attributes a ON ao.attribute_id = a.id AND a.code = 'tire_size'
                LEFT JOIN products p ON p.tire_size_label = ao.value AND p.deleted_at IS NULL AND p.status = 'active'
                GROUP BY ao.id, ao.value, ao.sort_order
                ORDER BY cnt DESC, ao.sort_order ASC, ao.value ASC
                LIMIT 25
            """)
            for r in cur.fetchall():
                sz = r['size'].strip() if r.get('size') else ''
                if sz and sz not in seen_sizes:
                    seen_sizes.add(sz)
                    filter_sizes.append({'size': sz, 'count': r['cnt']})

            # 4. Sidebar: Vehicle Types from DB
            cur.execute("""
                SELECT ao.value, ao.label, ao.sort_order
                FROM attribute_options ao
                JOIN attributes a ON ao.attribute_id = a.id AND a.code = 'vehicle_type'
                ORDER BY ao.sort_order ASC
            """)
            v_rows = cur.fetchall()

            cur.execute("""
                SELECT LOWER(vehicle_type) as vtype, COUNT(*) as cnt
                FROM products
                WHERE deleted_at IS NULL AND status = 'active' AND vehicle_type IS NOT NULL
                GROUP BY vehicle_type
            """)
            vehicle_prod_counts = {r['vtype']: r['cnt'] for r in cur.fetchall() if r.get('vtype')}
            vehicle_key_map = {
                'Passenger Car': 'car',
                'SUV / 4x4': 'suv',
                'Light Truck / Van': 'van',
                'Performance / Sport': 'sport',
                'Commercial Van': 'van',
                'Car': 'car',
                'SUV': 'suv',
                '4x4': '4x4',
                'EV': 'ev'
            }
            filter_vehicles = []
            seen_v_keys = set()
            for vr in v_rows:
                raw_val = vr.get('value') or ''
                lbl_raw = vr.get('label')
                label_dict = {}
                if isinstance(lbl_raw, str):
                    try:
                        label_dict = json.loads(lbl_raw)
                    except Exception:
                        label_dict = {'en': raw_val}
                elif isinstance(lbl_raw, dict):
                    label_dict = lbl_raw
                label = label_dict.get(locale) or label_dict.get('en') or raw_val
                key = vehicle_key_map.get(raw_val, raw_val.lower().replace(' ', '_'))
                cnt = vehicle_prod_counts.get(key, 0)
                if key == 'suv' and '4x4' in vehicle_prod_counts:
                    cnt += vehicle_prod_counts.get('4x4', 0)
                if key not in seen_v_keys:
                    seen_v_keys.add(key)
                    filter_vehicles.append({'key': key, 'label': label, 'count': cnt})

            for vk, vc in vehicle_prod_counts.items():
                if vk not in seen_v_keys:
                    seen_v_keys.add(vk)
                    filter_vehicles.append({
                        'key': vk,
                        'label': vk.upper() if len(vk) <= 3 else vk.replace('_', ' ').title(),
                        'count': vc
                    })

            # 5. Sidebar: Tyre Types / Seasons from DB
            cur.execute("""
                SELECT ao.value, ao.label, ao.sort_order
                FROM attribute_options ao
                JOIN attributes a ON ao.attribute_id = a.id AND a.code = 'season'
                ORDER BY ao.sort_order ASC
            """)
            season_rows = cur.fetchall()

            cur.execute("""
                SELECT LOWER(tire_type) as ttype, COUNT(*) as cnt
                FROM products
                WHERE deleted_at IS NULL AND status = 'active' AND tire_type IS NOT NULL
                GROUP BY tire_type
            """)
            tire_type_counts = {r['ttype']: r['cnt'] for r in cur.fetchall() if r.get('ttype')}

            cur.execute("""
                SELECT COUNT(*) as cnt
                FROM products
                WHERE deleted_at IS NULL AND status = 'active' AND run_flat = 1
            """)
            rf_res = cur.fetchone()
            run_flat_cnt = rf_res['cnt'] if rf_res else 0

            filter_tyre_types = []
            for sr in season_rows:
                raw_val = sr.get('value') or ''
                lbl_raw = sr.get('label')
                label_dict = {}
                if isinstance(lbl_raw, str):
                    try:
                        label_dict = json.loads(lbl_raw)
                    except Exception:
                        label_dict = {'en': raw_val}
                elif isinstance(lbl_raw, dict):
                    label_dict = lbl_raw
                label = label_dict.get(locale) or label_dict.get('en') or raw_val
                key = raw_val.lower().replace('-', '_').replace(' ', '_')
                filter_tyre_types.append({
                    'key': key,
                    'label': label,
                    'count': tire_type_counts.get(key, 0)
                })

            filter_tyre_types.append({
                'key': 'run_flat',
                'label': 'Run Flat',
                'count': run_flat_cnt
            })

            # 6. Sidebar: Price Range from DB
            cur.execute("""
                SELECT MIN(price) as min_p, MAX(price) as max_p
                FROM products
                WHERE deleted_at IS NULL AND status = 'active'
            """)
            pr_row = cur.fetchone()
            min_price = int(pr_row['min_p']) if pr_row and pr_row['min_p'] is not None else 100
            max_price = int(pr_row['max_p']) if pr_row and pr_row['max_p'] is not None else 2000
            if min_price >= max_price:
                max_price = min_price + 1000

            resp = make_response(render_template(
                'Client/ProductListing.html',
                products=products,
                total_count=total_count,
                current_page=current_page,
                per_page=per_page,
                total_pages=total_pages,
                filter_brands=filter_brands,
                filter_sizes=filter_sizes,
                filter_vehicles=filter_vehicles,
                filter_tyre_types=filter_tyre_types,
                min_price=min_price,
                max_price=max_price,
                active_brands=active_brands,
                active_vehicles=active_vehicles,
                active_sizes=active_sizes,
                active_types=active_types,
                active_max_price=active_max_price,
                active_min_price=active_min_price,
                active_sort=active_sort,
                locale=locale
            ))
            resp.set_cookie('site_locale', locale, max_age=31536000, path='/')
            return resp
    finally:
        conn.close()


@site_bp.route('/api/products')
@site_bp.route('/api/client/products')
def api_products():
    """Client storefront AJAX product catalog pagination and live filter endpoint."""
    locale = _get_locale()
    data = _fetch_catalog_products(request.args, locale)
    return jsonify(data)


@site_bp.route('/car-tyres')
@site_bp.route('/tyres')
@site_bp.route('/products')
def car_tyres_listing():
    """Client storefront Car Tyres / Product Listing catalog."""
    locale = _get_locale()
    return _render_product_listing(locale)


@site_bp.route('/car-tyres/<path:filter_path>')
@site_bp.route('/tyres/<path:filter_path>')
@site_bp.route('/products/<path:filter_path>')
def car_tyres_listing_slug(filter_path):
    """Client storefront Car Tyres / Product Listing catalog with URL slug filters."""
    locale = _get_locale()
    return _render_product_listing(locale, filter_path=filter_path)


@site_bp.route('/<string(length=2):lang_code>/car-tyres')
@site_bp.route('/<string(length=2):lang_code>/tyres')
@site_bp.route('/<string(length=2):lang_code>/products')
def car_tyres_listing_locale(lang_code):
    """Client storefront Car Tyres / Product Listing catalog with dynamic locale."""
    code = lang_code.lower()
    session['site_locale'] = code
    return _render_product_listing(code)


@site_bp.route('/<string(length=2):lang_code>/car-tyres/<path:filter_path>')
@site_bp.route('/<string(length=2):lang_code>/tyres/<path:filter_path>')
@site_bp.route('/<string(length=2):lang_code>/products/<path:filter_path>')
def car_tyres_listing_locale_slug(lang_code, filter_path):
    """Client storefront Car Tyres / Product Listing catalog with dynamic locale and URL slug filters."""
    code = lang_code.lower()
    session['site_locale'] = code
    return _render_product_listing(code, filter_path=filter_path)


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
    elif slug == 'mobile-tyre-fitting':
        return mobile_tyre_fitting_locale(code)
    elif slug in ('car-tyres', 'tyres', 'products'):
        return _render_product_listing(code)

    page = Page.find_by_slug(slug)
    if page:
        template = 'Client/AboutUs.html' if slug == 'about-us' else 'Client/Page.html'
        raw_sections = PageSection.all_for_page(slug, include_inactive=False)
        sections = [PageSection.to_localized_dict(s, locale=code) for s in raw_sections]
        resp = make_response(render_template(template, page=page, slug=slug, locale=code, sections=sections))
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
    if slug == 'mobile-tyre-fitting':
        return mobile_tyre_fitting()
    if slug in ('car-tyres', 'tyres', 'products'):
        return car_tyres_listing()
    locale = _get_locale()
    page = Page.find_by_slug(slug)
    if page:
        template = 'Client/AboutUs.html' if slug == 'about-us' else 'Client/Page.html'
        raw_sections = PageSection.all_for_page(slug, include_inactive=False)
        sections = [PageSection.to_localized_dict(s, locale=locale) for s in raw_sections]
        return render_template(template, page=page, slug=slug, locale=locale, sections=sections)
    blog = Blog.find_by_slug(slug)
    if blog:
        return redirect(f'/blog/{slug}')
    abort(404)
