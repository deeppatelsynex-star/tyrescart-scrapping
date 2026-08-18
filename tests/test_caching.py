import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'app'))

from cache_manager import cache, invalidate_scraper_cache, invalidate_log_cache, get_cached_excel_rows, get_cached_excel_urls
import files_repo
import reports_repo
import job_manager

def test_cache_system():
    print("=================================================")
    print("Testing In-Memory Caching System for Scrapers & Logs")
    print("=================================================")

    # 1. Basic TTLCache test
    cache.clear()
    cache.set('test:k1', {'foo': 'bar'}, ttl=1)
    assert cache.get('test:k1') == {'foo': 'bar'}
    time.sleep(1.1)
    assert cache.get('test:k1') is None, "TTL expiration failed!"
    print("1. TTLCache basic operations & TTL expiry OK.")

    # 2. Prefix invalidation test
    cache.set('files:1', 'f1', ttl=60)
    cache.set('files:2', 'f2', ttl=60)
    cache.set('logs:1', 'l1', ttl=60)
    cache.invalidate_prefix('files:')
    assert cache.get('files:1') is None
    assert cache.get('files:2') is None
    assert cache.get('logs:1') == 'l1'
    print("2. Prefix invalidation ('files:') OK.")

    # 3. Scraper data caching test (files_repo)
    cache.clear()
    res1, total1 = files_repo.list_files(page=1, per_page=10)
    # Cached hit
    assert cache.get('files:p1:pp10:dNone:qNone') is not None, "list_files was not cached!"
    res2, total2 = files_repo.list_files(page=1, per_page=10)
    assert total1 == total2
    print("3. files_repo.list_files in-memory caching OK.")

    # 4. Scraper file record caching & invalidation test
    if res1:
        fid = res1[0]['file_id']
        f_rec = files_repo.get_file(fid)
        assert cache.get(f'file:{fid}') is not None, "get_file was not cached!"
        # Test invalidation on update
        files_repo.set_working(fid, 0)
        assert cache.get(f'file:{fid}') is None, "Cache should be invalidated after set_working!"
        print(f"4. get_file(file_id={fid}) caching & invalidation OK.")

    # 5. Log stats & log query caching test (reports_repo)
    cache.clear()
    stats1 = reports_repo.get_logs_summary_stats()
    assert cache.get('stats:summary') is not None, "get_logs_summary_stats was not cached!"
    stats2 = reports_repo.get_logs_summary_stats()
    assert stats1 == stats2
    print("5. reports_repo.get_logs_summary_stats caching OK.")

    logs1, ltotal1 = reports_repo.list_logs(page=1, per_page=10)
    assert cache.get('logs:p1:pp10:sNone:uNone:fNone:qNone') is not None, "list_logs was not cached!"
    print("6. reports_repo.list_logs query caching OK.")

    # 6. Excel file row & URL caching test
    test_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'test_temp.txt')
    with open(test_file, 'w') as f:
        f.write("hello\nworld\n")

    call_count = [0]
    def mock_parser(path):
        call_count[0] += 1
        return 2

    c1 = get_cached_excel_rows(test_file, mock_parser)
    c2 = get_cached_excel_rows(test_file, mock_parser)
    assert c1 == 2 and c2 == 2
    assert call_count[0] == 1, "Cached Excel rows should only parse file once!"
    print("7. Excel parser file mtime caching OK.")

    if os.path.exists(test_file):
        os.remove(test_file)

    print("=================================================")
    print("ALL CACHING TESTS PASSED PERFECTLY!")
    print("=================================================")

if __name__ == '__main__':
    test_cache_system()
    os._exit(0)
