import os

# Production Gunicorn configuration optimized for Render & persistent scraping
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Use 1 worker with gthread (16 threads) so SSE streams and parallel requests have ample capacity
workers = 1
threads = int(os.environ.get('GUNICORN_THREADS', '16'))
worker_class = 'gthread'

# Disable worker timeouts (timeout = 0) so long crawls and SSE streams never get killed
timeout = 0
keepalive = 65
graceful_timeout = 30

# Disable automatic worker recycling to prevent killing active background scraper processes
max_requests = 0
max_requests_jitter = 0
