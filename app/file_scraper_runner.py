"""Background execution facade for registered scraper files.
Delegates to the centralized server-side job_manager engine.
"""

import os
import job_manager
import files_repo

BASE_DIR = files_repo.BASE_DIR
TMP_DIR = os.path.join(BASE_DIR, 'tmp', 'file_scrapers')
os.makedirs(TMP_DIR, exist_ok=True)

class StartError(Exception):
    """Raised with a user-facing message when a start request can't proceed."""


def is_running(file_id):
    """Returns True if there is an active job running for file_id."""
    active = job_manager.get_active_job(file_id)
    if active:
        return True
    rec = files_repo.get_file(file_id)
    return bool(rec and files_repo.bit_to_bool(rec.get('working')))


def running_count():
    """Counts currently active scraper jobs."""
    try:
        from db import get_connection
        conn = get_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) AS cnt FROM scraper_jobs WHERE status = 'RUNNING' AND finished_at IS NULL")
                row = cursor.fetchone()
                return row['cnt'] if row else 0
        finally:
            conn.close()
    except Exception:
        return 0


def get_statuses(file_id):
    """Returns live URL status list for file_id's active or recent job."""
    active = job_manager.get_active_job(file_id)
    if active:
        urls, _ = job_manager.get_job_urls(active['job_id'], current_user_id=active['started_by_user_id'])
        return urls
    return []


def get_output_path(file_id):
    """Returns absolute path to the XLSX output file for file_id."""
    active = job_manager.get_active_job(file_id)
    if active and active.get('output_file_path') and os.path.exists(active['output_file_path']):
        return active['output_file_path']
    fallback = os.path.join(TMP_DIR, f'file_{file_id}_output.xlsx')
    if os.path.exists(fallback):
        return fallback
    return None


def get_all_output_paths():
    """Returns mapping of file_id -> output file path for completed runs."""
    paths = {}
    if os.path.exists(TMP_DIR):
        for fname in os.listdir(TMP_DIR):
            if fname.startswith('file_') and fname.endswith('_output.xlsx'):
                try:
                    fid = int(fname.split('_')[1])
                    fpath = os.path.join(TMP_DIR, fname)
                    if os.path.exists(fpath):
                        paths[fid] = fpath
                except ValueError:
                    pass
    return paths


def start(file_id, user_id=None):
    """Starts file_id scraper or attaches to existing job."""
    res = job_manager.start_job(file_id, user_id=user_id)
    if not res.get('success'):
        raise StartError(res.get('error') or 'Could not start scraper.')
    return res


def stop(file_id):
    """Stops any running job for file_id."""
    res = job_manager.stop_file(file_id)
    return res.get('success', False)
