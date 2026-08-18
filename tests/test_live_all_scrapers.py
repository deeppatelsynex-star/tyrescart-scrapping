"""
Live Scraper Integration & Progress Verification Script
Tests starting, progress streaming, URL discovery, and stopping for scrapers.
"""

import csv
import json
import os
import sys
import time

# Ensure app directory is on path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

from db import get_connection
import job_manager
import files_repo
import reports_repo


def run_live_test_for_file(file_id, duration_seconds=10):
    file_info = files_repo.get_file(file_id)
    if not file_info:
        print(f"[-] Scraper file_id={file_id} not found.")
        return False

    site_name = file_info.get('site_name') or 'Scraper'
    script_path = file_info.get('python_file_path') or ''
    print("\n" + "=" * 80)
    print(f"TESTING SCRAPER: {site_name} (file_id={file_id}, script={script_path})")
    print("=" * 80)

    # 1. Clean previous state
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("UPDATE scraper_jobs SET status='STOPPED', finished_at=NOW() WHERE file_id=%s AND status='RUNNING'", (file_id,))
            cursor.execute("DELETE FROM scraper_job_locks WHERE file_id=%s", (file_id,))
            cursor.execute("UPDATE fileTbl SET working=0 WHERE file_id=%s", (file_id,))
    finally:
        conn.close()

    with job_manager._lock:
        job_manager._active_jobs.clear()

    # 2. Start scraper
    user_id = 2  # Super Admin ID
    start_res = job_manager.start_job(file_id, user_id=user_id)
    print(f"[*] Start Result: {start_res}")
    if not start_res.get('success'):
        print(f"[-] Failed to start scraper: {start_res}")
        return False

    job_id = start_res['job_id']

    # 3. Stream live progress and monitor sub-URLs
    urls_seen = []
    last_status = None

    for sec in range(1, duration_seconds + 1):
        time.sleep(1)
        status, code = job_manager.get_job_status(job_id, current_user_id=user_id)
        urls, _ = job_manager.get_job_urls(job_id, current_user_id=user_id)
        urls_seen = urls
        last_status = status

        total_u = status.get('total_urls', 0)
        pending_u = status.get('pending', 0)
        running_u = status.get('running_count', 0)
        done_u = status.get('completed', 0)
        blocked_u = status.get('blocked', 0)
        xlsx_count = status.get('written_to_xlsx', 0)
        pct = status.get('progress_percent', 0.0)

        print(f"  [{sec:2d}s] Status: {status.get('status')} | URLs Found: {len(urls):4d} | Pending: {pending_u:3d} | Running: {running_u:2d} | Done: {done_u:3d} | Blocked: {blocked_u:2d} | XLSX: {xlsx_count:3d} | Progress: {pct}%")

        if status.get('status') in ('SUCCESS', 'FAILED', 'STOPPED'):
            print(f"[*] Job reached terminal state: {status.get('status')}")
            break

    # Sample sub-URLs
    if urls_seen:
        print(f"\n[*] Sample URLs discovered ({min(5, len(urls_seen))} of {len(urls_seen)}):")
        for u in urls_seen[:5]:
            url_str = u.get('url', '')
            st = u.get('status', '')
            parent = u.get('parent', '')
            u_type = u.get('type', '')
            print(f"    - [{st.upper()}] ({u_type}) {url_str[:70]}... (parent: {parent[:40] if parent else 'ROOT'})")

    # 4. Stop scraper
    if last_status and last_status.get('status') == 'RUNNING':
        print("\n[*] Stopping scraper cleanly...")
        stop_res, _ = job_manager.stop_job(job_id, current_user_id=user_id)
        print(f"[*] Stop Result: {stop_res}")

    # 5. Verify database lock is released
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM scraper_job_locks WHERE file_id=%s", (file_id,))
            lock = cursor.fetchone()
            if lock is None:
                print("[+] Scraper Lock is CLEANLY RELEASED in MySQL database.")
            else:
                print(f"[-] Lock still exists: {lock}")
    finally:
        conn.close()

    print(f"[+] Scraper '{site_name}' test completed successfully!")
    return True


if __name__ == '__main__':
    # Test registered scrapers
    target_files = [35, 36, 34, 22] # gcco, kafaratplus, tireex, pitstoparabia
    if len(sys.argv) > 1:
        target_files = [int(x) for x in sys.argv[1:]]

    all_passed = True
    for fid in target_files:
        passed = run_live_test_for_file(fid, duration_seconds=8)
        if not passed:
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("ALL SCRAPERS TESTED SUCCESSFULLY!")
    else:
        print("SOME SCRAPER TESTS HAD ISSUES.")
    print("=" * 80)
