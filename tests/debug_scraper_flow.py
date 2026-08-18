import sys
sys.path.insert(0, 'app')
from app import app
from db import get_connection
import time

with app.test_client() as client:
    conn = get_connection()
    with conn.cursor() as c:
        c.execute('SELECT userid FROM userTbl WHERE Role = "SuperAdmin" LIMIT 1')
        user_id = c.fetchone()['userid']
    conn.close()

    with client.session_transaction() as sess:
        sess['user_id'] = user_id
        sess['role'] = 'SuperAdmin'
        sess['csrf_token'] = 'test_csrf'

    # Stop file 35 if running
    client.post('/api/files/35/stop', headers={'X-CSRF-Token': 'test_csrf'})

    # Start file 35
    start_res = client.post('/api/files/35/start', headers={'X-CSRF-Token': 'test_csrf'}).get_json()
    print('Start file 35:', start_res)
    job_id = start_res['job_id']

    time.sleep(3)

    status = client.get(f'/api/scraper/job/{job_id}/status').get_json()
    print('Job status after 3s:', status)

    urls = client.get(f'/api/scraper/job/{job_id}/urls').get_json()
    print('Job urls count after 3s:', len(urls))
    if urls:
        print('Sample urls:', urls[:3])

    client.post('/api/files/35/stop', headers={'X-CSRF-Token': 'test_csrf'})
