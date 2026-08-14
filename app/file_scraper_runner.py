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
_outputs_lock = threading.Lock()


def get_output_path(file_id):
    with _outputs_lock:
        path = _outputs.get(file_id)
    return path if path and os.path.exists(path) else None


def _run(file_id, script_path, urls):
    input_path = None
    output_placeholder = None
    if urls:
        os.makedirs(TMP_DIR, exist_ok=True)
        input_path = os.path.join(TMP_DIR, f'file_{file_id}_urls.csv')
        with open(input_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            for url in urls:
                writer.writerow([url])
        output_placeholder = os.path.join(TMP_DIR, f'file_{file_id}_output.xlsx')

    args = [sys.executable, '-u', script_path]
    if input_path:
        # Matches the "<output_file> <urls_csv>" argv convention
        # pitstoparabiabycsv.py / pitstoparabia-brand-1.py /
        # pitstoparabia-instock-3.py already use -- scripts that don't read
        # argv at all (scan*.py) simply ignore the extra arguments and run
        # with their own hardcoded defaults, per "do not unnecessarily
        # modify scraper logic that already supports URL input."
        args.extend([output_placeholder, input_path])

    logger.info('Starting scraper file_id=%s (%s)', file_id, os.path.basename(script_path))
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
    except OSError:
        logger.exception('Failed to launch scraper file_id=%s', file_id)
        files_repo.set_working(file_id, False)
        _cleanup_temp(input_path, output_placeholder)
        with _outputs_lock:
            _outputs.pop(file_id, None)
        return

    with _lock:
        _processes[file_id] = {'process': process}

    try:
        for line in iter(process.stdout.readline, ''):
            if not line:
                break
            _record_status_line(file_id, line.rstrip('\n'))
        process.stdout.close()
        process.wait()
        if process.returncode == 0:
            logger.info('Scraper file_id=%s finished successfully.', file_id)
        else:
            logger.warning('Scraper file_id=%s exited with code %s (treated as failed).', file_id, process.returncode)
    except Exception:
        logger.exception('Scraper file_id=%s crashed while being monitored.', file_id)
    finally:
        with _lock:
            _processes.pop(file_id, None)
        try:
            files_repo.set_working(file_id, False)
        except Exception:
            logger.exception('Failed to clear working flag for file_id=%s after it finished.', file_id)
        # Only the temp input CSV is cleanup -- the output workbook is kept
        # (see _outputs) so it can be downloaded after the run finishes.
        _cleanup_temp(input_path)
        if output_placeholder and os.path.exists(output_placeholder):
            with _outputs_lock:
                _outputs[file_id] = output_placeholder
        else:
            with _outputs_lock:
                _outputs.pop(file_id, None)


def start(file_id):
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

    # Set before the thread starts (not inside it) so a client polling
    # immediately after this call sees working=true right away, not a race
    # against the background thread getting scheduled.
    _reset_statuses(file_id)
    # Drop any previous run's output so a download requested mid-run can't
    # serve stale data before the new run has written anything.
    with _outputs_lock:
        _outputs.pop(file_id, None)
    files_repo.set_working(file_id, True)
    thread = threading.Thread(target=_run, args=(file_id, script_path, urls), daemon=True)
    thread.start()


def stop(file_id):
    """Terminates file_id's running subprocess (and any child process it
    spawned, e.g. scan.py's browser bridge -- see _kill_process_tree), if
    any. Returns True if a running process was found and signaled, False if
    it wasn't running. The background thread's own `finally` clears
    `working` once the process actually exits (this doesn't do that
    synchronously).
    """
    with _lock:
        entry = _processes.get(file_id)
        process = entry['process'] if entry else None

    if not process or process.poll() is not None:
        # Nothing tracked in this process's memory -- most commonly because
        # the app restarted since this scraper was started (a Flask reload,
        # a deploy, etc.), which wipes _processes but leaves fileTbl.working
        # stuck at 1 with no way to ever clear it again. Reconcile that
        # stale state here instead of leaving Stop permanently useless for
        # this row: if the DB still says it's running, correct it.
        record = files_repo.get_file(file_id)
        if record and files_repo.bit_to_bool(record['working']):
            files_repo.set_working(file_id, False)
            return True
        return False

    _kill_process_tree(process)
    try:
        process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        _kill_process_tree(process, force=True)
        process.wait()
    return True
