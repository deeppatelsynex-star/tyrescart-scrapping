import os
import re
import secrets
import subprocess
import sys
import threading
import time
import uuid
from datetime import datetime, timedelta

import pymysql
from flask import Flask, Response, jsonify, redirect, render_template, request, send_from_directory, session

from auth import (
    RESET_TOKEN_TTL_MINUTES,
    VALID_ROLES,
    bit_to_bool,
    consume_reset_token,
    create_password_reset_token,
    get_user_by_email,
    get_user_by_id,
    get_user_id_for_reset_token,
    has_superadmin,
    hash_password,
    list_users,
    login_required_api,
    login_required_page,
    require_csrf,
    role_required_api,
    role_required_page,
    serialize_user,
    verify_password,
)
from db import get_connection
from mailer import send_email
from scraper_status_utils import build_status_summary, parse_status_line

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

# This file lives in app/, but templates/, static/, scrapers/, and the scraper's
# xlsx output all live at the project root (one level up) -- everything below
# that needs a filesystem path is anchored to BASE_DIR, not this file's own directory.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)
# A random fallback key here would change on every process restart (e.g. Render's
# free-tier spin-down/cold-start), invalidating every existing session cookie and
# making the app look like it "reset" on refresh. Set FLASK_SECRET_KEY in the
# hosting environment so sessions survive restarts.
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-insecure-key-set-FLASK_SECRET_KEY-in-production')
app.permanent_session_lifetime = timedelta(days=7)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'

SCRIPT_PATH = os.path.join(BASE_DIR, 'scrapers', 'pitstoparabiabycsv.py')


class ScraperSession:
    """Per-browser-session scraper state, so concurrent users don't see or control each other's runs.

    job_status is a one-shot state machine:
      idle -> running -> completed_unseen/failed_unseen -> idle (archived)
    The completed/failed_unseen states are reported exactly once (by /scraper-status)
    then immediately archived back to idle, so a job that finished is never treated
    as "active" again on a later poll or a fresh page load (browser refresh).
    """

    def __init__(self):
        self.lock = threading.Lock()
        self.process = None
        self.thread = None
        self.url_statuses = []
        self.job_id = None
        self.job_status = 'idle'
        self.stopped = False
        self.output_file = None


scraper_sessions = {}
scraper_sessions_lock = threading.Lock()


def get_session_id():
    if 'sid' not in session:
        session.permanent = True
        session['sid'] = secrets.token_hex(16)
    return session['sid']


def get_scraper_session():
    session_id = get_session_id()
    with scraper_sessions_lock:
        state = scraper_sessions.get(session_id)
        if state is None:
            state = ScraperSession()
            scraper_sessions[session_id] = state
    return state


# @app.route('/')
# def index():
#     return render_template("Dashboard.html", page="Dashboard")


@app.route('/')
@login_required_page
def Scrap():
    return render_template("Scrap.html", page="scraping")


@app.route('/login', methods=['GET'])
def login_page():
    if 'user_id' in session:
        return redirect('/')
    return render_template('login.html')


LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60

_login_attempts_lock = threading.Lock()
_login_attempts = {}  # email -> {'count': int, 'locked_until': monotonic time or None}


def _login_lockout_remaining(email):
    """Returns seconds left in an active lockout for this email, or None if it can try again."""
    now = time.monotonic()
    with _login_attempts_lock:
        entry = _login_attempts.get(email)
        if not entry or not entry['locked_until']:
            return None
        remaining = entry['locked_until'] - now
        if remaining <= 0:
            # Lockout has expired -- give this email a fresh set of attempts.
            _login_attempts.pop(email, None)
            return None
        return remaining


def _record_login_failure(email):
    with _login_attempts_lock:
        entry = _login_attempts.setdefault(email, {'count': 0, 'locked_until': None})
        entry['count'] += 1
        if entry['count'] >= LOGIN_MAX_ATTEMPTS:
            entry['count'] = 0
            entry['locked_until'] = time.monotonic() + LOGIN_LOCKOUT_SECONDS


def _clear_login_failures(email):
    with _login_attempts_lock:
        _login_attempts.pop(email, None)


@app.route('/login', methods=['POST'])
def login_submit():
    data = request.get_json(silent=True) or request.form
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    remember = bool(data.get('remember'))

    if not email or not password:
        return jsonify({'error': 'Email and password are required.'}), 400

    remaining = _login_lockout_remaining(email)
    if remaining is not None:
        minutes = max(1, round(remaining / 60))
        return jsonify({'error': f'Too many failed attempts. Try again in {minutes} minute(s).'}), 429

    user = get_user_by_email(email)
    if not user or bit_to_bool(user['IsDeleted']) or not verify_password(password, user['password']):
        _record_login_failure(email)
        return jsonify({'error': 'Invalid email or password.'}), 401

    if not bit_to_bool(user['Status']):
        return jsonify({'error': 'This account has been disabled. Contact an administrator.'}), 403

    _clear_login_failures(email)

    # Regenerate the whole session (fresh sid + auth claims) on every successful
    # login so a pre-login session id can never be reused post-login (session fixation).
    session.clear()
    session.permanent = remember
    session['sid'] = secrets.token_hex(16)
    session['user_id'] = user['userid']
    session['name'] = user['Name']
    session['email'] = user['Email']
    session['role'] = user['Role']
    session['csrf_token'] = secrets.token_hex(16)

    return jsonify({'redirect': '/'})


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'redirect': '/login'})


RESET_REQUEST_COOLDOWN_SECONDS = 60
_reset_request_lock = threading.Lock()
_last_reset_request_at = {}


def _reset_request_allowed(email):
    """Throttles reset-link requests per email so the form can't be used to spam a mailbox."""
    now = time.monotonic()
    with _reset_request_lock:
        last = _last_reset_request_at.get(email)
        if last is not None and now - last < RESET_REQUEST_COOLDOWN_SECONDS:
            return False
        _last_reset_request_at[email] = now
        return True


@app.route('/forgot-password', methods=['GET'])
def forgot_password_page():
    if 'user_id' in session:
        return redirect('/')
    return render_template('forgot_password.html')


@app.route('/forgot-password', methods=['POST'])
def forgot_password_submit():
    data = request.get_json(silent=True) or request.form
    email = (data.get('email') or '').strip()

    if not email or not EMAIL_RE.match(email):
        return jsonify({'error': 'Please enter a valid email address.'}), 400

    # Unlike a public product, this is an internal admin-provisioned tool with
    # no self-service signup, so telling the user "no account exists" is more
    # useful than hiding it behind a generic message.
    user = get_user_by_email(email)
    if not user or bit_to_bool(user['IsDeleted']):
        return jsonify({'error': 'No account found for that email. Please sign up first'}), 404

    if not bit_to_bool(user['Status']):
        return jsonify({'error': 'This account has been disabled. Contact an administrator.'}), 403

    if not _reset_request_allowed(email):
        return jsonify({'error': 'A reset link was already sent recently. Check your inbox, or wait a minute and try again.'}), 429

    token = create_password_reset_token(user['userid'])
    reset_link = f"{request.url_root.rstrip('/')}/reset-password?token={token}"
    try:
        email_body = render_template(
            'emails/reset_password.html',
            reset_link=reset_link,
            expires_minutes=RESET_TOKEN_TTL_MINUTES,
            user_name=user['Name'],
            user_email=user['Email'],
        )
        send_email(user['Email'], 'Reset your TyresCart password', email_body)
    except Exception:
        app.logger.exception('Failed to send password reset email to %s', user['Email'])
        return jsonify({'error': 'Failed to send the reset email. Please try again later.'}), 500

    return jsonify({'message': 'A password reset link has been sent to your email.'})


@app.route('/reset-password', methods=['GET'])
def reset_password_page():
    if 'user_id' in session:
        return redirect('/')
    return render_template('reset_password.html')


@app.route('/reset-password', methods=['POST'])
def reset_password_submit():
    data = request.get_json(silent=True) or {}
    token = data.get('token') or ''
    new_password = data.get('new_password') or ''
    confirm_password = data.get('confirm_password') or ''

    if not token:
        return jsonify({'error': 'This reset link is invalid or has expired.'}), 400
    if not new_password or not confirm_password:
        return jsonify({'error': 'All fields are required.'}), 400
    if new_password != confirm_password:
        return jsonify({'error': 'Passwords do not match.'}), 400
    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters.'}), 400

    user_id = get_user_id_for_reset_token(token)
    if not user_id:
        return jsonify({'error': 'This reset link is invalid or has expired.'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE userTbl SET password = %s WHERE userid = %s', (hash_password(new_password), user_id))
    finally:
        conn.close()

    consume_reset_token(token)

    return jsonify({'message': 'Your password has been reset. You can now sign in.'})


@app.route('/api/me')
@login_required_api
def api_me():
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return jsonify({'error': 'Authentication required.'}), 401
    return jsonify({'user': serialize_user(user), 'csrfToken': session.get('csrf_token')})


@app.route('/api/profile', methods=['PUT'])
@login_required_api
@require_csrf
def api_update_profile():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    avatar = data.get('avatar')
    avatar = avatar.strip() if isinstance(avatar, str) else None
    avatar = avatar or None

    if not name:
        return jsonify({'error': 'Name is required.'}), 400
    if not email or not EMAIL_RE.match(email):
        return jsonify({'error': 'A valid email is required.'}), 400
    if avatar and len(avatar) > 500:
        return jsonify({'error': 'Avatar URL is too long.'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    'UPDATE userTbl SET Name = %s, Email = %s, avatar = %s WHERE userid = %s',
                    (name, email, avatar, session['user_id']),
                )
            except pymysql.err.IntegrityError:
                return jsonify({'error': 'That email is already in use.'}), 409
    finally:
        conn.close()

    session['name'] = name
    session['email'] = email

    user = get_user_by_id(session['user_id'])
    return jsonify({'user': serialize_user(user)})


@app.route('/api/profile/avatar', methods=['DELETE'])
@login_required_api
@require_csrf
def api_remove_avatar():
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE userTbl SET avatar = NULL WHERE userid = %s', (session['user_id'],))
    finally:
        conn.close()

    user = get_user_by_id(session['user_id'])
    return jsonify({'user': serialize_user(user)})


@app.route('/api/change-password', methods=['POST'])
@login_required_api
@require_csrf
def api_change_password():
    fail_count = session.get('pwd_fail_count', 0)
    if fail_count >= 5:
        session.clear()
        return jsonify({'error': 'Too many failed attempts. Please log in again.'}), 429

    data = request.get_json(silent=True) or {}
    current_password = data.get('current_password') or ''
    new_password = data.get('new_password') or ''
    confirm_password = data.get('confirm_password') or ''

    if not current_password or not new_password or not confirm_password:
        return jsonify({'error': 'All fields are required.'}), 400
    if new_password != confirm_password:
        return jsonify({'error': 'New password and confirmation do not match.'}), 400
    if len(new_password) < 8:
        return jsonify({'error': 'New password must be at least 8 characters.'}), 400

    user = get_user_by_id(session['user_id'])
    if not user or not verify_password(current_password, user['password']):
        session['pwd_fail_count'] = fail_count + 1
        return jsonify({'error': 'Current password is incorrect.'}), 400

    if verify_password(new_password, user['password']):
        return jsonify({'error': 'New password must be different from the current password.'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                'UPDATE userTbl SET password = %s WHERE userid = %s',
                (hash_password(new_password), session['user_id']),
            )
    finally:
        conn.close()

    session.pop('pwd_fail_count', None)
    # Rotate identifiers after a credential change so a stolen pre-change
    # session/CSRF token pairing can't be replayed.
    session['sid'] = secrets.token_hex(16)
    session['csrf_token'] = secrets.token_hex(16)

    return jsonify({'message': 'Password changed successfully.'})


@app.route('/Admin')
@login_required_page
@role_required_page('SuperAdmin', 'Admin')
def admin_page():
    return render_template('admin.html', page='admin')


@app.route('/api/admin/users', methods=['GET'])
@login_required_api
@role_required_api('SuperAdmin', 'Admin')
def api_admin_list_users():
    return jsonify({'users': [serialize_user(u) for u in list_users()]})


@app.route('/api/admin/users', methods=['POST'])
@login_required_api
@role_required_api('SuperAdmin')
@require_csrf
def api_admin_create_user():
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    password = data.get('password') or ''
    role = (data.get('role') or '').strip()
    status = data.get('status', True)

    if not name:
        return jsonify({'error': 'Name is required.'}), 400
    if not email or not EMAIL_RE.match(email):
        return jsonify({'error': 'A valid email is required.'}), 400
    if not password or len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters.'}), 400
    if role not in VALID_ROLES:
        return jsonify({'error': f"Role must be one of: {', '.join(VALID_ROLES)}."}), 400
    # Exactly one SuperAdmin may ever exist in the system.
    if role == 'SuperAdmin' and has_superadmin():
        return jsonify({'error': 'A SuperAdmin already exists. Only one SuperAdmin account is allowed.'}), 409

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    'INSERT INTO userTbl (Name, Email, password, Status, IsDeleted, Role) '
                    'VALUES (%s, %s, %s, %s, 0, %s)',
                    (name, email, hash_password(password), 1 if status else 0, role),
                )
            except pymysql.err.IntegrityError:
                return jsonify({'error': 'A user with that email already exists.'}), 409
            new_user_id = cursor.lastrowid
    finally:
        conn.close()

    return jsonify({'user': serialize_user(get_user_by_id(new_user_id))}), 201


@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@login_required_api
@role_required_api('SuperAdmin', 'Admin')
@require_csrf
def api_admin_update_user(user_id):
    target = get_user_by_id(user_id)
    if not target:
        return jsonify({'error': 'User not found.'}), 404

    actor_role = session.get('role')
    # An Admin can manage other Admins/Users, but never touch a SuperAdmin's
    # account -- that's reserved for SuperAdmins only.
    if target['Role'] == 'SuperAdmin' and actor_role != 'SuperAdmin':
        return jsonify({'error': 'Only a SuperAdmin can modify a SuperAdmin account.'}), 403

    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    email = (data.get('email') or '').strip()
    role = (data.get('role') or '').strip()
    password = data.get('password') or ''
    status = data.get('status', True)

    if not name:
        return jsonify({'error': 'Name is required.'}), 400
    if not email or not EMAIL_RE.match(email):
        return jsonify({'error': 'A valid email is required.'}), 400
    if role not in VALID_ROLES:
        return jsonify({'error': f"Role must be one of: {', '.join(VALID_ROLES)}."}), 400
    if role == 'SuperAdmin' and actor_role != 'SuperAdmin':
        return jsonify({'error': 'Only a SuperAdmin can grant the SuperAdmin role.'}), 403
    # Exactly one SuperAdmin may ever exist -- only exempt this check when the
    # target already holds the role (i.e. this edit isn't creating a new one).
    if role == 'SuperAdmin' and target['Role'] != 'SuperAdmin' and has_superadmin():
        return jsonify({'error': 'A SuperAdmin already exists. Only one SuperAdmin account is allowed.'}), 409
    if password and len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters.'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            try:
                if password:
                    cursor.execute(
                        'UPDATE userTbl SET Name = %s, Email = %s, Role = %s, Status = %s, password = %s '
                        'WHERE userid = %s',
                        (name, email, role, 1 if status else 0, hash_password(password), user_id),
                    )
                else:
                    cursor.execute(
                        'UPDATE userTbl SET Name = %s, Email = %s, Role = %s, Status = %s WHERE userid = %s',
                        (name, email, role, 1 if status else 0, user_id),
                    )
            except pymysql.err.IntegrityError:
                return jsonify({'error': 'That email is already in use.'}), 409
    finally:
        conn.close()

    updated = get_user_by_id(user_id)
    # Keep the acting user's own session in sync if they just edited themselves.
    if user_id == session.get('user_id'):
        session['name'] = updated['Name']
        session['email'] = updated['Email']
        session['role'] = updated['Role']

    return jsonify({'user': serialize_user(updated)})


@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@login_required_api
@role_required_api('SuperAdmin', 'Admin')
@require_csrf
def api_admin_delete_user(user_id):
    target = get_user_by_id(user_id)
    if not target:
        return jsonify({'error': 'User not found.'}), 404

    # A SuperAdmin account can never be deleted -- not by another SuperAdmin,
    # and not by an Admin.
    if target['Role'] == 'SuperAdmin':
        return jsonify({'error': 'SuperAdmin accounts can never be deleted.'}), 403

    # No one -- SuperAdmin or Admin -- can delete their own account.
    if user_id == session.get('user_id'):
        return jsonify({'error': 'You cannot delete your own account.'}), 403

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # Soft delete (matches how login/forgot-password already treat
            # IsDeleted) rather than removing the row outright.
            cursor.execute('UPDATE userTbl SET IsDeleted = 1 WHERE userid = %s', (user_id,))
    finally:
        conn.close()

    return jsonify({'message': 'User deleted.'})


@app.route('/api/admin/users/<int:user_id>/recover', methods=['POST'])
@login_required_api
@role_required_api('SuperAdmin')
@require_csrf
def api_admin_recover_user(user_id):
    target = get_user_by_id(user_id)
    if not target:
        return jsonify({'error': 'User not found.'}), 404
    if not bit_to_bool(target['IsDeleted']):
        return jsonify({'error': 'This account is not deleted.'}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE userTbl SET IsDeleted = 0 WHERE userid = %s', (user_id,))
    finally:
        conn.close()

    return jsonify({'message': 'User recovered.'})


def _read_scraper_output(state, process):
    try:
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            cleaned_line = line.rstrip('\n')
            with state.lock:
                parsed_status = parse_status_line(cleaned_line)
                if parsed_status:
                    existing = next((item for item in state.url_statuses if item['url'] == parsed_status['url']), None)
                    if existing:
                        existing['status'] = parsed_status['status']
                        if parsed_status.get('parent'):
                            existing['parent'] = parsed_status['parent']
                        if parsed_status.get('type'):
                            existing['type'] = parsed_status['type']
                    else:
                        state.url_statuses.append({
                            'url': parsed_status['url'],
                            'status': parsed_status['status'],
                            'parent': parsed_status.get('parent') or '',
                            'type': parsed_status.get('type') or 'root',
                        })
        process.stdout.close()
        process.wait()
    finally:
        with state.lock:
            if state.stopped:
                state.job_status = 'idle'
            elif process.returncode not in (0, None):
                state.job_status = 'failed_unseen'
            else:
                state.job_status = 'completed_unseen'


@app.route('/StartScraper', methods=['POST'])
@login_required_api
def start_scraper():
    state = get_scraper_session()

    with state.lock:
        if state.process and state.process.poll() is None:
            return Response('Scraper is already running.', status=409, mimetype='text/plain')

        state.url_statuses.clear()
        state.stopped = False
        state.job_id = uuid.uuid4().hex
        state.job_status = 'running'

        timestamp = datetime.now().strftime('%d-%m-%Y_%H%M%S')
        output_file = os.path.join(BASE_DIR, f'pitstoparabia_data_{get_session_id()[:8]}_{timestamp}.xlsx')
        state.output_file = output_file

        process = subprocess.Popen(
            [sys.executable, '-u', SCRIPT_PATH, output_file],
            cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
        )

        state.process = process
        state.thread = threading.Thread(target=_read_scraper_output, args=(state, process), daemon=True)
        state.thread.start()

    return Response(
        f'Background scraper started with PID {process.pid}. Job ID: {state.job_id}',
        status=200,
        mimetype='text/plain'
    )


@app.route('/stop-scraper', methods=['POST'])
@login_required_api
def stop_scraper():
    state = get_scraper_session()
    with state.lock:
        if not state.process or state.process.poll() is not None:
            return jsonify({'stopped': False, 'message': 'No scraper process is running.'})

        state.stopped = True
        try:
            state.process.terminate()
            state.process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            state.process.kill()
            state.process.wait()
        finally:
            state.process = None

    return jsonify({'stopped': True, 'message': 'Scraper has been stopped.'})

@app.route('/scraper-url-statuses')
@login_required_api
def scraper_url_statuses_endpoint():
    state = get_scraper_session()
    with state.lock:
        statuses = list(state.url_statuses)
        running = state.process is not None and state.process.poll() is None
        # A completed/failed job's tree is served exactly once (the same request
        # cycle that /scraper-status reports it in), then cleared. Any later
        # fetch -- including a fresh page load after a refresh -- sees the
        # empty/idle tree instead of restoring a job that already finished.
        if not running and state.job_status == 'idle' and state.url_statuses:
            state.url_statuses.clear()

    return jsonify({
        'statuses': statuses,
        'summary': build_status_summary(statuses),
    })


@app.route('/scraper-status')
@login_required_api
def scraper_status():
    state = get_scraper_session()
    with state.lock:
        running = state.process is not None and state.process.poll() is None
        if running:
            state.job_status = 'running'

        current = state.job_status
        if current in ('completed_unseen', 'failed_unseen'):
            reported_status = 'completed' if current == 'completed_unseen' else 'failed'
            # One-shot: archive immediately so no later request (poll or page
            # refresh) ever sees this finished job as active again.
            state.job_status = 'idle'
        elif current == 'running':
            reported_status = 'running'
        else:
            reported_status = 'idle'

        has_active_job = reported_status == 'running'
        job_id = state.job_id if has_active_job else None
        output_file = state.output_file

    output_available = bool(output_file and os.path.exists(output_file))

    return jsonify({
        # Legacy fields kept for the existing frontend.
        'running': reported_status == 'running',
        'done': reported_status in ('completed', 'failed'),
        'outputAvailable': output_available,
        'outputFile': os.path.basename(output_file) if output_available else '',
        # New fields: explicit job status/identity.
        'status': reported_status,
        'hasActiveJob': has_active_job,
        'jobId': job_id,
    })


@app.route('/download-output')
@login_required_api
def download_output():
    state = get_scraper_session()
    with state.lock:
        output_file = state.output_file

    if not output_file or not os.path.exists(output_file):
        return Response('No output file found.', status=404, mimetype='text/plain')

    return send_from_directory(BASE_DIR, os.path.basename(output_file), as_attachment=True)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)
