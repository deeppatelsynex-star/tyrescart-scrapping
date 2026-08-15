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

# Simple resource-safety cap for "Start Selected" -- several of the
# registered scrapers are heavy (scan.py launches a full non-headless
# Chromium), so an unbounded number of simultaneous starts isn't safe.
MAX_CONCURRENT_SCRAPERS = 4

_processes = {}  # file_id -> {'process': Popen}
_lock = threading.Lock()

# Live per-URL status, so a scraper started from /files can be watched on the
# main Scraper page (redirected there with ?fileId=<id>) the same way an
# ad-hoc /StartScraper job is. Scripts that never print URL_STATUS lines
# (e.g. scan*.py, which don't emit that format) simply leave this empty --
# is_running()/working still reflect that they're running, just without a
# per-URL tree.
_statuses = {}  # file_id -> [{'url', 'status', 'parent', 'type'}, ...]
_statuses_lock = threading.Lock()


class StartError(Exception):
    """Raised with a user-facing message when a start request can't proceed."""


def is_running(file_id):
    with _lock:
        entry = _processes.get(file_id)
        return bool(entry and entry['process'].poll() is None)


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
    stop() -- some scrapers (scan.py) spawn their own child process (a
    Playwright browser bridge); without this, terminate()/kill() only signal
    the top-level process and leave that child orphaned and running.
    """
    if os.name == 'nt':
        return {'creationflags': subprocess.CREATE_NEW_PROCESS_GROUP}
    return {'start_new_session': True}


def _kill_process_tree(process, force=False):
    if os.name == 'nt':
        # taskkill's /T walks the process tree by parent PID -- this is the
        # forceful default on Windows either way (Popen.terminate() there is
        # already just TerminateProcess, not a soft signal).
        subprocess.run(['taskkill', '/F', '/T', '/PID', str(process.pid)], capture_output=True)
        return
    try:
        os.killpg(os.getpgid(process.pid), signal.SIGKILL if force else signal.SIGTERM)
    except ProcessLookupError:
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


# Latest output workbook per file_id, so the Scraper page (watching via
# ?fileId=<id>) can offer a real download once a run finishes -- unlike
# input CSVs, this is deliberately NOT deleted in _run()'s cleanup; a later
# run for the same file_id just overwrites it (one output per registered
# scraper, same "latest run" semantic the ad-hoc /StartScraper flow has).
_outputs = {}  # file_id -> absolute path
import reports_repo

_outputs_lock = threading.Lock()


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
    # Also check TMP_DIR files on disk
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
                reports_repo.finish_report_run(report_id, status='FAILED', error_message=str(exc))
            except Exception:
                pass
        _cleanup_temp(input_path, output_placeholder)
        with _outputs_lock:
            _outputs.pop(file_id, None)
        return

    with _lock:
        _processes[file_id] = {'process': process, 'report_id': report_id, 'stopped': False}

    returncode = -1
    was_stopped = False
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
        with _lock:
            proc_info = _processes.pop(file_id, None)
            if proc_info:
                was_stopped = proc_info.get('stopped', False)

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

        if was_stopped:
            final_status = 'STOPPED'
        elif returncode == 0:
            final_status = 'FINISHED'
        else:
            final_status = 'FAILED'

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
                )
            except Exception:
                logger.exception('Failed to update log entry for report_id=%s', report_id)

        _cleanup_temp(input_path)


def start(file_id, user_id=None):
    """Starts file_id's scraper as a background subprocess and returns
    immediately. Raises StartError with a user-facing message (never an
    absolute filesystem path) if it can't be started.
    """
    record = files_repo.get_file(file_id)
    if not record:
        raise StartError('Scraper not found.')

    if is_running(file_id):
        raise StartError('This scraper is already running.')

    if running_count() >= MAX_CONCURRENT_SCRAPERS:
        raise StartError(f'Too many scrapers are already running (limit: {MAX_CONCURRENT_SCRAPERS}). Wait for one to finish.')

    try:
        script_path = files_repo.resolve_script_path(record['python_file_path'])
    except files_repo.FileValidationError as exc:
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
        scraper_name = f"{record['site_name']} ({record['python_file_path']})"
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
    """Terminates file_id's running subprocess (and any child process it
    spawned, e.g. scan.py's browser bridge -- see _kill_process_tree), if
    any. Returns True if a running process was found and signaled, False if
    it wasn't running.
    """
    with _lock:
        entry = _processes.get(file_id)
        process = entry['process'] if entry else None
        if entry:
            entry['stopped'] = True

    if not process or process.poll() is not None:
        return False

    _kill_process_tree(process)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _kill_process_tree(process, force=True)
        process.wait()
    return True
