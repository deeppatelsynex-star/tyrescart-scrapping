import os

# Production Gunicorn configuration optimized for Render & low-memory environments
bind = f"0.0.0.0:{os.environ.get('PORT', '5000')}"

# Use 1-2 workers with gthread for concurrent web requests without memory bloat
workers = int(os.environ.get('WEB_CONCURRENCY', '1'))
threads = 4
worker_class = 'gthread'

# Extended timeout (5 minutes) to prevent Gunicorn from killing workers during long scrapers / exports
timeout = 300
keepalive = 5
graceful_timeout = 30

# Periodic recycling to prevent memory leaks over time
max_requests = 1000
max_requests_jitter = 50
