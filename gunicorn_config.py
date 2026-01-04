"""
Gunicorn configuration for production deployment.
Optimized for high traffic and millions of users.
"""
import multiprocessing
import os

# Server socket
bind = os.getenv('GUNICORN_BIND', '0.0.0.0:8000')
backlog = 2048

# Worker processes
workers = int(os.getenv('GUNICORN_WORKERS', multiprocessing.cpu_count() * 2 + 1))
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 5

# Logging
accesslog = '-'
errorlog = '-'
loglevel = os.getenv('GUNICORN_LOG_LEVEL', 'info')
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = 'football_predictor'

# Server mechanics
daemon = False
pidfile = '/tmp/gunicorn.pid'
umask = 0
user = None
group = None
tmp_upload_dir = None

# SSL (if using HTTPS directly)
# keyfile = '/path/to/keyfile'
# certfile = '/path/to/certfile'

# Performance tuning
max_requests = 1000  # Restart workers after this many requests to prevent memory leaks
max_requests_jitter = 50  # Add randomness to prevent all workers restarting at once
preload_app = True  # Load application code before forking workers

# Graceful timeout for worker shutdown
graceful_timeout = 30

# StatsD integration (optional, for monitoring)
# statsd_host = 'localhost:8125'
# statsd_prefix = 'gunicorn'

