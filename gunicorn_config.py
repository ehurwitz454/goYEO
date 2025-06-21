# gunicorn_config.py
import multiprocessing
import os

# Use only 1 worker for Dash apps to avoid callback issues
workers = 1  # Don't use multiple workers with Dash!
worker_class = "sync"  # or "gevent" for async
worker_connections = 1000
timeout = 120
keepalive = 5

# Important for Dash
preload_app = True  # This can cause issues with Dash, try False if having problems

# Binding
bind = f"0.0.0.0:{os.environ.get('PORT', 8050)}"

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
