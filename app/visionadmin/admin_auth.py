"""
app/visionadmin/admin_auth.py - Authentication & Repository Layer for admin_users Table.

Manages administrator login authentication, rate limiting, and password reset tokens
specifically backed by the `admin_users` database table and `password_reset_tokens`.
"""

import hashlib
import os
import re
import secrets
import sys
import time
import bcrypt

# Ensure parent app folder is importable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from db import get_connection

EMAIL_REGEX = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

# Valid roles in admin_users table
VALID_ADMIN_ROLES = ('super_admin', 'manager', 'support')

# Rate limiting configurations
LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 900  # 15 minutes
FORGOT_PASSWORD_COOLDOWN_SECONDS = 60  # 1 minute
RESET_PASSWORD_MAX_ATTEMPTS = 10
RESET_PASSWORD_WINDOW_SECONDS = 300

# In-memory tracking structures
_admin_login_attempts = {}       # email -> [timestamps]
_admin_forgot_requests = {}      # email -> timestamp
_admin_reset_attempts = []       # [timestamps]


# ============================================================================
# 1. RATE LIMITING HELPERS
# ============================================================================

def check_admin_login_rate_limit(email: str):
    """Returns (is_locked: bool, seconds_remaining: int, message: str)."""
    now = time.time()
    email_key = email.strip().lower()
    timestamps = [t for t in _admin_login_attempts.get(email_key, []) if now - t < LOGIN_LOCKOUT_SECONDS]
    _admin_login_attempts[email_key] = timestamps

    if len(timestamps) >= LOGIN_MAX_ATTEMPTS:
        oldest_relevant = min(timestamps)
        seconds_remaining = int(LOGIN_LOCKOUT_SECONDS - (now - oldest_relevant))
        if seconds_remaining > 0:
            minutes = max(1, (seconds_remaining + 59) // 60)
            return True, seconds_remaining, f"Too many failed login attempts. Please try again in {minutes} minute(s)."
    return False, 0, ""


def record_admin_login_failure(email: str):
    """Records a failed login attempt for the given email."""
    email_key = email.strip().lower()
    if email_key not in _admin_login_attempts:
        _admin_login_attempts[email_key] = []
    _admin_login_attempts[email_key].append(time.time())


def clear_admin_login_failures(email: str):
    """Clears failed login attempt history on successful login."""
    email_key = email.strip().lower()
    _admin_login_attempts.pop(email_key, None)


def check_admin_forgot_password_rate_limit(email: str):
    """Returns (is_limited: bool, seconds_remaining: int, message: str)."""
    now = time.time()
    email_key = email.strip().lower()
    last_request = _admin_forgot_requests.get(email_key)
    if last_request and (now - last_request) < FORGOT_PASSWORD_COOLDOWN_SECONDS:
        seconds_remaining = int(FORGOT_PASSWORD_COOLDOWN_SECONDS - (now - last_request))
        return True, seconds_remaining, f"Please wait {seconds_remaining} seconds before requesting another reset link."
    return False, 0, ""


def record_admin_forgot_password_request(email: str):
    """Records a forgot password request timestamp."""
    _admin_forgot_requests[email.strip().lower()] = time.time()


def check_admin_reset_password_rate_limit():
    """Global burst limiting for password reset attempts."""
    now = time.time()
    global _admin_reset_attempts
    _admin_reset_attempts = [t for t in _admin_reset_attempts if now - t < RESET_PASSWORD_WINDOW_SECONDS]
    if len(_admin_reset_attempts) >= RESET_PASSWORD_MAX_ATTEMPTS:
        return True, RESET_PASSWORD_WINDOW_SECONDS, "Too many password reset requests. Please try again in a few minutes."
    return False, 0, ""


def record_admin_reset_password_attempt():
    """Records a reset password attempt."""
    _admin_reset_attempts.append(time.time())


# ============================================================================
# 2. PASSWORD HASHING & VERIFICATION
# ============================================================================

def hash_admin_password(raw_password: str) -> str:
    """Hashes password with bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(raw_password.encode('utf-8'), salt).decode('utf-8')


def verify_admin_password(raw_password: str, hashed_password: str) -> bool:
    """Verifies plain password against bcrypt hash (compatible with $2y$, $2b$, $2a$)."""
    if not raw_password or not hashed_password:
        return False
    try:
        hash_bytes = hashed_password.encode('utf-8')
        raw_bytes = raw_password.encode('utf-8')
        try:
            return bcrypt.checkpw(raw_bytes, hash_bytes)
        except ValueError:
            # If $2y$ prefix is rejected by certain bcrypt builds, replace with $2b$
            if hashed_password.startswith('$2y$'):
                fixed_hash = hashed_password.replace('$2y$', '$2b$', 1).encode('utf-8')
                return bcrypt.checkpw(raw_bytes, fixed_hash)
            return False
    except Exception:
        return False


# ============================================================================
# 3. DATABASE CRUD ON admin_users TABLE
# ============================================================================

def get_admin_user_by_email(email: str, include_deleted: bool = False):
    """Fetches an admin_user record by email."""
    if not email:
        return None
    email_clean = email.strip().lower()
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if include_deleted:
                cur.execute("""
                    SELECT id, name, email, password, role, is_active, is_deleted, deleted_at, last_login_at, remember_token, created_at, updated_at
                    FROM `admin_users`
                    WHERE LOWER(TRIM(email)) = %s
                    LIMIT 1
                """, (email_clean,))
            else:
                cur.execute("""
                    SELECT id, name, email, password, role, is_active, is_deleted, deleted_at, last_login_at, remember_token, created_at, updated_at
                    FROM `admin_users`
                    WHERE LOWER(TRIM(email)) = %s AND (is_deleted = 0 OR is_deleted IS NULL)
                    LIMIT 1
                """, (email_clean,))
            return cur.fetchone()
    finally:
        conn.close()


def get_admin_user_by_id(admin_id: int, include_deleted: bool = True):
    """Fetches an admin_user record by ID."""
    if not admin_id:
        return None
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if include_deleted:
                cur.execute("""
                    SELECT id, name, email, password, role, is_active, is_deleted, deleted_at, last_login_at, remember_token, created_at, updated_at
                    FROM `admin_users`
                    WHERE id = %s
                    LIMIT 1
                """, (admin_id,))
            else:
                cur.execute("""
                    SELECT id, name, email, password, role, is_active, is_deleted, deleted_at, last_login_at, remember_token, created_at, updated_at
                    FROM `admin_users`
                    WHERE id = %s AND (is_deleted = 0 OR is_deleted IS NULL)
                    LIMIT 1
                """, (admin_id,))
            return cur.fetchone()
    finally:
        conn.close()


def create_admin_user(name: str, email: str, password: str, role: str = 'super_admin', is_active: int = 1):
    """Creates a new record in admin_users table."""
    conn = get_connection()
    try:
        hashed = hash_admin_password(password)
        email_clean = email.strip().lower()
        role_clean = role if role in VALID_ADMIN_ROLES else 'manager'
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO `admin_users` (`name`, `email`, `password`, `role`, `is_active`, `created_at`, `updated_at`)
                VALUES (%s, %s, %s, %s, %s, NOW(), NOW())
            """, (name.strip(), email_clean, hashed, role_clean, is_active))
            new_id = cur.lastrowid
        conn.commit()
        return new_id
    finally:
        conn.close()


def serialize_admin_user(u: dict) -> dict:
    """Serializes an admin_users row with formatted and raw dates."""
    if not u:
        return {}
    created_raw = u['created_at'].isoformat() + 'Z' if u.get('created_at') and hasattr(u['created_at'], 'isoformat') else str(u.get('created_at') or '')
    updated_raw = u['updated_at'].isoformat() + 'Z' if u.get('updated_at') and hasattr(u['updated_at'], 'isoformat') else str(u.get('updated_at') or '')
    last_login_raw = u['last_login_at'].isoformat() + 'Z' if u.get('last_login_at') and hasattr(u['last_login_at'], 'isoformat') else None
    deleted_raw = u['deleted_at'].isoformat() + 'Z' if u.get('deleted_at') and hasattr(u['deleted_at'], 'isoformat') else None
    
    # Format human-readable date
    def fmt_date(dt):
        if not dt:
            return 'Never'
        try:
            return dt.strftime('%d %b %Y, %I:%M %p')
        except Exception:
            return str(dt)

    return {
        'id': u['id'],
        'name': u.get('name', ''),
        'email': u.get('email', ''),
        'role': u.get('role', 'manager'),
        'role_display': (u.get('role', 'manager') or '').replace('_', ' ').title(),
        'is_active': bool(u.get('is_active', 1)),
        'is_deleted': bool(u.get('is_deleted', 0)),
        'deleted_at': fmt_date(u.get('deleted_at')),
        'deleted_raw': deleted_raw,
        'last_login_at': fmt_date(u.get('last_login_at')),
        'last_login_raw': last_login_raw,
        'created_at': fmt_date(u.get('created_at')),
        'created_raw': created_raw,
        'updated_at': fmt_date(u.get('updated_at')),
        'updated_raw': updated_raw,
    }


def list_admin_users(is_trash: bool = False):
    """Fetches active or deleted administrator accounts from admin_users table."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            if is_trash:
                cur.execute("""
                    SELECT id, name, email, password, role, is_active, is_deleted, deleted_at, last_login_at, remember_token, created_at, updated_at
                    FROM `admin_users`
                    WHERE is_deleted = 1
                    ORDER BY deleted_at DESC, id DESC
                """)
            else:
                cur.execute("""
                    SELECT id, name, email, password, role, is_active, is_deleted, deleted_at, last_login_at, remember_token, created_at, updated_at
                    FROM `admin_users`
                    WHERE is_deleted = 0 OR is_deleted IS NULL
                    ORDER BY id ASC
                """)
            rows = cur.fetchall()
            return [serialize_admin_user(r) for r in rows]
    finally:
        conn.close()


def get_admin_user_metrics() -> dict:
    """Returns metric counters including active, super admins, managers, and trash."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    COUNT(CASE WHEN is_deleted = 0 OR is_deleted IS NULL THEN 1 END) AS total,
                    COUNT(CASE WHEN (is_deleted = 0 OR is_deleted IS NULL) AND role = 'super_admin' THEN 1 END) AS super,
                    COUNT(CASE WHEN (is_deleted = 0 OR is_deleted IS NULL) AND role IN ('manager', 'support') THEN 1 END) AS managers,
                    COUNT(CASE WHEN (is_deleted = 0 OR is_deleted IS NULL) AND is_active = 1 THEN 1 END) AS active,
                    COUNT(CASE WHEN is_deleted = 1 THEN 1 END) AS trash
                FROM `admin_users`
            """)
            res = cur.fetchone()
            return {
                'total': res['total'] if res else 0,
                'super': res['super'] if res else 0,
                'managers': res['managers'] if res else 0,
                'active': res['active'] if res else 0,
                'trash': res['trash'] if res else 0,
            }
    finally:
        conn.close()


def count_super_admins() -> int:
    """Returns number of active non-deleted super_admin users."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS c FROM `admin_users` WHERE `role` = 'super_admin' AND `is_active` = 1 AND (is_deleted = 0 OR is_deleted IS NULL)")
            res = cur.fetchone()
            return res['c'] if res else 0
    finally:
        conn.close()


def update_admin_user(admin_id: int, name: str, email: str, role: str, is_active: int = 1, new_password: str = None):
    """Updates an existing administrator account in admin_users table."""
    conn = get_connection()
    try:
        email_clean = email.strip().lower()
        role_clean = role if role in VALID_ADMIN_ROLES else 'manager'
        with conn.cursor() as cur:
            if new_password:
                hashed = hash_admin_password(new_password)
                cur.execute("""
                    UPDATE `admin_users`
                    SET `name` = %s, `email` = %s, `role` = %s, `is_active` = %s, `password` = %s, `updated_at` = NOW()
                    WHERE `id` = %s
                """, (name.strip(), email_clean, role_clean, is_active, hashed, admin_id))
            else:
                cur.execute("""
                    UPDATE `admin_users`
                    SET `name` = %s, `email` = %s, `role` = %s, `is_active` = %s, `updated_at` = NOW()
                    WHERE `id` = %s
                """, (name.strip(), email_clean, role_clean, is_active, admin_id))
        conn.commit()
    finally:
        conn.close()


def delete_admin_user(admin_id: int):
    """Moves an administrator account to trash (soft delete)."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE `admin_users`
                SET is_deleted = 1, deleted_at = NOW(), updated_at = NOW()
                WHERE `id` = %s
            """, (admin_id,))
        conn.commit()
    finally:
        conn.close()


soft_delete_admin_user = delete_admin_user


def restore_admin_user(admin_id: int):
    """Restores a soft-deleted administrator account from trash."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE `admin_users`
                SET is_deleted = 0, deleted_at = NULL, updated_at = NOW()
                WHERE `id` = %s
            """, (admin_id,))
        conn.commit()
    finally:
        conn.close()


def permanent_delete_admin_user(admin_id: int):
    """Permanently deletes an administrator account from admin_users table."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM `admin_users` WHERE `id` = %s", (admin_id,))
        conn.commit()
    finally:
        conn.close()


def toggle_admin_user_status(admin_id: int) -> bool:
    """Toggles is_active between 1 and 0, returns new status."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT is_active FROM `admin_users` WHERE id = %s", (admin_id,))
            row = cur.fetchone()
            if not row:
                return False
            new_status = 0 if row.get('is_active', 1) else 1
            cur.execute("UPDATE `admin_users` SET is_active = %s, updated_at = NOW() WHERE id = %s", (new_status, admin_id))
        conn.commit()
        return bool(new_status)
    finally:
        conn.close()


def update_admin_user_password(admin_id: int, new_password: str):
    """Updates password in admin_users table."""
    conn = get_connection()
    try:
        hashed = hash_admin_password(new_password)
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE `admin_users`
                SET `password` = %s, `updated_at` = NOW()
                WHERE `id` = %s
            """, (hashed, admin_id))
        conn.commit()
    finally:
        conn.close()


def record_admin_login_success(admin_id: int):
    """Updates last_login_at timestamp in admin_users table."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE `admin_users`
                SET `last_login_at` = NOW(), `updated_at` = NOW()
                WHERE `id` = %s
            """, (admin_id,))
        conn.commit()
    finally:
        conn.close()


# ============================================================================
# 4. PASSWORD RESET TOKENS FOR admin_users
# ============================================================================

def create_admin_password_reset_token(email: str) -> str:
    """
    Generates a secure random reset token and stores it in `password_reset_tokens`
    associated with the admin user's email.
    """
    raw_token = secrets.token_urlsafe(32)
    email_clean = email.strip().lower()
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Remove any previous reset tokens for this email
            cur.execute("DELETE FROM `password_reset_tokens` WHERE LOWER(TRIM(email)) = %s", (email_clean,))
            # Insert new token
            cur.execute("""
                INSERT INTO `password_reset_tokens` (`email`, `token`, `created_at`)
                VALUES (%s, %s, NOW())
            """, (email_clean, raw_token))
        conn.commit()
        return raw_token
    finally:
        conn.close()


def verify_and_consume_admin_reset_token(token: str, max_age_seconds: int = 1800):
    """
    Verifies a reset token against `password_reset_tokens` table.
    If valid and within expiration TTL (default 30 mins), deletes the token
    and returns the corresponding admin_user dict. Returns None if invalid or expired.
    """
    if not token:
        return None
    token_clean = token.strip()
    
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT email, token, created_at
                FROM `password_reset_tokens`
                WHERE token = %s
                LIMIT 1
            """, (token_clean,))
            row = cur.fetchone()
            
            if not row:
                return None
            
            # Check token age if created_at timestamp is present
            if row.get('created_at'):
                token_time = row['created_at'].timestamp() if hasattr(row['created_at'], 'timestamp') else time.time()
                if (time.time() - token_time) > max_age_seconds:
                    cur.execute("DELETE FROM `password_reset_tokens` WHERE token = %s", (token_clean,))
                    conn.commit()
                    return None
            
            email = row['email'].strip().lower()
            # Consume (delete) token so it cannot be reused
            cur.execute("DELETE FROM `password_reset_tokens` WHERE LOWER(TRIM(email)) = %s", (email,))
            
            # Fetch the associated admin_user
            cur.execute("""
                SELECT id, name, email, password, role, is_active, last_login_at, created_at, updated_at
                FROM `admin_users`
                WHERE LOWER(TRIM(email)) = %s
                LIMIT 1
            """, (email,))
            admin_user = cur.fetchone()
            
        conn.commit()
        return admin_user
    finally:
        conn.close()
