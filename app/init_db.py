from db import get_connection

CREATE_ADMIN_USERS_TBL = """
CREATE TABLE IF NOT EXISTS admin_users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('super_admin', 'manager', 'support') NOT NULL DEFAULT 'super_admin',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    last_login_at TIMESTAMP NULL DEFAULT NULL,
    remember_token VARCHAR(100) NULL DEFAULT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_admin_email (email),
    INDEX idx_admin_role (role),
    INDEX idx_admin_active (is_active)
)
"""

CREATE_PASSWORD_RESET_TOKENS_TBL = """
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_reset_token (token),
    INDEX idx_reset_email (email)
)
"""

CREATE_USER_TBL = """
CREATE TABLE IF NOT EXISTS userTbl (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    Status BIT(1) NOT NULL DEFAULT 1,
    IsDeleted BIT(1) NOT NULL DEFAULT 0,
    Role VARCHAR(50) NOT NULL,
    avatar VARCHAR(500) NULL,
    updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    INDEX idx_user_deleted_id (IsDeleted, userid),
    INDEX idx_user_role (Role)
)
"""

NEW_USER_COLUMNS = {
    "avatar": "ALTER TABLE userTbl ADD COLUMN avatar VARCHAR(500) NULL",
    "updated_at": "ALTER TABLE userTbl ADD COLUMN updated_at TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP",
    "created_at": "ALTER TABLE userTbl ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
    "deleted_at": "ALTER TABLE userTbl ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL",
}


CREATE_FILE_TBL = """
CREATE TABLE IF NOT EXISTS fileTbl (
    file_id INT AUTO_INCREMENT PRIMARY KEY,
    logo VARCHAR(500) NULL,
    site_name VARCHAR(255) NOT NULL,
    python_file_path VARCHAR(255) NOT NULL UNIQUE,
    urls_json TEXT NULL,
    working BIT(1) NOT NULL DEFAULT 0,
    is_deleted BIT(1) NOT NULL DEFAULT 0,
    deleted_at TIMESTAMP NULL DEFAULT NULL,
    created_by INT NULL,
    create_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    update_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_file_deleted_id (is_deleted, file_id),
    INDEX idx_file_site_name (site_name),
    INDEX idx_file_working (working)
)
"""

NEW_FILE_COLUMNS = {
    "is_deleted": "ALTER TABLE fileTbl ADD COLUMN is_deleted BIT(1) NOT NULL DEFAULT 0",
    "deleted_at": "ALTER TABLE fileTbl ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL",
    "created_by": "ALTER TABLE fileTbl ADD COLUMN created_by INT NULL",
}


CREATE_LOG_TBL = """
CREATE TABLE IF NOT EXISTS logTbl (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id VARCHAR(32) NULL UNIQUE,
    scraper VARCHAR(255) NOT NULL,
    file_id INT NULL,
    user_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL DEFAULT NULL,
    no_of_url_found INT NOT NULL DEFAULT 0,
    total_success_url INT NOT NULL DEFAULT 0,
    total_block_url INT NOT NULL DEFAULT 0,
    data_scraped INT NOT NULL DEFAULT 0,
    total_products INT NOT NULL DEFAULT 0,
    pending_urls INT NOT NULL DEFAULT 0,
    running_urls INT NOT NULL DEFAULT 0,
    completed_urls INT NOT NULL DEFAULT 0,
    blocked_urls INT NOT NULL DEFAULT 0,
    main_url_done INT NOT NULL DEFAULT 0,
    product_url_done INT NOT NULL DEFAULT 0,
    progress_percent FLOAT NOT NULL DEFAULT 0.0,
    status VARCHAR(50) NOT NULL DEFAULT 'RUNNING',
    output_file_path VARCHAR(500) NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    process_id INT NULL,
    FOREIGN KEY (user_id) REFERENCES userTbl(userid) ON DELETE CASCADE,
    INDEX idx_log_user_id (user_id),
    INDEX idx_log_file_id (file_id),
    INDEX idx_log_start_time (start_time),
    INDEX idx_log_file_id_id (file_id, id),
    INDEX idx_log_status_id (status, id),
    INDEX idx_log_user_id_id (user_id, id),
    INDEX idx_log_scraper (scraper)
)
"""

NEW_LOG_COLUMNS = {
    "process_id": "ALTER TABLE logTbl ADD COLUMN process_id INT NULL",
    "job_id": "ALTER TABLE logTbl ADD COLUMN job_id VARCHAR(32) NULL UNIQUE",
    "progress_percent": "ALTER TABLE logTbl ADD COLUMN progress_percent FLOAT NOT NULL DEFAULT 0.0",
    "total_products": "ALTER TABLE logTbl ADD COLUMN total_products INT NOT NULL DEFAULT 0",
    "pending_urls": "ALTER TABLE logTbl ADD COLUMN pending_urls INT NOT NULL DEFAULT 0",
    "completed_urls": "ALTER TABLE logTbl ADD COLUMN completed_urls INT NOT NULL DEFAULT 0",
    "blocked_urls": "ALTER TABLE logTbl ADD COLUMN blocked_urls INT NOT NULL DEFAULT 0",
    "main_url_done": "ALTER TABLE logTbl ADD COLUMN main_url_done INT NOT NULL DEFAULT 0",
    "product_url_done": "ALTER TABLE logTbl ADD COLUMN product_url_done INT NOT NULL DEFAULT 0",
}

CREATE_PAGES_TBL = """
CREATE TABLE IF NOT EXISTS `pages` (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `title` json NOT NULL,
  `slug` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` json DEFAULT NULL,
  `banner_image` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `seo_title` json DEFAULT NULL,
  `meta_description` json DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `created_by` bigint UNSIGNED DEFAULT NULL,
  `updated_by` bigint UNSIGNED DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` timestamp NULL DEFAULT NULL,
  UNIQUE KEY `uq_pages_slug` (`slug`),
  KEY `idx_pages_is_active` (`is_active`),
  KEY `idx_pages_deleted_at` (`deleted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

CREATE_PAGE_SECTIONS_TBL = """
CREATE TABLE IF NOT EXISTS `page_sections` (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `page_slug` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'about-us',
  `section_type` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `section_title` json NOT NULL,
  `section_subtitle` json DEFAULT NULL,
  `content` json DEFAULT NULL,
  `image` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `image_position` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'right',
  `button_text` json DEFAULT NULL,
  `button_url` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `section_data` json DEFAULT NULL,
  `sort_order` int NOT NULL DEFAULT 0,
  `is_active` tinyint(1) NOT NULL DEFAULT 1,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` timestamp NULL DEFAULT NULL,
  KEY `idx_sections_slug` (`page_slug`),
  KEY `idx_sections_active_order` (`page_slug`, `is_active`, `sort_order`),
  KEY `idx_sections_deleted_at` (`deleted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

CREATE_BLOGS_TBL = """
CREATE TABLE IF NOT EXISTS `blogs` (
  `id` bigint UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY,
  `title` json NOT NULL,
  `slug` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content` json NOT NULL,
  `short_description` json DEFAULT NULL,
  `image` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `category_name` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `blog_category_id` bigint UNSIGNED DEFAULT NULL,
  `author_id` bigint UNSIGNED DEFAULT NULL,
  `status` enum('draft','published','archived') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'draft',
  `published_at` timestamp NULL DEFAULT NULL,
  `meta_title` json DEFAULT NULL,
  `meta_desc` json DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `deleted_at` timestamp NULL DEFAULT NULL,
  `created_by` bigint UNSIGNED DEFAULT NULL,
  `updated_by` bigint UNSIGNED DEFAULT NULL,
  UNIQUE KEY `blogs_slug_unique` (`slug`),
  KEY `blogs_status_index` (`status`),
  KEY `blogs_published_at_index` (`published_at`),
  KEY `blogs_category_name_index` (`category_name`),
  KEY `blogs_blog_category_id_index` (`blog_category_id`),
  KEY `blogs_created_by_foreign` (`created_by`),
  KEY `blogs_updated_by_foreign` (`updated_by`),
  KEY `idx_blogs_deleted_at` (`deleted_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
"""

NEW_BLOG_COLUMNS = {
    "category_name": "ALTER TABLE blogs ADD COLUMN category_name VARCHAR(255) NULL AFTER image",
}

PERFORMANCE_INDEXES = [
    ("logTbl", "idx_log_file_id_id", "(file_id, id)"),
    ("logTbl", "idx_log_status_id", "(status, id)"),
    ("logTbl", "idx_log_user_id_id", "(user_id, id)"),
    ("logTbl", "idx_log_scraper", "(scraper)"),
    ("fileTbl", "idx_file_deleted_id", "(is_deleted, file_id)"),
    ("fileTbl", "idx_file_site_name", "(site_name)"),
    ("fileTbl", "idx_file_working", "(working)"),
    ("userTbl", "idx_user_deleted_id", "(IsDeleted, userid)"),
    ("userTbl", "idx_user_role", "(Role)"),
]


def add_missing_columns(cursor):
    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'userTbl'"
    )
    existing_user = {row["COLUMN_NAME"] for row in cursor.fetchall()}
    for column, statement in NEW_USER_COLUMNS.items():
        if column not in existing_user:
            cursor.execute(statement)

    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'fileTbl'"
    )
    existing_file = {row["COLUMN_NAME"] for row in cursor.fetchall()}
    for column, statement in NEW_FILE_COLUMNS.items():
        if column not in existing_file:
            cursor.execute(statement)

    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'logTbl'"
    )
    existing_log = {row["COLUMN_NAME"] for row in cursor.fetchall()}
    for column, statement in NEW_LOG_COLUMNS.items():
        if column not in existing_log:
            try:
                cursor.execute(statement)
            except Exception:
                pass

    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'blogs'"
    )
    existing_blogs = {row["COLUMN_NAME"] for row in cursor.fetchall()}
    for column, statement in NEW_BLOG_COLUMNS.items():
        if column not in existing_blogs:
            try:
                cursor.execute(statement)
            except Exception:
                pass


def add_missing_indexes(cursor):
    """Ensures high-performance database indexes exist across all core tables."""
    for table, index_name, cols in PERFORMANCE_INDEXES:
        cursor.execute(
            """
            SELECT COUNT(*) AS cnt 
            FROM information_schema.STATISTICS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = %s 
              AND INDEX_NAME = %s
            """,
            (table, index_name),
        )
        if cursor.fetchone()["cnt"] == 0:
            try:
                cursor.execute(f"CREATE INDEX {index_name} ON {table} {cols}")
            except Exception:
                pass


def cleanup_deprecated_tables(cursor):
    """Drops deprecated tables and triggers per user requirement."""
    cursor.execute("DROP TRIGGER IF EXISTS before_scraper_job_insert")
    cursor.execute("DROP TRIGGER IF EXISTS after_scraper_job_update")
    cursor.execute("DROP TABLE IF EXISTS password_reset_tbl")
    cursor.execute("DROP TABLE IF EXISTS scraper_job_locks")
    cursor.execute("DROP TABLE IF EXISTS scraper_jobs")
    cursor.execute("DROP TABLE IF EXISTS scraperReportTbl")


def update_legacy_stopped_logs(cursor):
    """Backfills legacy logs where scraper was stopped by user to status='STOPPED'."""
    cursor.execute(
        """
        UPDATE logTbl 
        SET status = 'STOPPED' 
        WHERE status != 'STOPPED' 
          AND (
            LOWER(error_message) LIKE '%stopped by user%' 
            OR LOWER(error_message) LIKE '%status: stopped%'
            OR status = 'STOP'
          )
        """
    )


def seed_default_about_us_sections(cursor):
    """Populates default predefined sections for about-us if empty."""
    import json
    cursor.execute("SELECT COUNT(*) as cnt FROM page_sections WHERE page_slug = 'about-us' AND deleted_at IS NULL")
    if cursor.fetchone()["cnt"] > 0:
        return

    default_sections = [
        (
            "about-us",
            "hero",
            json.dumps({"en": "Driven by Confidence,\nBuilt for the Road.", "ar": "مدفوعون بالثقة،\nمصممون للطريق."}, ensure_ascii=False),
            json.dumps({"en": "ABOUT US", "ar": "من نحن"}, ensure_ascii=False),
            json.dumps({"en": "At TyresVision, we deliver premium tyres that combine cutting-edge technology, superior performance, and lasting reliability. Because every journey deserves confidence.", "ar": "في تايرز فيجن، نقدم إطارات فائقة الجودة تجمع بين أحدث التقنيات والأداء المتميز والاعتمادية الدائمة. لأن كل رحلة تستحق قيادة واثقة وآمنة."}, ensure_ascii=False),
            "/static/assets/about/hero-tyre-showroom.jpg",
            "right",
            json.dumps({"en": "Our Journey →", "ar": "استكشف مسيرتنا ←"}, ensure_ascii=False),
            "#our-story",
            json.dumps({
                "features": [
                    {"icon": "shield-check", "title": {"en": "Premium Quality", "ar": "جودة ممتازة"}, "sub": {"en": "Trusted brands and superior quality.", "ar": "علامات تجارية موثوقة وجودة فائقة."}},
                    {"icon": "dollar-sign", "title": {"en": "Best Prices", "ar": "أفضل الأسعار"}, "sub": {"en": "Competitive prices every day.", "ar": "أسعار تنافسية وشفافة كل يوم."}},
                    {"icon": "truck", "title": {"en": "Fast Delivery", "ar": "توصيل سريع"}, "sub": {"en": "Quick and reliable delivery.", "ar": "توصيل وتركيب سريع وموثوق."}},
                    {"icon": "headset", "title": {"en": "Expert Support", "ar": "دعم الخبراء"}, "sub": {"en": "We're here to help you anytime.", "ar": "نحن هنا لمساعدتك في أي وقت."}}
                ]
            }, ensure_ascii=False),
            1,
            1
        ),
        (
            "about-us",
            "content_image",
            json.dumps({"en": "The Road That Started Our Journey.", "ar": "الطريق الذي بدأ منه مشوارنا."}, ensure_ascii=False),
            json.dumps({"en": "OUR STORY", "ar": "قصتنا"}, ensure_ascii=False),
            json.dumps({"en": "TyresVision was built with a simple mission — to make high-quality tyres accessible to everyone. What started as a small idea is today a trusted name for thousands of customers.\n\nWe partner with world-class brands, use advanced technology, and maintain rigorous quality standards to ensure you get the best performance, every single time.\n\nFrom city streets to highway adventures, we're here to keep you moving forward with confidence.", "ar": "أُنشئت تايرز فيجن بمهمة واضحة وبسيطة — توفير إطارات سيارات عالية الجودة بأسعار عادلة ومتاحة للجميع. ما بدأ كفكرة رقمية مبتكرة أصبح اليوم اسماً موثوقاً لآلاف السائقين في دولة الإمارات.\n\nنتعاون مع كبرى الشركات المصنعة العالمية، ونستخدم أحدث التقنيات لضمان معايير جودة صارمة تمنحك الأداء الأفضل في كل مرة تنطلق فيها على الطريق.\n\nمن شوارع المدينة إلى الطرق السريعة الطويلة، نحن هنا لنضمن استمرار رحلتك بكل أمان وثقة."}, ensure_ascii=False),
            "/static/assets/about/warehouse-tyres.jpg",
            "left",
            json.dumps({"en": "Learn More About Us →", "ar": "تعرف أكثر على قصتنا ←"}, ensure_ascii=False),
            "/#why",
            json.dumps({
                "badge_title": {"en": "Customer First", "ar": "العميل أولاً"},
                "badge_sub": {"en": "Your safety and satisfaction are our priority.", "ar": "سلامتك ورضاك هما أولويتنا القصوى."},
                "badge_icon": "users"
            }, ensure_ascii=False),
            2,
            1
        ),
        (
            "about-us",
            "features",
            json.dumps({"en": "What Drives Us Forward", "ar": "ما يدفعنا دوماً إلى الأمام"}, ensure_ascii=False),
            json.dumps({"en": "OUR VALUES", "ar": "قيمنا ومبادئنا"}, ensure_ascii=False),
            json.dumps({"en": "Our values guide everything we do and help us build lasting relationships with our customers.", "ar": "ترشدنا قيمنا في كل خطوة نبني بها علاقات طويلة الأمد مع عملائنا وشركائنا."}, ensure_ascii=False),
            None,
            "right",
            None,
            None,
            json.dumps({
                "cards": [
                    {"icon": "shield", "title": {"en": "Integrity", "ar": "النزاهة والصدق"}, "desc": {"en": "Honest business practices and transparent relationships.", "ar": "ممارسات تجارية نزيهة وعلاقات واضحة وشفافة."}},
                    {"icon": "award", "title": {"en": "Quality", "ar": "أعلى معايير الجودة"}, "desc": {"en": "We never compromise on the quality of products and services.", "ar": "لا نساوم أبداً على جودة الإطارات والخدمات المقدمة."}},
                    {"icon": "heart", "title": {"en": "Customer Focus", "ar": "التركيز على العميل"}, "desc": {"en": "Your needs inspire us to deliver better every single day.", "ar": "احتياجاتك تلهمنا لتقديم خدمة أسرع وأفضل كل يوم."}},
                    {"icon": "zap", "title": {"en": "Innovation", "ar": "الابتكار المستمر"}, "desc": {"en": "Constantly improving through technology and smarter solutions.", "ar": "تطوير مستمر من خلال الحلول الرقمية والتقنيات الذكية."}},
                    {"icon": "globe", "title": {"en": "Sustainability", "ar": "الاستدامة والمسؤولية"}, "desc": {"en": "Responsible choices for a better tomorrow.", "ar": "خيارات مسؤولة وحلول بيئية لمستقبل أفضل."}}
                ]
            }, ensure_ascii=False),
            3,
            1
        ),
        (
            "about-us",
            "stats",
            json.dumps({"en": "Our Numbers Speak", "ar": "أرقامنا تتحدث"}, ensure_ascii=False),
            json.dumps({"en": "STATISTICS", "ar": "الإحصائيات"}, ensure_ascii=False),
            None,
            None,
            "right",
            None,
            None,
            json.dumps({
                "metrics": [
                    {"icon": "users", "number": "50K+", "heading": {"en": "Happy Customers", "ar": "عميل سعيد وموثوق"}, "subtext": {"en": "Trusted by drivers across the country.", "ar": "موثوق من آلاف السائقين عبر الدولة."}},
                    {"icon": "disc", "number": "20K+", "heading": {"en": "Tyres Sold", "ar": "إطار تم تركيبه"}, "subtext": {"en": "A wide range of tyres for every need.", "ar": "تشكيلة ضخمة تغطي كافة الاحتياجات."}},
                    {"icon": "globe", "number": "100+", "heading": {"en": "Top Brands", "ar": "علامة تجارية رائدة"}, "subtext": {"en": "Offering the world's most trusted tyre brands.", "ar": "نقدم أشهر الماركات العالمية المعتمدة."}},
                    {"icon": "award", "number": "10+", "heading": {"en": "Years of Experience", "ar": "سنوات من الخبرة"}, "subtext": {"en": "Decade of expertise in tyre industry.", "ar": "عقد من التميز والاحترافية في قطاع الإطارات."}}
                ]
            }, ensure_ascii=False),
            4,
            1
        ),
        (
            "about-us",
            "mission_vision",
            json.dumps({"en": "People Behind Our Performance", "ar": "الكوادر وراء تميز أدائنا"}, ensure_ascii=False),
            json.dumps({"en": "OUR TEAM", "ar": "فريق العمل"}, ensure_ascii=False),
            json.dumps({"en": "Our team is made up of passionate professionals who live and breathe automotive excellence.\n\nFrom product experts to customer support, we work together to ensure you get the best experience with every interaction.", "ar": "يتكون فريقنا من محترفين شغوفين يعيشون ويتنفسون التميز في عالم السيارات وخدمات الإطارات.\n\nمن خبراء المنتجات والمقاسات إلى مهندسي خدمة العملاء وفنيي التركيب المتنقل، نعمل معاً لضمان حصولك على أفضل تجربة مع كل تواصل."}, ensure_ascii=False),
            "/static/assets/about/team-specialists.jpg",
            "right",
            json.dumps({"en": "Meet Our Team →", "ar": "تعرف على فريقنا ←"}, ensure_ascii=False),
            "https://wa.me/971505069575?text=Hi%20TyresVision%20Team",
            json.dumps({}, ensure_ascii=False),
            5,
            1
        ),
        (
            "about-us",
            "features",
            json.dumps({"en": "Committed to Quality. Committed to You.", "ar": "ملتزمون بالجودة. ملتزمون برضاك."}, ensure_ascii=False),
            json.dumps({"en": "OUR COMMITMENT", "ar": "التزامنا الدائم"}, ensure_ascii=False),
            json.dumps({"en": "We are committed to providing premium quality tyres, exceptional service, and honest advice. Your trust is what drives us to keep raising the bar.", "ar": "نحن ملتزمون بتقديم إطارات سيارات فائقة الجودة، وخدمة استثنائية، ومشورة صادقة. ثقتكم هي دافعنا الدائم للارتقاء بالمعايير."}, ensure_ascii=False),
            None,
            "right",
            None,
            None,
            json.dumps({
                "cards": [
                    {"icon": "shield-check", "title": {"en": "Safe & Reliable", "ar": "أمان واعتمادية"}, "desc": {"en": "Tyres you can count on for every journey.", "ar": "إطارات يمكنك الاعتماد عليها في كل رحلة."}},
                    {"icon": "award", "title": {"en": "Tested & Trusted", "ar": "مختبرة وموثوقة"}, "desc": {"en": "Every product meets strict quality standards.", "ar": "كل منتج يطابق أعلى معايير الجودة الصارمة."}},
                    {"icon": "headset", "title": {"en": "Always Here", "ar": "دائماً بجانبك"}, "desc": {"en": "Support you can rely on, whenever you need.", "ar": "دعم يمكنك الاعتماد عليه كلما احتجت."}},
                    {"icon": "users", "title": {"en": "Long-Term Partnership", "ar": "شراكة طويلة الأمد"}, "desc": {"en": "Building relationships beyond just business.", "ar": "نبني علاقات ثقة تتجاوز مجرد المعاملات التجارية."}}
                ]
            }, ensure_ascii=False),
            6,
            1
        ),
        (
            "about-us",
            "cta",
            json.dumps({"en": "Let's Move Forward Together.", "ar": "دعنا ننطلق معاً إلى الأمام."}, ensure_ascii=False),
            json.dumps({"en": "GET STARTED", "ar": "ابدأ الآن"}, ensure_ascii=False),
            json.dumps({"en": "Explore our range of premium tyres and experience the difference with TyresVision.", "ar": "استكشف مجموعتنا من الإطارات الممتازة وجرّب الفارق مع تايرز فيجن."}, ensure_ascii=False),
            "/static/assets/about/wheel-rim.png",
            "left",
            json.dumps({"en": "Contact Us Today →", "ar": "تواصل معنا اليوم ←"}, ensure_ascii=False),
            "https://wa.me/971505069575?text=Hi%20TyresVision%2C%20I%20would%20like%20to%20contact%20you%20today.",
            json.dumps({}, ensure_ascii=False),
            7,
            1
        )
    ]

    sql = """
        INSERT INTO page_sections (
            page_slug, section_type, section_title, section_subtitle,
            content, image, image_position, button_text, button_url,
            section_data, sort_order, is_active
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for sec in default_sections:
        cursor.execute(sql, sec)


def main():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_ADMIN_USERS_TBL)
            cursor.execute(CREATE_PASSWORD_RESET_TOKENS_TBL)
            cursor.execute(CREATE_USER_TBL)
            cursor.execute(CREATE_FILE_TBL)
            cursor.execute(CREATE_LOG_TBL)
            cursor.execute(CREATE_PAGES_TBL)
            cursor.execute(CREATE_PAGE_SECTIONS_TBL)
            cursor.execute(CREATE_BLOGS_TBL)
            add_missing_columns(cursor)
            cleanup_deprecated_tables(cursor)
            add_missing_indexes(cursor)
            update_legacy_stopped_logs(cursor)
            seed_default_about_us_sections(cursor)
        conn.commit()
        print("Schema verified: admin_users, password_reset_tokens, userTbl, fileTbl, logTbl, pages, page_sections, blogs are ready.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
