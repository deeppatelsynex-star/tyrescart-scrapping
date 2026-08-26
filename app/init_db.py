from db import get_connection

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


def main():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_USER_TBL)
            cursor.execute(CREATE_FILE_TBL)
            cursor.execute(CREATE_LOG_TBL)
            cursor.execute(CREATE_PAGES_TBL)
            cursor.execute(CREATE_BLOGS_TBL)
            add_missing_columns(cursor)
            cleanup_deprecated_tables(cursor)
            add_missing_indexes(cursor)
            update_legacy_stopped_logs(cursor)
        print("Schema verified: userTbl, fileTbl, logTbl, pages, blogs are ready.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
