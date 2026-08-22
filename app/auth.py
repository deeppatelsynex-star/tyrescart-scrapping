import functools
import hashlib
import secrets
from datetime import datetime, timedelta

import bcrypt
from flask import jsonify, redirect, request, session

from db import get_connection

RESET_TOKEN_TTL_MINUTES = 30
VALID_ROLES = ('SuperAdmin', 'Admin', 'User')


def hash_password(plain_password):
    return bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password, password_hash):
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), password_hash.encode('utf-8'))
    except ValueError:
        return False


def bit_to_bool(value):
    if isinstance(value, bytes):
        return value != b'\x00'
    return bool(value)


USER_COLUMNS = 'userid, Name, Email, password, Status, IsDeleted, Role, avatar, updated_at, created_at, deleted_at'


def get_user_by_email(email):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f'SELECT {USER_COLUMNS} FROM userTbl WHERE Email = %s',
                (email,),
            )
            return cursor.fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f'SELECT {USER_COLUMNS} FROM userTbl WHERE userid = %s',
                (user_id,),
            )
            return cursor.fetchone()
    finally:
        conn.close()


from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


def to_ist_12h(dt, with_seconds=False):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    ist_dt = dt.astimezone(IST)
    fmt = '%d %b %Y %I:%M:%S %p' if with_seconds else '%d %b %Y %I:%M %p'
    return ist_dt.strftime(fmt)


def serialize_user(user):
    return {
        'userId': user['userid'],
        'name': user['Name'],
        'email': user['Email'],
        'role': user['Role'],
        'status': bit_to_bool(user['Status']),
        'isDeleted': bit_to_bool(user['IsDeleted']),
        'avatar': user.get('avatar'),
        'updatedAt': to_ist_12h(user.get('updated_at')),
        'createdAt': to_ist_12h(user.get('created_at')),
        'createdAtRaw': user['created_at'].isoformat() + 'Z' if user.get('created_at') else None,
        'deletedAt': to_ist_12h(user.get('deleted_at')),
        'deletedAtRaw': user['deleted_at'].isoformat() + 'Z' if user.get('deleted_at') else None,
    }


def list_users():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT {USER_COLUMNS} FROM userTbl ORDER BY userid')
            return cursor.fetchall()
    finally:
        conn.close()


def list_active_users():
    """Users for the main User Management table -- never includes soft-deleted rows."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT {USER_COLUMNS} FROM userTbl WHERE IsDeleted = 0 ORDER BY userid')
            return cursor.fetchall()
    finally:
        conn.close()


def list_deleted_users():
    """Users for the Trash table -- only soft-deleted rows."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT {USER_COLUMNS} FROM userTbl WHERE IsDeleted = 1 ORDER BY deleted_at DESC')
            return cursor.fetchall()
    finally:
        conn.close()


def has_superadmin():
    """Whether a SuperAdmin already exists -- caps the system to exactly one."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM userTbl WHERE Role = 'SuperAdmin' AND IsDeleted = 0 LIMIT 1")
            return cursor.fetchone() is not None
    finally:
        conn.close()


def login_required_page(view):
    """Protects a page route: redirects unauthenticated visitors to /tcsadmin/login."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/tcsadmin/login')
        return view(*args, **kwargs)
    return wrapped


def login_required_api(view):
    """Protects a JSON/API route: returns 401 instead of redirecting."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required.'}), 401
        return view(*args, **kwargs)
    return wrapped


def role_required_page(*roles):
    """Protects a page route: sends users without an allowed role back to the dashboard.

    Must sit inside @login_required_page (closer to the view function) so
    session['role'] is already known to exist by the time this runs.
    """
    def decorator(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            if session.get('role') not in roles:
                return redirect('/tcsadmin')
            return view(*args, **kwargs)
        return wrapped
    return decorator


def role_required_api(*roles):
    """Protects a JSON/API route: returns 403 for users without an allowed role."""
    def decorator(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            if session.get('role') not in roles:
                return jsonify({'error': 'You do not have permission to do that.'}), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


def require_csrf(view):
    """Rejects state-changing requests whose X-CSRF-Token doesn't match the session's."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        token = request.headers.get('X-CSRF-Token')
        if not token or token != session.get('csrf_token'):
            return jsonify({'error': 'Invalid or missing CSRF token.'}), 403
        return view(*args, **kwargs)
    return wrapped


import threading

_reset_tokens = {}
_reset_lock = threading.Lock()


def create_password_reset_token(user_id):
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
    expires_at = datetime.now() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)
    with _reset_lock:
        now = datetime.now()
        expired = [k for k, v in _reset_tokens.items() if v['expires_at'] < now]
        for k in expired:
            _reset_tokens.pop(k, None)
        _reset_tokens[token_hash] = {
            'user_id': user_id,
            'expires_at': expires_at,
        }
    return token


def verify_and_consume_reset_token(token):
    if not token or not isinstance(token, str):
        return None
    token_hash = hashlib.sha256(token.strip().encode('utf-8')).hexdigest()
    with _reset_lock:
        info = _reset_tokens.get(token_hash)
        if not info:
            return None
        if info['expires_at'] < datetime.now():
            _reset_tokens.pop(token_hash, None)
            return None
        _reset_tokens.pop(token_hash, None)
        return info['user_id']


def update_user_password(user_id, new_password):
    hashed = hash_password(new_password)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE userTbl SET password = %s, updated_at = CURRENT_TIMESTAMP WHERE userid = %s',
                (hashed, user_id),
            )
    finally:
        conn.close()

#updated