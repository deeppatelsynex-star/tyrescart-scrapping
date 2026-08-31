"""
app/visionadmin/Visionadminroute.py - VisionAdmin CMS Authentication & Studio Page Routes.

Serves the VisionAdmin HTML pages only (Pages/Blogs/Sections/Settings/Enquiries).
Authenticated and authorized against the `admin_users` table in the database.
"""

import functools
import re
import secrets
from flask import jsonify, redirect, render_template, request, session

from visionadmin.admin_auth import (
    check_admin_forgot_password_rate_limit,
    check_admin_login_rate_limit,
    check_admin_reset_password_rate_limit,
    clear_admin_login_failures,
    create_admin_password_reset_token,
    get_admin_user_by_email,
    get_admin_user_by_id,
    record_admin_forgot_password_request,
    record_admin_login_failure,
    record_admin_login_success,
    record_admin_reset_password_attempt,
    update_admin_user_password,
    verify_admin_password,
    verify_and_consume_admin_reset_token,
)
from mailer import send_email

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

ALLOWED_ADMIN_ROLES = {'super_admin', 'superadmin', 'manager', 'support', 'admin'}


def is_authorized_admin(role: str) -> bool:
    """Case-insensitive check for admin privileges."""
    if not role:
        return False
    normalized = str(role).strip().lower().replace('-', '_').replace(' ', '_')
    return normalized in ALLOWED_ADMIN_ROLES or role.strip() in ('SuperAdmin', 'Admin')


def login_required_visionadmin(view):
    """Protects VisionAdmin page routes: requires authenticated administrator from admin_users table."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get('admin_user_id') or session.get('user_id')
        email = session.get('email')
        if not user_id and not email:
            return redirect(f'/visionadmin/login?next={request.path}')

        admin_u = None
        if user_id:
            admin_u = get_admin_user_by_id(user_id)
        if not admin_u and email:
            admin_u = get_admin_user_by_email(email)
            if admin_u:
                session['admin_user_id'] = admin_u['id']
                session['user_id'] = admin_u['id']
                session['name'] = admin_u['name']
                session['email'] = admin_u['email']
                session['role'] = admin_u['role']
                session['is_visionadmin'] = True

        if not admin_u:
            session.clear()
            return redirect(f'/visionadmin/login?next={request.path}')

        role = admin_u.get('role') or session.get('role')
        if not is_authorized_admin(role):
            return render_template(
                '404.html',
                page='403',
                requested_path=request.path,
                user_name=session.get('name'),
                user_email=session.get('email'),
                user_role=role,
                error_message='You do not have administrative permission to access VisionAdmin CMS.',
                unread_notifications=0,
                notifications=[]
            ), 403
        return view(*args, **kwargs)
    return wrapped


def register_visionadmin_routes(app):
    """Registers the /visionadmin (and /visonadmin, /admin aliases) authentication and page routes."""

    # ========================================================================
    # 1. AUTHENTICATION & SESSION ROUTES (admin_users table)
    # ========================================================================

    @app.route('/visionadmin/login', methods=['GET'])
    @app.route('/visonadmin/login', methods=['GET'])
    def visionadmin_login_page():
        """Renders the VisionAdmin login page or redirects if already signed in."""
        user_id = session.get('admin_user_id') or session.get('user_id')
        role = session.get('role')
        if user_id and is_authorized_admin(role):
            next_url = request.args.get('next') or '/visionadmin/pages'
            return redirect(next_url)
        return render_template('visionadmin/login.html')

    @app.route('/visionadmin/login', methods=['POST'])
    @app.route('/visonadmin/login', methods=['POST'])
    def visionadmin_login_submit():
        """Authenticates administrator against admin_users table with email & password."""
        data = request.get_json(silent=True) or request.form
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        remember = bool(data.get('remember'))

        if not email or not password:
            return jsonify({'error': 'Email and password are required.'}), 400

        # Rate limiting check
        is_locked, seconds_remaining, msg = check_admin_login_rate_limit(email)
        if is_locked:
            return jsonify({'error': msg}), 429

        # Query admin_users table
        admin_user = get_admin_user_by_email(email)
        if not admin_user or not verify_admin_password(password, admin_user.get('password', '')):
            record_admin_login_failure(email)
            return jsonify({'error': 'Invalid email or password.'}), 401

        # Check if active
        if not admin_user.get('is_active', 1):
            return jsonify({'error': 'This administrator account has been disabled. Contact support.'}), 403

        # Check role permission
        role = admin_user.get('role', 'manager')
        if not is_authorized_admin(role):
            return jsonify({'error': 'Access denied. Administrator privileges required.'}), 403

        # Success - Clear rate limit counters and record login timestamp
        clear_admin_login_failures(email)
        record_admin_login_success(admin_user['id'])

        session.clear()
        session.permanent = remember
        session['sid'] = secrets.token_hex(16)
        session['admin_user_id'] = admin_user['id']
        session['user_id'] = admin_user['id']
        session['userid'] = admin_user['id']
        session['id'] = admin_user['id']
        session['name'] = admin_user['name']
        session['Name'] = admin_user['name']
        session['email'] = admin_user['email']
        session['Email'] = admin_user['email']
        session['role'] = 'SuperAdmin' if admin_user['role'] in ('super_admin', 'superadmin', 'SuperAdmin') else ('Admin' if admin_user['role'] in ('manager', 'admin', 'Admin') else 'User')
        session['admin_role'] = admin_user['role']
        session['csrf_token'] = secrets.token_hex(16)
        session['is_visionadmin'] = True
        session['logged_in'] = True

        next_url = request.args.get('next') or '/visionadmin/pages'
        return jsonify({
            'success': True,
            'redirect': next_url,
            'user': {
                'id': admin_user['id'],
                'name': admin_user['name'],
                'email': admin_user['email'],
                'role': admin_user['role']
            }
        })

    @app.route('/visionadmin/logout', methods=['GET', 'POST'])
    @app.route('/visonadmin/logout', methods=['GET', 'POST'])
    def visionadmin_logout():
        """Clears administrator session and redirects to VisionAdmin login."""
        session.clear()
        if request.method == 'GET' or not (request.is_json or (request.headers.get('Accept') and 'application/json' in request.headers.get('Accept'))):
            return redirect('/visionadmin/login')
        return jsonify({'success': True, 'redirect': '/visionadmin/login'})

    @app.route('/visionadmin/forgot-password', methods=['GET', 'POST'])
    @app.route('/visonadmin/forgot-password', methods=['GET', 'POST'])
    def visionadmin_forgot_password():
        """Handles password reset requests for administrators using admin_users table."""
        if request.method == 'GET':
            return render_template('visionadmin/forgot_password.html')

        data = request.get_json(silent=True) or request.form or {}
        email = (data.get('email') or '').strip().lower()

        if not email or not EMAIL_RE.match(email):
            return jsonify({'error': 'Please enter a valid email address.'}), 400

        is_limited, seconds_remaining, msg = check_admin_forgot_password_rate_limit(email)
        if is_limited:
            return jsonify({'error': msg}), 429

        record_admin_forgot_password_request(email)

        # Lookup in admin_users table
        admin_user = get_admin_user_by_email(email)
        if admin_user and admin_user.get('is_active', 1):
            try:
                assets_url = 'https://tyrescart-scrapping.klever.ae' if ('localhost' in request.host_url or '127.0.0.1' in request.host_url) else request.host_url.rstrip('/')
                token = create_admin_password_reset_token(admin_user['email'])
                reset_link = f"{request.host_url.rstrip('/')}/visionadmin/reset-password?token={token}"
                html_body = render_template(
                    'emails/vison_forgotpass.html',
                    user_name=admin_user.get('name') or 'there',
                    user_email=admin_user.get('email') or email,
                    reset_link=reset_link,
                    expires_minutes=30,
                    assets_url=assets_url,
                )
                send_email(
                    admin_user['email'],
                    'Reset Your VisionAdmin Password',
                    html_body,
                )
            except Exception as e:
                app.logger.error(f'Error sending password reset email to admin: {e}')
                return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

        return jsonify({
            'success': True,
            'message': 'If an administrator account exists with that email, a password reset link has been sent.',
        })

    @app.route('/visionadmin/reset-password', methods=['GET', 'POST'])
    @app.route('/visonadmin/reset-password', methods=['GET', 'POST'])
    def visionadmin_reset_password():
        """Handles password reset token consumption for admin_users table."""
        if request.method == 'GET':
            return render_template('visionadmin/reset_password.html', token=request.args.get('token', ''))

        data = request.get_json(silent=True) or request.form or {}
        token = (data.get('token') or '').strip()
        new_password = data.get('new_password') or ''
        confirm_password = data.get('confirm_password') or ''

        is_limited, seconds_remaining, msg = check_admin_reset_password_rate_limit()
        if is_limited:
            return jsonify({'error': msg}), 429

        record_admin_reset_password_attempt()

        if not token:
            return jsonify({'error': 'Reset token is required.'}), 400

        if not new_password or not confirm_password:
            return jsonify({'error': 'Both password fields are required.'}), 400

        if new_password != confirm_password:
            return jsonify({'error': 'Passwords do not match.'}), 400

        if len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters long.'}), 400

        # Verify and consume reset token against password_reset_tokens / admin_users
        admin_user = verify_and_consume_admin_reset_token(token)
        if not admin_user:
            return jsonify({'error': 'Invalid or expired reset link. Please request a new one.'}), 400

        if not admin_user.get('is_active', 1):
            return jsonify({'error': 'Account not found or inactive.'}), 404

        update_admin_user_password(admin_user['id'], new_password)
        return jsonify({
            'success': True,
            'message': 'Your password has been reset successfully. You can now sign in to VisionAdmin.',
            'redirect': '/visionadmin/login'
        })

    # ========================================================================
    # 2. VISIONADMIN CMS STUDIO PAGES (PROTECTED)
    # ========================================================================

    @app.route('/visionadmin', methods=['GET'])
    @app.route('/visionadmin/', methods=['GET'])
    @app.route('/visionadmin/pages', methods=['GET'])
    @app.route('/visonadmin', methods=['GET'])
    @app.route('/visonadmin/', methods=['GET'])
    @app.route('/admin/pages', methods=['GET'])
    @login_required_visionadmin
    def visionadmin_pages():
        return render_template('visionadmin/pages.html', page='pages')

    @app.route('/visionadmin/blogs', methods=['GET'])
    @app.route('/visonadmin/blogs', methods=['GET'])
    @app.route('/admin/blogs', methods=['GET'])
    @login_required_visionadmin
    def visionadmin_blogs():
        return render_template('visionadmin/blogs.html', page='blogs')

    @app.route('/visionadmin/sections', methods=['GET'])
    @app.route('/visionadmin/about-sections', methods=['GET'])
    @app.route('/visonadmin/sections', methods=['GET'])
    @app.route('/visonadmin/about-sections', methods=['GET'])
    @app.route('/admin/sections', methods=['GET'])
    @app.route('/admin/about-sections', methods=['GET'])
    @login_required_visionadmin
    def visionadmin_sections():
        return render_template('visionadmin/sections.html', page='sections')

    @app.route('/visionadmin/settings', methods=['GET'])
    @app.route('/visionadmin/config', methods=['GET'])
    @app.route('/visionadmin/reviewer-settings', methods=['GET'])
    @app.route('/visonadmin/settings', methods=['GET'])
    @app.route('/visonadmin/config', methods=['GET'])
    @login_required_visionadmin
    def visionadmin_settings():
        return render_template('visionadmin/settings.html', page='settings')

    @app.route('/visionadmin/enquiries', methods=['GET'])
    @app.route('/visionadmin/enquiry', methods=['GET'])
    @app.route('/visionadmin/leads', methods=['GET'])
    @app.route('/visonadmin/enquiries', methods=['GET'])
    @app.route('/visonadmin/enquiry', methods=['GET'])
    @login_required_visionadmin
    def visionadmin_enquiries():
        return render_template('visionadmin/enquiries.html', page='enquiries')

    @app.route('/visionadmin/users', methods=['GET'])
    @app.route('/visionadmin/admin-users', methods=['GET'])
    @app.route('/visonadmin/users', methods=['GET'])
    @app.route('/visonadmin/admin-users', methods=['GET'])
    @login_required_visionadmin
    def visionadmin_users():
        """Renders Admin Users Management Studio (Super Admin only)."""
        role_norm = str(session.get('role') or '').strip().lower().replace('-', '_').replace(' ', '_')
        if role_norm not in ('super_admin', 'superadmin') and session.get('role') != 'SuperAdmin':
            return render_template(
                '404.html',
                page='403',
                requested_path=request.path,
                user_name=session.get('name'),
                user_email=session.get('email'),
                user_role=session.get('role'),
                error_message='Super Administrator privileges required to manage VisionAdmin accounts.',
                unread_notifications=0,
                notifications=[]
            ), 403
        return render_template('visionadmin/users.html', page='users')

    @app.route('/visionadmin/scrapers', methods=['GET'])
    @app.route('/visionadmin/scraper', methods=['GET'])
    @app.route('/visionadmin/scraper-dashboard', methods=['GET'])
    @app.route('/visionadmin/files', methods=['GET'])
    @app.route('/visonadmin/scrapers', methods=['GET'])
    @app.route('/visonadmin/scraper', methods=['GET'])
    @app.route('/visonadmin/files', methods=['GET'])
    @login_required_visionadmin
    def visionadmin_scrapers():
        return redirect('/tcsadmin/files')

    @app.route('/visionadmin/reports', methods=['GET'])
    @app.route('/visonadmin/reports', methods=['GET'])
    @login_required_visionadmin
    def visionadmin_reports():
        return redirect('/tcsadmin/reports')
