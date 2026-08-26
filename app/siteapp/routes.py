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

# Curated reference posts matching TyresVision / TyresCart design
REFERENCE_BLOG_POSTS = [
    {
        'slug': 'nitrogen-vs-air-in-tyres-what-will-work-better-for-your-car',
        'title': 'NITROGEN VS. AIR IN TYRES: WHAT WILL WORK BETTER FOR YOUR CAR',
        'title_ar': 'النيتروجين مقابل الهواء في الإطارات: أيهما أفضل لسيارتك في الإمارات',
        'excerpt': 'For most UAE drivers, both nitrogen and regular compressed air are suitable options for inflating tyres....',
        'excerpt_ar': 'بالنسبة لمعظم السائقين في الإمارات، يعتبر النيتروجين والهواء المضغوط العادي خيارين مناسبين لنفخ الإطارات...',
        'published_at': '24 Aug 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': [{'label': 'AIR'}]
    },
    {
        'slug': 'rfid-in-tyres-explained-how-it-works-benefits-and-why-it-matters',
        'title': 'RFID IN TYRES EXPLAINED: HOW IT WORKS, BENEFITS, AND WHY IT MATTERS',
        'title_ar': 'تقنية RFID في إطارات السيارات: كيف تعمل وفوائدها وأهميتها',
        'excerpt': 'RFID in tyres provides a digital identity to each tyre, which can be read without the need to use a printed label....',
        'excerpt_ar': 'توفر شريحة RFID في الإطارات هوية رقمية لكل إطار يمكن قراءتها دون الحاجة لملصقات ورقية مطبوعة...',
        'published_at': '22 Aug 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': []
    },
    {
        'slug': 'comfort-first-tyre-selection-for-bentley-rolls-royce-and-s-class',
        'title': 'COMFORT-FIRST TYRE SELECTION FOR BENTLEY, ROLLS-ROYCE AND S-CLASS',
        'title_ar': 'اختيار الإطارات المريحة والهادئة لسيارات بنتلي ورولز رويس ومرسيدس إس كلاس',
        'excerpt': 'If you drive a Bentley, Rolls-Royce, or S-Class, you know the car tires are more than just a basic vehicle part....',
        'excerpt_ar': 'إذا كنت تقود سيارة بنتلي أو رولز رويس أو إس كلاس، فإن اختيار الإطار المناسب يصنع الفارق في الهدوء والراحة...',
        'published_at': '19 Aug 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': []
    },
    {
        'slug': 'best-tyres-for-the-ford-ranger-and-ranger-raptor-in-uae',
        'title': 'BEST TYRES FOR THE FORD RANGER AND RANGER RAPTOR IN UAE',
        'title_ar': 'أفضل إطارات لفورد رينجر ورينجر رابتور في الإمارات للصحراء والطرق السريعة',
        'excerpt': 'Tyre selection for your Ford Ranger and Raptor requires taking into consideration not just the ability to fit....',
        'excerpt_ar': 'يتطلب اختيار إطارات فورد رينجر ورابتور مراعاة المتانة وقوة التماسك في الرمال وعلى الطرق المعبدة...',
        'published_at': '14 Aug 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': [{'label': 'Ranger and Raptor'}]
    },
    {
        'slug': 'when-tyre-wear-bars-become-visible-what-you-should-do',
        'title': 'WHEN TYRE WEAR BARS BECOME VISIBLE: WHAT YOU SHOULD DO',
        'title_ar': 'عندما تظهر مؤشرات تآكل مداس الإطار: متى يجب التغيير فوراً',
        'excerpt': 'When tyre wear bars become level with the surrounding tread, the tyre has approximately 1.6 mm of tread....',
        'excerpt_ar': 'عندما تصبح مؤشرات التآكل بمستوى مداس الإطار الخارجي، يكون عمق المداس قد وصل إلى 1.6 مم ويجب استبداله...',
        'published_at': '11 Aug 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': []
    },
    {
        'slug': 'michelin-pilot-sport-vs-continental-sportcontact-for-track-days',
        'title': 'MICHELIN PILOT SPORT VS CONTINENTAL SPORTCONTACT FOR TRACK DAYS',
        'title_ar': 'مقارنة ميشلان بايلوت سبورت ضد كونتيننتال سبورت كونتاكت لحلبات السباق',
        'excerpt': 'When attending Dubai Autodrome track days, choosing the right performance tires for your car is key....',
        'excerpt_ar': 'عند القيادة في حلبة دبي أوتودروم، فإن اختيار الإطارات عالية الأداء المناسبة يمنحك التماسك والتحكم الكامل...',
        'published_at': '07 Aug 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': [{'label': 'CONTINENTAL'}]
    },
    {
        'slug': 'tyre-rotation-in-uae-how-often-why-it-matters-and-what-to-expect',
        'title': 'TYRE ROTATION IN UAE: HOW OFTEN, WHY IT MATTERS, AND WHAT TO EXPECT',
        'title_ar': 'تدوير الإطارات في الإمارات: كم مرة وما هي أهميته لإطالة عمر الإطار',
        'excerpt': 'Yes, the most basic and easy methods of extending tyre life, enhancing driving safety, and ensuring uniform wear....',
        'excerpt_ar': 'يعد تدوير الإطارات دورياً من أسهل وأفضل الطرق لضمان التآكل المتساوي وتوفير استهلاك الوقود...',
        'published_at': '25 Jul 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': []
    },
    {
        'slug': 'buy-tyres-online-in-uae-and-get-them-fitted-at-home-how-it-works',
        'title': 'BUY TYRES ONLINE IN UAE AND GET THEM FITTED AT HOME: HOW IT WORKS',
        'title_ar': 'شراء الإطارات أونلاين في الإمارات مع خدمة التركيب المتنقل عند باب المنزل',
        'excerpt': 'Buying tyres online and having them fitted at your home or workplace has become one of the most convenient options....',
        'excerpt_ar': 'شراء الإطارات عبر الإنترنت وتركيبها في منزلك أو مقر عملك أصبح الخيار الأكثر راحة وتوفيراً للوقت...',
        'published_at': '23 Jul 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': []
    },
    {
        'slug': 'tyre-care-for-dubai-taxi-drivers-how-to-make-every-set-last-longer',
        'title': 'TYRE CARE FOR DUBAI TAXI DRIVERS: HOW TO MAKE EVERY SET LAST LONGER',
        'title_ar': 'العناية بالإطارات لسائقي التاكسي والأسطول في دبي: نصائح لزيادة عمر الإطارات',
        'excerpt': 'Adequate tyre care Dubai considerations can greatly enhance tyre life, decrease operating expenses, and improve comfort....',
        'excerpt_ar': 'تساعد الصيانة المناسبة للإطارات وضبط الضغط بانتظام على خفض التكاليف التشغيلية وتحسين راحة الركاب...',
        'published_at': '22 Jul 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': []
    },
    {
        'slug': 'uae-tyre-and-road-safety-laws-every-driver-must-know-in-2026',
        'title': 'UAE TYRE AND ROAD SAFETY LAWS EVERY DRIVER MUST KNOW IN 2026',
        'title_ar': 'قوانين سلامة الإطارات والمرور في الإمارات لعام 2026 التي يجب على كل سائق معرفتها',
        'excerpt': 'Tyres should meet the rules of tyre safety in the UAE if you want to drive without being caught and not be fined....',
        'excerpt_ar': 'يجب أن تتطابق الإطارات مع معايير السلامة المعتمدة في دولة الإمارات لتجنب المخالفات والحفاظ على سلامتك...',
        'published_at': '21 Jul 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': []
    },
    {
        'slug': 'off-road-driving-in-uae-wadis-and-sand-dunes-best-tyre-choices',
        'title': 'OFF-ROAD DRIVING IN UAE WADIS & SAND DUNES: BEST TYRE CHOICES',
        'title_ar': 'القيادة في الأودية والكثبان الرملية بالإمارات: أفضل خيارات الإطارات الوعرة',
        'excerpt': 'When off-roading in UAE sand dunes or rocky wadis, the two essential factors to consider are tire pressure and compound durability....',
        'excerpt_ar': 'عند القيادة على الرمال أو الطرق الوعرة في الإمارات، فإن تنفيس الإطارات واختيار النقشة المناسبة هما الأساس...',
        'published_at': '18 Jul 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': []
    },
    {
        'slug': 'brake-service-guide-for-uae-drivers-when-to-replace-pads-and-discs',
        'title': 'BRAKE SERVICE GUIDE FOR UAE DRIVERS: WHEN TO REPLACE PADS AND DISCS',
        'title_ar': 'دليل صيانة الفرامل في الإمارات: متى يجب استبدال الفحمات وأقراص المكابح',
        'excerpt': 'Brakes are one of the most important safety features in your vehicle. The frequent traffic, high-speed highways, and heat....',
        'excerpt_ar': 'تعد المكابح أهم أنظمة الأمان في سيارتك، خاصة مع حرارة الصيف والسرعات العالية على الطرق السريعة...',
        'published_at': '15 Jul 2026',
        'cover_image_url': '/static/assets/online-tyres-shop-dubai.png',
        'badges': []
    }
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


def _build_page_range(current_page, num_pages):
    """Builds an intuitive pagination range with ellipses (e.g. 1 2 3 4 5 ... 16)."""
    if num_pages <= 7:
        return list(range(1, num_pages + 1))
    
    if current_page <= 4:
        return [1, 2, 3, 4, 5, '...', num_pages]
    elif current_page >= num_pages - 3:
        return [1, '...', num_pages - 4, num_pages - 3, num_pages - 2, num_pages - 1, num_pages]
    else:
        return [1, '...', current_page - 1, current_page, current_page + 1, '...', num_pages]


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

    # Load from DB or fallback to curated seed reference list
    db_blogs = Blog.published()
    if db_blogs and len(db_blogs) > 0:
        all_posts = []
        for b in db_blogs:
            all_posts.append({
                'id': b.id,
                'slug': b.slug,
                'title': b.get_title(locale),
                'excerpt': b.get_short_desc(locale) or '',
                'cover_image_url': b.image or '/static/assets/online-tyres-shop-dubai.png',
                'published_at': b.published_at or b.created_at,
                'badges': [{'label': 'Featured'}] if b.id == 1 else [],
                'image': b.image
            })
    else:
        all_posts = []
        for ref in REFERENCE_BLOG_POSTS:
            all_posts.append({
                'id': ref['slug'],
                'slug': ref['slug'],
                'title': ref['title_ar'] if locale == 'ar' and 'title_ar' in ref else ref['title'],
                'excerpt': ref['excerpt_ar'] if locale == 'ar' and 'excerpt_ar' in ref else ref['excerpt'],
                'cover_image_url': ref['cover_image_url'],
                'published_at': ref['published_at'],
                'badges': ref.get('badges', []),
                'image': ref['cover_image_url']
            })

    # Keyword filter
    if search_query:
        all_posts = [
            p for p in all_posts
            if search_query.lower() in p['title'].lower() or
               search_query.lower() in p['excerpt'].lower()
        ]

    total_count = max(len(all_posts), 185 if len(all_posts) >= 12 else len(all_posts))

    try:
        page_num = max(1, int(request.args.get('page', 1)))
    except (ValueError, TypeError):
        page_num = 1

    try:
        per_page = int(request.args.get('per_page', request.args.get('limit', 12)))
        if per_page not in (4, 8, 12, 16, 24):
            per_page = 12
    except (ValueError, TypeError):
        per_page = 12

    num_pages = max(1, math.ceil(total_count / per_page))
    if page_num > num_pages:
        page_num = num_pages

    start_idx = (page_num - 1) * per_page
    end_idx = min(start_idx + per_page, total_count)
    page_posts = all_posts[start_idx:end_idx] if start_idx < len(all_posts) else all_posts[:per_page]

    start_item = start_idx + 1 if total_count > 0 else 0
    end_item = end_idx

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
        'next_num': page_num + 1,
        'pages': _build_page_range(page_num, num_pages)
    }

    return render_template(
        'Client/BlogList.html',
        posts=page_posts,
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
    
    # If not in DB, search reference list
    ref_match = None
    if not blog:
        for ref in REFERENCE_BLOG_POSTS:
            if ref['slug'] == slug:
                ref_match = ref
                break

    if not blog and not ref_match:
        page = Page.find_by_slug(slug)
        if page:
            return render_template('Client/Page.html', page=page, locale=locale)
        abort(404)

    all_published = Blog.published()
    prev_post = None
    next_post = None

    if blog and all_published:
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
    recent_posts = []
    if all_published and len(all_published) > 1:
        recent_candidates = [b for b in all_published if b.slug != slug][:5]
        for rb in recent_candidates:
            recent_posts.append({
                'slug': rb.slug,
                'title': rb.get_title(locale),
                'thumbnail_url': rb.image or '/static/assets/online-tyres-shop-dubai.png',
                'image': rb.image
            })
    else:
        for ref in REFERENCE_BLOG_POSTS[:5]:
            if ref['slug'] != slug:
                recent_posts.append({
                    'slug': ref['slug'],
                    'title': ref['title_ar'] if locale == 'ar' and 'title_ar' in ref else ref['title'],
                    'thumbnail_url': ref['cover_image_url'],
                    'image': ref['cover_image_url']
                })

    # Prepare author & article data
    if blog:
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
            'categories': CATEGORY_LIST
        }
    else:
        post_data = {
            'id': ref_match['slug'],
            'slug': ref_match['slug'],
            'title': ref_match['title_ar'] if locale == 'ar' and 'title_ar' in ref_match else ref_match['title'],
            'published_at': None,
            'updated_at': None,
            'cover_image_url': ref_match['cover_image_url'],
            'image': ref_match['cover_image_url'],
            'body_html': None,
            'author': {
                'name': 'Sharvil Kumar',
                'role': 'Tyre Selection Specialist, TyresVision' if locale != 'ar' else 'أخصائي اختيار الإطارات، تايرز فيجن',
                'bio': 'Sharvil Kumar oversees technical guidance at TyresVision, helping UAE drivers select safe, GCC-spec tyres tailored for extreme summer heat and highway conditions.' if locale != 'ar' else 'يشرف شارفيل كومار على المحتوى الفني في تايرز فيجن لمساعدة السائقين في اختيار الإطارات المتوافقة مع حرارة صيف الإمارات.',
                'avatar_initials': 'SK',
                'reviewed_at': 'August 24, 2026'
            },
            'categories': CATEGORY_LIST
        }

    return render_template(
        'Client/BlogDetail.html',
        post=post_data,
        blog=blog,
        recent_posts=recent_posts,
        faqs=DEFAULT_FAQS,
        prev_post=prev_post,
        next_post=next_post,
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
