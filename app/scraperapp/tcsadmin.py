"""
app/scraperapp/tcsadmin.py - Scraper admin ("tcsadmin") page routes.

Serves the tcsadmin HTML pages (login, dashboard, files, reports, admin,
trash, docs) plus the auth/session endpoints (login/logout/password reset)
that sit alongside them. The JSON API endpoints that back these pages
(/tcsadmin/api/*) live in the unified app/api.py alongside the visionadmin
and public client APIs.
"""

import re
import secrets
import threading
import time

from flask import jsonify, redirect, render_template, request, session

import job_manager
from auth import (
    bit_to_bool,
    check_forgot_password_rate_limit,
    check_login_rate_limit,
    check_reset_password_rate_limit,
    clear_login_failures,
    create_password_reset_token,
    get_client_ip,
    get_user_by_email,
    get_user_by_id,
    login_required_page,
    record_forgot_password_request,
    record_login_failure,
    record_reset_password_attempt,
    role_required_page,
    update_user_password,
    verify_and_consume_reset_token,
    verify_password,
)
from db import get_connection
from mailer import send_email

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def register_tcsadmin_routes(app):
    """Registers all /tcsadmin page and auth/session routes."""

    # ========================================================================
    # 1. SCRAPER ADMIN PAGE ROUTES
    # Base URL: https://tyrescart-scrapping.klever.ae/tcsadmin/
    # ========================================================================

    @app.route('/tcsadmin/login', methods=['GET'])
    @app.route('/tcsadmin', methods=['GET'])
    @app.route('/tcsadmin/', methods=['GET'])
    @app.route('/login', methods=['GET'])
    def login_page():
        user_id = session.get('admin_user_id') or session.get('user_id')
        if user_id:
            return redirect('/tcsadmin/files')
        return redirect('/visionadmin/login?next=/tcsadmin/files')

    @app.route('/tcsadmin/docs/scraper')
    @app.route('/tcsadmin/scrapers')
    @app.route('/tcsadmin/scraper')
    @app.route('/tcsadmin/files')
    @app.route('/files')
    @login_required_page
    def files_page():
        return render_template('files.html', page='files')

    @app.route('/tcsadmin/scraperpage')
    @login_required_page
    def Scrap():
        file_id = request.args.get('fileId')
        if not file_id:
            user_id = session.get('admin_user_id') or session.get('user_id')
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
    @role_required_page('SuperAdmin', 'super_admin')
    def reports_page():
        return render_template('reports.html', page='reports')

    @app.route('/tcsadmin/Admin')
    @login_required_page
    @role_required_page('SuperAdmin', 'super_admin', 'Admin', 'manager')
    def admin_page():
        return redirect('/visionadmin/users')

    @app.route('/tcsadmin/trash')
    @login_required_page
    @role_required_page('SuperAdmin', 'super_admin', 'Admin', 'manager')
    def trash_page():
        return redirect('/visionadmin/users')

    @app.route('/tcsadmin/docs/guide')
    @app.route('/tcsadmin/docs/scraper-guide')
    @login_required_page
    def scraper_guide_page():
        return render_template('scraper_guide.html', page='docs')

    # ========================================================================
    # 2. AUTHENTICATION & PASSWORD RESET ENDPOINTS (UNIFIED WITH VISIONADMIN)
    # ========================================================================

    @app.route('/tcsadmin/login', methods=['POST'])
    @app.route('/tcsadmin', methods=['POST'])
    @app.route('/login', methods=['POST'])
    def login_submit():
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
        if not user or not verify_password(password, user['password']):
            record_login_failure(email)
            return jsonify({'error': 'Invalid email or password.'}), 401

        if not user.get('is_active', 1) and not user.get('Status', 1):
            return jsonify({'error': 'This account has been disabled. Contact an administrator.'}), 403

        clear_login_failures(email)

        session.clear()
        session.permanent = remember
        session['sid'] = secrets.token_hex(16)
        session['admin_user_id'] = user['id']
        session['user_id'] = user['id']
        session['userid'] = user['id']
        session['id'] = user['id']
        session['name'] = user['name']
        session['Name'] = user['name']
        session['email'] = user['email']
        session['Email'] = user['email']
        session['role'] = 'SuperAdmin' if user['role'] in ('super_admin', 'superadmin', 'SuperAdmin') else ('Admin' if user['role'] in ('manager', 'admin', 'Admin') else 'User')
        session['admin_role'] = user['role']
        session['csrf_token'] = secrets.token_hex(16)
        session['is_visionadmin'] = True
        session['logged_in'] = True

        return jsonify({'redirect': '/tcsadmin/files'})

    @app.route('/tcsadmin/logout', methods=['GET', 'POST'])
    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        session.clear()
        if request.method == 'GET' or not (request.is_json or (request.headers.get('Accept') and 'application/json' in request.headers.get('Accept'))):
            return redirect('/visionadmin/login')
        return jsonify({'redirect': '/visionadmin/login'})

    @app.route('/tcsadmin/forgot-password', methods=['GET', 'POST'])
    @app.route('/forgot-password', methods=['GET', 'POST'])
    def forgot_password_page():
        return redirect('/visionadmin/forgot-password')

    @app.route('/tcsadmin/reset-password', methods=['GET', 'POST'])
    @app.route('/reset-password', methods=['GET', 'POST'])
    def reset_password_page():
        token = request.args.get('token', '')
        return redirect(f'/visionadmin/reset-password?token={token}' if token else '/visionadmin/forgot-password')

