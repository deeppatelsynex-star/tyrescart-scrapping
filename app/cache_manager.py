"""Thread-Safe In-Memory Caching System for Scrapers, Logs, and Report Statistics.

Provides:
- Fast in-memory cache with configurable TTL
- Prefix-based invalidation (e.g. invalidate all 'files:*' on scraper create/update/delete)
- Excel file row count and URL list caching by file modification time
"""

import functools
import hashlib
import json
import logging
import os
import threading
import time

logger = logging.getLogger(__name__)


class TTLCache:
    """Thread-safe in-memory key-value cache with TTL and prefix invalidation."""

    def __init__(self, default_ttl=30):
        self.default_ttl = default_ttl
        self._store = {}
        self._lock = threading.RLock()

    def get(self, key):
        with self._lock:
            entry = self._store.get(key)
            if entry is None:
                return None
            val, expires_at = entry
            if time.time() > expires_at:
                del self._store[key]
                return None
            return val

    def set(self, key, value, ttl=None):
        ttl = self.default_ttl if ttl is None else ttl
        expires_at = time.time() + ttl
        with self._lock:
            self._store[key] = (value, expires_at)

    def delete(self, key):
        with self._lock:
            self._store.pop(key, None)

    def invalidate_prefix(self, prefix):
        """Invalidates all keys starting with prefix (e.g. 'files:', 'logs:', 'stats:')."""
        with self._lock:
            keys_to_del = [k for k in self._store if k.startswith(prefix)]
            for k in keys_to_del:
                del self._store[k]

    def clear(self):
        with self._lock:
            self._store.clear()


# Singleton global cache
cache = TTLCache(default_ttl=30)


# ==============================================================================
# Helper Invalidation Functions
# ==============================================================================

def invalidate_scraper_cache(file_id=None):
    """Invalidates cached scraper file lists and individual scraper records."""
    cache.invalidate_prefix("files:")
    if file_id:
        cache.delete(f"file:{file_id}")


def invalidate_log_cache(file_id=None):
    """Invalidates cached logs and report statistics."""
    cache.invalidate_prefix("logs:")
    cache.invalidate_prefix("stats:")
    if file_id:
        cache.delete(f"active_log:{file_id}")


# ==============================================================================
# Excel File Cache (Cached by file path + modification time)
# ==============================================================================

_excel_cache = {}
_excel_cache_lock = threading.Lock()


def get_cached_excel_rows(excel_path, count_func):
    """Caches the row count of an Excel file by (path, mtime) so heavy openpyxl
    file parsing isn't repeated on every status check.
    """
    if not excel_path or not os.path.exists(excel_path):
        return 0
    try:
        mtime = os.path.getmtime(excel_path)
    except OSError:
        return 0

    with _excel_cache_lock:
        cached = _excel_cache.get(excel_path)
        if cached and cached.get('mtime') == mtime and 'rows' in cached:
            return cached['rows']

    rows = count_func(excel_path)

    with _excel_cache_lock:
        if excel_path not in _excel_cache:
            _excel_cache[excel_path] = {}
        _excel_cache[excel_path]['mtime'] = mtime
        _excel_cache[excel_path]['rows'] = rows

    return rows


def get_cached_excel_urls(excel_path, parse_func):
    """Caches parsed URLs from a completed run's Excel file by (path, mtime)."""
    if not excel_path or not os.path.exists(excel_path):
        return []
    try:
        mtime = os.path.getmtime(excel_path)
    except OSError:
        return []

    with _excel_cache_lock:
        cached = _excel_cache.get(excel_path)
        if cached and cached.get('mtime') == mtime and 'urls' in cached:
            return cached['urls']

    urls = parse_func(excel_path)

    with _excel_cache_lock:
        if excel_path not in _excel_cache:
            _excel_cache[excel_path] = {}
        _excel_cache[excel_path]['mtime'] = mtime
        _excel_cache[excel_path]['urls'] = urls

    return urls
