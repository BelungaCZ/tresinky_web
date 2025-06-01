# Gunicorn configuration file
# Documentation: https://docs.gunicorn.org/en/stable/settings.html

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
# Recommendation: (2 x CPU cores) + 1
# For production with sufficient RAM, use 4 workers
# Currently using 1 worker due to 512MB RAM limitation on server
workers = 1

# Worker class
worker_class = "sync"
worker_connections = 1000

# Worker timeout
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Preload application for better performance
preload_app = True

# Logging
loglevel = "info"
# Log to file with size limit (1MB max)
accesslog = "/app/logs/gunicorn.log"
errorlog = "/app/logs/gunicorn.log"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Log rotation settings (requires logrotate or manual management)
# Create logs directory in Dockerfile

# Process naming
proc_name = "tresinky_web"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (disabled, handled by nginx-proxy)
# keyfile = None
# certfile = None

# Performance tuning for low-memory server
worker_tmp_dir = "/dev/shm"  # Use shared memory for better performance 