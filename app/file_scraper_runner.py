"""Background execution engine for registered scraper files (fileTbl).

Runs each scraper as its own tracked subprocess in a daemon thread -- never
`subprocess.run()` inside a request -- so /api/files/<id>/start returns
immediately and the request thread is never blocked while a scraper runs.
This mirrors the existing pattern in app.py's _run_job_groups/ScraperSession
(Popen + background thread reading stdout, working state flipped back once
the process exits, success or crash) rather than inventing a second one.

`working` in fileTbl is the persistent source of truth the frontend reads on
page load/poll (see files_repo.set_working) -- this module's in-memory
`_processes` registry only exists within this process's lifetime, to prevent
double-starts and support Stop; it does not survive a Flask restart, the same
limitation app.py's existing per-session scraper_sessions registry already
has (a scraper still "running" in the DB when the process restarts will stay
marked working=1 until started/stopped again -- see CLAUDE.md/README notes).
"""

import csv
import json
import logging
import os
import signal
import subprocess
import sys
import threading

import files_repo
from scraper_status_utils import parse_status_line

logger = logging.getLogger(__name__)

BASE_DIR = files_repo.BASE_DIR
TMP_DIR = os.path.join(BASE_DIR, 'tmp', 'file_scrapers')

# Maximum execution runtime: 6 hours (in seconds)
MAX_RUNTIME_SECONDS = 6 * 3600

# Simple resource-safety cap for "Start Selected" -- several of the
# registered scrapers are heavy (scan.py launches a full non-headless
# Chromium), so an unbounded number of simultaneous starts isn't safe.
MAX_CONCURRENT_SCRAPERS = 4

_processes = {}  # file_id -> {'process': Popen, 'report_id': int, 'timer': Timer, 'stopped': bool, 'timeout_stopped': bool}
_lock = threading.RLock()

# Live per-URL status, so a scraper started from /files can be watched on the
# main Scraper page (redirected there with ?fileId=<id>) the same way an
# ad-hoc /StartScraper job is.
_statuses = {}  # file_id -> [{'url', 'status', 'parent', 'type'}, ...]
_statuses_lock = threading.RLock()


class StartError(Exception):
    """Raised with a user-facing message when a start request can't proceed."""


def is_running(file_id):
    with _lock:
        entry = _processes.get(file_id)
        if entry and entry['process'].poll() is None:
            return True
    # Also check persistent working state in database with bit_to_bool
    rec = files_repo.get_file(file_id)
    return bool(rec and files_repo.bit_to_bool(rec.get('working')))


def running_count():
    with _lock:
        return sum(1 for entry in _processes.values() if entry['process'].poll() is None)


def _cleanup_temp(*paths):
    for path in paths:
        try:
            if path and os.path.exists(path):
                os.remove(path)
        except OSError:
            pass


def _popen_kwargs():
    """Extra Popen kwargs so the whole process tree can be killed together on
    stop() or 6-hour timeout.
    """
    if os.name == 'nt':
        return {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
    return {'start_new_session': True}


def _kill_process_tree(process, force=False):
    if not process:
        return
    if os.name == 'nt':
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], capture_output=True)
        return
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL if force else signal.SIGTERM)
    except (ProcessLookupError, OSError):
        pass


def _reset_statuses(file_id):
    with _statuses_lock:
        _statuses[file_id] = []


def _record_status_line(file_id, line):
    parsed = parse_status_line(line)
    if not parsed:
        return
    with _statuses_lock:
        statuses = _statuses.setdefault(file_id, [])
        existing = next((item for item in statuses if item['url'] == parsed['url']), None)
        if existing:
            existing['status'] = parsed['status']
            if parsed.get('parent'):
                existing['parent'] = parsed['parent']
            if parsed.get('type'):
                existing['type'] = parsed['type']
        else:
            statuses.append({
                'url': parsed['url'],
                'status': parsed['status'],
                'parent': parsed.get('parent') or '',
                'type': parsed.get('type') or 'root',
            })


def get_statuses(file_id):
    with _statuses_lock:
        return list(_statuses.get(file_id, []))


_outputs = {}  # file_id -> absolute path
import reports_repo

_outputs_lock = threading.RLock()


def get_output_path(file_id):
    with _outputs_lock:
        path = _outputs.get(file_id)
    if path and os.path.exists(path):
        return path
    fallback = os.path.join(TMP_DIR, f'file_{file_id}_output.xlsx')
    if os.path.exists(fallback):
        return fallback
    return None


def get_all_output_paths():
    with _outputs_lock:
        paths = {fid: path for fid, path in _outputs.items() if path and os.path.exists(path)}
    if os.path.exists(TMP_DIR):
        for fname in os.listdir(TMP_DIR):
            if fname.startswith('file_') and fname.endswith('_output.xlsx'):
                try:
                    fid = int(fname.split('_')[1])
                    if fid not in paths:
                        paths[fid] = os.path.join(TMP_DIR, fname)
                except ValueError:
                    pass
    return paths


def _handle_timeout(file_id):
    """Callback fired when a scraper reaches the 6-hour maximum runtime."""
    logger.warning('Scraper file_id=%s reached maximum runtime of 6 hours. Automatically terminating...', file_id)
    with _lock:
        entry = _processes.get(file_id)
        if entry:
            entry['stopped'] = True
            entry['timeout_stopped'] = True
            process = entry.get('process')
        else:
            process = None

    if process and process.poll() is None:
        _kill_process_tree(process, force=True)


def _run(file_id, script_path, urls, report_id=None):
    input_path = None
    os.makedirs(TMP_DIR, exist_ok=True)
    output_placeholder = os.path.join(TMP_DIR, f'file_{file_id}_output.xlsx')
    if urls:
        input_path = os.path.join(TMP_DIR, f'file_{file_id}_urls.csv')
        with open(input_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for url in urls:
                writer.writerow([url])

    args = [sys.executable, '-u', script_path, output_placeholder]
    if input_path:
        args.append(input_path)

    logger.info('Starting scraper file_id=%s (%s), report_id=%s', file_id, os.path.basename(script_path), report_id)
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
        logger.exception('Failed to launch scraper file_id=%s', file_id)
        if report_id:
            try:
                reports_repo.finish_log_entry(report_id, status='FAIL', error_message=str(exc))
            except Exception:
                pass
        _cleanup_temp(input_path, output_placeholder)
        with _outputs_lock:
            _outputs.pop(file_id, None)
        files_repo.set_working(file_id, 0)
        return

    # Start 6-hour automatic timeout watchdog timer
    timeout_timer = threading.Timer(MAX_RUNTIME_SECONDS, _handle_timeout, args=(file_id,))
    timeout_timer.daemon = True
    timeout_timer.start()

    with _lock:
        _processes[file_id] = {
            'process': process,
            'report_id': report_id,
            'timer': timeout_timer,
            'stopped': False,
            'timeout_stopped': False,
        }

    returncode = -1
    was_stopped = False
    was_timeout = False
    try:
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            _record_status_line(file_id, line.rstrip('\n'))
        process.stdout.close()
        process.wait()
        returncode = process.returncode
        if returncode == 0:
            logger.info('Scraper file_id=%s finished successfully.', file_id)
        else:
            logger.warning('Scraper file_id=%s exited with code %s.', file_id, returncode)
    except Exception as exc:
        logger.exception('Scraper file_id=%s crashed while being monitored.', file_id)
    finally:
        # Cancel watchdog timer
        timeout_timer.cancel()

        with _lock:
            proc_info = _processes.pop(file_id, None)
            if proc_info:
                was_stopped = proc_info.get('stopped', False)
                was_timeout = proc_info.get('timeout_stopped', False)

        # Count URL stats: total discovered, success, blocked
        statuses = _statuses.get(file_id, [])
        no_of_url_found = len(statuses) if statuses else len(urls)
        total_success_url = sum(1 for s in statuses if (s.get('status') or '').lower() in ('done', 'success'))
        total_block_url = sum(1 for s in statuses if (s.get('status') or '').lower() in ('blocked', 'failed'))

        final_output_path = None
        if output_placeholder and os.path.exists(output_placeholder):
            final_output_path = output_placeholder
            with _outputs_lock:
                _outputs[file_id] = output_placeholder
        else:
            with _outputs_lock:
                _outputs.pop(file_id, None)

        data_scraped = reports_repo.count_excel_data_rows(final_output_path) if final_output_path else 0

        # Determine normalized final status and error/stop message
        # Requirement: Status column only uses RUNNING, SUCCESS, FAIL.
        # Timeouts and stops map to FAIL with specific reason in details.
        error_message = None
        if was_timeout:
            final_status = 'FAIL'
            error_message = 'Scraper automatically stopped because execution time exceeded 6 hours. Status: STOPPED Reason: TIMEOUT (>6 HOURS)'
        elif was_stopped:
            final_status = 'FAIL'
            error_message = 'Scraper stopped by user. Status: STOPPED'
        elif returncode == 0:
            final_status = 'SUCCESS'
        else:
            final_status = 'FAIL'
            error_message = f'Scraper process exited with return code {returncode}.'

        if report_id:
            try:
                reports_repo.finish_log_entry(
                    report_id,
                    status=final_status,
                    no_of_url_found=no_of_url_found,
                    total_success_url=total_success_url,
                    total_block_url=total_block_url,
                    data_scraped=data_scraped,
                    output_file_path=final_output_path,
                    error_message=error_message,
                )
            except Exception:
                logger.exception('Failed to update log entry for report_id=%s', report_id)

        # Always release scraper working status in database
        files_repo.set_working(file_id, 0)
        _cleanup_temp(input_path)


def start(file_id, user_id=None):
    """Starts file_id's scraper as a background subprocess and returns
    immediately. Raises StartError with a user-facing message if it can't be started.
    """
    record = files_repo.get_file(file_id)
    if not record:
        raise StartError('Scraper not found.')

    with _lock:
        if is_running(file_id):
            raise StartError('Scraper is currently running. Please wait until the current process is completed.')

        if running_count() >= MAX_CONCURRENT_SCRAPERS:
            raise StartError(f'Too many scrapers are already running (limit: {MAX_CONCURRENT_SCRAPERS}). Wait for one to finish.')

        # Mark working in DB under lock immediately
        files_repo.set_working(file_id, 1)

    try:
        script_path = files_repo.resolve_script_path(record['python_file_path'])
    except files_repo.FileValidationError as exc:
        files_repo.set_working(file_id, 0)
        raise StartError(str(exc))

    urls = []
    if record.get('urls_json'):
        try:
            urls = json.loads(record['urls_json'])
        except (json.JSONDecodeError, TypeError):
            urls = []

    _reset_statuses(file_id)
    with _outputs_lock:
        _outputs.pop(file_id, None)

    # Create run report in logTbl
    report_id = None
    try:
        actual_user_id = user_id or record.get('created_by') or 1
        scraper_name = record.get('site_name') or 'Scraper'
        report_id = reports_repo.create_log_entry(
            user_id=actual_user_id,
            file_id=file_id,
            scraper_name=scraper_name,
        )
    except Exception:
        logger.exception('Failed to create log entry for file_id=%s', file_id)

    thread = threading.Thread(target=_run, args=(file_id, script_path, urls, report_id), daemon=True)
    thread.start()


def stop(file_id):
    """Terminates file_id's running subprocess (and any child processes).
    Returns True if a running process was found and signaled, False if it wasn't running.
    """
    with _lock:
        entry = _processes.get(file_id)
        process = entry['process'] if entry else None
        if entry:
            entry['stopped'] = True
            if entry.get('timer'):
                entry['timer'].cancel()

    if not process or process.poll() is not None:
        files_repo.set_working(file_id, 0)
        return False

    _kill_process_tree(process)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _kill_process_tree(process, force=True)
        process.wait()

    files_repo.set_working(file_id, 0)
    return True


def init_cleanup():
    """Cleans up any orphaned running records from previous server runs."""
    try:
        from db import get_connection
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE fileTbl SET working = 0 WHERE working = 1")
                cursor.execute("""
                    UPDATE logTbl 
                    SET status = 'FAIL', 
                        end_time = NOW(), 
                        error_message = 'Scraper stopped because server restarted.' 
                    WHERE status = 'RUNNING' AND end_time IS NULL
                """)
        finally:
            conn.close()
    except Exception:
        pass


init_cleanup()
