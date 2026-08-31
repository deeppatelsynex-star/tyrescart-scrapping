import functools
import hashlib
import secrets
from datetime import datetime, timedelta

import bcrypt
from flask import jsonify, redirect, render_template, request, session

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


USER_COLUMNS = 'id AS userid, id, name AS Name, name, email AS Email, email, password, is_active AS Status, is_active, role AS Role, role, NULL AS avatar, created_at, updated_at, NULL AS deleted_at, 0 AS IsDeleted'


def get_user_by_email(email):
    if not email:
        return None
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f'SELECT {USER_COLUMNS} FROM `admin_users` WHERE LOWER(TRIM(email)) = %s LIMIT 1',
                (email.strip().lower(),),
            )
            return cursor.fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    if not user_id:
        return None
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                f'SELECT {USER_COLUMNS} FROM `admin_users` WHERE id = %s LIMIT 1',
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
    fmt = '%d-%m-%Y %I:%M:%S %p' if with_seconds else '%d-%m-%Y %I:%M %p'
    return ist_dt.strftime(fmt)


def serialize_user(user):
    if not user:
        return {}
    u_id = user.get('id') or user.get('userid')
    u_name = user.get('name') or user.get('Name') or ''
    u_email = user.get('email') or user.get('Email') or ''
    raw_role = user.get('role') or user.get('Role') or 'manager'
    
    role_display = 'SuperAdmin' if raw_role in ('super_admin', 'SuperAdmin') else ('Admin' if raw_role in ('manager', 'Admin') else 'User')
    is_active = bool(user.get('is_active', 1)) if 'is_active' in user else bit_to_bool(user.get('Status', 1))
    is_deleted = bool(user.get('is_deleted', 0)) if 'is_deleted' in user else bit_to_bool(user.get('IsDeleted', 0))
    
    created_at = user.get('created_at')
    updated_at = user.get('updated_at')
    deleted_at = user.get('deleted_at')

    return {
        'userId': u_id,
        'userid': u_id,
        'id': u_id,
        'name': u_name,
        'Name': u_name,
        'email': u_email,
        'Email': u_email,
        'role': role_display,
        'Role': role_display,
        'raw_role': raw_role,
        'status': is_active,
        'Status': 1 if is_active else 0,
        'isDeleted': is_deleted,
        'IsDeleted': 1 if is_deleted else 0,
        'avatar': user.get('avatar'),
        'updatedAt': to_ist_12h(updated_at),
        'createdAt': to_ist_12h(created_at),
        'createdAtRaw': created_at.isoformat() + 'Z' if created_at and hasattr(created_at, 'isoformat') else None,
        'deletedAt': to_ist_12h(deleted_at),
        'deletedAtRaw': deleted_at.isoformat() + 'Z' if deleted_at and hasattr(deleted_at, 'isoformat') else None,
    }


def list_users():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT {USER_COLUMNS} FROM `admin_users` ORDER BY id ASC')
            return cursor.fetchall()
    finally:
        conn.close()


def list_active_users():
    """Users for the main User Management table -- active admin users."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT {USER_COLUMNS} FROM `admin_users` WHERE is_active = 1 ORDER BY id ASC')
            return cursor.fetchall()
    finally:
        conn.close()


def list_deleted_users():
    """Users for the Trash table -- inactive/disabled admin users."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(f'SELECT {USER_COLUMNS} FROM `admin_users` WHERE is_active = 0 ORDER BY updated_at DESC')
            return cursor.fetchall()
    finally:
        conn.close()


def has_superadmin():
    """Whether a SuperAdmin already exists in admin_users."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM `admin_users` WHERE (`role` = 'super_admin' OR `role` = 'SuperAdmin') AND `is_active` = 1 LIMIT 1")
            return cursor.fetchone() is not None
    finally:
        conn.close()


def login_required_page(view):
    """Protects a page route: redirects to VisionAdmin login when unauthenticated."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get('admin_user_id') or session.get('user_id')
        email = session.get('email')
        if not user_id and not email:
            return redirect(f"/visionadmin/login?next={request.path}")

        u = None
        if user_id:
            u = get_user_by_id(user_id)
        if not u and email:
            u = get_user_by_email(email)
            if u:
                session['admin_user_id'] = u['id']
                session['user_id'] = u['id']
                session['name'] = u['name']
                session['email'] = u['email']
                session['role'] = u['role']
                session['is_visionadmin'] = True

        if not u:
            session.clear()
            return redirect(f"/visionadmin/login?next={request.path}")

        return view(*args, **kwargs)
    return wrapped


def login_required_api(view):
    """Protects a JSON/API route: returns 401 instead of redirecting."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get('admin_user_id') or session.get('user_id')
        email = session.get('email')
        if not user_id and not email:
            return jsonify({'error': 'Authentication required. Please sign in to VisionAdmin.'}), 401

        u = None
        if user_id:
            u = get_user_by_id(user_id)
        if not u and email:
            u = get_user_by_email(email)
            if u:
                session['admin_user_id'] = u['id']
                session['user_id'] = u['id']
                session['name'] = u['name']
                session['email'] = u['email']
                session['role'] = u['role']
                session['is_visionadmin'] = True

        if not u:
            return jsonify({'error': 'Authentication required. Please sign in to VisionAdmin.'}), 401

        return view(*args, **kwargs)
    return wrapped


def role_required_page(*roles):
    """Protects a page route: checks normalized user role."""
    def decorator(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            user_role = str(session.get('role') or '').strip().lower().replace('-', '_').replace(' ', '_')
            allowed_norm = {r.strip().lower().replace('-', '_').replace(' ', '_') for r in roles}
            if 'superadmin' in allowed_norm or 'super_admin' in allowed_norm:
                allowed_norm.update({'super_admin', 'superadmin'})
            if 'admin' in allowed_norm or 'manager' in allowed_norm:
                allowed_norm.update({'admin', 'manager'})
            if 'user' in allowed_norm or 'support' in allowed_norm:
                allowed_norm.update({'user', 'support'})

            if user_role not in allowed_norm and session.get('role') not in roles:
                return redirect('/visionadmin/pages')
            return view(*args, **kwargs)
        return wrapped
    return decorator


def role_required_api(*roles):
    """Protects a JSON/API route: returns 403 for unauthorized roles."""
    def decorator(view):
        @functools.wraps(view)
        def wrapped(*args, **kwargs):
            user_role = str(session.get('role') or '').strip().lower().replace('-', '_').replace(' ', '_')
            allowed_norm = {r.strip().lower().replace('-', '_').replace(' ', '_') for r in roles}
            if 'superadmin' in allowed_norm or 'super_admin' in allowed_norm:
                allowed_norm.update({'super_admin', 'superadmin'})
            if 'admin' in allowed_norm or 'manager' in allowed_norm:
                allowed_norm.update({'admin', 'manager'})
            if 'user' in allowed_norm or 'support' in allowed_norm:
                allowed_norm.update({'user', 'support'})

            if user_role not in allowed_norm and session.get('role') not in roles:
                return jsonify({'error': 'Forbidden. Administrator privileges required.'}), 403
            return view(*args, **kwargs)
        return wrapped
    return decorator


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
import time

_reset_tokens = {}
_reset_lock = threading.Lock()

LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60

FORGOT_PASSWORD_MAX_PER_EMAIL = 3
FORGOT_PASSWORD_COOLDOWN_SECONDS = 60
FORGOT_PASSWORD_MAX_PER_IP = 10
FORGOT_PASSWORD_WINDOW_SECONDS = 15 * 60

RESET_PASSWORD_MAX_PER_IP = 5
RESET_PASSWORD_WINDOW_SECONDS = 15 * 60

_rate_limit_lock = threading.Lock()
_login_failed_attempts = {}       # key: "email:<email>" or "ip:<ip>" -> [timestamp, timestamp, ...]
_forgot_pwd_requests = {}        # key: "email:<email>" or "ip:<ip>" -> [timestamp, timestamp, ...]
_reset_pwd_attempts = {}         # key: "ip:<ip>" -> [timestamp, timestamp, ...]


def get_client_ip():
    """Safely gets the real client IP address from proxy headers or remote_addr."""
    forwarded = request.headers.get('X-Forwarded-For')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.remote_addr or '127.0.0.1'


def check_login_rate_limit(email, ip=None):
    """
    Checks if login attempts are currently locked out for this email or IP.
    Returns (is_locked, seconds_remaining, message) or (False, 0, None).
    """
    now = time.time()
    ip = ip or get_client_ip()
    email_key = f"email:{(email or '').strip().lower()}"
    ip_key = f"ip:{ip}"

    with _rate_limit_lock:
        for key, max_attempts in [(email_key, LOGIN_MAX_ATTEMPTS), (ip_key, LOGIN_MAX_ATTEMPTS * 2)]:
            attempts = _login_failed_attempts.get(key, [])
            valid_attempts = [t for t in attempts if now - t < LOGIN_LOCKOUT_SECONDS]
            _login_failed_attempts[key] = valid_attempts

            if len(valid_attempts) >= max_attempts:
                oldest_in_window = valid_attempts[0]
                elapsed = now - oldest_in_window
                remaining = max(1, int(LOGIN_LOCKOUT_SECONDS - elapsed))
                minutes = max(1, round(remaining / 60))
                return True, remaining, f"Too many failed login attempts. Please try again in {minutes} minute(s)."

    return False, 0, None


def record_login_failure(email, ip=None):
    """Records a failed login attempt for the given email and IP."""
    now = time.time()
    ip = ip or get_client_ip()
    email_key = f"email:{(email or '').strip().lower()}"
    ip_key = f"ip:{ip}"

    with _rate_limit_lock:
        for key in [email_key, ip_key]:
            attempts = _login_failed_attempts.get(key, [])
            valid_attempts = [t for t in attempts if now - t < LOGIN_LOCKOUT_SECONDS]
            valid_attempts.append(now)
            _login_failed_attempts[key] = valid_attempts


def clear_login_failures(email, ip=None):
    """Clears failed login attempts after successful authentication."""
    ip = ip or get_client_ip()
    email_key = f"email:{(email or '').strip().lower()}"
    ip_key = f"ip:{ip}"

    with _rate_limit_lock:
        _login_failed_attempts.pop(email_key, None)
        _login_failed_attempts.pop(ip_key, None)


def check_forgot_password_rate_limit(email, ip=None):
    """
    Checks rate limits for forgot password requests:
    - Minimum 60s cooldown between requests for same email
    - Max 3 requests per 10 minutes per email
    - Max 10 requests per 15 minutes per IP
    """
    now = time.time()
    ip = ip or get_client_ip()
    email_key = f"email:{(email or '').strip().lower()}"
    ip_key = f"ip:{ip}"

    with _rate_limit_lock:
        # Check email cooldown & frequency
        email_attempts = _forgot_pwd_requests.get(email_key, [])
        valid_email_attempts = [t for t in email_attempts if now - t < 600]
        _forgot_pwd_requests[email_key] = valid_email_attempts

        if valid_email_attempts:
            last_attempt = valid_email_attempts[-1]
            if now - last_attempt < FORGOT_PASSWORD_COOLDOWN_SECONDS:
                remaining_cooldown = int(FORGOT_PASSWORD_COOLDOWN_SECONDS - (now - last_attempt))
                return True, remaining_cooldown, f"Please wait {remaining_cooldown} seconds before requesting another reset link."

            if len(valid_email_attempts) >= FORGOT_PASSWORD_MAX_PER_EMAIL:
                return True, 600, "Too many password reset requests for this email. Please try again in 10 minutes."

        # Check IP frequency
        ip_attempts = _forgot_pwd_requests.get(ip_key, [])
        valid_ip_attempts = [t for t in ip_attempts if now - t < FORGOT_PASSWORD_WINDOW_SECONDS]
        _forgot_pwd_requests[ip_key] = valid_ip_attempts

        if len(valid_ip_attempts) >= FORGOT_PASSWORD_MAX_PER_IP:
            return True, FORGOT_PASSWORD_WINDOW_SECONDS, "Too many requests from your network. Please try again later."

    return False, 0, None


def record_forgot_password_request(email, ip=None):
    """Records a password reset request timestamp for email and IP."""
    now = time.time()
    ip = ip or get_client_ip()
    email_key = f"email:{(email or '').strip().lower()}"
    ip_key = f"ip:{ip}"

    with _rate_limit_lock:
        for key, window in [(email_key, 600), (ip_key, FORGOT_PASSWORD_WINDOW_SECONDS)]:
            attempts = _forgot_pwd_requests.get(key, [])
            valid_attempts = [t for t in attempts if now - t < window]
            valid_attempts.append(now)
            _forgot_pwd_requests[key] = valid_attempts


def check_reset_password_rate_limit(ip=None):
    """Checks rate limits for password reset token submission."""
    now = time.time()
    ip = ip or get_client_ip()
    ip_key = f"ip:{ip}"

    with _rate_limit_lock:
        attempts = _reset_pwd_attempts.get(ip_key, [])
        valid_attempts = [t for t in attempts if now - t < RESET_PASSWORD_WINDOW_SECONDS]
        _reset_pwd_attempts[ip_key] = valid_attempts

        if len(valid_attempts) >= RESET_PASSWORD_MAX_PER_IP:
            return True, RESET_PASSWORD_WINDOW_SECONDS, "Too many password reset attempts. Please try again in 15 minutes."

    return False, 0, None


def record_reset_password_attempt(ip=None):
    """Records a password reset token submission attempt."""
    now = time.time()
    ip = ip or get_client_ip()
    ip_key = f"ip:{ip}"

    with _rate_limit_lock:
        attempts = _reset_pwd_attempts.get(ip_key, [])
        valid_attempts = [t for t in attempts if now - t < RESET_PASSWORD_WINDOW_SECONDS]
        valid_attempts.append(now)
        _reset_pwd_attempts[ip_key] = valid_attempts


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
                'UPDATE `admin_users` SET `password` = %s, `updated_at` = NOW() WHERE `id` = %s',
                (hashed, user_id),
            )
            conn.commit()
    finally:
        conn.close()