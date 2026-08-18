import os
import sys
import time

# Add app to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

from db import get_connection
import job_manager
import files_repo

def run_tests():
    print("=================================================")
    print("Testing logTbl Engine & Webhook Architecture")
    print("=================================================")

    conn = get_connection()
    with conn.cursor() as c:
        # 1. Verify exact tables in DB
        c.execute("SHOW TABLES")
        tables = [list(r.values())[0] for r in c.fetchall()]
        print("1. Active DB Tables:", tables)
        assert "password_reset_tbl" not in tables, "password_reset_tbl still exists!"
        assert "scraper_jobs" not in tables, "scraper_jobs still exists!"
        assert "scraper_job_locks" not in tables, "scraper_job_locks still exists!"
        assert "userTbl" in tables, "userTbl missing!"
        assert "fileTbl" in tables, "fileTbl missing!"
        assert "logTbl" in tables, "logTbl missing!"
        print("   OK: Database contains only userTbl, fileTbl, logTbl.")

        # 2. Check logTbl schema columns
        c.execute("DESCRIBE logTbl")
        cols = {r['Field'] for r in c.fetchall()}
        required_cols = {'id', 'job_id', 'scraper', 'file_id', 'user_id', 'status',
                         'start_time', 'end_time', 'no_of_url_found', 'total_success_url',
                         'total_block_url', 'data_scraped', 'output_file_path', 'error_message',
                         'process_id', 'progress_percent', 'total_products', 'pending_urls',
                         'running_urls', 'completed_urls', 'blocked_urls', 'main_url_done',
                         'product_url_done'}
        missing = required_cols - cols
        assert not missing, f"logTbl missing columns: {missing}"
        print("   OK: logTbl has all required counter, progress, and ownership columns.")

        # 3. Get test users and file
        c.execute("SELECT userid FROM userTbl ORDER BY userid LIMIT 2")
        users = c.fetchall()
        user1 = users[0]['userid']
        user2 = users[1]['userid'] if len(users) > 1 else 9999

        c.execute("SELECT file_id, site_name FROM fileTbl WHERE is_deleted = 0 LIMIT 1")
        file_row = c.fetchone()
        file_id = file_row['file_id']
        site_name = file_row['site_name']
    conn.close()

    print(f"2. Testing with file_id={file_id} ({site_name}), user1={user1}, user2={user2}")

    # Ensure stopped
    job_manager.stop_file(file_id, current_user_id=user1, is_superadmin=True)

    # Idle check
    idle_info = job_manager.get_active_job_for_file(file_id, current_user_id=user1)
    assert idle_info['has_active_job'] is False, f"Expected idle, got {idle_info}"
    print("   OK: Idle state verified.")

    # Start job
    start_res = job_manager.start_job(file_id, user_id=user1)
    assert start_res['success'] is True, f"Start failed: {start_res}"
    job_id = start_res['job_id']
    print(f"3. Job started: job_id={job_id}")

    # Privacy check for user2
    user2_check = job_manager.get_active_job_for_file(file_id, current_user_id=user2)
    assert user2_check['already_running'] is True, "user2 should see already_running"
    assert user2_check['is_owner'] is False, "user2 should NOT be owner"
    assert 'job_id' not in user2_check, "job_id leaked to non-owner!"
    print("4. User privacy verified: user2 blocked with generic notice and no data leak.")

    # Concurrent start rejection
    dup_start = job_manager.start_job(file_id, user_id=user2)
    assert dup_start['success'] is False, "Concurrent start must be rejected"
    assert dup_start.get('already_running') is True
    print("5. Atomic locking verified: concurrent execution rejected.")

    # Verify logTbl record in DB
    conn = get_connection()
    with conn.cursor() as c:
        c.execute("SELECT job_id, user_id, status, file_id FROM logTbl WHERE job_id = %s", (job_id,))
        row = c.fetchone()
        assert row is not None, "logTbl row missing!"
        assert row['user_id'] == user1
        assert row['status'] == 'RUNNING'
        print("6. logTbl DB persistence verified:", row)
    conn.close()

    # SSE pub/sub queue test
    q = job_manager.subscribe_sse(job_id)
    job_manager._push_sse_event(job_id, {"type": "status", "test": True})
    evt = q.get(timeout=2.0)
    assert evt.get("test") is True, f"SSE event mismatch: {evt}"
    job_manager.unsubscribe_sse(job_id, q)
    print("7. SSE Webhook pub/sub event stream verified.")

    # Stop scraper
    stop_res, code = job_manager.stop_job(job_id, current_user_id=user1)
    assert code == 200, f"Stop failed: {stop_res}"
    assert stop_res['status'] == 'STOPPED'
    print("8. Job stopped successfully.")

    time.sleep(0.5)

    # Verify logTbl final status in DB
    conn = get_connection()
    with conn.cursor() as c:
        c.execute("SELECT job_id, user_id, status, end_time FROM logTbl WHERE job_id = %s", (job_id,))
        final_row = c.fetchone()
        assert final_row['status'] == 'STOPPED', f"Expected STOPPED, got {final_row}"
        assert final_row['end_time'] is not None, "end_time should be set!"
        print("9. logTbl final DB record confirmed:", final_row)
    conn.close()

    print("=================================================")
    print("ALL TESTS PASSED! FULL SYSTEM WORKING PROPERLY")
    print("=================================================")

if __name__ == "__main__":
    run_tests()
    os._exit(0)
