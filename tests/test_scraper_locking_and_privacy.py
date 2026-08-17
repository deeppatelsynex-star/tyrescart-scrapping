"""Full Automated Test Suite for Scraper Locking, Multi-User Isolation,
MySQL Trigger Locking, Process Safety, API Security, and Privacy Protection.

Run using:
    venv\\Scripts\\python.exe tests/test_scraper_locking_and_privacy.py
or
    venv\\Scripts\\pytest tests/test_scraper_locking_and_privacy.py
"""

import json
import os
import sys
import time
import unittest
from datetime import datetime, timezone

# Anchor to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(BASE_DIR, 'app'))

from app import app
from db import get_connection
import files_repo
import job_manager
import reports_repo


class TestScraperLockingAndPrivacy(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.file_id = 35
        cls.user_a_id = 51
        cls.user_a_email = "usera@example.com"
        cls.user_b_id = 52
        cls.user_b_email = "userb@example.com"

        app.config['TESTING'] = True
        app.config['SECRET_KEY'] = 'test-secret-key-12345'
        cls.client = app.test_client()

    def setUp(self):
        """Clean up active locks and running jobs before each test."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM scraper_jobs WHERE job_id LIKE 'test_%'")
                cursor.execute("""
                    UPDATE scraper_jobs
                    SET status = 'STOPPED', finished_at = NOW()
                    WHERE file_id = %s AND status = 'RUNNING'
                """, (self.file_id,))
                cursor.execute("DELETE FROM scraper_job_locks WHERE file_id = %s", (self.file_id,))
        finally:
            conn.close()

        with job_manager._lock:
            job_manager._active_jobs.clear()

    def tearDown(self):
        """Clean up any spawned jobs after each test."""
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM scraper_jobs WHERE job_id LIKE 'test_%'")
                cursor.execute("""
                    UPDATE scraper_jobs
                    SET status = 'STOPPED', finished_at = NOW()
                    WHERE file_id = %s AND status = 'RUNNING'
                """, (self.file_id,))
                cursor.execute("DELETE FROM scraper_job_locks WHERE file_id = %s", (self.file_id,))
        finally:
            conn.close()

        with job_manager._lock:
            for job_id, state in list(job_manager._active_jobs.items()):
                proc = state.get('process')
                if proc:
                    job_manager._kill_process_tree(proc, force=True)
            job_manager._active_jobs.clear()

    # ==========================================================================
    # TEST 1: Direct MySQL Trigger Lock Acquisition and Release
    # ==========================================================================
    def test_01_mysql_trigger_lock_and_release(self):
        """Validates that MySQL before_scraper_job_insert acquires the lock and
        after_scraper_job_update releases it automatically."""
        test_job_id = "test_trigger_01"
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                # 1. Insert RUNNING job -> trigger acquires lock in scraper_job_locks
                cursor.execute("""
                    INSERT INTO scraper_jobs (job_id, file_id, started_by_user_id, status, started_at)
                    VALUES (%s, %s, %s, 'RUNNING', NOW())
                """, (test_job_id, self.file_id, self.user_a_id))

                cursor.execute("SELECT * FROM scraper_job_locks WHERE file_id = %s", (self.file_id,))
                lock = cursor.fetchone()
                self.assertIsNotNone(lock, "Lock must be created in scraper_job_locks")
                self.assertEqual(lock['job_id'], test_job_id)
                self.assertEqual(lock['started_by_user_id'], self.user_a_id)

                # 2. Attempt duplicate insert with status='RUNNING' -> MySQL 1062 Integrity Error
                with self.assertRaises(Exception):
                    cursor.execute("""
                        INSERT INTO scraper_jobs (job_id, file_id, started_by_user_id, status, started_at)
                        VALUES (%s, %s, %s, 'RUNNING', NOW())
                    """, ("test_trigger_dup", self.file_id, self.user_b_id))

                # 3. Update job to STOPPED with finished_at -> trigger deletes lock
                cursor.execute("""
                    UPDATE scraper_jobs
                    SET status = 'STOPPED', finished_at = NOW()
                    WHERE job_id = %s
                """, (test_job_id,))

                cursor.execute("SELECT * FROM scraper_job_locks WHERE file_id = %s", (self.file_id,))
                lock_after = cursor.fetchone()
                self.assertIsNone(lock_after, "Lock must be deleted after job finishes")
        finally:
            conn.close()

    # ==========================================================================
    # TEST 2: Two-User End-to-End Execution and Ownership Privacy
    # ==========================================================================
    def test_02_two_user_isolation_and_privacy(self):
        """Validates that User A starts the scraper and User B is blocked, receives
        409 on duplicate start, 403 on monitoring endpoints, and no information is leaked."""
        client_a = app.test_client()
        client_b = app.test_client()

        # Setup User A session
        with client_a.session_transaction() as sess:
            sess['user_id'] = self.user_a_id
            sess['role'] = 'User'
            sess['email'] = self.user_a_email
            sess['csrf_token'] = 'token-a-123'

        # Setup User B session
        with client_b.session_transaction() as sess:
            sess['user_id'] = self.user_b_id
            sess['role'] = 'User'
            sess['email'] = self.user_b_email
            sess['csrf_token'] = 'token-b-456'

        # 1. User A starts scraper
        res_a_start = client_a.post(
            '/api/scraper/start',
            data=json.dumps({'file_id': self.file_id}),
            headers={'X-CSRF-Token': 'token-a-123', 'Content-Type': 'application/json'}
        )
        self.assertEqual(res_a_start.status_code, 200)
        data_a_start = res_a_start.get_json()
        self.assertTrue(data_a_start['success'])
        self.assertTrue(data_a_start['is_owner'])
        job_id_a = data_a_start['job_id']
        self.assertIsNotNone(job_id_a)

        # Allow worker thread to spin up
        time.sleep(1)

        # 2. User B queries active-job status
        res_b_active = client_b.get(f'/api/scraper/file/{self.file_id}/active-job')
        self.assertEqual(res_b_active.status_code, 200)
        data_b_active = res_b_active.get_json()

        self.assertTrue(data_b_active['has_active_job'])
        self.assertTrue(data_b_active['already_running'])
        self.assertFalse(data_b_active['is_owner'])
        self.assertEqual(data_b_active['status'], 'RUNNING')
        self.assertEqual(data_b_active['message'], 'This scraper is currently being used by another user.')

        # CRITICAL PRIVACY CHECK: User B must NEVER receive User A's execution details
        self.assertNotIn('job_id', data_b_active, "Job ID must not be leaked to User B")
        self.assertNotIn('process_id', data_b_active, "Process ID must not be leaked to User B")
        self.assertNotIn('started_by_user_id', data_b_active, "Owner user ID must not be leaked to User B")
        self.assertNotIn('progress_percent', data_b_active, "Progress must not be leaked to User B")
        self.assertNotIn('urls', data_b_active, "URLs must not be leaked to User B")

        # 3. User B attempts to start the same scraper -> HTTP 409 Conflict
        res_b_start = client_b.post(
            '/api/scraper/start',
            data=json.dumps({'file_id': self.file_id}),
            headers={'X-CSRF-Token': 'token-b-456', 'Content-Type': 'application/json'}
        )
        self.assertEqual(res_b_start.status_code, 409)
        data_b_start = res_b_start.get_json()
        self.assertFalse(data_b_start['success'])
        self.assertTrue(data_b_start['already_running'])
        self.assertFalse(data_b_start['is_owner'])
        self.assertEqual(data_b_start['message'], 'This scraper is currently being used by another user.')

        # 4. User B attempts to query User A's job status and URLs -> HTTP 403 Forbidden
        res_b_status = client_b.get(f'/api/scraper/job/{job_id_a}/status')
        self.assertEqual(res_b_status.status_code, 403)
        self.assertFalse(res_b_status.get_json().get('success', True))

        res_b_urls = client_b.get(f'/api/scraper/job/{job_id_a}/urls')
        self.assertEqual(res_b_urls.status_code, 403)

        # 5. User B attempts to Stop User A's scraper -> HTTP 403 Forbidden
        res_b_stop = client_b.post(
            f'/api/scraper/job/{job_id_a}/stop',
            headers={'X-CSRF-Token': 'token-b-456'}
        )
        self.assertEqual(res_b_stop.status_code, 403)

        # 6. User A checks own live progress -> HTTP 200 OK with live metrics
        res_a_status = client_a.get(f'/api/scraper/job/{job_id_a}/status')
        self.assertEqual(res_a_status.status_code, 200)
        data_a_status = res_a_status.get_json()
        self.assertEqual(data_a_status['status'], 'RUNNING')
        self.assertTrue(data_a_status['running'])
        self.assertIn('progress_percent', data_a_status)

        # 7. User A stops own scraper -> HTTP 200 OK and lock is deleted
        res_a_stop = client_a.post(
            f'/api/scraper/job/{job_id_a}/stop',
            headers={'X-CSRF-Token': 'token-a-123'}
        )
        self.assertEqual(res_a_stop.status_code, 200)
        self.assertEqual(res_a_stop.get_json()['status'], 'STOPPED')

        # Verify lock is removed in database
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM scraper_job_locks WHERE file_id = %s", (self.file_id,))
                lock = cursor.fetchone()
                self.assertIsNone(lock, "Lock must be released after owner stops job")
        finally:
            conn.close()

        # 8. User B now checks active job -> returns IDLE (available to run)
        res_b_active_after = client_b.get(f'/api/scraper/file/{self.file_id}/active-job')
        self.assertEqual(res_b_active_after.status_code, 200)
        self.assertFalse(res_b_active_after.get_json()['has_active_job'])

        # 9. User B starts the scraper -> Successfully acquires lock as new owner
        res_b_new_start = client_b.post(
            '/api/scraper/start',
            data=json.dumps({'file_id': self.file_id}),
            headers={'X-CSRF-Token': 'token-b-456', 'Content-Type': 'application/json'}
        )
        self.assertEqual(res_b_new_start.status_code, 200)
        data_b_new = res_b_new_start.get_json()
        self.assertTrue(data_b_new['success'])
        self.assertTrue(data_b_new['is_owner'])
        job_id_b = data_b_new['job_id']
        self.assertNotEqual(job_id_a, job_id_b)

        # Clean up User B's job
        client_b.post(f'/api/scraper/job/{job_id_b}/stop', headers={'X-CSRF-Token': 'token-b-456'})

    # ==========================================================================
    # TEST 3: Audit Log (logTbl) Synchronization on Completion
    # ==========================================================================
    def test_03_audit_log_synchronization(self):
        """Validates that logTbl status and duration are properly synchronized
        and never displayed as 'Running...' once stopped."""
        client = app.test_client()
        with client.session_transaction() as sess:
            sess['user_id'] = self.user_a_id
            sess['role'] = 'User'
            sess['email'] = self.user_a_email
            sess['csrf_token'] = 'token-a-123'

        # Start and immediately stop
        res_start = client.post(
            '/api/scraper/start',
            data=json.dumps({'file_id': self.file_id}),
            headers={'X-CSRF-Token': 'token-a-123', 'Content-Type': 'application/json'}
        )
        self.assertEqual(res_start.status_code, 200)
        job_id = res_start.get_json()['job_id']

        time.sleep(1)

        res_stop = client.post(f'/api/scraper/job/{job_id}/stop', headers={'X-CSRF-Token': 'token-a-123'})
        self.assertEqual(res_stop.status_code, 200)

        # Check logTbl record
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM logTbl 
                    WHERE file_id = %s 
                    ORDER BY id DESC LIMIT 1
                """, (self.file_id,))
                log_entry = cursor.fetchone()
                self.assertIsNotNone(log_entry)
                self.assertEqual(log_entry['status'], 'STOPPED')
                self.assertIsNotNone(log_entry['end_time'])

                serialized = reports_repo.serialize_log(log_entry)
                self.assertEqual(serialized['status'], 'STOPPED')
                self.assertNotEqual(serialized['duration'], 'Running...', "Duration must not be 'Running...' once stopped")
        finally:
            conn.close()

    # ==========================================================================
    # TEST 4: Fault Tolerance on Script Launch Failure
    # ==========================================================================
    def test_04_fault_tolerance_failed_script_releases_lock(self):
        """Validates that if a scraper script fails to launch, the lock is instantly freed."""
        # Create a dummy bad file record
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO fileTbl (site_name, python_file_path, urls_json, working)
                    VALUES ('BadScraper', 'non_existent_script.py', '[]', 0)
                """)
                bad_file_id = cursor.lastrowid
        finally:
            conn.close()

        try:
            result = job_manager.start_job(bad_file_id, user_id=self.user_a_id)
            self.assertFalse(result['success'])

            # Verify no orphaned lock
            conn = get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM scraper_job_locks WHERE file_id = %s", (bad_file_id,))
                    lock = cursor.fetchone()
                    self.assertIsNone(lock, "No lock should remain when script resolution fails")
            finally:
                conn.close()
        finally:
            conn = get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("DELETE FROM fileTbl WHERE file_id = %s", (bad_file_id,))
            finally:
                conn.close()


def run_full_suite():
    print("=" * 80)
    print("RUNNING FULL TEST SUITE: SCRAPER LOCKS, TRIGGERS & MULTI-USER PRIVACY")
    print("=" * 80)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestScraperLockingAndPrivacy)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        print("\n" + "=" * 80)
        print("ALL TESTS PASSED WITH 100% SUCCESS!")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("SOME TESTS FAILED.")
        print("=" * 80)
        sys.exit(1)


if __name__ == '__main__':
    run_full_suite()
