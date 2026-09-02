"""DB access + validation for fileTbl (the /files scraper-management page).

Follows the same conventions as auth.py's userTbl helpers: one pymysql
connection per call via db.get_connection(), a *_COLUMNS constant, and a
serialize_*() function that returns both a human-formatted date and a raw ISO
one (so the frontend can render in the viewer's local timezone, same reason
serialize_user() does it for created_at/deleted_at).
"""

import json
import os

import pymysql
from werkzeug.utils import secure_filename

from db import get_connection
from cache_manager import cache, invalidate_scraper_cache

FILE_COLUMNS = 'file_id, logo, site_name, python_file_path, urls_json, working, is_deleted, deleted_at, created_by, create_date, update_date'
FILE_SELECT_FIELDS = 'f.file_id, f.logo, f.site_name, f.python_file_path, f.urls_json, f.working, f.is_deleted, f.deleted_at, f.created_by, f.create_date, f.update_date, u.name AS created_by_name, u.email AS created_by_email, (SELECT MAX(start_time) FROM logTbl l WHERE l.file_id = f.file_id) AS last_used_at'

# scrapers/ lives at the project root. This file is app/scraperapp/files_repo.py,
# so the project root is two directories up from this file's own directory
# (scraperapp -> app -> root) -- same BASE_DIR anchoring app.py already uses.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SCRAPERS_DIR = os.path.join(BASE_DIR, 'scrapers')

# Helper/config modules in scrapers/ that aren't standalone runnable spiders,
# so they're excluded from both the registerable-script dropdown and the
# path-validation allow list.
_NON_SCRAPER_FILES = {'scraper_config.py', 'scraper_input.py', '_cf_cookie_fetcher.py'}


class FileValidationError(Exception):
    """Raised with a user-facing message for a bad create/update/start request."""


def bit_to_bool(value):
    if isinstance(value, bytes):
        return value != b'\x00'
    return bool(value)


def list_available_scripts():
    """Every standalone scraper .py file in scrapers/, for the create/edit
    form's dropdown (cached with 30s TTL).
    """
    cached = cache.get('files:scripts')
    if cached is not None:
        return cached

    if not os.path.isdir(SCRAPERS_DIR):
        return []
    names = [
        f for f in os.listdir(SCRAPERS_DIR)
        if f.endswith('.py') and not f.startswith('_') and f not in _NON_SCRAPER_FILES
    ]
    result = sorted(names)
    cache.set('files:scripts', result, ttl=30)
    return result


def validate_python_file_path(relative_path):
    """Validates a user-supplied python_file_path is a real, safe scraper
    script before it's ever stored or executed.

    Raises FileValidationError (user-facing message, no absolute paths in it)
    if the path is empty, not a .py file, escapes scrapers/ (e.g. via "..",
    an absolute path, or a symlink resolving outside it), or doesn't exist.
    Returns the cleaned relative path (e.g. "pitstoparabiabycsv.py") to store.
    """
    relative_path = (relative_path or '').strip()
    if not relative_path:
        raise FileValidationError('Python file path is required.')
    if not relative_path.lower().endswith('.py'):
        raise FileValidationError('Only .py files can be registered.')
    if os.path.isabs(relative_path) or '..' in relative_path.replace('\\', '/').split('/'):
        raise FileValidationError('Invalid file path.')

    candidate = os.path.realpath(os.path.join(SCRAPERS_DIR, relative_path))
    scrapers_real = os.path.realpath(SCRAPERS_DIR)
    if os.path.commonpath([candidate, scrapers_real]) != scrapers_real:
        raise FileValidationError('Invalid file path.')
    if os.path.basename(candidate) in _NON_SCRAPER_FILES:
        raise FileValidationError('That file is not a registerable scraper.')
    if not os.path.isfile(candidate):
        raise FileValidationError('That Python file does not exist in the scrapers folder.')

    return relative_path.replace('\\', '/')


MAX_SCRIPT_UPLOAD_BYTES = 2 * 1024 * 1024  # 2 MB -- scraper scripts are plain text, generous enough


def save_uploaded_script(upload):
    """Saves an uploaded .py file into scrapers/ and returns its filename,
    ready to pass straight into create_file()/update_file() as
    python_file_path. Only ever called from a route already gated to
    SuperAdmin/Admin -- uploading code that will later be executed on the
    server is a materially bigger privilege than picking from the existing,
    already-vetted dropdown, so it isn't offered to every logged-in user.

    Raises FileValidationError for anything unsafe or invalid: not a .py
    file, empty, too large, or not valid Python syntax. Re-uploading a name
    that already exists in scrapers/ overwrites it in place (the workflow
    this exists for -- updating a registered scraper's code) -- the caller
    is responsible for checking the target isn't currently running first
    (see api_upload_script in app.py; kept out of this function to avoid a
    files_repo <-> file_scraper_runner import cycle).
    """
    filename = secure_filename(upload.filename or '')
    if not filename:
        raise FileValidationError('Invalid file name.')
    if not filename.lower().endswith('.py'):
        raise FileValidationError('Only .py files can be uploaded.')
    if filename in _NON_SCRAPER_FILES:
        raise FileValidationError('That file name is reserved.')

    raw_bytes = upload.read()
    if not raw_bytes:
        raise FileValidationError('The uploaded file is empty.')
    if len(raw_bytes) > MAX_SCRIPT_UPLOAD_BYTES:
        raise FileValidationError('The uploaded file is too large (max 2 MB).')

    try:
        source_text = raw_bytes.decode('utf-8')
    except UnicodeDecodeError:
        raise FileValidationError('The uploaded file must be valid UTF-8 Python source.')

    try:
        compile(source_text, filename, 'exec')
    except SyntaxError as exc:
        raise FileValidationError(f'That file is not valid Python: {exc}')

    destination = os.path.join(SCRAPERS_DIR, filename)
    os.makedirs(SCRAPERS_DIR, exist_ok=True)
    with open(destination, 'wb') as f:
        f.write(raw_bytes)

    return filename


def resolve_script_path(relative_path):
    """Re-validates and returns the absolute path to run -- called again at
    Start Script time (not just at create/edit time) in case the file was
    moved/deleted since it was registered.
    """
    validated = validate_python_file_path(relative_path)
    return os.path.join(SCRAPERS_DIR, validated)


from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))


def to_ist_12h(dt, with_seconds=False):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ist_dt = dt.astimezone(IST)
    fmt = '%d-%m-%Y %I:%M:%S %p' if with_seconds else '%d-%m-%Y %I:%M %p'
    return ist_dt.strftime(fmt)


def serialize_file(row):
    urls = []
    if row.get('urls_json'):
        try:
            urls = json.loads(row['urls_json'])
        except (json.JSONDecodeError, TypeError):
            urls = []

    is_deleted = bit_to_bool(row.get('is_deleted'))
    created_by_name = (row.get('created_by_name') or '').strip() or 'Admin'
    return {
        'fileId': row['file_id'],
        'logo': row.get('logo'),
        'siteName': row['site_name'],
        'pythonFilePath': row['python_file_path'],
        'working': bit_to_bool(row['working']),
        'isDeleted': is_deleted,
        'isEnabled': not is_deleted,
        'deletedDate': to_ist_12h(row.get('deleted_at')),
        'deletedDateRaw': row['deleted_at'].isoformat() + 'Z' if row.get('deleted_at') else None,
        'createdBy': row.get('created_by'),
        'createdByName': created_by_name,
        'createdByEmail': row.get('created_by_email'),
        'urls': urls,
        'urlCount': len(urls),
        'createDate': to_ist_12h(row.get('create_date')),
        'createDateRaw': row['create_date'].isoformat() + 'Z' if row.get('create_date') else None,
        'updateDate': to_ist_12h(row.get('update_date')),
        'updateDateRaw': row['update_date'].isoformat() + 'Z' if row.get('update_date') else None,
        'lastUsed': to_ist_12h(row.get('last_used_at')) if row.get('last_used_at') else None,
        'lastUsedRaw': row['last_used_at'].isoformat() + 'Z' if row.get('last_used_at') else None,
    }


def list_files(search=None, is_deleted=None, page=1, per_page=20):
    """Returns (rows, total_count). If `is_deleted` is None, returns all scrapers (cached with 30s TTL)."""
    page = max(1, page)
    per_page = max(1, min(per_page, 200))
    offset = (page - 1) * per_page

    cache_key = f"files:p{page}:pp{per_page}:d{is_deleted}:q{search}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            where_clauses = []
            params = []

            if is_deleted is not None:
                where_clauses.append('f.is_deleted = %s')
                params.append(1 if is_deleted else 0)

            if search:
                like = f'%{search}%'
                where_clauses.append('(f.site_name LIKE %s OR f.python_file_path LIKE %s OR u.name LIKE %s)')
                params.extend([like, like, like])

            where_str = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

            count_query = f"SELECT COUNT(*) AS total FROM fileTbl f LEFT JOIN admin_users u ON f.created_by = u.id {where_str}"
            cursor.execute(count_query, tuple(params))
            total = cursor.fetchone()['total']

            select_query = (
                f"SELECT {FILE_SELECT_FIELDS} FROM fileTbl f "
                f"LEFT JOIN admin_users u ON f.created_by = u.id "
                f"{where_str} "
                f"ORDER BY f.file_id DESC LIMIT %s OFFSET %s"
            )
            cursor.execute(select_query, tuple(params + [per_page, offset]))
            result = (cursor.fetchall(), total)
            cache.set(cache_key, result, ttl=30)
            return result
    finally:
        conn.close()


def get_file(file_id):
    """Fetches a single file record by file_id (cached with 60s TTL)."""
    cache_key = f"file:{file_id}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f'SELECT {FILE_SELECT_FIELDS} FROM fileTbl f '
                'LEFT JOIN admin_users u ON f.created_by = u.id '
                'WHERE f.file_id = %s',
                (file_id,),
            )
            row = cursor.fetchone()
            if row:
                cache.set(cache_key, row, ttl=60)
            return row
    finally:
        conn.close()


def get_file_by_path(python_file_path):
    """Looks up the (at most one, python_file_path is UNIQUE) scraper record
    pointing at this filename -- used before an upload overwrites an existing
    file, to check whether that scraper is currently running.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f'SELECT {FILE_SELECT_FIELDS} FROM fileTbl f '
                'LEFT JOIN admin_users u ON f.created_by = u.id '
                'WHERE f.python_file_path = %s',
                (python_file_path,),
            )
            return cursor.fetchone()
    finally:
        conn.close()


def create_file(logo, site_name, python_file_path, created_by=None):
    validated_path = validate_python_file_path(python_file_path)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    'INSERT INTO fileTbl (logo, site_name, python_file_path, created_by) VALUES (%s, %s, %s, %s)',
                    (logo or None, site_name, validated_path, created_by or None),
                )
            except pymysql.err.IntegrityError:
                raise FileValidationError('That Python file is already registered as a scraper.')
            new_id = cursor.lastrowid
            invalidate_scraper_cache()
            return new_id
    finally:
        conn.close()


def update_file(file_id, logo, site_name, python_file_path):
    validated_path = validate_python_file_path(python_file_path)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    'UPDATE fileTbl SET logo = %s, site_name = %s, python_file_path = %s WHERE file_id = %s',
                    (logo or None, site_name, validated_path, file_id),
                )
            except pymysql.err.IntegrityError:
                raise FileValidationError('That Python file is already registered as a scraper.')
            invalidate_scraper_cache(file_id)
    finally:
        conn.close()


def soft_delete_file(file_id):
    """Soft-deletes a scraper (moves it to Trash/Disabled) by setting
    is_deleted = 1 and deleted_at = CURRENT_TIMESTAMP. The scraper's .py
    file is NOT deleted from disk so it can be restored anytime.
    """
    invalidate_scraper_cache(file_id)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE fileTbl SET is_deleted = 1, deleted_at = CURRENT_TIMESTAMP WHERE file_id = %s',
                (file_id,),
            )
    finally:
        conn.close()


def restore_file(file_id):
    """Restores a trashed/disabled scraper back to active status."""
    invalidate_scraper_cache(file_id)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE fileTbl SET is_deleted = 0, deleted_at = NULL WHERE file_id = %s',
                (file_id,),
            )
    finally:
        conn.close()


def set_file_enabled(file_id, enabled):
    """Toggles a scraper enabled (0) or disabled/trashed (1)."""
    if enabled:
        restore_file(file_id)
    else:
        soft_delete_file(file_id)


def delete_file(file_id):
    """Permanently deletes the fileTbl record AND removes its .py file from scrapers/."""
    record = get_file(file_id)
    invalidate_scraper_cache(file_id)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM fileTbl WHERE file_id = %s', (file_id,))
    finally:
        conn.close()

    if record and record.get('python_file_path'):
        try:
            script_path = resolve_script_path(record['python_file_path'])
            os.remove(script_path)
        except (FileValidationError, OSError):
            pass


def set_working(file_id, working):
    invalidate_scraper_cache(file_id)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE fileTbl SET working = %s WHERE file_id = %s', (1 if working else 0, file_id))
    finally:
        conn.close()


def set_urls(file_id, urls):
    invalidate_scraper_cache(file_id)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE fileTbl SET urls_json = %s WHERE file_id = %s',
                (json.dumps(urls), file_id),
            )
    finally:
        conn.close()
