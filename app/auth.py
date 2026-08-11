import functools
import hashlib
import secrets
from datetime import datetime, timedelta

import bcrypt
from flask import jsonify, redirect, request, session

from db import get_connection

RESET_TOKEN_TTL_MINUTES = 30


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


USER_COLUMNS = 'userid, Name, Email, password, Status, IsDeleted, Role, avatar, updated_at'


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


def serialize_user(user):
    return {
        'userId': user['userid'],
        'name': user['Name'],
        'email': user['Email'],
        'role': user['Role'],
        'status': bit_to_bool(user['Status']),
        'avatar': user.get('avatar'),
        'updatedAt': user['updated_at'].strftime('%d %b %Y %H:%M') if user.get('updated_at') else None,
    }


def _hash_reset_token(raw_token):
    return hashlib.sha256(raw_token.encode('utf-8')).hexdigest()


def create_password_reset_token(user_id):
    """Issues a new single-use reset token, invalidating any previous ones for this user.

    Only the SHA-256 hash is stored, so a leaked database dump can't be used to
    reset accounts -- the raw token (put in the emailed link) never touches the DB.
    """
    raw_token = secrets.token_urlsafe(32)
    token_hash = _hash_reset_token(raw_token)
    expires_at = datetime.utcnow() + timedelta(minutes=RESET_TOKEN_TTL_MINUTES)

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('DELETE FROM password_reset_tbl WHERE userid = %s', (user_id,))
            cursor.execute(
                'INSERT INTO password_reset_tbl (userid, token_hash, expires_at) VALUES (%s, %s, %s)',
                (user_id, token_hash, expires_at),
            )
    finally:
        conn.close()
    return raw_token


def get_user_id_for_reset_token(raw_token):
    """Returns the userid for a valid, unused, unexpired token, else None.

    UTC_TIMESTAMP() is used (rather than NOW()) so the expiry check is correct
    regardless of the MySQL session's configured timezone.
    """
    if not raw_token:
        return None

    token_hash = _hash_reset_token(raw_token)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'SELECT userid FROM password_reset_tbl '
                'WHERE token_hash = %s AND used = 0 AND expires_at > UTC_TIMESTAMP()',
                (token_hash,),
            )
            row = cursor.fetchone()
            return row['userid'] if row else None
    finally:
        conn.close()


def consume_reset_token(raw_token):
    token_hash = _hash_reset_token(raw_token)
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE password_reset_tbl SET used = 1 WHERE token_hash = %s', (token_hash,))
    finally:
        conn.close()


def login_required_page(view):
    """Protects a page route: redirects unauthenticated visitors to /login."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
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


def require_csrf(view):
    """Rejects state-changing requests whose X-CSRF-Token doesn't match the session's."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        token = request.headers.get('X-CSRF-Token')
        if not token or token != session.get('csrf_token'):
            return jsonify({'error': 'Invalid or missing CSRF token.'}), 403
        return view(*args, **kwargs)
    return wrapped
