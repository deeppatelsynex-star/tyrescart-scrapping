import os
from datetime import datetime
import openpyxl

from db import get_connection

LOG_SELECT_FIELDS = (
    'l.id, l.scraper, l.file_id, l.user_id, l.start_time, l.end_time, '
    'l.no_of_url_found, l.total_success_url, l.total_block_url, l.data_scraped, '
    'l.status, l.output_file_path, l.error_message, l.created_at, '
    'u.Name AS user_name, u.Email AS user_email, u.Role AS user_role, u.avatar AS user_avatar, '
    'f.site_name, f.python_file_path, f.logo AS file_logo'
)


def count_excel_data_rows(excel_path):
    """Safely counts non-empty data rows (excluding header) from an Excel file."""
    if not excel_path or not os.path.exists(excel_path):
        return 0
    try:
        wb = openpyxl.load_workbook(excel_path, read_only=True, data_only=True)
        sheet = wb.active
        if not sheet:
            wb.close()
            return 0
        count = 0
        for i, row in enumerate(sheet.iter_rows(values_only=True)):
            if i > 0 and row and any(row):
                count += 1
        wb.close()
        return count
    except Exception:
        return 0


def create_log_entry(user_id, file_id, scraper_name, process_id=None):
    """Inserts a new scraper run audit record into logTbl when a crawler starts."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO logTbl
                    (scraper, file_id, user_id, status, start_time, process_id)
                VALUES
                    (%s, %s, %s, 'RUNNING', NOW(), %s)
                """,
                (scraper_name, file_id, user_id, process_id),
            )
            return cursor.lastrowid
    finally:
        conn.close()


def get_active_log_for_file(file_id):
    """Returns the single active execution log from logTbl for file_id, or None."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, scraper, file_id, user_id, start_time, end_time, status, process_id,
                       no_of_url_found, total_success_url, total_block_url, data_scraped,
                       output_file_path, error_message
                FROM logTbl
                WHERE file_id = %s
                  AND (status = 'RUNNING' OR end_time IS NULL)
                ORDER BY id DESC
                LIMIT 1
                """,
                (file_id,),
            )
            return cursor.fetchone()
    finally:
        conn.close()


def update_log_progress(log_id, no_of_url_found=None, total_success_url=None, total_block_url=None, data_scraped=None):
    """Updates live crawling and scraping numbers in logTbl."""
    if not log_id:
        return
    sets = []
    params = []
    if no_of_url_found is not None:
        sets.append('no_of_url_found = %s')
        params.append(no_of_url_found)
    if total_success_url is not None:
        sets.append('total_success_url = %s')
        params.append(total_success_url)
    if total_block_url is not None:
        sets.append('total_block_url = %s')
        params.append(total_block_url)
    if data_scraped is not None:
        sets.append('data_scraped = %s')
        params.append(data_scraped)

    if not sets:
        return

    params.append(log_id)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f"UPDATE logTbl SET {', '.join(sets)} WHERE id = %s",
                tuple(params),
            )
    finally:
        conn.close()


def finish_log_entry(log_id, status='SUCCESS', no_of_url_found=0, total_success_url=0, total_block_url=0, data_scraped=0, output_file_path=None, error_message=None):
    """Records completion/stop/failure of a scraper run in logTbl.
    Statuses allowed: RUNNING, SUCCESS, FAIL, STOPPED.
    """
    if not log_id:
        return

    # Normalize status
    st = (status or '').upper()
    if st in ('FINISHED', 'SUCCESS', 'DONE'):
        normalized_status = 'SUCCESS'
    elif st in ('FAILED', 'FAIL', 'ERROR'):
        normalized_status = 'FAIL'
    elif st == 'STOPPED':
        normalized_status = 'STOPPED'
    elif st == 'RUNNING':
        normalized_status = 'RUNNING'
    else:
        normalized_status = 'SUCCESS'

    # If data_scraped is 0 or not given, calculate directly from output excel file
    if data_scraped <= 0 and output_file_path and os.path.exists(output_file_path):
        data_scraped = count_excel_data_rows(output_file_path)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE logTbl
                SET end_time = NOW(),
                    status = %s,
                    no_of_url_found = %s,
                    total_success_url = %s,
                    total_block_url = %s,
                    data_scraped = %s,
                    output_file_path = %s,
                    error_message = %s
                WHERE id = %s
                """,
                (normalized_status, no_of_url_found, total_success_url, total_block_url, data_scraped, output_file_path, error_message, log_id),
            )
    finally:
        conn.close()


def format_duration(start_time, end_time):
    """Formats human-readable duration (e.g. '2m 15s' or 'Running')."""
    if not start_time:
        return '—'
    final_time = end_time or datetime.utcnow()
    total_seconds = max(0, int((final_time - start_time).total_seconds()))

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def serialize_log(row):
    """Serializes a log row from logTbl into a structured API response."""
    start_time = row.get('start_time')
    end_time = row.get('end_time')
    raw_status = (row.get('status') or 'UNKNOWN').upper()
    error_msg = row.get('error_message') or ''

    # Normalize status to strictly RUNNING, SUCCESS, STOPPED, or FAIL per requirements
    if raw_status in ('FINISHED', 'SUCCESS', 'DONE'):
        status = 'SUCCESS'
    elif raw_status == 'RUNNING' and end_time is None:
        status = 'RUNNING'
    elif raw_status in ('STOPPED', 'STOP') or 'stopped by user' in error_msg.lower() or 'status: stopped' in error_msg.lower():
        status = 'STOPPED'
    else:
        status = 'FAIL' if raw_status not in ('RUNNING',) else 'SUCCESS'

    output_path = row.get('output_file_path')
    output_available = bool(output_path and os.path.exists(output_path))

    duration_str = format_duration(start_time, end_time) if (status != 'RUNNING' and end_time is not None) else 'Running…'
    duration_secs = int((end_time - start_time).total_seconds()) if (start_time and end_time) else None

    scraper_name = row.get('scraper') or row.get('site_name') or 'Scraper'

    return {
        'id': row['id'],
        'scraper': scraper_name,
        'siteName': row.get('site_name') or scraper_name,
        'pythonFilePath': row.get('python_file_path') or '',
        'fileId': row.get('file_id'),
        'fileLogo': row.get('file_logo'),
        'userId': row.get('user_id'),
        'userName': row.get('user_name') or 'Admin',
        'userEmail': row.get('user_email') or '',
        'userRole': row.get('user_role') or 'Admin',
        'userAvatar': row.get('user_avatar'),
        'status': status,
        'startTime': start_time.strftime('%d %b %Y %H:%M:%S') if start_time else None,
        'startTimeRaw': start_time.isoformat() + 'Z' if start_time else None,
        'endTime': end_time.strftime('%d %b %Y %H:%M:%S') if end_time else None,
        'endTimeRaw': end_time.isoformat() + 'Z' if end_time else None,
        'duration': duration_str,
        'durationSeconds': duration_secs,
        'noOfUrlFound': row.get('no_of_url_found', 0) or 0,
        'totalSuccessUrl': row.get('total_success_url', 0) or 0,
        'totalBlockUrl': row.get('total_block_url', 0) or 0,
        'dataScraped': row.get('data_scraped', 0) or 0,
        'outputAvailable': output_available,
        'errorMessage': row.get('error_message'),
    }


def reconcile_stale_logs():
    """Reconciles any logTbl rows marked as RUNNING when scraper_jobs or process is already finished."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Match finished scraper_jobs to update any lingering RUNNING logTbl rows
            cursor.execute("""
                UPDATE logTbl l
                JOIN scraper_jobs j ON l.file_id = j.file_id AND l.user_id = j.started_by_user_id
                SET l.status = CASE
                        WHEN j.status = 'SUCCESS' THEN 'SUCCESS'
                        WHEN j.status = 'STOPPED' THEN 'STOPPED'
                        ELSE 'FAIL'
                    END,
                    l.end_time = COALESCE(j.finished_at, NOW()),
                    l.error_message = COALESCE(j.error_message, l.error_message),
                    l.no_of_url_found = GREATEST(l.no_of_url_found, j.total_urls),
                    l.total_success_url = GREATEST(l.total_success_url, j.completed_urls),
                    l.total_block_url = GREATEST(l.total_block_url, j.blocked_urls),
                    l.data_scraped = GREATEST(l.data_scraped, j.written_to_xlsx)
                WHERE (l.status = 'RUNNING' OR l.end_time IS NULL)
                  AND j.status IN ('SUCCESS', 'FAILED', 'STOPPED')
                  AND j.finished_at IS NOT NULL
            """)

            # 2. For any other RUNNING log without an active lock in scraper_job_locks
            cursor.execute("""
                UPDATE logTbl l
                LEFT JOIN scraper_job_locks k ON l.file_id = k.file_id
                SET l.status = 'STOPPED',
                    l.end_time = NOW(),
                    l.error_message = 'Scraper execution finished.'
                WHERE (l.status = 'RUNNING' OR l.end_time IS NULL)
                  AND k.file_id IS NULL
            """)
    except Exception:
        pass
    finally:
        conn.close()


def list_logs(search=None, status=None, user_id=None, file_id=None, page=1, per_page=20):
    """Returns (rows, total_count) from logTbl for the SuperAdmin reports view or per-scraper drawer."""
    reconcile_stale_logs()
    page = max(1, page)
    per_page = max(1, min(per_page, 200))
    offset = (page - 1) * per_page

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            where_clauses = []
            params = []

            if status:
                st = status.upper()
                if st == 'SUCCESS':
                    where_clauses.append("l.status IN ('SUCCESS', 'FINISHED')")
                elif st in ('STOPPED', 'STOP'):
                    where_clauses.append("l.status IN ('STOPPED', 'STOP')")
                elif st in ('FAIL', 'FAILED'):
                    where_clauses.append("l.status IN ('FAIL', 'FAILED')")
                else:
                    where_clauses.append('l.status = %s')
                    params.append(st)

            if user_id:
                where_clauses.append('l.user_id = %s')
                params.append(user_id)

            if file_id:
                where_clauses.append('l.file_id = %s')
                params.append(file_id)

            if search:
                like = f'%{search}%'
                where_clauses.append(
                    '(l.scraper LIKE %s OR u.Name LIKE %s OR u.Email LIKE %s OR f.site_name LIKE %s)'
                )
                params.extend([like, like, like, like])

            where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            count_query = (
                f"SELECT COUNT(*) AS total FROM logTbl l "
                f"LEFT JOIN userTbl u ON l.user_id = u.userid "
                f"LEFT JOIN fileTbl f ON l.file_id = f.file_id "
                f"{where_str}"
            )
            cursor.execute(count_query, tuple(params))
            total = cursor.fetchone()['total']

            select_query = (
                f"SELECT {LOG_SELECT_FIELDS} FROM logTbl l "
                f"LEFT JOIN userTbl u ON l.user_id = u.userid "
                f"LEFT JOIN fileTbl f ON l.file_id = f.file_id "
                f"{where_str} "
                f"ORDER BY l.id DESC LIMIT %s OFFSET %s"
            )
            cursor.execute(select_query, tuple(params + [per_page, offset]))
            return cursor.fetchall(), total
    finally:
        conn.close()


def get_logs_summary_stats():
    """Calculates overall metrics from logTbl across all scraping sessions."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    COUNT(*) AS total_runs,
                    COALESCE(SUM(no_of_url_found), 0) AS total_urls_found,
                    COALESCE(SUM(total_success_url), 0) AS total_success_urls,
                    COALESCE(SUM(total_block_url), 0) AS total_block_urls,
                    COALESCE(SUM(data_scraped), 0) AS total_data_scraped,
                    SUM(CASE WHEN status = 'RUNNING' THEN 1 ELSE 0 END) AS active_runs,
                    SUM(CASE WHEN status IN ('SUCCESS', 'FINISHED') THEN 1 ELSE 0 END) AS finished_runs,
                    SUM(CASE WHEN status = 'STOPPED' THEN 1 ELSE 0 END) AS stopped_runs,
                    SUM(CASE WHEN status IN ('FAIL', 'FAILED') THEN 1 ELSE 0 END) AS failed_runs
                FROM logTbl
                """
            )
            row = cursor.fetchone()
            return {
                'totalRuns': int(row.get('total_runs') or 0),
                'totalUrlsFound': int(row.get('total_urls_found') or 0),
                'totalSuccessUrls': int(row.get('total_success_urls') or 0),
                'totalBlockUrls': int(row.get('total_block_urls') or 0),
                'totalDataScraped': int(row.get('total_data_scraped') or 0),
                'activeRuns': int(row.get('active_runs') or 0),
                'finishedRuns': int(row.get('finished_runs') or 0),
                'stoppedRuns': int(row.get('stopped_runs') or 0),
                'failedRuns': int(row.get('failed_runs') or 0),
            }
    finally:
        conn.close()
