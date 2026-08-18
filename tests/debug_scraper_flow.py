import sys
sys.path.insert(0, 'app')
from app import app
from db import get_connection
import json

with app.test_client() as client:
    conn = get_connection()
    with conn.cursor() as c:
        c.execute('SELECT file_id, site_name FROM fileTbl WHERE is_deleted = 0 LIMIT 1')
        file_row = c.fetchone()
        file_id = file_row['file_id']
        site_name = file_row['site_name']
        c.execute('SELECT userid FROM userTbl WHERE Role = "SuperAdmin" LIMIT 1')
        user_id = c.fetchone()['userid']
    conn.close()

    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['role'] = 'SuperAdmin'
        sess['csrf_token'] = 'test_csrf'

    print('--- 1. Testing IDLE file_id =', file_id, '(', site_name, ')')
    r_active = client.get(f'/api/scraper/file/{file_id}/active-job')
    print('/active-job:', r_active.status_code, r_active.get_json())

    r_status = client.get(f'/api/files/{file_id}/status')
    print('/status:', r_status.status_code, r_status.get_json())

    r_urls = client.get(f'/api/files/{file_id}/url-statuses')
    urls_data = r_urls.get_json()
    count = len(urls_data.get('statuses', [])) if isinstance(urls_data, dict) else len(urls_data)
    print('/url-statuses:', r_urls.status_code, 'count:', count)

    print('\n--- 2. Starting file_id =', file_id)
    r_start = client.post(f'/api/files/{file_id}/start', headers={'X-CSRF-Token': 'test_csrf'})
    start_data = r_start.get_json()
    print('/start response:', r_start.status_code, start_data)
    job_id = start_data['job_id']

    r_active_run = client.get(f'/api/scraper/file/{file_id}/active-job')
    print('/active-job while running:', r_active_run.status_code, r_active_run.get_json())

    r_job_status = client.get(f'/api/scraper/job/{job_id}/status')
    print('/job/status while running:', r_job_status.status_code, r_job_status.get_json())

    r_job_urls = client.get(f'/api/scraper/job/{job_id}/urls')
    urls_job_data = r_job_urls.get_json()
    print('/job/urls while running:', r_job_urls.status_code, 'count:', len(urls_job_data))

    client.post(f'/api/files/{file_id}/stop', headers={'X-CSRF-Token': 'test_csrf'})
