"""
app/visionadmin/Visionadminroute.py - VisionAdmin CMS Authentication & Studio Page Routes.

Serves the VisionAdmin HTML pages only (Pages/Blogs/Sections/Settings/Enquiries).
Protected by session-based authentication & role-based authorization (SuperAdmin, Admin).
"""

import functools
import secrets
from flask import jsonify, redirect, render_template, request, session

from auth import bit_to_bool, get_user_by_email, verify_password


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

        user = get_user_by_email(email)
        if not user or bit_to_bool(user['IsDeleted']) or not verify_password(password, user['password']):
            return jsonify({'error': 'Invalid email or password.'}), 401

        if not bit_to_bool(user['Status']):
            return jsonify({'error': 'This account has been disabled. Contact an administrator.'}), 403

        if user.get('Role') not in ('SuperAdmin', 'Admin'):
            return jsonify({'error': 'Access denied. Administrator privileges required.'}), 403

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
