import os
import sys

# Ensure app directory and project root are always in sys.path for direct imports
_app_dir = os.path.dirname(os.path.abspath(__file__))
_root_dir = os.path.dirname(_app_dir)
for _p in [_app_dir, _root_dir]:
    if _p not in sys.path:
        sys.path.insert(0, _p)

import secrets
import threading
import time
from datetime import timedelta

from flask import Flask, abort, jsonify, redirect, render_template, request, session

import re

from api import register_api_routes
from vison_api import register_vison_api_routes
from auth import (
    bit_to_bool,
    create_password_reset_token,
    get_user_by_email,
    get_user_by_id,
    login_required_page,
    role_required_page,
    update_user_password,
    verify_and_consume_reset_token,
    verify_password,
)
from db import get_connection

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')
import job_manager
from mailer import send_email

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'scrapers'))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static'),
)

# High-Performance HTTP Response Compression (Brotli + Gzip)
try:
    from flask_compress import Compress
    Compress(app)
    app.config['COMPRESS_ALGORITHM'] = ['brotli', 'gzip', 'deflate']
    app.config['COMPRESS_MIN_SIZE'] = 500
except ImportError:
    pass

app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'dev-only-insecure-key-set-FLASK_SECRET_KEY-in-production')
app.permanent_session_lifetime = timedelta(days=7)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 604800  # 7 days browser cache for static files


@app.after_request
def add_performance_headers(response):
    """Adds caching headers for static assets and enables keep-alive."""
    if request.path.startswith('/static/'):
        response.headers['Cache-Control'] = 'public, max-age=604800, stale-while-revalidate=86400'
    return response


# ============================================================================
# 1. CLIENT-SIDE STOREFRONT ROUTES
# ============================================================================

@app.route('/')
@app.route('/home')
def client_home():
    """Client storefront home landing page."""
    return render_template('Client/Home.html')


# ============================================================================
# 2. SCRAPER ADMIN PAGE ROUTES
# Base URL: https://tyrescart-scrapping.klever.ae/tcsadmin/
# ============================================================================

@app.route('/tcsadmin/login', methods=['GET'])
@app.route('/tcsadmin', methods=['GET'])
@app.route('/tcsadmin/', methods=['GET'])
def login_page():
    if 'user_id' in session:
        return redirect('/tcsadmin/docs/scraper')
    return render_template('login.html')


@app.route('/tcsadmin/docs/scraper')
@app.route('/tcsadmin/scrapers')
@app.route('/tcsadmin/scraper')
@app.route('/tcsadmin/files')
@login_required_page
def files_page():
    return render_template('files.html', page='files')


@app.route('/tcsadmin/scraperpage')
@login_required_page
def Scrap():
    file_id = request.args.get('fileId')
    if not file_id:
        user_id = session.get('user_id')
        active_map = job_manager.get_all_active_jobs_map()
        running_for_user = [fid for fid, info in active_map.items() if info.get('user_id') == user_id]
        if running_for_user:
            return redirect(f'/tcsadmin/scraperpage?fileId={running_for_user[0]}')
        if active_map:
            return redirect(f'/tcsadmin/scraperpage?fileId={list(active_map.keys())[0]}')

        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT file_id FROM logTbl ORDER BY id DESC LIMIT 1")
                latest_log = cursor.fetchone()
                if latest_log and latest_log.get('file_id'):
                    return redirect(f'/tcsadmin/scraperpage?fileId={latest_log["file_id"]}')
                cursor.execute("SELECT file_id FROM fileTbl WHERE is_deleted = 0 ORDER BY file_id ASC LIMIT 1")
                first_file = cursor.fetchone()
                if first_file:
                    return redirect(f'/tcsadmin/scraperpage?fileId={first_file["file_id"]}')
        finally:
            conn.close()

    return render_template("Scrap.html", page="scraping")


@app.route('/tcsadmin/reports')
@app.route('/tcsadmin/scraper-runs')
@app.route('/tcsadmin/logs')
@login_required_page
@role_required_page('SuperAdmin')
def reports_page():
    return render_template('reports.html', page='reports')


@app.route('/tcsadmin/Admin')
@login_required_page
@role_required_page('SuperAdmin', 'Admin')
def admin_page():
    return render_template('admin.html', page='admin')


@app.route('/tcsadmin/trash')
@login_required_page
@role_required_page('SuperAdmin', 'Admin')
def trash_page():
    return render_template('trash.html', page='trash')


@app.route('/tcsadmin/docs/guide')
@app.route('/tcsadmin/docs/scraper-guide')
@login_required_page
def scraper_guide_page():
    return render_template('scraper_guide.html', page='docs')


# ============================================================================
# 3. AUTHENTICATION & PASSWORD RESET ENDPOINTS
# ============================================================================

LOGIN_MAX_ATTEMPTS = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60

_login_attempts = {}
_login_attempts_lock = threading.Lock()


def _login_lockout_remaining(email):
    with _login_attempts_lock:
        info = _login_attempts.get(email)
        if not info:
            return None
        attempts, first_failed_at = info
        if attempts < LOGIN_MAX_ATTEMPTS:
            return None
        elapsed = time.time() - first_failed_at
        if elapsed >= LOGIN_LOCKOUT_SECONDS:
            del _login_attempts[email]
            return None
        return LOGIN_LOCKOUT_SECONDS - elapsed


def _record_login_failure(email):
    with _login_attempts_lock:
        now = time.time()
        info = _login_attempts.get(email)
        if not info:
            _login_attempts[email] = (1, now)
        else:
            attempts, first_failed_at = info
            if now - first_failed_at >= LOGIN_LOCKOUT_SECONDS:
                _login_attempts[email] = (1, now)
            else:
                _login_attempts[email] = (attempts + 1, first_failed_at)


def _clear_login_failures(email):
    with _login_attempts_lock:
        _login_attempts.pop(email, None)


@app.route('/tcsadmin/login', methods=['POST'])
@app.route('/tcsadmin', methods=['POST'])
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

    session.clear()
    session.permanent = remember
    session['sid'] = secrets.token_hex(16)
    session['user_id'] = user['userid']
    session['name'] = user['Name']
    session['email'] = user['Email']
    session['role'] = user['Role']
    session['csrf_token'] = secrets.token_hex(16)

    return jsonify({'redirect': '/tcsadmin/docs/scraper'})


@app.route('/tcsadmin/logout', methods=['GET', 'POST'])
@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    if request.method == 'GET' or not (request.is_json or (request.headers.get('Accept') and 'application/json' in request.headers.get('Accept'))):
        return redirect('/tcsadmin/login')
    return jsonify({'redirect': '/tcsadmin/login'})


@app.route('/tcsadmin/forgot-password', methods=['GET', 'POST'])
@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password_page():
    if request.method == 'GET':
        return render_template('forgot_password.html')

    data = request.get_json(silent=True) or request.form or {}
    email = (data.get('email') or '').strip().lower()

    if not email or not EMAIL_RE.match(email):
        return jsonify({'error': 'Please enter a valid email address.'}), 400

    user = get_user_by_email(email)
    if user and bit_to_bool(user.get('Status')) and not bit_to_bool(user.get('IsDeleted')):
        try:
            token = create_password_reset_token(user['userid'])
            reset_link = f"{request.host_url.rstrip('/')}/tcsadmin/reset-password?token={token}"
            html_body = render_template(
                'emails/reset_password.html',
                user_name=user.get('Name') or 'there',
                user_email=user.get('Email') or email,
                reset_link=reset_link,
                expires_minutes=30,
            )
            send_email(user['Email'], 'Reset your TyresCart password', html_body)
        except Exception as e:
            app.logger.error(f'Error sending password reset email: {e}')
            return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

    return jsonify({
        'success': True,
        'message': 'If an account exists with that email, a password reset link has been sent.',
    })


@app.route('/tcsadmin/reset-password', methods=['GET', 'POST'])
@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password_page():
    if request.method == 'GET':
        return render_template('reset_password.html')

    data = request.get_json(silent=True) or request.form or {}
    token = (data.get('token') or '').strip()
    new_password = data.get('new_password') or ''
    confirm_password = data.get('confirm_password') or ''

    if not token:
        return jsonify({'error': 'Reset token is required.'}), 400

    if not new_password or not confirm_password:
        return jsonify({'error': 'Both password fields are required.'}), 400

    if new_password != confirm_password:
        return jsonify({'error': 'Passwords do not match.'}), 400

    if len(new_password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long.'}), 400

    user_id = verify_and_consume_reset_token(token)
    if not user_id:
        return jsonify({'error': 'Invalid or expired reset link. Please request a new one.'}), 400

    user = get_user_by_id(user_id)
    if not user or not bit_to_bool(user.get('Status')) or bit_to_bool(user.get('IsDeleted')):
        return jsonify({'error': 'Account not found or inactive.'}), 404

    update_user_password(user_id, new_password)
    return jsonify({
        'success': True,
        'message': 'Your password has been reset successfully. You can now sign in.',
    })


# ============================================================================
# 3. TYRESVISION CMS PAGE ROUTES (/visonadmin/*)
# Base URL: https://tyrescart-scrapping.klever.ae/visonadmin/
# ============================================================================

@app.route('/visonadmin/login', methods=['GET'])
@app.route('/visonadmin', methods=['GET'])
@app.route('/visonadmin/', methods=['GET'])
def vison_login_page():
    if 'user_id' in session:
        return redirect('/visonadmin/dashboard')
    return render_template('visonadmin/login.html')


@app.route('/visonadmin/dashboard')
@login_required_page
def vison_dashboard_page():
    return render_template('visonadmin/dashboard.html', page='dashboard')


@app.route('/visonadmin/pages')
@login_required_page
def vison_pages_page():
    return render_template('visonadmin/pages.html', page='pages')


@app.route('/visonadmin/media')
@login_required_page
def vison_media_page():
    return render_template('visonadmin/media.html', page='media')


@app.route('/visonadmin/settings')
@login_required_page
def vison_settings_page():
    return render_template('visonadmin/settings.html', page='settings')


# ============================================================================
# 4. REGISTER CENTRALIZED API LAYERS
# ============================================================================

register_api_routes(app)
register_vison_api_routes(app)


# ============================================================================
# 5. ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def handle_404_error(e):
    """Gracefully handles unwanted page or API requests by serving custom 404."""
    if request.path.startswith('/tcsadmin/api/') or request.headers.get('Accept') == 'application/json':
        return jsonify({
            'error': 'The requested API resource was not found.',
            'status': 404,
            'path': request.path
        }), 404
    return render_template(
        '404.html',
        page='404',
        requested_path=request.path,
        user_name=session.get('name'),
        user_email=session.get('email'),
        user_role=session.get('role'),
        user_avatar=session.get('avatar'),
        unread_notifications=0,
        notifications=[]
    ), 404


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8090))
    app.run(host="0.0.0.0", port=port, debug=True)