"""Centralized Scraper Execution Engine using scraper_jobs + scraper_job_locks Table & Triggers.

Architectural Guarantees:
1. GLOBAL SCRAPER LOCK:
   - Lock table `scraper_job_locks` with PRIMARY KEY (file_id) ensures exactly 1 active execution globally.
   - MySQL trigger `before_scraper_job_insert` acquires the lock automatically when status='RUNNING' and finished_at IS NULL.
   - Duplicate starts fail at the database level with code 1062 duplicate key error.
2. USER-OWNED EXECUTION & PRIVACY:
   - The user who started the scraper is the designated OWNER (started_by_user_id).
   - Only the owner can view live counters, progress, logs, URLs, and Stop button.
   - Non-owners receive ONLY:
     {"already_running": true, "is_owner": false, "message": "This scraper is currently being used by another user."}
   - No job_id, process_id, logs, timestamps, or usernames are ever leaked to non-owners.
3. LOCK RELEASE & LIFECYCLE:
   - MySQL trigger `after_scraper_job_update` automatically deletes the lock when status IN ('SUCCESS', 'FAILED', 'STOPPED') and finished_at IS NOT NULL.
   - 6-Hour Timeout Watchdog and Dead Process Recovery ensure dead jobs never keep the lock.
"""

import csv
import json
import logging
import os
import signal
import subprocess
import sys
import threading
import time
import uuid
from collections import OrderedDict
from datetime import datetime, timezone

import psutil
import pymysql

from db import get_connection
import files_repo
import reports_repo
from scraper_status_utils import parse_status_line

logger = logging.getLogger(__name__)

BASE_DIR = files_repo.BASE_DIR
TMP_DIR = os.path.join(BASE_DIR, 'tmp', 'file_scrapers')
os.makedirs(TMP_DIR, exist_ok=True)

# Maximum execution runtime: 6 hours
MAX_RUNTIME_SECONDS = 6 * 3600

_lock = threading.RLock()
_start_lock = threading.Lock()

# In-memory live progress registry: job_id -> dict with process, urls, counters, etc.
_active_jobs = {}


def _popen_kwargs():
    """Returns platform-appropriate Popen kwargs for clean process isolation."""
    if os.name == 'nt':
        return {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
    return {'start_new_session': True}


def _kill_process_tree(process, force=False):
    """Safely terminates only the targeted scraper process and its direct child
    processes using psutil, never touching web workers or sibling scrapers.
    """
    if not process:
        return
    pid = process.pid if hasattr(process, 'pid') else process
    if not pid:
        return
    try:
        if psutil.pid_exists(pid):
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    if force:
                        child.kill()
                    else:
                        child.terminate()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            try:
                if force:
                    parent.kill()
                else:
                    parent.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
            return
    except Exception:
        pass

    if hasattr(process, 'terminate'):
        try:
            if force:
                process.kill()
            else:
                process.terminate()
        except (ProcessLookupError, OSError):
            pass


def _cleanup_temp(*paths):
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except OSError:
            pass


# ==============================================================================
# Database Job Query Helpers (Source of Truth = scraper_jobs)
# ==============================================================================

def get_active_job(file_id):
    """Returns the single active record from scraper_jobs for file_id, or None.
    A job is active ONLY when status = 'RUNNING' AND finished_at IS NULL.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT job_id, file_id, started_by_user_id, status,
                       total_urls, pending_urls, running_urls, completed_urls, blocked_urls,
                       total_products, written_to_xlsx, main_url_done, product_url_done,
                       progress_percent, output_file_path, error_message, process_id,
                       started_at, finished_at
                FROM scraper_jobs
                WHERE file_id = %s
                  AND status = 'RUNNING'
                  AND finished_at IS NULL
                ORDER BY created_at DESC
                LIMIT 1
            """, (file_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def get_job_by_id(job_id):
    """Fetches a specific job record from scraper_jobs."""
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT job_id, file_id, started_by_user_id, status,
                       total_urls, pending_urls, running_urls, completed_urls, blocked_urls,
                       total_products, written_to_xlsx, main_url_done, product_url_done,
                       progress_percent, output_file_path, error_message, process_id,
                       started_at, finished_at
                FROM scraper_jobs
                WHERE job_id = %s
                LIMIT 1
            """, (job_id,))
            return cursor.fetchone()
    finally:
        conn.close()


def finalize_job(job_id, status, error_message=None, output_file_path=None):
    """Updates a job to terminal state (SUCCESS, FAILED, STOPPED) with finished_at.
    The MySQL trigger `after_scraper_job_update` automatically deletes the lock.
    Also synchronizes and finalizes the corresponding record in logTbl.
    """
    conn = get_connection()
    try:
        with conn.cursor() as cursor:
            # 1. Fetch job details
            cursor.execute("""
                SELECT file_id, started_by_user_id, process_id, total_urls, completed_urls, blocked_urls, written_to_xlsx
                FROM scraper_jobs
                WHERE job_id = %s
            """, (job_id,))
            job_row = cursor.fetchone()

            # 2. Update scraper_jobs
            cursor.execute("""
                UPDATE scraper_jobs
                SET status = %s,
                    finished_at = NOW(),
                    error_message = COALESCE(%s, error_message),
                    output_file_path = COALESCE(%s, output_file_path),
                    updated_at = NOW()
                WHERE job_id = %s
            """, (status, error_message, output_file_path, job_id))

            # 3. Ensure lock is deleted from scraper_job_locks
            cursor.execute("""
                DELETE FROM scraper_job_locks
                WHERE job_id = %s
            """, (job_id,))

            # 4. Synchronize logTbl so audit log is never left as RUNNING when job finishes!
            log_status = 'SUCCESS' if status == 'SUCCESS' else ('STOPPED' if status == 'STOPPED' else 'FAIL')
            if job_row:
                fid = job_row['file_id']
                uid = job_row['started_by_user_id']
                pid = job_row.get('process_id')
                total_u = job_row.get('total_urls') or 0
                comp_u = job_row.get('completed_urls') or 0
                block_u = job_row.get('blocked_urls') or 0
                data_s = job_row.get('written_to_xlsx') or 0

                if pid:
                    cursor.execute("""
                        UPDATE logTbl
                        SET status = %s,
                            end_time = NOW(),
                            error_message = COALESCE(%s, error_message),
                            output_file_path = COALESCE(%s, output_file_path),
                            no_of_url_found = GREATEST(no_of_url_found, %s),
                            total_success_url = GREATEST(total_success_url, %s),
                            total_block_url = GREATEST(total_block_url, %s),
                            data_scraped = GREATEST(data_scraped, %s)
                        WHERE process_id = %s AND (status = 'RUNNING' OR end_time IS NULL)
                    """, (log_status, error_message, output_file_path, total_u, comp_u, block_u, data_s, pid))

                cursor.execute("""
                    UPDATE logTbl
                    SET status = %s,
                        end_time = NOW(),
                        error_message = COALESCE(%s, error_message),
                        output_file_path = COALESCE(%s, output_file_path),
                        no_of_url_found = GREATEST(no_of_url_found, %s),
                        total_success_url = GREATEST(total_success_url, %s),
                        total_block_url = GREATEST(total_block_url, %s),
                        data_scraped = GREATEST(data_scraped, %s)
                    WHERE file_id = %s AND user_id = %s AND (status = 'RUNNING' OR end_time IS NULL)
                """, (log_status, error_message, output_file_path, total_u, comp_u, block_u, data_s, fid, uid))
    except Exception:
        logger.exception("Error finalizing job_id=%s in database.", job_id)
    finally:
        conn.close()


# ==============================================================================
# Counter Calculation (Server-Side)
# ==============================================================================

def _recalc_counters(job_state):
    """Calculates all authoritative counter metrics from the URL queue."""
    urls_dict = job_state.get('urls', {})
    items = list(urls_dict.values())

    main_urls = [u for u in items if u.get('type') == 'sitemap' or 'sitemap' in u.get('url', '').lower()]
    product_urls = [u for u in items if u.get('type') == 'product' or '/product/' in u.get('url', '').lower() or u not in main_urls]

    main_url_done = sum(1 for u in main_urls if (u.get('status') or '').lower() in ('done', 'success'))
    product_url_done = sum(1 for u in product_urls if (u.get('status') or '').lower() in ('done', 'success'))

    total_products = len(product_urls)
    total_urls = len(items)

    pending = sum(1 for u in items if (u.get('status') or '').lower() == 'pending')
    running = sum(1 for u in items if (u.get('status') or '').lower() == 'running')
    blocked = sum(1 for u in items if (u.get('status') or '').lower() in ('blocked', 'failed'))
    completed = main_url_done + product_url_done

    written_to_xlsx = product_url_done
    output_path = job_state.get('output_file_path')
    if output_path and os.path.exists(output_path):
        excel_rows = reports_repo.count_excel_data_rows(output_path)
        if excel_rows > 0:
            written_to_xlsx = excel_rows

    if total_products > 0:
        progress_pct = round(min(100.0, (product_url_done / float(total_products)) * 100.0), 1)
    elif total_urls > 0:
        progress_pct = round(min(100.0, (completed / float(total_urls)) * 100.0), 1)
    else:
        progress_pct = 0.0

    job_state['main_url_done'] = main_url_done
    job_state['product_url_done'] = product_url_done
    job_state['total_products'] = total_products
    job_state['total_urls'] = total_urls
    job_state['pending'] = pending
    job_state['running'] = running
    job_state['blocked'] = blocked
    job_state['completed'] = completed
    job_state['written_to_xlsx'] = written_to_xlsx
    job_state['progress_percent'] = progress_pct


# ==============================================================================
# Worker Thread Execution
# ==============================================================================

def _run_worker(job_id, file_id, log_id, script_path, input_path, output_placeholder):
    """Background monitoring thread reading stdout from scraper process."""
    with _lock:
        job_state = _active_jobs.get(job_id)
        if not job_state:
            return
        process = job_state['process']

    returncode = -1
    was_stopped = False
    was_timeout = False

    try:
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            line_str = line.rstrip('\n')
            parsed = parse_status_line(line_str)
            if parsed:
                with _lock:
                    if job_id in _active_jobs:
                        state = _active_jobs[job_id]
                        url_key = parsed['url']
                        existing = state['urls'].get(url_key)
                        if existing:
                            existing['status'] = parsed['status']
                            if parsed.get('parent'):
                                existing['parent'] = parsed['parent']
                            if parsed.get('type'):
                                existing['type'] = parsed['type']
                        else:
                            state['urls'][url_key] = {
                                'url': parsed['url'],
                                'status': parsed['status'],
                                'parent': parsed.get('parent') or '',
                                'type': parsed.get('type') or 'root',
                            }
                        _recalc_counters(state)

                        # Sync progress to database every 3 seconds
                        now = time.time()
                        if now - state.get('last_db_sync', 0) >= 3.0:
                            state['last_db_sync'] = now
                            conn = get_connection()
                            try:
                                with conn.cursor() as cursor:
                                    cursor.execute("""
                                        UPDATE scraper_jobs
                                        SET total_urls = %s,
                                            pending_urls = %s,
                                            running_urls = %s,
                                            completed_urls = %s,
                                            blocked_urls = %s,
                                            total_products = %s,
                                            written_to_xlsx = %s,
                                            main_url_done = %s,
                                            product_url_done = %s,
                                            progress_percent = %s
                                        WHERE job_id = %s
                                    """, (
                                        state['total_urls'], state['pending'], state['running'],
                                        state['completed'], state['blocked'], state['total_products'],
                                        state['written_to_xlsx'], state['main_url_done'],
                                        state['product_url_done'], state['progress_percent'],
                                        job_id
                                    ))
                            finally:
                                conn.close()

                            if log_id:
                                reports_repo.update_log_progress(
                                    log_id,
                                    no_of_url_found=state['total_urls'],
                                    total_success_url=state['completed'],
                                    total_block_url=state['blocked'],
                                    data_scraped=state['written_to_xlsx'],
                                )

        process.stdout.close()
        process.wait()
        returncode = process.returncode
    except Exception:
        logger.exception("Scraper job_id=%s crashed during monitoring.", job_id)
    finally:
        with _lock:
            state = _active_jobs.get(job_id, {})
            was_stopped = state.get('stopped', False)
            was_timeout = state.get('timeout_stopped', False)
            _recalc_counters(state)

        final_output_path = None
        if output_placeholder and os.path.exists(output_placeholder):
            final_output_path = output_placeholder

        total_blocked = state.get('blocked', 0)
        total_completed = state.get('completed', 0)
        written_count = state.get('written_to_xlsx', 0)

        if was_stopped:
            final_status = 'STOPPED'
            error_message = 'Scraper stopped by user.'
        elif was_timeout:
            final_status = 'STOPPED'
            error_message = 'Automatically stopped after maximum runtime of 6 hours.'
        elif total_blocked > 0 and total_completed == 0:
            final_status = 'FAILED'
            error_message = f'Scraping failed: {total_blocked} URLs blocked by target website.'
        elif returncode == 0:
            final_status = 'SUCCESS'
            error_message = None
        else:
            final_status = 'FAILED'
            error_message = f'Scraper process exited with return code {returncode}.'

        # Finalize job in scraper_jobs (Trigger releases the lock)
        finalize_job(
            job_id=job_id,
            status=final_status,
            error_message=error_message,
            output_file_path=final_output_path,
        )

        if log_id:
            reports_repo.finish_log_entry(
                log_id,
                status=final_status,
                no_of_url_found=state.get('total_urls', 0),
                total_success_url=total_completed,
                total_block_url=total_blocked,
                data_scraped=written_count,
                output_file_path=final_output_path,
                error_message=error_message,
            )

        files_repo.set_working(file_id, 0)
        _cleanup_temp(input_path)

        with _lock:
            if job_id in _active_jobs:
                _active_jobs[job_id]['status'] = final_status
                _active_jobs[job_id]['running'] = 0


# ==============================================================================
# Public APIs: Start, Status, URLs, Stop
# ==============================================================================

def start_job(file_id, user_id):
    """Starts a scraper job atomically using scraper_jobs + MySQL triggers.

    Order of execution:
    1. Authenticate user / get file_id.
    2. Check if current user already owns an active running job on file_id -> resume.
    3. Generate job_id, insert RUNNING job into scraper_jobs table.
       -> MySQL trigger before_scraper_job_insert acquires PRIMARY KEY (file_id) lock in scraper_job_locks.
       -> If another user is already running, insert fails with 1062 duplicate key error.
       -> We catch 1062 and return HTTP 409 Conflict generic message.
    4. Start Python subprocess, save process_id in scraper_jobs.
    5. Return job information to owner.
    """
    record = files_repo.get_file(file_id)
    if not record:
        return {'success': False, 'error': 'Scraper not found.'}

    if files_repo.bit_to_bool(record.get('is_deleted')):
        return {'success': False, 'error': 'This scraper is disabled. Please enable it first.'}

    with _start_lock:
        active = get_active_job(file_id)
        if active:
            with _lock:
                in_memory = (active['job_id'] in _active_jobs)
            pid = active.get('process_id')
            is_alive = in_memory or (pid and psutil.pid_exists(pid))

            if is_alive:
                if active['started_by_user_id'] == user_id:
                    return {
                        'success': True,
                        'job_id': active['job_id'],
                        'file_id': file_id,
                        'is_owner': True,
                        'is_new_job': False,
                        'message': 'Resuming your active scraper execution.'
                    }
                else:
                    return {
                        'success': False,
                        'already_running': True,
                        'is_owner': False,
                        'message': 'This scraper is currently being used by another user.'
                    }
            else:
                # Dead process: finalize and free lock
                finalize_job(active['job_id'], status='FAILED', error_message='Process terminated unexpectedly.')
                files_repo.set_working(file_id, 0)

        job_id = uuid.uuid4().hex[:16]

        # Step 3: Insert RUNNING job into scraper_jobs (Trigger acquires lock)
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO scraper_jobs (
                        job_id, file_id, started_by_user_id, status, started_at
                    )
                    VALUES (%s, %s, %s, 'RUNNING', NOW())
                """, (job_id, file_id, user_id))
        except (pymysql.err.IntegrityError, Exception) as exc:
            # Duplicate key error (1062) means another user acquired the lock simultaneously
            logger.info("Job start lock rejected for file_id=%s: %s", file_id, exc)
            return {
                'success': False,
                'already_running': True,
                'is_owner': False,
                'message': 'This scraper is currently being used by another user.'
            }
        finally:
            conn.close()

        # Step 4: Start Python subprocess
        try:
            script_path = files_repo.resolve_script_path(record['python_file_path'])
        except Exception as exc:
            finalize_job(job_id, status='FAILED', error_message=f'Failed to resolve script: {exc}')
            files_repo.set_working(file_id, 0)
            return {'success': False, 'error': str(exc)}

        urls = []
        if record.get('urls_json'):
            try:
                urls = json.loads(record['urls_json'])
            except Exception:
                urls = []

        output_placeholder = os.path.join(TMP_DIR, f'file_{file_id}_output.xlsx')
        input_path = None
        if urls:
            input_path = os.path.join(TMP_DIR, f'file_{file_id}_urls.csv')
            with open(input_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                for u in urls:
                    writer.writerow([u])

        args = [sys.executable, '-u', script_path, output_placeholder]
        if input_path:
            args.append(input_path)

        try:
            process = subprocess.Popen(
                args,
                cwd=BASE_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                **_popen_kwargs(),
            )
        except OSError as exc:
            _cleanup_temp(input_path, output_placeholder)
            finalize_job(job_id, status='FAILED', error_message='Failed to start scraper process')
            files_repo.set_working(file_id, 0)
            return {'success': False, 'error': f'Failed to launch process: {exc}'}

        scraper_name = record.get('site_name') or 'Scraper'

        # Update process_id in scraper_jobs
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE scraper_jobs
                    SET process_id = %s,
                        total_urls = %s,
                        total_products = %s,
                        pending_urls = %s,
                        output_file_path = %s
                    WHERE job_id = %s
                """, (process.pid, len(urls), len(urls), len(urls), output_placeholder, job_id))
        finally:
            conn.close()

        # Also create report log in logTbl for audit trail
        log_id = reports_repo.create_log_entry(
            user_id=user_id,
            file_id=file_id,
            scraper_name=scraper_name,
            process_id=process.pid,
        )

        files_repo.set_working(file_id, 1)

        initial_urls = OrderedDict()
        for u in urls:
            initial_urls[u] = {'url': u, 'status': 'pending', 'parent': '', 'type': 'root'}

        with _lock:
            _active_jobs[job_id] = {
                'job_id': job_id,
                'file_id': file_id,
                'log_id': log_id,
                'started_by_user_id': user_id,
                'site_name': scraper_name,
                'process': process,
                'pid': process.pid,
                'started_at': datetime.now(timezone.utc),
                'status': 'RUNNING',
                'urls': initial_urls,
                'total_products': len(urls),
                'total_urls': len(urls),
                'written_to_xlsx': 0,
                'pending': len(urls),
                'running': 0,
                'blocked': 0,
                'completed': 0,
                'main_url_done': 0,
                'product_url_done': 0,
                'progress_percent': 0.0,
                'output_file_path': output_placeholder,
                'error_message': None,
                'stopped': False,
                'timeout_stopped': False,
                'last_db_sync': time.time(),
            }

        worker = threading.Thread(
            target=_run_worker,
            args=(job_id, file_id, log_id, script_path, input_path, output_placeholder),
            daemon=True,
        )
        worker.start()

        return {
            'success': True,
            'job_id': job_id,
            'file_id': file_id,
            'is_owner': True,
            'is_new_job': True,
            'message': 'Scraper job started successfully.'
        }


def get_active_job_for_file(file_id, current_user_id):
    """Checks active job for file_id and strictly enforces user privacy.

    - If no active job -> returns {has_active_job: false, is_owner: true, status: 'IDLE'}
    - If active and owner == current_user_id -> returns {has_active_job: true, is_owner: true, job_id: ...}
    - If active and owner != current_user_id -> returns {has_active_job: true, already_running: true, is_owner: false, message: '...'}
      (NEVER leaks job_id, process_id, counters, URLs, logs, or username to non-owners).
    """
    active = get_active_job(file_id)
    record = files_repo.get_file(file_id)
    site_name = record['site_name'] if record else 'Scraper'

    if not active:
        return {
            'has_active_job': False,
            'already_running': False,
            'is_owner': True,
            'file_id': file_id,
            'site_name': site_name,
            'status': 'IDLE'
        }

    with _lock:
        in_memory = (active['job_id'] in _active_jobs)

    pid = active.get('process_id')
    is_alive = in_memory or (pid and psutil.pid_exists(pid))
    if not is_alive:
        finalize_job(active['job_id'], status='FAILED', error_message='Process terminated unexpectedly.')
        files_repo.set_working(file_id, 0)
        return {
            'has_active_job': False,
            'already_running': False,
            'is_owner': True,
            'file_id': file_id,
            'site_name': site_name,
            'status': 'IDLE'
        }

    is_owner = (active['started_by_user_id'] == current_user_id)

    if not is_owner:
        return {
            'has_active_job': True,
            'already_running': True,
            'is_owner': False,
            'file_id': file_id,
            'site_name': site_name,
            'status': 'RUNNING',
            'message': 'This scraper is currently being used by another user.'
        }

    return {
        'has_active_job': True,
        'already_running': True,
        'is_owner': True,
        'job_id': active['job_id'],
        'file_id': file_id,
        'site_name': site_name,
        'status': active['status']
    }


def get_job_status(job_id, current_user_id):
    """Returns live authoritative progress ONLY to the authenticated owner."""
    with _lock:
        state = _active_jobs.get(job_id)
        if state:
            if state['started_by_user_id'] != current_user_id:
                return {'success': False, 'error': 'Forbidden'}, 403
            _recalc_counters(state)
            return {
                'job_id': job_id,
                'file_id': state['file_id'],
                'site_name': state.get('site_name', 'Scraper'),
                'status': state['status'],
                'running': state['status'] == 'RUNNING',
                'done': state['status'] in ('SUCCESS', 'FAILED', 'STOPPED'),
                'total_product_urls': state['total_products'],
                'total_urls': state['total_urls'],
                'written_to_xlsx': state['written_to_xlsx'],
                'pending': state['pending'],
                'running_count': state['running'],
                'blocked': state['blocked'],
                'completed': state['completed'],
                'main_url_done': state['main_url_done'],
                'product_url_done': state['product_url_done'],
                'progress_percent': state['progress_percent'],
                'started_at': state['started_at'].isoformat() if isinstance(state.get('started_at'), datetime) else None,
                'output_available': bool(state.get('output_file_path') and os.path.exists(state['output_file_path']) and state['status'] != 'RUNNING'),
                'output_file_path': state.get('output_file_path'),
                'error_message': state.get('error_message'),
            }, 200

    job = get_job_by_id(job_id)
    if not job:
        return {'success': False, 'error': 'Job not found.'}, 404

    if job['started_by_user_id'] != current_user_id:
        return {'success': False, 'error': 'Forbidden'}, 403

    is_running = (job['status'] == 'RUNNING' and job['finished_at'] is None)
    output_path = job.get('output_file_path')
    record = files_repo.get_file(job['file_id'])

    return {
        'job_id': job['job_id'],
        'file_id': job['file_id'],
        'site_name': record['site_name'] if record else 'Scraper',
        'status': job['status'],
        'running': is_running,
        'done': not is_running,
        'total_product_urls': job.get('total_products') or 0,
        'total_urls': job.get('total_urls') or 0,
        'written_to_xlsx': job.get('written_to_xlsx') or 0,
        'pending': job.get('pending_urls') or 0,
        'running_count': job.get('running_urls') or 0,
        'blocked': job.get('blocked_urls') or 0,
        'completed': job.get('completed_urls') or 0,
        'main_url_done': job.get('main_url_done') or 0,
        'product_url_done': job.get('product_url_done') or 0,
        'progress_percent': job.get('progress_percent') or 0.0,
        'started_at': job['started_at'].isoformat() if job.get('started_at') else None,
        'output_available': bool(output_path and os.path.exists(output_path) and not is_running),
        'output_file_path': output_path,
        'error_message': job.get('error_message'),
    }, 200


def get_job_urls(job_id, current_user_id):
    """Returns URL queue and statuses ONLY to the authenticated owner."""
    with _lock:
        state = _active_jobs.get(job_id)
        if state:
            if state['started_by_user_id'] != current_user_id:
                return {'success': False, 'error': 'Forbidden'}, 403
            return list(state['urls'].values()), 200

    job = get_job_by_id(job_id)
    if not job:
        return {'success': False, 'error': 'Job not found.'}, 404

    if job['started_by_user_id'] != current_user_id:
        return {'success': False, 'error': 'Forbidden'}, 403

    if job.get('output_file_path') and os.path.exists(job['output_file_path']):
        try:
            import openpyxl
            wb = openpyxl.load_workbook(job['output_file_path'], read_only=True, data_only=True)
            sheet = wb.active
            headers = [str(c).strip().lower() for c in next(sheet.iter_rows(values_only=True), [])]
            url_col_idx = next((idx for idx, h in enumerate(headers) if h in ('url', 'source', 'product url', 'link')), None)
            urls = []
            if url_col_idx is not None:
                for row in sheet.iter_rows(min_row=2, values_only=True):
                    if row and len(row) > url_col_idx and row[url_col_idx]:
                        urls.append({
                            'url': str(row[url_col_idx]).strip(),
                            'status': 'done',
                            'parent': '',
                            'type': 'product'
                        })
            wb.close()
            return urls, 200
        except Exception:
            pass

    return [], 200


def stop_job(job_id, current_user_id, is_superadmin=False):
    """Terminates the scraper process if requested by the owner (or SuperAdmin)."""
    job = get_job_by_id(job_id)
    if not job:
        return {'success': False, 'error': 'Job not found.'}, 404

    if job['started_by_user_id'] != current_user_id and not is_superadmin:
        return {'success': False, 'error': 'Forbidden'}, 403

    file_id = job.get('file_id')
    process = None

    with _lock:
        state = _active_jobs.get(job_id)
        if state:
            state['stopped'] = True
            state['status'] = 'STOPPED'
            state['running'] = 0
            process = state.get('process')

    pid = job.get('process_id')
    if pid and psutil.pid_exists(pid):
        _kill_process_tree(pid, force=True)

    if process:
        _kill_process_tree(process)
        try:
            process.wait(timeout=3)
        except subprocess.TimeoutExpired:
            _kill_process_tree(process, force=True)
            try:
                process.wait(timeout=2)
            except Exception:
                pass

    finalize_job(job_id, status='STOPPED', error_message='Scraper stopped by user.')

    if file_id:
        files_repo.set_working(file_id, 0)

    return {'success': True, 'job_id': job_id, 'status': 'STOPPED', 'message': 'Scraper stopped successfully.'}, 200


def stop_file(file_id, current_user_id, is_superadmin=False):
    """Stops the active execution for file_id after validating ownership."""
    active = get_active_job(file_id)
    if active:
        res, code = stop_job(active['job_id'], current_user_id, is_superadmin=is_superadmin)
        return res, code

    files_repo.set_working(file_id, 0)
    return {'success': True, 'file_id': file_id, 'message': 'Scraper is not running.'}, 200


# ==============================================================================
# 6-Hour Timeout & Dead Process Watchdog
# ==============================================================================

def _watchdog_loop():
    """Background watchdog thread that:
    1. Terminates executions exceeding 6 hours max runtime.
    2. Only cleans up dead processes managed by THIS local instance.
       (Never kills jobs from remote instances/other servers sharing the DB!).
    """
    while True:
        try:
            time.sleep(15)
            now = datetime.now(timezone.utc)

            # 1. First, check jobs managed in memory by THIS instance
            with _lock:
                managed_jobs = list(_active_jobs.items())

            for jid, state in managed_jobs:
                proc = state.get('process')
                pid = state.get('pid')
                started_at = state.get('started_at')

                # Check 6-hour timeout
                if started_at and (now - started_at).total_seconds() > MAX_RUNTIME_SECONDS:
                    logger.warning("Local Job %s exceeded 6 hours. Auto-terminating...", jid)
                    if pid and psutil.pid_exists(pid):
                        _kill_process_tree(pid, force=True)
                    finalize_job(
                        jid,
                        status='STOPPED',
                        error_message='Automatically stopped after maximum runtime of 6 hours.'
                    )
                    continue

                # Check if local process died
                if proc and proc.poll() is not None and state.get('status') == 'RUNNING':
                    ret = proc.poll()
                    logger.info("Local Job %s process %s exited with code %s.", jid, pid, ret)
                    final_st = 'SUCCESS' if ret == 0 else 'FAILED'
                    err = None if ret == 0 else f'Process exited with return code {ret}.'
                    finalize_job(jid, status=final_st, error_message=err)

            # 2. Database level: only terminate globally if job is > 6 hours old
            conn = get_connection()
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        UPDATE scraper_jobs
                        SET status = 'STOPPED',
                            finished_at = NOW(),
                            error_message = 'Automatically stopped after maximum runtime of 6 hours.'
                        WHERE status = 'RUNNING'
                          AND finished_at IS NULL
                          AND started_at < NOW() - INTERVAL 6 HOUR
                    """)
            finally:
                conn.close()

        except Exception:
            pass


_watchdog_thread_started = False

def start_watchdog():
    global _watchdog_thread_started
    if not _watchdog_thread_started:
        _watchdog_thread_started = True
        t = threading.Thread(target=_watchdog_loop, daemon=True)
        t.start()


start_watchdog()
