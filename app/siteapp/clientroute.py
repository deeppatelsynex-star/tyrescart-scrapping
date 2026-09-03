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


def _get_locale():
    req_locale = request.args.get('locale')
    if req_locale in ('en', 'ar'):
        session['site_locale'] = req_locale
        return req_locale
    if 'site_locale' in session and session['site_locale'] in ('en', 'ar'):
        return session['site_locale']
    cookie_locale = request.cookies.get('site_locale')
    if cookie_locale in ('en', 'ar'):
        session['site_locale'] = cookie_locale
        return cookie_locale
    return 'en'


# ============================================================================
# CLIENT STOREFRONT (HOME, BLOG, STATIC CMS PAGES WITH FULL LOCALE SUPPORT)
# ============================================================================

# --- HOME ROUTES ---
def _get_home_sections(locale: str = 'en'):
    """Helper to fetch and localize all active home page sections from DB."""
    try:
        from models.page_section import PageSection
        raw_sections = PageSection.all_for_page('home', include_inactive=False)
        return [PageSection.to_localized_dict(s, locale=locale) for s in raw_sections]
    except Exception as err:
        current_app.logger.warning(f"Error fetching home page sections from DB: {err}")
        return []


@site_bp.route('/')
@site_bp.route('/home')
def home():
    """Client storefront home landing page (EN only)."""
    sections = _get_home_sections('en')
    return render_template('Client/Home.html', sections=sections, locale='en')


@site_bp.route('/en')
@site_bp.route('/en/')
@site_bp.route('/en/home')
def home_en():
    """Redirect legacy /en to root /."""
    return redirect('/', code=301)


@site_bp.route('/ar')
@site_bp.route('/ar/')
@site_bp.route('/ar/home')
def home_ar():
    """Redirect legacy /ar to root /."""
    return redirect('/', code=301)


# --- BLOG LISTING ROUTES ---
@site_bp.route('/en/blog')
@site_bp.route('/en/blog/')
@site_bp.route('/en/blogs')
@site_bp.route('/en/blogs/')
def blog_en():
    """Redirect legacy /en/blog to /blog."""
    return redirect('/blog', code=301)


@site_bp.route('/ar/blog')
@site_bp.route('/ar/blog/')
@site_bp.route('/ar/blogs')
@site_bp.route('/ar/blogs/')
def blog_ar():
    """Redirect legacy /ar/blog to /blog."""
    return redirect('/blog', code=301)


@site_bp.route('/blog')
@site_bp.route('/blog/')
@site_bp.route('/blogs')
@site_bp.route('/blogs/')
def blog_default():
    """Default blog catalog route."""
    locale = _get_locale()
    categories = Blog.distinct_categories()
    selected_category = (request.args.get('category') or '').strip()
    return render_template('Client/Blog.html', locale=locale, categories=categories, selected_category=selected_category)


# --- BLOG DETAIL ROUTES ---
@site_bp.route('/en/blog/<slug>')
@site_bp.route('/en/blogs/<slug>')
def blog_detail_en(slug):
    """Redirect legacy /en/blog/<slug> to /blog/<slug>."""
    return redirect(f'/blog/{slug}', code=301)


@site_bp.route('/ar/blog/<slug>')
@site_bp.route('/ar/blogs/<slug>')
def blog_detail_ar(slug):
    """Redirect legacy /ar/blog/<slug> to /blog/<slug>."""
    return redirect(f'/blog/{slug}', code=301)


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

    cat_name = blog.category_name or ('Blog' if locale != 'ar' else 'مدونة')

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
        'read_time': '5 min read' if locale != 'ar' else 'قراءة 5 دقائق',
        'faqs': blog.get_faqs(locale),
        'author': {
            'name': 'Admin' if locale != 'ar' else 'المشرف',
            'role': 'Tyre Specialist, TyresVision' if locale != 'ar' else 'أخصائي إطارات، تايرز فيجن',
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
def _build_about_us_context(page, locale='en'):
    """
    Constructs a complete dynamic data dictionary for every section of the About Us page,
    supporting localized overrides from the database (Page model / content JSON)
    with robust defaults matching the design specification.
    """
    page_title = page.get_title(locale) if page else None
    page_meta = page.get_meta_desc(locale) if page else None
    page_banner = page.banner_image if (page and page.banner_image) else None
    page_content = page.get_content(locale) if page else None

    parsed_json = {}
    if page and isinstance(page.content, dict):
        loc_content = page.content.get(locale) or page.content
        if isinstance(loc_content, dict):
            parsed_json = loc_content
        elif isinstance(loc_content, str) and loc_content.strip().startswith('{'):
            try:
                parsed_json = json.loads(loc_content)
            except Exception:
                pass

    is_ar = (locale == 'ar')

    # HERO SECTION
    hero = {
        'breadcrumb_home': 'الرئيسية' if is_ar else 'Home',
        'breadcrumb_current': 'من نحن' if is_ar else 'About Us',
        'eyebrow': parsed_json.get('hero_eyebrow') or ('من نحن — تايرز فيجن' if is_ar else 'About Us'),
        'title': page_title or parsed_json.get('hero_title') or ('إطارات أصلية، خدمة موثوقة — مصممة لسائقي الإمارات' if is_ar else 'Genuine Tyres, Honest Service — Built for UAE Drivers'),
        'lead': page_meta or parsed_json.get('hero_lead') or (
            'نحن ملتزمون بتقديم إطارات سيارات أصلية معتمدة، وأسعار شفافة وشاملة، وخدمة تركيب متنقلة عند باب منزلك أو في أكثر من ٣٥٠ مركزاً معتمداً في كافة أنحاء الإمارات.'
            if is_ar else
            'We are committed to providing genuine certified tyres, transparent upfront pricing, and effortless mobile doorstep fitting or workshop installation across the UAE.'
        ),
        'cta_text': parsed_json.get('hero_cta_text') or ('استكشف قصتنا ومسيرتنا' if is_ar else 'Our Journey & Story'),
        'cta_link': parsed_json.get('hero_cta_link') or '#our-story',
        'image': page_banner or parsed_json.get('hero_image') or '/static/assets/images/online-tyres-shop-dubai.png'
    }

    # STORY SECTION
    story = {
        'eyebrow': parsed_json.get('story_eyebrow') or ('قصتنا' if is_ar else 'Our Story'),
        'title': parsed_json.get('story_title') or ('مدفوعون بالشفافية وسلامة الطريق' if is_ar else 'Driven by Transparency & Road Safety'),
        'badge_title': parsed_json.get('story_badge_title') or ('إطارات أصلية ١٠٠٪' if is_ar else '100% Genuine Tyres'),
        'badge_sub': parsed_json.get('story_badge_sub') or ('ضمان الوكيل وتواريخ حديثة' if is_ar else 'Official Warranty & GCC Spec'),
        'image': parsed_json.get('story_image') or '/static/assets/images/online-tyres-shop-dubai.png',
        'content_html': page_content if (page_content and len(page_content) > 60) else None,
        'p1': parsed_json.get('story_p1') or (
            'بدأت رحلتنا بإيمان بسيط: يجب أن يكون شراء وتركيب إطارات السيارات في دولة الإمارات تجربة شفافة ومريحة وموثوقة دون الحاجة لزيارة المناطق الصناعية ومقارنة الأسعار لساعات.'
            if is_ar else
            'Our journey began with a simple belief — buying and replacing tyres in the UAE should be transparent, effortless, and dependable, without the hassle of driving to industrial areas or comparing confusing quotes in person.'
        ),
        'p2': parsed_json.get('story_p2') or (
            'ما بدأ كمنصة متخصصة سرعان ما نما ليصبح شبكة متكاملة تضم أكثر من ٦٠ علامة تجارية عالمية، وأسطول فانات تركيب متنقلة تصلك إلى منزلك، وشراكة مع أكثر من ٣٥٠ مركز خدمة معتمد في جميع أنحاء الدولة.'
            if is_ar else
            'What started as a digital tyre platform has quickly expanded into a nationwide network connecting motorists directly with over 60 global manufacturers, mobile van fitting at your door, and 350+ certified garage partners across all 7 Emirates.'
        ),
        'cta_text': parsed_json.get('story_cta_text') or ('تعرف أكثر على مميزاتنا' if is_ar else 'Learn More About Us'),
        'cta_link': parsed_json.get('story_cta_link') or (f'/{locale}#why' if locale in ('en', 'ar') else '/#why')
    }

    # VALUES SECTION (5 Cards)
    default_values = [
        {
            'icon': 'shield',
            'title': 'إطارات أصلية ١٠٠٪' if is_ar else '100% Genuine',
            'desc': 'توريد مباشر من الوكلاء المعتمدين بتواريخ إنتاج حديثة ومواصفات خليجية.' if is_ar else 'Directly sourced with fresh production dates and official GCC warranty.'
        },
        {
            'icon': 'van',
            'title': 'تركيب متنقل عند الباب' if is_ar else 'Mobile Doorstep Van',
            'desc': 'فانات مجهزة بالكامل لفك وتركيب وترصيص الإطارات في موقعك مجاناً.' if is_ar else 'Fully equipped vans fitting and balancing tyres at your home or workplace.'
        },
        {
            'icon': 'heart',
            'title': 'التركيز على العميل' if is_ar else 'Customer First',
            'desc': 'نصائح صادقة واختيار المقاس والماركة الأنسب لاحتياجك وميزانيتك.' if is_ar else 'Honest recommendations focused on your safety, budget, and driving habits.'
        },
        {
            'icon': 'tag',
            'title': 'شفافية تامة بالأسعار' if is_ar else 'Full Transparency',
            'desc': 'أسعار شاملة التوصيل، والتركيب، والترصيص، وضريبة القيمة المضافة.' if is_ar else 'All-inclusive pricing with zero hidden fees — delivery, fitting, and VAT included.'
        },
        {
            'icon': 'network',
            'title': 'شبكة ٣٥٠+ مركز' if is_ar else '350+ Garage Network',
            'desc': 'شراكات مع مراكز صيانة معتمدة في كافة مدن وإمارات الدولة.' if is_ar else 'Partner fitting garages across Dubai, Abu Dhabi, Sharjah, and Northern Emirates.'
        }
    ]
    values = {
        'eyebrow': parsed_json.get('values_eyebrow') or ('قيمنا ومبادئنا' if is_ar else 'Our Values'),
        'title': parsed_json.get('values_title') or ('ما الذي يدفعنا للتميز' if is_ar else 'What Drives Us'),
        'cards': parsed_json.get('values_cards') or parsed_json.get('values_items') or default_values
    }

    # STATS SECTION (4 Metrics)
    default_stats = [
        {
            'icon': 'brand',
            'num': '60+',
            'label': 'علامة تجارية عالمية' if is_ar else 'Global Tyre Brands',
            'sub': 'ميشلان، بريدجستون، بيريللي، والمزيد' if is_ar else 'Michelin, Continental, Bridgestone & more'
        },
        {
            'icon': 'garage',
            'num': '350+',
            'label': 'مركز تركيب معتمد' if is_ar else 'Partner Fitting Centres',
            'sub': 'تغطية شاملة لجميع الإمارات السبع' if is_ar else 'Across all 7 UAE Emirates'
        },
        {
            'icon': 'drivers',
            'num': '10,000+',
            'label': 'سائق في الإمارات' if is_ar else 'Satisfied Motorists',
            'sub': 'خدمة سريعة وتقييمات موثوقة' if is_ar else 'Trusted roadside & home installation'
        },
        {
            'icon': 'shield',
            'num': '100%',
            'label': 'ضمان وجودة معتمدة' if is_ar else 'Certified Genuine Quality',
            'sub': 'ضمان الوكيل وتواريخ حديثة' if is_ar else 'Official manufacturer warranty'
        }
    ]
    stats = {
        'metrics': parsed_json.get('stats_metrics') or parsed_json.get('stats_items') or default_stats
    }

    # TEAM SECTION
    team = {
        'eyebrow': parsed_json.get('team_eyebrow') or ('فريقنا وخبرائنا' if is_ar else 'Our Team'),
        'title': parsed_json.get('team_title') or ('فريق شغوف، وخدمة احترافية مخصصة' if is_ar else 'Passionate Specialists, Purposeful Work'),
        'desc': parsed_json.get('team_desc') or (
            'يتكون فريقنا من فنيين محترفين، وخبراء فك وتركيب معتمدين، ومستشاري خدمة عملاء متاحين دائماً لمساعدتك في اختيار الإطار الأنسب لسيارتك وتنسيق موعد التركيب في الوقت والمكان الذي يناسبك تماماً.'
            if is_ar else
            'Our team is made up of certified automotive technicians, master fitters, logistics coordinators, and tyre specialists dedicated to delivering seamless tyre replacement right to your doorstep.'
        ),
        'cta_text': parsed_json.get('team_cta_text') or ('تواصل مع فريقنا' if is_ar else 'Meet Our Team'),
        'cta_link': parsed_json.get('team_cta_link') or 'https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20would%20like%20to%20connect%20with%20your%20team.',
        'image': parsed_json.get('team_image') or '/static/assets/images/online-tyres-shop-dubai.png'
    }

    # ACTION CALLOUT BANNER
    cta_banner = {
        'title': parsed_json.get('banner_title') or ('هل أنت مستعد لقيادة أكثر أماناً وراحة؟' if is_ar else 'Let\'s Drive a Safer Tomorrow Together'),
        'desc': parsed_json.get('banner_desc') or (
            'تواصل مع خبرائنا عبر واتساب للحصول على عروض أسعار فورية وحجز موعد التركيب المتنقل.'
            if is_ar else
            'Message our specialists on WhatsApp for instant sizing assistance and price quotes across 60+ brands.'
        ),
        'cta_text': parsed_json.get('banner_cta_text') or ('تواصل معنا عبر واتساب ←' if is_ar else 'Get In Touch →'),
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


@site_bp.route('/en/about-us')
def about_us_en_redirect():
    return redirect('/about-us', code=301)


@site_bp.route('/ar/about-us')
def about_us_ar():
    """Redirect legacy /ar/about-us to /about-us."""
    return redirect('/about-us', code=301)


@site_bp.route('/en/page/<slug>')
@site_bp.route('/en/<slug>')
def page_detail_en(slug):
    """Redirect legacy /en/<slug> to /<slug>."""
    if slug in ('blog', 'blogs'):
        return redirect('/blog', code=301)
    if slug == 'about-us':
        return redirect('/about-us', code=301)
    return redirect(f'/{slug}', code=301)


@site_bp.route('/ar/page/<slug>')
@site_bp.route('/ar/<slug>')
def page_detail_ar(slug):
    """Redirect legacy /ar/<slug> to clean canonical URL."""
    if slug in ('blog', 'blogs'):
        return redirect('/blog', code=301)
    if slug == 'about-us':
        return redirect('/about-us', code=301)
    return redirect(f'/{slug}', code=301)


@site_bp.route('/page/<slug>')
@site_bp.route('/<slug>')
def page_detail(slug):
    """Generic static CMS content page reader with dynamic sections support."""
    if slug in ('tcsadmin', 'visionadmin', 'visonadmin', 'admin', 'static', 'api', 'login', 'logout', 'forgot-password', 'reset-password', 'favicon.ico', 'en', 'ar'):
        abort(404)
    locale = _get_locale()
    page = Page.find_by_slug(slug)
    if page:
        return render_template('Client/AboutUs.html', page=page, slug=slug, locale=locale)
    blog = Blog.find_by_slug(slug)
    if blog:
        prefix = f'/{locale}' if locale in ('en', 'ar') else ''
        return redirect(f'{prefix}/blog/{slug}')
    abort(404)
