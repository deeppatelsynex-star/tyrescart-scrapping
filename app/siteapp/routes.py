# app/siteapp/routes.py - TyresVision Customer Storefront Blueprint ('site')
import math
from flask import Blueprint, render_template, request, session, jsonify, abort, redirect, url_for
from models.blog import Blog
from models.page import Page

site_bp = Blueprint('site', __name__)


def _get_locale():
    req_locale = request.args.get('locale')
    if req_locale in ('en', 'ar'):
        session['site_locale'] = req_locale
        return req_locale
    return session.get('site_locale', 'en')


# Fallback curated blogs if database is fresh / empty
FALLBACK_BLOGS = [
    {
        'id': 1,
        'slug': 'how-to-read-your-tyre-size',
        'title': 'How to read your tyre size (and why it matters)',
        'title_ar': 'كيفية قراءة مقاس إطارات سيارتك ولماذا هو مهم جداً',
        'short_description': "Those numbers on your sidewall — 235/55 R19 105W — aren't random. Here's what each part means and why getting even one digit wrong can affect handling and warranty.",
        'short_description_ar': 'تلك الأرقام المطبوعة على جدار الإطار — 235/55 R19 105W — ليست عشوائية. إليك شرح كامل لكل رقم وكيف يؤثر على القيادة والضمان.',
        'content': '<p>Those numbers on your sidewall — 235/55 R19 105W — aren\'t random. Here\'s what each part means and why getting even one digit wrong can affect handling and warranty.</p>',
        'category': 'Buying Guide',
        'category_ar': 'دليل الشراء',
        'thumb_class': 't-buying',
        'image': '/static/assets/online-tyres-shop-dubai.png',
        'published_at': '12 Jan 2026',
        'read_time': '4 min read'
    },
    {
        'id': 2,
        'slug': 'nitrogen-vs-air-uae-heat',
        'title': 'Nitrogen vs. regular air: what actually changes in UAE heat',
        'title_ar': 'النيتروجين مقابل الهواء العادي: الفروقات الحقيقية في حرارة صيف الإمارات',
        'short_description': 'Asphalt temperatures here can push tyre pressure further than almost anywhere else. We break down whether nitrogen fill is worth it, and how often to check pressure in summer.',
        'short_description_ar': 'تصل حرارة الإسفلت في الإمارات إلى مستويات قياسية. نوضح لك هل يستحق النيتروجين التجربة وكم مرة يجب فحص الضغط صيفاً.',
        'content': '<p>Asphalt temperatures here can push tyre pressure further than almost anywhere else. We break down whether nitrogen fill is worth it, and how often to check pressure in summer.</p>',
        'category': 'Maintenance',
        'category_ar': 'الصيانة',
        'thumb_class': 't-maint',
        'image': '/static/assets/online-tyres-shop-dubai.png',
        'published_at': '28 Jan 2026',
        'read_time': '5 min read'
    },
    {
        'id': 3,
        'slug': 'signs-you-need-a-wheel-alignment',
        'title': '5 signs your wheels need an alignment',
        'title_ar': '5 علامات تدل على أن سيارتك بحاجة إلى ميزان ومحاذاة للعجلات',
        'short_description': 'Pulling to one side, uneven tread wear, a slightly off-centre steering wheel — small clues that are cheaper to fix now than as a full tyre replacement later.',
        'short_description_ar': 'انحراف المقود، التآكل غير المتساوي، أو اهتزاز السيارة — علامات مبكرة إصلاحها الآن يوفر عليك تكلفة استبدال الإطارات بالكامل.',
        'content': '<p>Pulling to one side, uneven tread wear, a slightly off-centre steering wheel — small clues that are cheaper to fix now than as a full tyre replacement later.</p>',
        'category': 'Maintenance',
        'category_ar': 'الصيانة',
        'thumb_class': 't-maint',
        'image': '/static/assets/online-tyres-shop-dubai.png',
        'published_at': '6 Feb 2026',
        'read_time': '3 min read'
    },
    {
        'id': 4,
        'slug': 'how-mobile-tyre-fitting-works',
        'title': 'Mobile tyre fitting: what happens when we come to you',
        'title_ar': 'خدمة تركيب الإطارات المتنقلة: كيف نصل إليك ونقوم بتبديل الإطارات في موقعك',
        'short_description': 'A walkthrough of a typical mobile fitting visit — from booking on WhatsApp to the van arriving at your building, office, or the mall car park.',
        'short_description_ar': 'شرح شامل لزيارة شاحنة التركيب المتنقلة — من لحظة الطلب عبر واتساب حتى وصول الفني إلى منزلك أو مقر عملك.',
        'content': '<p>A walkthrough of a typical mobile fitting visit — from booking on WhatsApp to the van arriving at your building, office, or the mall car park.</p>',
        'category': 'How It Works',
        'category_ar': 'كيف تعمل الخدمة',
        'thumb_class': 't-uae',
        'image': '/static/assets/online-tyres-shop-dubai.png',
        'published_at': '19 Feb 2026',
        'read_time': '4 min read'
    },
    {
        'id': 5,
        'slug': 'best-tyres-for-long-highway-drives',
        'title': 'Best tyres for long highway drives across the Gulf',
        'title_ar': 'أفضل الإطارات للرحلات الطويلة والخطوط السريعة بين مدن الإمارات والخليج',
        'short_description': "Dubai to Abu Dhabi on repeat, or the odd Oman road trip? Here's what load rating and compound to look for so a long drive doesn't turn into a breakdown.",
        'short_description_ar': 'سواء كنت تتنقل يومياً بين دبي وأبوظبي أو تسافر براً، إليك معايير مؤشر الحمولة والنقشة الهادئة للرحلات الطويلة.',
        'content': '<p>Dubai to Abu Dhabi on repeat, or the odd Oman road trip? Here\'s what load rating and compound to look for so a long drive doesn\'t turn into a breakdown.</p>',
        'category': 'Buying Guide',
        'category_ar': 'دليل الشراء',
        'thumb_class': 't-buying',
        'image': '/static/assets/online-tyres-shop-dubai.png',
        'published_at': '3 Mar 2026',
        'read_time': '5 min read'
    },
    {
        'id': 6,
        'slug': 'when-to-replace-a-tyre',
        'title': 'When should you actually replace a tyre?',
        'title_ar': 'متى يجب عليك استبدال إطارات سيارتك فعلياً؟',
        'short_description': 'Tread depth, sidewall cracking, age — the real signals to watch for, and why a tyre that "looks fine" can still be due for a swap.',
        'short_description_ar': 'عمق المداس، تشققات الجدار الجانبي، وعمر الإطار — الإشارات الحقيقية التي يجب الانتباه لها لسلامتك على الطريق.',
        'content': '<p>Tread depth, sidewall cracking, age — the real signals to watch for, and why a tyre that "looks fine" can still be due for a swap.</p>',
        'category': 'Maintenance',
        'category_ar': 'الصيانة',
        'thumb_class': 't-maint',
        'image': '/static/assets/online-tyres-shop-dubai.png',
        'published_at': '21 Mar 2026',
        'read_time': '4 min read'
    }
]


# ============================================================================
# 1. JSON API ENDPOINTS (GET BLOG FROM API)
# ============================================================================

@site_bp.route('/api/blogs', methods=['GET'])
@site_bp.route('/api/blog', methods=['GET'])
def api_get_blogs():
    """
    Public JSON API: Fetch published blogs with pagination, locale,
    search, and category filtering.
    """
    locale = _get_locale()
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

    if db_blogs and len(db_blogs) > 0:
        for b in db_blogs:
            formatted_blogs.append({
                'id': b.id,
                'slug': b.slug,
                'title': b.get_title(locale),
                'short_description': b.get_short_desc(locale) or '',
                'excerpt': b.get_short_desc(locale) or '',
                'content': b.get_content(locale),
                'image': b.image or '/static/assets/online-tyres-shop-dubai.png',
                'cover_image_url': b.image or '/static/assets/online-tyres-shop-dubai.png',
                'published_at': b.published_at.strftime('%d %b %Y') if b.published_at else (b.created_at.strftime('%d %b %Y') if b.created_at else '24 Aug 2026'),
                'category': 'Buying Guide' if 'choose' in b.slug or 'size' in b.slug else 'Maintenance',
                'thumb_class': 't-buying' if 'choose' in b.slug else 't-maint',
                'read_time': '4 min read',
                'url': f'/blog/{b.slug}'
            })

    # Include fallback articles so rich results are always returned
    for fb in FALLBACK_BLOGS:
        if not any(b['slug'] == fb['slug'] for b in formatted_blogs):
            formatted_blogs.append({
                'id': fb['id'],
                'slug': fb['slug'],
                'title': fb['title_ar'] if locale == 'ar' else fb['title'],
                'short_description': fb['short_description_ar'] if locale == 'ar' else fb['short_description'],
                'excerpt': fb['short_description_ar'] if locale == 'ar' else fb['short_description'],
                'content': fb['content'],
                'image': fb['image'],
                'cover_image_url': fb['image'],
                'published_at': fb['published_at'],
                'category': fb['category_ar'] if locale == 'ar' else fb['category'],
                'thumb_class': fb.get('thumb_class', 't-buying'),
                'read_time': fb.get('read_time', '4 min read'),
                'url': f'/blog/{fb["slug"]}'
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
            if cat_filter in b['category'].lower()
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
    locale = _get_locale()
    blog = Blog.find_by_slug(slug)
    
    if blog:
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
                'name': 'Sharvil Kumar',
                'role': 'Tyre Selection Specialist, TyresVision' if locale != 'ar' else 'أخصائي اختيار الإطارات، تايرز فيجن',
                'avatar_initials': 'SK'
            }
        }
        return jsonify({'success': True, 'blog': data})

    # Search in fallback articles
    for fb in FALLBACK_BLOGS:
        if fb['slug'] == slug:
            data = {
                'id': fb['id'],
                'slug': fb['slug'],
                'title': fb['title_ar'] if locale == 'ar' else fb['title'],
                'short_description': fb['short_description_ar'] if locale == 'ar' else fb['short_description'],
                'content': fb['content'],
                'image': fb['image'],
                'cover_image_url': fb['image'],
                'published_at': fb['published_at'],
                'author': {
                    'name': 'Sharvil Kumar',
                    'role': 'Tyre Selection Specialist, TyresVision' if locale != 'ar' else 'أخصائي اختيار الإطارات، تايرز فيجن',
                    'avatar_initials': 'SK'
                }
            }
            return jsonify({'success': True, 'blog': data})

    return jsonify({'success': False, 'error': 'Blog not found'}), 404


# ============================================================================
# 2. CLIENT STOREFRONT BLOG & STATIC PAGES
# ============================================================================

@site_bp.route('/')
@site_bp.route('/home')
def home():
    """Client storefront home landing page."""
    return render_template('Client/Home.html')


@site_bp.route('/blog')
@site_bp.route('/blog/')
@site_bp.route('/blogs')
@site_bp.route('/blogs/')
def blog():
    """Client blog catalog page."""
    return render_template('Client/Blog.html')


@site_bp.route('/blog/<slug>')
@site_bp.route('/blogs/<slug>')
def blog_detail(slug):
    """Client single blog detail reader."""
    locale = _get_locale()
    blog = Blog.find_by_slug(slug)
    
    if not blog:
        for fb in FALLBACK_BLOGS:
            if fb['slug'] == slug:
                blog_data = {
                    'title': fb['title_ar'] if locale == 'ar' else fb['title'],
                    'content': fb['content'],
                    'short_description': fb['short_description_ar'] if locale == 'ar' else fb['short_description'],
                    'cover_image_url': fb['image'],
                    'published_at': fb['published_at'],
                    'author': {'name': 'Sharvil Kumar', 'role': 'Tyre Specialist', 'avatar_initials': 'SK'}
                }
                return render_template('Client/BlogDetail.html', post=blog_data, locale=locale)
        abort(404)

    blog_data = {
        'title': blog.get_title(locale),
        'content': blog.get_content(locale),
        'short_description': blog.get_short_desc(locale),
        'cover_image_url': blog.image or '/static/assets/online-tyres-shop-dubai.png',
        'published_at': blog.published_at.strftime('%B %d, %Y') if blog.published_at else 'August 24, 2026',
        'author': {'name': 'Sharvil Kumar', 'role': 'Tyre Specialist', 'avatar_initials': 'SK'}
    }
    return render_template('Client/BlogDetail.html', post=blog_data, locale=locale)


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
