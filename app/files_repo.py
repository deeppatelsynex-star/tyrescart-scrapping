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

FILE_COLUMNS = 'file_id, logo, site_name, python_file_path, urls_json, working, create_date, update_date'

# scrapers/ lives at the project root, one level up from app/ (this file's
# own directory) -- same BASE_DIR anchoring app.py already uses.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
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
    form's dropdown -- registration is restricted to files that actually
    exist there, rather than letting a user type an arbitrary path.
    """
    if not os.path.isdir(SCRAPERS_DIR):
        return []
    names = [
        f for f in os.listdir(SCRAPERS_DIR)
        if f.endswith('.py') and not f.startswith('_') and f not in _NON_SCRAPER_FILES
    ]
    return sorted(names)


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
    # secure_filename() already strips any leading "_"/"." (its own defence
    # against hidden/dotfiles), so a sanitized name can never collide with or
    # overwrite a real underscore-prefixed helper file like
    # _cf_cookie_fetcher.py -- this only guards the non-underscore reserved names.
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


def serialize_file(row):
    urls = []
    if row.get('urls_json'):
        try:
            urls = json.loads(row['urls_json'])
        except (json.JSONDecodeError, TypeError):
            urls = []

    return {
        'fileId': row['file_id'],
        'logo': row.get('logo'),
        'siteName': row['site_name'],
        'pythonFilePath': row['python_file_path'],
        'working': bit_to_bool(row['working']),
        'urls': urls,
        'urlCount': len(urls),
        'createDate': row['create_date'].strftime('%d %b %Y %H:%M') if row.get('create_date') else None,
        'createDateRaw': row['create_date'].isoformat() + 'Z' if row.get('create_date') else None,
        'updateDate': row['update_date'].strftime('%d %b %Y %H:%M') if row.get('update_date') else None,
        'updateDateRaw': row['update_date'].isoformat() + 'Z' if row.get('update_date') else None,
    }


def list_files(search=None, page=1, per_page=20):
    """Returns (rows, total_count). `search` matches site_name or python_file_path."""
    page = max(1, page)
    per_page = max(1, min(per_page, 200))
    offset = (page - 1) * per_page

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            if search:
                like = f'%{search}%'
                cursor.execute(
                    'SELECT COUNT(*) AS total FROM fileTbl WHERE site_name LIKE %s OR python_file_path LIKE %s',
                    (like, like),
                )
                total = cursor.fetchone()['total']
                cursor.execute(
                    f'SELECT {FILE_COLUMNS} FROM fileTbl WHERE site_name LIKE %s OR python_file_path LIKE %s '
                    'ORDER BY file_id DESC LIMIT %s OFFSET %s',
                    (like, like, per_page, offset),
                )
            else:
                cursor.execute('SELECT COUNT(*) AS total FROM fileTbl')
                total = cursor.fetchone()['total']
                cursor.execute(
                    f'SELECT {FILE_COLUMNS} FROM fileTbl ORDER BY file_id DESC LIMIT %s OFFSET %s',
                    (per_page, offset),
                )
            return cursor.fetchall(), total
    finally:
        conn.close()


def get_file(file_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT {FILE_COLUMNS} FROM fileTbl WHERE file_id = %s', (file_id,))
            return cursor.fetchone()
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
            cursor.execute(f'SELECT {FILE_COLUMNS} FROM fileTbl WHERE python_file_path = %s', (python_file_path,))
            return cursor.fetchone()
    finally:
        conn.close()


def create_file(logo, site_name, python_file_path):
    validated_path = validate_python_file_path(python_file_path)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    'INSERT INTO fileTbl (logo, site_name, python_file_path) VALUES (%s, %s, %s)',
                    (logo or None, site_name, validated_path),
                )
            except pymysql.err.IntegrityError:
                raise FileValidationError('That Python file is already registered as a scraper.')
            return cursor.lastrowid
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
    finally:
        conn.close()


def delete_file(file_id):
    """Deletes the fileTbl record AND removes its .py file from scrapers/.

    Unlike userTbl's soft-delete/Trash, this is genuinely irreversible -- no
    undo, no recovery. The caller (app.py's route) is responsible for
    confirming with the user and for checking the scraper isn't currently
    running before calling this.
    """
    record = get_file(file_id)

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
            # The DB registration is already gone -- a missing/unreadable
            # file at this point shouldn't be reported as a failed delete.
            pass


def set_working(file_id, working):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE fileTbl SET working = %s WHERE file_id = %s', (1 if working else 0, file_id))
    finally:
        conn.close()


def set_urls(file_id, urls):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE fileTbl SET urls_json = %s WHERE file_id = %s',
                (json.dumps(urls), file_id),
            )
    finally:
        conn.close()
