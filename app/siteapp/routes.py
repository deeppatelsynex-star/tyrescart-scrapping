# app/siteapp/routes.py - TyresVision Customer Frontend Blueprint ('site')
import math
from flask import Blueprint, render_template, request, session, jsonify, abort, redirect, url_for
from models.blog import Blog
from models.page import Page

site_bp = Blueprint('site', __name__)

CATEGORY_LIST = [
    {'name': 'Motorcycle', 'name_ar': 'دراجات نارية', 'slug': 'motorcycle', 'icon': 'bike', 'count': 4},
    {'name': 'Tyres', 'name_ar': 'إطارات السيارات', 'slug': 'tyres', 'icon': 'disc', 'count': 18},
    {'name': 'Battery', 'name_ar': 'بطاريات السيارات', 'slug': 'battery', 'icon': 'zap', 'count': 6},
    {'name': 'Bike Tyres', 'name_ar': 'إطارات الدراجات', 'slug': 'bike-tyres', 'icon': 'circle', 'count': 3},
    {'name': 'Wheels & Rims', 'name_ar': 'جنوط وإطارات', 'slug': 'wheels-rims', 'icon': 'sun', 'count': 8},
    {'name': 'Oil Change', 'name_ar': 'تغيير الزيت', 'slug': 'oil-change', 'icon': 'droplet', 'count': 5},
    {'name': 'Car Service', 'name_ar': 'خدمات وصيانة السيارات', 'slug': 'car-service', 'icon': 'tool', 'count': 12},
    {'name': 'News', 'name_ar': 'الأخبار', 'slug': 'news', 'icon': 'file-text', 'count': 7},
    {'name': 'News & Tips', 'name_ar': 'نصائح وإرشادات', 'slug': 'news-tips', 'icon': 'help-circle', 'count': 14}
]

DEFAULT_FAQS = [
    {
        'question': 'How do I find my tyre size?',
        'question_ar': 'كيف أعرف مقاس إطارات سيارتي؟',
        'answer_html': 'It’s printed on the sidewall of your current tyre &mdash; something like <strong>235/55 R19 105W</strong>. Send a photo on WhatsApp if you’re not sure, or share your car’s make, model and year and TyresVision will look it up.',
        'answer_ar': 'المقاس مطبوع على الجدار الجانبي لإطار سيارتك الحالي (مثل 235/55 R19). يمكنك إرسال صورة للإطار عبر واتساب وسيقوم فريقنا بتحديده فوراً.'
    },
    {
        'question': 'Is nitrogen genuinely better than regular air?',
        'question_ar': 'هل النيتروجين أفضل فعلاً من الهواء العادي؟',
        'answer_html': 'Nitrogen offers slower pressure loss and lower moisture content. Air is more readily available and cheaper. For everyday vehicles maintained at the correct pressure, both are suitable.',
        'answer_ar': 'يحافظ النيتروجين على ثبات ضغط الإطارات لفترة أطول ويقلل الرطوبة والحرارة داخل الإطار، وهو مفيد جداً في درجات حرارة الصيف العالية بالإمارات.'
    },
    {
        'question': 'Is fitting included in the price?',
        'question_ar': 'هل التركيب مشمول في السعر؟',
        'answer_html': 'Delivery to your chosen fitting centre is free and fitting is arranged for you. Mobile fitting at your own location and extras such as laser alignment are quoted upfront with no hidden fees.',
        'answer_ar': 'التوصيل لمركز التركيب مجاني ومشمول، والتركيب المتنقل عند باب بيتك يُعرض بسعر واضح ومباشر بدون أي رسوم خفية.'
    },
    {
        'question': 'Are the tyres new and date-fresh (DOT)?',
        'question_ar': 'هل الإطارات جديدة كلياً وبتاريخ إنتاج حديث؟',
        'answer_html': 'Yes. Every tyre is 100% brand new with a fresh manufacturing date code, sourced through authorised GCC channels with manufacturer-backed warranty.',
        'answer_ar': 'نعم، جميع إطاراتنا جديدة 100% بتواريخ إنتاج حديثة ومطابقة للمواصفات الخليجية مع ضمان الوكيل المعتمد.'
    }
]

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
# 2. BLOG CATALOG (PAGE A: /blog & /blogs)
# ============================================================================

@site_bp.route('/blog')
@site_bp.route('/blog/')
@site_bp.route('/blogs')
@site_bp.route('/blogs/')
def blog_index():
    """
    Blog Index — Paginated grid of post cards with header banner.
    """
    locale = _get_locale()
    cat_filter = request.args.get('category', '').strip().lower()
    search_query = request.args.get('q', '').strip()

    all_published = Blog.published()

    # Keyword filter
    if search_query:
        all_published = [
            b for b in all_published
            if search_query.lower() in b.get_title(locale).lower() or
               search_query.lower() in (b.get_short_desc(locale) or '').lower() or
               search_query.lower() in (b.get_content(locale) or '').lower()
        ]

    total_count = len(all_published)

    try:
        page_num = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page_num = 1

    try:
        per_page = int(request.args.get('per_page', request.args.get('limit', 8)))
        if per_page not in (4, 8, 12, 16, 24):
            per_page = 8
    except (ValueError, TypeError):
        per_page = 8

    num_pages = max(1, math.ceil(total_count / per_page))
    if page_num > num_pages:
        page_num = num_pages

    start_idx = (page_num - 1) * per_page
    end_idx = min(start_idx + per_page, total_count)
    page_blogs = all_published[start_idx:end_idx]

    start_item = start_idx + 1 if total_count > 0 else 0
    end_item = end_idx

    # Format posts for template context
    posts = []
    for b in page_blogs:
        posts.append({
            'id': b.id,
            'slug': b.slug,
            'title': b.get_title(locale),
            'excerpt': b.get_short_desc(locale) or '',
            'cover_image_url': b.image or '/static/assets/online-tyres-shop-dubai.png',
            'published_at': b.published_at or b.created_at,
            'badges': [{'icon': 'star', 'label': 'Featured'}] if b.id == 1 else [],
            'get_title': b.get_title,
            'get_short_desc': b.get_short_desc,
            'image': b.image
        })

    pagination = {
        'page': page_num,
        'per_page': per_page,
        'total': total_count,
        'num_pages': num_pages,
        'start': start_item,
        'end': end_item,
        'has_prev': page_num > 1,
        'has_next': page_num < num_pages,
        'prev_num': page_num - 1,
        'next_num': page_num + 1
    }

    return render_template(
        'Client/BlogList.html',
        posts=posts,
        blogs=page_blogs,
        pagination=pagination,
        categories=CATEGORY_LIST,
        active_cat=cat_filter,
        search_query=search_query,
        locale=locale
    )


# ============================================================================
# 3. BLOG DETAIL (PAGE B: /blog/<slug>)
# ============================================================================

@site_bp.route('/blog/<slug>')
@site_bp.route('/blogs/<slug>')
def blog_detail(slug):
    """
    Blog Detail — Single article reader with author box, share row,
    rich body, comparison table, FAQ accordion, prev/next, and sidebar.
    """
    locale = _get_locale()
    blog = Blog.find_by_slug(slug)
    if not blog:
        page = Page.find_by_slug(slug)
        if page:
            return render_template('Client/Page.html', page=page, locale=locale)
        abort(404)

    all_published = Blog.published()
    prev_post = None
    next_post = None
    for i, b in enumerate(all_published):
        if b.slug == slug:
            if i > 0:
                prev_b = all_published[i - 1]
                prev_post = {'slug': prev_b.slug, 'title': prev_b.get_title(locale)}
            if i < len(all_published) - 1:
                next_b = all_published[i + 1]
                next_post = {'slug': next_b.slug, 'title': next_b.get_title(locale)}
            break

    # Build recent posts list (up to 5)
    recent_candidates = [b for b in all_published if b.slug != slug][:5]
    recent_posts = []
    for rb in recent_candidates:
        recent_posts.append({
            'slug': rb.slug,
            'title': rb.get_title(locale),
            'thumbnail_url': rb.image or '/static/assets/online-tyres-shop-dubai.png',
            'image': rb.image,
            'get_title': rb.get_title
        })

    # Prepare author & article data
    post_data = {
        'id': blog.id,
        'slug': blog.slug,
        'title': blog.get_title(locale),
        'published_at': blog.published_at or blog.created_at,
        'updated_at': blog.updated_at,
        'cover_image_url': blog.image or '/static/assets/online-tyres-shop-dubai.png',
        'image': blog.image,
        'body_html': blog.get_content(locale),
        'author': {
            'name': 'Sharvil Kumar',
            'role': 'Tyre Selection Specialist, TyresVision' if locale != 'ar' else 'أخصائي اختيار الإطارات، تايرز فيجن',
            'bio': 'Sharvil Kumar oversees technical guidance at TyresVision, helping UAE drivers select safe, GCC-spec tyres tailored for extreme summer heat and highway conditions.' if locale != 'ar' else 'يشرف شارفيل كومار على المحتوى الفني في تايرز فيجن لمساعدة السائقين في اختيار الإطارات المتوافقة مع حرارة صيف الإمارات.',
            'avatar_initials': 'SK',
            'reviewed_at': (blog.published_at or blog.created_at).strftime('%B %d, %Y') if (blog.published_at or blog.created_at) else 'August 24, 2026'
        },
        'categories': CATEGORY_LIST,
        'get_title': blog.get_title,
        'get_content': blog.get_content,
        'get_meta_title': blog.get_meta_title,
        'get_meta_desc': blog.get_meta_desc,
        'get_short_desc': blog.get_short_desc
    }

    return render_template(
        'Client/BlogDetail.html',
        post=post_data,
        blog=blog,
        recent_posts=recent_posts,
        recent_blogs=recent_candidates,
        faqs=DEFAULT_FAQS,
        prev_post=prev_post,
        next_post=next_post,
        prev_blog=prev_post,
        next_blog=next_post,
        categories=CATEGORY_LIST,
        locale=locale
    )


# ============================================================================
# 4. STATIC CMS PAGES
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

    blog = Blog.find_by_slug(slug)
    if blog:
        return redirect(url_for('site.blog_detail', slug=slug, locale=locale))

    abort(404)
