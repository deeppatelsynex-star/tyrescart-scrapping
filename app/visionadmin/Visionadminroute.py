"""
app/visionadmin/Visionadminroute.py - VisionAdmin CMS Authentication & Studio Page Routes.

Serves the VisionAdmin HTML pages only (Pages/Blogs/Sections/Settings/Enquiries).
Protected by session-based authentication & role-based authorization (SuperAdmin, Admin).
"""

import functools
import re
import secrets
from flask import jsonify, redirect, render_template, request, session

from auth import (
    bit_to_bool,
    check_forgot_password_rate_limit,
    check_login_rate_limit,
    check_reset_password_rate_limit,
    clear_login_failures,
    create_password_reset_token,
    get_user_by_email,
    get_user_by_id,
    record_forgot_password_request,
    record_login_failure,
    record_reset_password_attempt,
    update_user_password,
    verify_and_consume_reset_token,
    verify_password,
)
from mailer import send_email

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def login_required_visionadmin(view):
    """Protects VisionAdmin page routes: requires authenticated SuperAdmin or Admin."""
    @functools.wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get('user_id')
        role = session.get('role')
        if not user_id:
            return redirect(f'/visionadmin/login?next={request.path}')
        if role not in ('SuperAdmin', 'Admin'):
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
    # 1. AUTHENTICATION & SESSION ROUTES
    # ========================================================================

    @app.route('/visionadmin/login', methods=['GET'])
    @app.route('/visonadmin/login', methods=['GET'])
    def visionadmin_login_page():
        """Renders the VisionAdmin login page or redirects if already signed in."""
        if 'user_id' in session and session.get('role') in ('SuperAdmin', 'Admin'):
            next_url = request.args.get('next') or '/visionadmin/pages'
            return redirect(next_url)
        return render_template('visionadmin/login.html')

    @app.route('/visionadmin/login', methods=['POST'])
    @app.route('/visonadmin/login', methods=['POST'])
    def visionadmin_login_submit():
        """Authenticates administrator with email & password."""
        data = request.get_json(silent=True) or request.form
        email = (data.get('email') or '').strip().lower()
        password = data.get('password') or ''
        remember = bool(data.get('remember'))

        if not email or not password:
            return jsonify({'error': 'Email and password are required.'}), 400

        is_locked, seconds_remaining, msg = check_login_rate_limit(email)
        if is_locked:
            return jsonify({'error': msg}), 429

        user = get_user_by_email(email)
        if not user or bit_to_bool(user['IsDeleted']) or not verify_password(password, user['password']):
            record_login_failure(email)
            return jsonify({'error': 'Invalid email or password.'}), 401

        if not bit_to_bool(user['Status']):
            return jsonify({'error': 'This account has been disabled. Contact an administrator.'}), 403

        if user.get('Role') not in ('SuperAdmin', 'Admin'):
            return jsonify({'error': 'Access denied. Administrator privileges required.'}), 403

        clear_login_failures(email)

        session.clear()
        session.permanent = remember
        session['sid'] = secrets.token_hex(16)
        session['user_id'] = user['userid']
        session['name'] = user['Name']
        session['email'] = user['Email']
        session['role'] = user['Role']
        session['csrf_token'] = secrets.token_hex(16)

        next_url = request.args.get('next') or '/visionadmin/pages'
        return jsonify({
            'success': True,
            'redirect': next_url,
            'user': {
                'id': user['userid'],
                'name': user['Name'],
                'email': user['Email'],
                'role': user['Role']
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
        """Handles password reset requests for VisionAdmin administrators."""
        if request.method == 'GET':
            return render_template('forgot_password.html')

        data = request.get_json(silent=True) or request.form or {}
        email = (data.get('email') or '').strip().lower()

        if not email or not EMAIL_RE.match(email):
            return jsonify({'error': 'Please enter a valid email address.'}), 400

        is_limited, seconds_remaining, msg = check_forgot_password_rate_limit(email)
        if is_limited:
            return jsonify({'error': msg}), 429

        record_forgot_password_request(email)

        user = get_user_by_email(email)
        if user and bit_to_bool(user.get('Status')) and not bit_to_bool(user.get('IsDeleted')):
            try:
                token = create_password_reset_token(user['userid'])
                reset_link = f"{request.host_url.rstrip('/')}/visionadmin/reset-password?token={token}"
                html_body = render_template(
                    'emails/reset_password.html',
                    user_name=user.get('Name') or 'there',
                    user_email=user.get('Email') or email,
                    reset_link=reset_link,
                    expires_minutes=30,
                )
                send_email(user['Email'], 'Reset your TyresVision Admin password', html_body)
            except Exception as e:
                app.logger.error(f'Error sending password reset email: {e}')
                return jsonify({'error': f'Failed to send email: {str(e)}'}), 500

        return jsonify({
            'success': True,
            'message': 'If an administrator account exists with that email, a password reset link has been sent.',
        })

    @app.route('/visionadmin/reset-password', methods=['GET', 'POST'])
    @app.route('/visonadmin/reset-password', methods=['GET', 'POST'])
    def visionadmin_reset_password():
        """Handles password reset token consumption for VisionAdmin administrators."""
        if request.method == 'GET':
            return render_template('reset_password.html')

        data = request.get_json(silent=True) or request.form or {}
        token = (data.get('token') or '').strip()
        new_password = data.get('new_password') or ''
        confirm_password = data.get('confirm_password') or ''

        is_limited, seconds_remaining, msg = check_reset_password_rate_limit()
        if is_limited:
            return jsonify({'error': msg}), 429

        record_reset_password_attempt()

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
            'message': 'Your password has been reset successfully. You can now sign in to VisionAdmin.',
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
