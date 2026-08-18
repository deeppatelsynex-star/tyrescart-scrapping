import sys, json, time
sys.path.insert(0, 'app')
from db import get_connection
import job_manager

file_id = 35
user_id = 2

# Clean state
conn = get_connection()
with conn.cursor() as c:
    c.execute('UPDATE scraper_jobs SET status=%s, finished_at=NOW() WHERE file_id=%s AND status=%s', ('STOPPED', file_id, 'RUNNING'))
    c.execute('DELETE FROM scraper_job_locks WHERE file_id=%s', (file_id,))
    c.execute('UPDATE fileTbl SET working=0 WHERE file_id=%s', (file_id,))
conn.close()

with job_manager._lock:
    job_manager._active_jobs.clear()

# Start job
result = job_manager.start_job(file_id, user_id=user_id)
print('START:', json.dumps(result, default=str))
job_id = result['job_id']

# Wait 3 seconds
time.sleep(3)

# Check active-job response (what the browser gets first)
active = job_manager.get_active_job_for_file(file_id, current_user_id=user_id)
print('ACTIVE-JOB RESPONSE:', json.dumps(active, default=str))

# Check URLs (what the browser gets using job_id)
urls, code = job_manager.get_job_urls(job_id, current_user_id=user_id)
print('URLS RESPONSE CODE:', code)
url_count = len(urls) if isinstance(urls, list) else 'NOT A LIST: ' + str(type(urls))
print('URLS COUNT:', url_count)

if isinstance(urls, list) and urls:
    print('FIRST 3 URLS:', json.dumps(urls[:3], default=str))

# Simulate what app.py sends to browser (wraps statuses)
response_body = {'job_id': job_id, 'statuses': urls if isinstance(urls, list) else [], 'count': len(urls) if isinstance(urls, list) else 0}
print('API RESPONSE KEYS:', list(response_body.keys()))
print('statuses is array:', isinstance(response_body['statuses'], list))

# Stop
job_manager.stop_job(job_id, current_user_id=user_id)
print('STOPPED OK')
