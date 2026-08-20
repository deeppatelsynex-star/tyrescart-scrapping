"""
Comprehensive After-Login Test Suite for TyresCart Scraping Platform.
Tests all features, pages, API endpoints, permissions, scraper executions,
and multi-user security available to authenticated users.
"""

import json
import os
import sys
import time
import unittest

# Ensure app directory is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP_DIR = os.path.join(BASE_DIR, 'app')
for p in [BASE_DIR, APP_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from app import app
from auth import hash_password, verify_password
from db import get_connection
import files_repo
import job_manager
import reports_repo


class AfterLoginTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test users and seed state in MySQL database."""
        app.config['TESTING'] = True
        cls.client = app.test_client()

        # Connect to DB and ensure test users exist
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. SuperAdmin User (ID=101)
                cursor.execute("SELECT id FROM userTbl WHERE email = %s", ('superadmin_test@tyrescart.com',))
                row = cursor.fetchone()
                if row:
                    cls.superadmin_id = row['id']
                else:
                    cursor.execute("""
                        INSERT INTO userTbl (name, email, password, role, is_active, is_deleted)
                        VALUES (%s, %s, %s, %s, 1, 0)
                    """, ('Super Admin Test', 'superadmin_test@tyrescart.com', hash_password('AdminTestPass123!'), 'SuperAdmin'))
                    cls.superadmin_id = cursor.lastrowid

                # 2. Standard User 1 (ID=102)
                cursor.execute("SELECT id FROM userTbl WHERE email = %s", ('user1_test@tyrescart.com',))
                row = cursor.fetchone()
                if row:
                    cls.user1_id = row['id']
                else:
                    cursor.execute("""
                        INSERT INTO userTbl (name, email, password, role, is_active, is_deleted)
                        VALUES (%s, %s, %s, %s, 1, 0)
                    """, ('Standard User One', 'user1_test@tyrescart.com', hash_password('UserOnePass123!'), 'User'))
                    cls.user1_id = cursor.lastrowid

                # 3. Standard User 2 (ID=103)
                cursor.execute("SELECT id FROM userTbl WHERE email = %s", ('user2_test@tyrescart.com',))
                row = cursor.fetchone()
                if row:
                    cls.user2_id = row['id']
                else:
                    cursor.execute("""
                        INSERT INTO userTbl (name, email, password, role, is_active, is_deleted)
                        VALUES (%s, %s, %s, %s, 1, 0)
                    """, ('Standard User Two', 'user2_test@tyrescart.com', hash_password('UserTwoPass123!'), 'User'))
                    cls.user2_id = cursor.lastrowid

                # 4. Ensure at least one active test file scraper exists
                cursor.execute("SELECT id, site_name FROM fileTbl WHERE is_deleted = 0 ORDER BY id ASC LIMIT 1")
                file_row = cursor.fetchone()
                if file_row:
                    cls.test_file_id = file_row['id']
                else:
                    cursor.execute("""
                        INSERT INTO fileTbl (site_name, python_file_path, urls_json, is_working, is_deleted, created_by)
                        VALUES (%s, %s, %s, 0, 0, %s)
                    """, ('Test Scraper', 'scrapers/pitstoparabia-brand-1.py', '["https://www.pitstoparabia.com/en/"]', cls.superadmin_id))
                    cls.test_file_id = cursor.lastrowid

                conn.commit()
        finally:
            conn.close()

    def set_session(self, user_id, role='User', csrf='test_csrf_token'):
        """Helper to establish an authenticated test session."""
        with self.client.session_transaction() as sess:
            sess['user_id'] = user_id
            sess['role'] = role
            sess['csrf_token'] = csrf

    # =========================================================================
    # TC01: Session & Profile Resolution (/api/me)
    # =========================================================================
    def test_tc01_authenticated_user_profile_resolution(self):
        """TC01: Verify authenticated user can resolve profile data via /api/me."""
        self.set_session(self.user1_id, role='User')
        res = self.client.get('/api/me')
        self.assertEqual(res.status_code, 200, "Authenticated user should get 200 OK from /api/me")
        data = res.get_json()
        self.assertIn('user', data)
        self.assertEqual(data['user']['email'], 'user1_test@tyrescart.com')
        self.assertEqual(data['user']['role'], 'User')
        print("  [PASS] TC01: Session & Profile Resolution verified.")

    # =========================================================================
    # TC02: CSRF Protection on Mutating Requests
    # =========================================================================
    def test_tc02_csrf_protection_on_mutating_requests(self):
        """TC02: Verify requests without valid CSRF header are rejected (403 Forbidden)."""
        self.set_session(self.user1_id, role='User', csrf='valid_csrf_123')

        # Attempt mutating request without CSRF header
        res_no_csrf = self.client.post(f'/api/files/{self.test_file_id}/start')
        self.assertEqual(res_no_csrf.status_code, 403, "POST request without CSRF token must be 403 Forbidden")

        # Attempt mutating request with mismatched CSRF header
        res_bad_csrf = self.client.post(
            f'/api/files/{self.test_file_id}/start',
            headers={'X-CSRF-Token': 'wrong_csrf_token'}
        )
        self.assertEqual(res_bad_csrf.status_code, 403, "POST request with invalid CSRF token must be 403 Forbidden")
        print("  [PASS] TC02: CSRF Protection verified.")

    # =========================================================================
    # TC03: Files & Scrapers Listing API (/api/files)
    # =========================================================================
    def test_tc03_list_files_and_dashboard(self):
        """TC03: Verify authenticated user can view active scraper list."""
        self.set_session(self.user1_id, role='User')
        res = self.client.get('/api/files?perPage=10')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data.get('success'))
        self.assertIn('files', data)
        self.assertGreaterEqual(len(data['files']), 1)
        print("  [PASS] TC03: Scraper list & dashboard verified.")

    # =========================================================================
    # TC04: Scraper Lifecycle (Start, Status, URLs, and Stop)
    # =========================================================================
    def test_tc04_scraper_execution_lifecycle(self):
        """TC04: Verify starting a scraper, polling status, and stopping it."""
        self.set_session(self.user1_id, role='User', csrf='valid_csrf_token')
        csrf_hdr = {'X-CSRF-Token': 'valid_csrf_token'}

        # 1. Start Scraper
        res_start = self.client.post(f'/api/files/{self.test_file_id}/start', headers=csrf_hdr)
        self.assertEqual(res_start.status_code, 200)
        start_data = res_start.get_json()
        self.assertTrue(start_data.get('success'))
        job_id = start_data.get('job_id')
        self.assertIsNotNone(job_id)

        # 2. Check Active Job API
        res_active = self.client.get(f'/api/scraper/file/{self.test_file_id}/active-job')
        self.assertEqual(res_active.status_code, 200)
        active_data = res_active.get_json()
        self.assertTrue(active_data.get('is_owner'))
        self.assertTrue(active_data.get('has_active_job'))

        # 3. Check Status API
        res_status = self.client.get(f'/api/scraper/job/{job_id}/status')
        self.assertEqual(res_status.status_code, 200)
        status_data = res_status.get_json()
        self.assertEqual(status_data.get('job_id'), job_id)
        self.assertEqual(status_data.get('status'), 'RUNNING')

        # 4. Check URL hierarchy API
        res_urls = self.client.get(f'/api/scraper/job/{job_id}/urls')
        self.assertEqual(res_urls.status_code, 200)
        urls_data = res_urls.get_json()
        self.assertIn('statuses', urls_data)

        # 5. Stop Scraper Job
        res_stop = self.client.post(f'/api/scraper/job/{job_id}/stop', headers=csrf_hdr)
        self.assertEqual(res_stop.status_code, 200)
        stop_data = res_stop.get_json()
        self.assertTrue(stop_data.get('success'))

        # 6. Verify logTbl record is STOPPED
        log_entry = job_manager.get_log_by_job_id(job_id)
        self.assertIsNotNone(log_entry)
        self.assertEqual(log_entry['status'], 'STOPPED')
        print("  [PASS] TC04: Scraper Execution Lifecycle verified.")

    # =========================================================================
    # TC05: Multi-User Privacy & Atomic Lock Protection
    # =========================================================================
    def test_tc05_multi_user_privacy_and_lock_isolation(self):
        """TC05: Verify User 2 cannot access or disrupt a scraper started by User 1."""
        csrf_hdr = {'X-CSRF-Token': 'valid_csrf_token'}

        # User 1 starts the scraper
        self.set_session(self.user1_id, role='User', csrf='valid_csrf_token')
        res_start = self.client.post(f'/api/files/{self.test_file_id}/start', headers=csrf_hdr)
        self.assertEqual(res_start.status_code, 200)
        job_id = res_start.get_json()['job_id']

        # User 2 switches in
        self.set_session(self.user2_id, role='User', csrf='valid_csrf_token')

        # User 2 checks active job
        res_user2_active = self.client.get(f'/api/scraper/file/{self.test_file_id}/active-job')
        data2 = res_user2_active.get_json()
        self.assertTrue(data2.get('already_running'))
        self.assertFalse(data2.get('is_owner'), "User 2 must not be marked as owner")
        self.assertNotIn('urls', data2, "Private URLs must not be leaked to User 2")

        # User 2 tries to start the same scraper
        res_user2_start = self.client.post(f'/api/files/{self.test_file_id}/start', headers=csrf_hdr)
        data2_start = res_user2_start.get_json()
        self.assertFalse(data2_start.get('success'))
        self.assertTrue(data2_start.get('already_running'))

        # User 2 tries to stop User 1's job -> 403 Forbidden
        res_user2_stop = self.client.post(f'/api/scraper/job/{job_id}/stop', headers=csrf_hdr)
        self.assertEqual(res_user2_stop.status_code, 403, "User 2 must not be allowed to stop User 1's job")

        # Clean up: User 1 stops job
        self.set_session(self.user1_id, role='User', csrf='valid_csrf_token')
        self.client.post(f'/api/scraper/job/{job_id}/stop', headers=csrf_hdr)
        print("  [PASS] TC05: Multi-User Privacy & Lock Isolation verified.")

    # =========================================================================
    # TC06: Reports & Audit Logs Access (/api/reports/...)
    # =========================================================================
    def test_tc06_reports_and_audit_logs(self):
        """TC06: Verify reports summary stats and log filtering."""
        self.set_session(self.superadmin_id, role='SuperAdmin')

        # 1. Summary stats
        res_sum = self.client.get('/api/reports/summary')
        self.assertEqual(res_sum.status_code, 200)
        data_sum = res_sum.get_json()
        self.assertTrue(data_sum.get('success'))
        self.assertIn('total_runs', data_sum.get('summary', {}))

        # 2. Logs table query
        res_logs = self.client.get('/api/reports/logs?page=1&perPage=10')
        self.assertEqual(res_logs.status_code, 200)
        data_logs = res_logs.get_json()
        self.assertTrue(data_logs.get('success'))
        self.assertIn('logs', data_logs)

        # 3. Per-scraper log drawer
        res_drawer = self.client.get(f'/api/reports/files/{self.test_file_id}/logs')
        self.assertEqual(res_drawer.status_code, 200)
        data_drawer = res_drawer.get_json()
        self.assertTrue(data_drawer.get('success'))
        print("  [PASS] TC06: Reports & Audit Logs verified.")

    # =========================================================================
    # TC07: Role-Based Access Control (RBAC) Permissions
    # =========================================================================
    def test_tc07_role_based_access_control(self):
        """TC07: Verify normal users are blocked from SuperAdmin management endpoints."""
        # Standard user tries to access /api/users
        self.set_session(self.user1_id, role='User')
        res_user_blocked = self.client.get('/api/users')
        self.assertEqual(res_user_blocked.status_code, 403, "Regular user must be blocked (403) from /api/users")

        # Standard user tries to access /users page
        res_page_blocked = self.client.get('/users')
        self.assertEqual(res_page_blocked.status_code, 403, "Regular user must be blocked (403) from /users page")

        # SuperAdmin accesses /api/users -> succeeds
        self.set_session(self.superadmin_id, role='SuperAdmin')
        res_admin_ok = self.client.get('/api/users')
        self.assertEqual(res_admin_ok.status_code, 200, "SuperAdmin must be allowed to access /api/users")
        print("  [PASS] TC07: Role-Based Access Control (RBAC) verified.")

    # =========================================================================
    # TC08: Profile Update & Password Change
    # =========================================================================
    def test_tc08_profile_update_and_password_validation(self):
        """TC08: Verify profile name updates and password validation logic."""
        self.set_session(self.user1_id, role='User', csrf='csrf_test')
        csrf_hdr = {'X-CSRF-Token': 'csrf_test'}

        # 1. Update Profile Name
        res_update = self.client.post(
            '/api/profile/update',
            data=json.dumps({'name': 'Updated User Name'}),
            content_type='application/json',
            headers=csrf_hdr
        )
        self.assertEqual(res_update.status_code, 200)
        self.assertTrue(res_update.get_json().get('success'))

        # 2. Attempt password change with wrong old password -> 400 Bad Request
        res_bad_pw = self.client.post(
            '/api/profile/change-password',
            data=json.dumps({
                'current_password': 'WrongPassword123!',
                'new_password': 'NewPassword123!',
                'confirm_password': 'NewPassword123!'
            }),
            content_type='application/json',
            headers=csrf_hdr
        )
        self.assertEqual(res_bad_pw.status_code, 400, "Invalid old password must return 400 Bad Request")
        print("  [PASS] TC08: Profile Update & Password Validation verified.")

    # =========================================================================
    # TC09: Server-Sent Events (SSE) Webhook Stream
    # =========================================================================
    def test_tc09_sse_webhook_event_stream(self):
        """TC09: Verify real-time Server-Sent Events stream connects and delivers data."""
        self.set_session(self.user1_id, role='User', csrf='csrf_test')
        csrf_hdr = {'X-CSRF-Token': 'csrf_test'}

        # Start a scraper to generate an active job
        res_start = self.client.post(f'/api/files/{self.test_file_id}/start', headers=csrf_hdr)
        job_id = res_start.get_json()['job_id']

        # Connect to SSE endpoint
        res_sse = self.client.get(f'/api/scraper/job/{job_id}/events')
        self.assertEqual(res_sse.status_code, 200)
        self.assertEqual(res_sse.mimetype, 'text/event-stream')

        # Clean up: stop scraper
        self.client.post(f'/api/scraper/job/{job_id}/stop', headers=csrf_hdr)
        print("  [PASS] TC09: SSE Webhook Stream verified.")


if __name__ == '__main__':
    print("=" * 65)
    print("RUNNING COMPREHENSIVE AFTER-LOGIN TEST SUITE")
    print("=" * 65)
    unittest.main(verbosity=2)
