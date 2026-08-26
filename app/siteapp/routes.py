# app/siteapp/routes.py - TyresVision Customer Storefront Blueprint ('site')
import math
from flask import Blueprint, render_template, request, session, jsonify, abort, redirect, url_for, make_response
from models.blog import Blog
from models.page import Page

site_bp = Blueprint('site', __name__)


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
# 1. JSON API ENDPOINTS (GET BLOG FROM DATABASE VIA API)
# ============================================================================

@site_bp.route('/api/blogs', methods=['GET'])
@site_bp.route('/api/blog', methods=['GET'])
def api_get_blogs():
    """
    Public JSON API: Fetch published blogs with pagination, locale,
    search, and category filtering.
    """
    locale = request.args.get('locale') or _get_locale()
    query = (request.args.get('q') or '').strip().lower()
    cat_filter = (request.args.get('category') or '').strip().lower()

    try:
        page_num = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page_num = 1

    try:
        per_page = int(request.args.get('per_page', request.args.get('limit', 12)))
        if per_page not in (4, 6, 8, 12, 16, 24):
            per_page = 12
    except (ValueError, TypeError):
        per_page = 12

    db_blogs = Blog.published()
    formatted_blogs = []

    if db_blogs:
        for b in db_blogs:
            title = b.get_title(locale)
            short_desc = b.get_short_desc(locale)
            content = b.get_content(locale)

            cat_name = b.category_name or ('Blog' if locale != 'ar' else 'مدونة')

            prefix = f'/{locale}' if locale in ('en', 'ar') else ''
            blog_url = f'{prefix}/blog/{b.slug}'

            formatted_blogs.append({
                'id': b.id,
                'slug': b.slug,
                'title': title,
                'short_description': short_desc or '',
                'excerpt': short_desc or '',
                'content': content or '',
                'image': b.image or '/static/assets/online-tyres-shop-dubai.png',
                'cover_image_url': b.image or '/static/assets/online-tyres-shop-dubai.png',
                'published_at': b.published_at.strftime('%d %b %Y') if b.published_at else (b.created_at.strftime('%d %b %Y') if b.created_at else '2026'),
                'published_at_raw': b.published_at.isoformat() if b.published_at else (b.created_at.isoformat() if b.created_at else None),
                'category': cat_name,
                'thumb_class': 't-buying' if 'choose' in (b.slug or '') else 't-maint',
                'read_time': '4 min read' if locale != 'ar' else 'قراءة 4 دقائق',
                'url': blog_url
            })

    # Filter by search keyword
    if query:
        formatted_blogs = [
            b for b in formatted_blogs
            if query in b['title'].lower() or query in b['short_description'].lower()
        ]

    # Filter by category
    if cat_filter:
        formatted_blogs = [
            b for b in formatted_blogs
            if cat_filter == (b.get('category') or '').strip().lower() 
            or cat_filter in (b.get('category') or '').strip().lower() 
            or cat_filter == Blog.slugify(b.get('category') or '')
        ]

    total_count = len(formatted_blogs)
    num_pages = max(1, math.ceil(total_count / per_page))
    if page_num > num_pages:
        page_num = num_pages

    start_idx = (page_num - 1) * per_page
    end_idx = min(start_idx + per_page, total_count)
    page_blogs = formatted_blogs[start_idx:end_idx]

    pagination = {
        'page': page_num,
        'per_page': per_page,
        'total': total_count,
        'num_pages': num_pages,
        'start': start_idx + 1 if total_count > 0 else 0,
        'end': end_idx,
        'has_prev': page_num > 1,
        'has_next': page_num < num_pages,
        'prev_num': page_num - 1,
        'next_num': page_num + 1
    }

    return jsonify({
        'success': True,
        'locale': locale,
        'blogs': page_blogs,
        'count': len(page_blogs),
        'pagination': pagination
    })


@site_bp.route('/api/blogs/<slug>', methods=['GET'])
@site_bp.route('/api/blog/<slug>', methods=['GET'])
def api_get_blog_detail(slug):
    """
    Public JSON API: Fetch a single blog article by slug.
    """
    locale = request.args.get('locale') or _get_locale()
    blog = Blog.find_by_slug(slug)
    
    if not blog:
        return jsonify({'success': False, 'error': 'Blog not found'}), 404

    data = {
        'id': blog.id,
        'slug': blog.slug,
        'title': blog.get_title(locale),
        'short_description': blog.get_short_desc(locale),
        'content': blog.get_content(locale),
        'image': blog.image or '/static/assets/online-tyres-shop-dubai.png',
        'cover_image_url': blog.image or '/static/assets/online-tyres-shop-dubai.png',
        'published_at': blog.published_at.strftime('%B %d, %Y') if blog.published_at else 'August 24, 2026',
        'meta_title': blog.get_meta_title(locale),
        'meta_desc': blog.get_meta_desc(locale),
        'author': {
            'name': 'Sharvil Kumar' if locale != 'ar' else 'شارفيل كومار',
            'role': 'Tyre Selection Specialist, TyresVision' if locale != 'ar' else 'أخصائي اختيار الإطارات، تايرز فيجن',
            'avatar_initials': 'SK'
        }
    }
    return jsonify({'success': True, 'blog': data})


# ============================================================================
# 2. CLIENT STOREFRONT (HOME, BLOG, STATIC CMS PAGES WITH FULL LOCALE SUPPORT)
# ============================================================================

# --- HOME ROUTES ---
@site_bp.route('/')
@site_bp.route('/home')
def home():
    """Client storefront home landing page (default/session locale)."""
    locale = _get_locale()
    return render_template('Client/Home.html', locale=locale)


@site_bp.route('/en')
@site_bp.route('/en/')
@site_bp.route('/en/home')
def home_en():
    """Client storefront home landing page in English."""
    session['site_locale'] = 'en'
    resp = make_response(render_template('Client/Home.html', locale='en'))
    resp.set_cookie('site_locale', 'en', max_age=31536000, path='/')
    return resp


@site_bp.route('/ar')
@site_bp.route('/ar/')
@site_bp.route('/ar/home')
def home_ar():
    """Client storefront home landing page in Arabic."""
    session['site_locale'] = 'ar'
    resp = make_response(render_template('Client/Home.html', locale='ar'))
    resp.set_cookie('site_locale', 'ar', max_age=31536000, path='/')
    return resp


# --- BLOG LISTING ROUTES ---
@site_bp.route('/en/blog')
@site_bp.route('/en/blog/')
@site_bp.route('/en/blogs')
@site_bp.route('/en/blogs/')
def blog_en():
    """English blog listing route: /en/blog."""
    session['site_locale'] = 'en'
    categories = Blog.distinct_categories()
    selected_category = (request.args.get('category') or '').strip()
    resp = make_response(render_template('Client/Blog.html', locale='en', categories=categories, selected_category=selected_category))
    resp.set_cookie('site_locale', 'en', max_age=31536000, path='/')
    return resp


@site_bp.route('/ar/blog')
@site_bp.route('/ar/blog/')
@site_bp.route('/ar/blogs')
@site_bp.route('/ar/blogs/')
def blog_ar():
    """Arabic blog listing route: /ar/blog."""
    session['site_locale'] = 'ar'
    categories = Blog.distinct_categories()
    selected_category = (request.args.get('category') or '').strip()
    resp = make_response(render_template('Client/Blog.html', locale='ar', categories=categories, selected_category=selected_category))
    resp.set_cookie('site_locale', 'ar', max_age=31536000, path='/')
    return resp


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
    """English single blog detail route: /en/blog/<slug>."""
    session['site_locale'] = 'en'
    return _render_blog_detail(slug, 'en')


@site_bp.route('/ar/blog/<slug>')
@site_bp.route('/ar/blogs/<slug>')
def blog_detail_ar(slug):
    """Arabic single blog detail route: /ar/blog/<slug>."""
    session['site_locale'] = 'ar'
    return _render_blog_detail(slug, 'ar')


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
                    'cover_image_url': all_published[idx - 1].image or '/static/assets/online-tyres-shop-dubai.png',
                    'url': f"/{locale}/blog/{all_published[idx - 1].slug}" if locale in ('en', 'ar') else f"/blog/{all_published[idx - 1].slug}"
                }
            if idx < len(all_published) - 1:
                next_post = {
                    'title': all_published[idx + 1].get_title(locale),
                    'slug': all_published[idx + 1].slug,
                    'cover_image_url': all_published[idx + 1].image or '/static/assets/online-tyres-shop-dubai.png',
                    'url': f"/{locale}/blog/{all_published[idx + 1].slug}" if locale in ('en', 'ar') else f"/blog/{all_published[idx + 1].slug}"
                }
            break

    # If no other blogs in DB, create fallback prev/next
    if not prev_post and other_blogs:
        prev_post = {
            'title': other_blogs[0].get_title(locale),
            'slug': other_blogs[0].slug,
            'cover_image_url': other_blogs[0].image or '/static/assets/online-tyres-shop-dubai.png',
            'url': f"/{locale}/blog/{other_blogs[0].slug}"
        }

    # Related posts for sidebar
    related_posts = []
    for b in other_blogs[:5]:
        related_posts.append({
            'title': b.get_title(locale),
            'slug': b.slug,
            'cover_image_url': b.image or '/static/assets/online-tyres-shop-dubai.png',
            'published_at': b.published_at.strftime('%B %d, %Y') if b.published_at else 'August 24, 2026',
            'url': f"/{locale}/blog/{b.slug}" if locale in ('en', 'ar') else f"/blog/{b.slug}"
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

    blog_data = {
        'id': blog.id,
        'slug': blog.slug,
        'title': blog.get_title(locale),
        'content': blog.get_content(locale),
        'short_description': blog.get_short_desc(locale),
        'category': cat_name,
        'cover_image_url': blog.image or '/static/assets/online-tyres-shop-dubai.png',
        'published_at': blog.published_at.strftime('%B %d, %Y') if blog.published_at else (blog.created_at.strftime('%B %d, %Y') if blog.created_at else 'August 24, 2026'),
        'read_time': '5 min read' if locale != 'ar' else 'قراءة 5 دقائق',
        'author': {
            'name': 'Admin' if locale != 'ar' else 'المشرف',
            'role': 'Tyre Specialist, TyresVision' if locale != 'ar' else 'أخصائي إطارات، تايرز فيجن',
            'avatar_initials': 'TV'
        }
    }

    resp = make_response(render_template(
        'Client/BlogDetail.html',
        post=blog_data,
        related_posts=related_posts,
        categories=categories,
        prev_post=prev_post,
        next_post=next_post,
        locale=locale
    ))
    resp.set_cookie('site_locale', locale, max_age=31536000, path='/')
    return resp


# --- CMS PAGES ---
@site_bp.route('/en/page/<slug>')
@site_bp.route('/en/<slug>')
def page_detail_en(slug):
    """Generic English CMS page reader."""
    if slug in ('tcsadmin', 'visionadmin', 'visonadmin', 'admin', 'static', 'api', 'login', 'logout', 'forgot-password', 'reset-password', 'favicon.ico', 'en', 'ar', 'blog', 'blogs'):
        abort(404)
    page = Page.find_by_slug(slug)
    if page:
        return render_template('Client/Page.html', page=page, locale='en')
    blog = Blog.find_by_slug(slug)
    if blog:
        return redirect(f'/en/blog/{slug}')
    abort(404)


@site_bp.route('/ar/page/<slug>')
@site_bp.route('/ar/<slug>')
def page_detail_ar(slug):
    """Generic Arabic CMS page reader."""
    if slug in ('tcsadmin', 'visionadmin', 'visonadmin', 'admin', 'static', 'api', 'login', 'logout', 'forgot-password', 'reset-password', 'favicon.ico', 'en', 'ar', 'blog', 'blogs'):
        abort(404)
    page = Page.find_by_slug(slug)
    if page:
        return render_template('Client/Page.html', page=page, locale='ar')
    blog = Blog.find_by_slug(slug)
    if blog:
        return redirect(f'/ar/blog/{slug}')
    abort(404)


@site_bp.route('/page/<slug>')
@site_bp.route('/<slug>')
def page_detail(slug):
    """Generic static CMS content page reader."""
    if slug in ('tcsadmin', 'visionadmin', 'visonadmin', 'admin', 'static', 'api', 'login', 'logout', 'forgot-password', 'reset-password', 'favicon.ico', 'en', 'ar'):
        abort(404)

    locale = _get_locale()
    page = Page.find_by_slug(slug)
    if page:
        return render_template('Client/Page.html', page=page, locale=locale)

    blog = Blog.find_by_slug(slug)
    if blog:
        prefix = f'/{locale}' if locale in ('en', 'ar') else ''
        return redirect(f'{prefix}/blog/{slug}')

    abort(404)
