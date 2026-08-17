from db import get_connection

CREATE_USER_TBL = """
CREATE TABLE IF NOT EXISTS userTbl (
    userid INT AUTO_INCREMENT PRIMARY KEY,
    Name VARCHAR(50) NOT NULL,
    Email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    Status BIT(1) NOT NULL DEFAULT 1,
    IsDeleted BIT(1) NOT NULL DEFAULT 0,
    Role VARCHAR(50) NOT NULL
)
"""

CREATE_PASSWORD_RESET_TBL = """
CREATE TABLE IF NOT EXISTS password_reset_tbl (
    id INT AUTO_INCREMENT PRIMARY KEY,
    userid INT NOT NULL,
    token_hash CHAR(64) NOT NULL UNIQUE,
    expires_at DATETIME NOT NULL,
    used BIT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (userid) REFERENCES userTbl(userid) ON DELETE CASCADE
)
"""

# Additive columns for the profile/avatar and trash features. Existence is
# checked via information_schema before adding, so this stays safe to re-run.
NEW_COLUMNS = {
    "avatar": "ALTER TABLE userTbl ADD COLUMN avatar VARCHAR(500) NULL",
    "updated_at": (
        "ALTER TABLE userTbl ADD COLUMN updated_at TIMESTAMP NULL "
        "DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"
    ),
    # Fixed at insert time (no ON UPDATE) so editing a user later doesn't
    # change when their account was originally created.
    "created_at": "ALTER TABLE userTbl ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP",
    # Set when a user is soft-deleted, cleared on restore. NULL for accounts
    # that have never been deleted (and for rows soft-deleted before this
    # column existed).
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
    update_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
)
"""

NEW_FILE_COLUMNS = {
    "is_deleted": "ALTER TABLE fileTbl ADD COLUMN is_deleted BIT(1) NOT NULL DEFAULT 0",
    "deleted_at": "ALTER TABLE fileTbl ADD COLUMN deleted_at TIMESTAMP NULL DEFAULT NULL",
    "created_by": "ALTER TABLE fileTbl ADD COLUMN created_by INT NULL",
}

NEW_LOG_COLUMNS = {
    "process_id": "ALTER TABLE logTbl ADD COLUMN process_id INT NULL",
}


CREATE_LOG_TBL = """
CREATE TABLE IF NOT EXISTS logTbl (
    id INT AUTO_INCREMENT PRIMARY KEY,
    scraper VARCHAR(255) NOT NULL,
    file_id INT NULL,
    user_id INT NOT NULL,
    start_time TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP NULL DEFAULT NULL,
    no_of_url_found INT NOT NULL DEFAULT 0,
    total_success_url INT NOT NULL DEFAULT 0,
    total_block_url INT NOT NULL DEFAULT 0,
    data_scraped INT NOT NULL DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'RUNNING',
    output_file_path VARCHAR(500) NULL,
    error_message TEXT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
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

CREATE_SCRAPER_JOBS_TBL = """
CREATE TABLE IF NOT EXISTS scraper_jobs (
    job_id VARCHAR(64) PRIMARY KEY,
    file_id INT NOT NULL,
    started_by_user_id INT NULL,
    status ENUM('QUEUED', 'RUNNING', 'STOPPING', 'SUCCESS', 'FAILED', 'STOPPED') NOT NULL DEFAULT 'QUEUED',
    total_urls INT DEFAULT 0,
    pending_urls INT DEFAULT 0,
    running_urls INT DEFAULT 0,
    completed_urls INT DEFAULT 0,
    blocked_urls INT DEFAULT 0,
    total_products INT DEFAULT 0,
    written_to_xlsx INT DEFAULT 0,
    main_url_done INT DEFAULT 0,
    product_url_done INT DEFAULT 0,
    progress_percent FLOAT DEFAULT 0.0,
    output_file_path VARCHAR(500) NULL,
    error_message TEXT NULL,
    process_id INT NULL,
    started_at DATETIME NULL,
    finished_at DATETIME NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_job_file_status (file_id, status),
    INDEX idx_job_status (status),
    INDEX idx_job_started_at (started_at),
    FOREIGN KEY (file_id) REFERENCES fileTbl(file_id) ON DELETE CASCADE
)
"""

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
    ("scraper_jobs", "idx_job_file_status", "(file_id, status)"),
]


def add_missing_columns(cursor):
    cursor.execute(
        "SELECT COLUMN_NAME FROM information_schema.COLUMNS "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'userTbl'"
    )
    existing_user = {row["COLUMN_NAME"] for row in cursor.fetchall()}
    for column, statement in NEW_COLUMNS.items():
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
            cursor.execute(statement)


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
            cursor.execute(f"CREATE INDEX {index_name} ON {table} {cols}")


CREATE_SCRAPER_JOB_LOCKS_TBL = """
CREATE TABLE IF NOT EXISTS scraper_job_locks (
    file_id INT NOT NULL PRIMARY KEY,
    job_id VARCHAR(255) NOT NULL,
    started_by_user_id INT NULL,
    locked_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""

TRIGGER_BEFORE_INSERT = """
CREATE TRIGGER before_scraper_job_insert
BEFORE INSERT ON scraper_jobs
FOR EACH ROW
BEGIN
    IF NEW.status = 'RUNNING' AND NEW.finished_at IS NULL THEN
        INSERT INTO scraper_job_locks (
            file_id,
            job_id,
            started_by_user_id
        )
        VALUES (
            NEW.file_id,
            NEW.job_id,
            NEW.started_by_user_id
        );
    END IF;
END;
"""

TRIGGER_AFTER_UPDATE = """
CREATE TRIGGER after_scraper_job_update
AFTER UPDATE ON scraper_jobs
FOR EACH ROW
BEGIN
    IF NEW.finished_at IS NOT NULL AND NEW.status IN ('SUCCESS', 'FAILED', 'STOPPED') THEN
        DELETE FROM scraper_job_locks
        WHERE file_id = NEW.file_id
          AND job_id = NEW.job_id;
    END IF;
END;
"""


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


def setup_triggers(cursor):
    """Initializes scraper_job_locks table, syncs active locks, and installs MySQL triggers."""
    cursor.execute(CREATE_SCRAPER_JOB_LOCKS_TBL)

    # Resolve any duplicate stale active jobs in scraper_jobs
    cursor.execute("""
        UPDATE scraper_jobs
        SET status = 'STOPPED', finished_at = NOW()
        WHERE status = 'RUNNING' AND finished_at IS NULL
    """)
    cursor.execute("DELETE FROM scraper_job_locks")

    # Install triggers safely
    cursor.execute("DROP TRIGGER IF EXISTS before_scraper_job_insert")
    cursor.execute(TRIGGER_BEFORE_INSERT)

    cursor.execute("DROP TRIGGER IF EXISTS after_scraper_job_update")
    cursor.execute(TRIGGER_AFTER_UPDATE)


def main():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(CREATE_USER_TBL)
            add_missing_columns(cursor)
            cursor.execute(CREATE_PASSWORD_RESET_TBL)
            cursor.execute(CREATE_FILE_TBL)
            cursor.execute("DROP TABLE IF EXISTS scraperReportTbl")
            cursor.execute(CREATE_LOG_TBL)
            cursor.execute(CREATE_SCRAPER_JOBS_TBL)
            setup_triggers(cursor)
            add_missing_indexes(cursor)
            update_legacy_stopped_logs(cursor)
        print("userTbl, password_reset_tbl, fileTbl, logTbl, scraper_jobs, and scraper_job_locks with triggers are ready.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
