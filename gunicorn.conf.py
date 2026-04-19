"""Gunicorn settings: ASGI (Uvicorn worker) for FastAPI — avoids WSGI/sync worker misconfiguration."""
import os

bind = f"0.0.0.0:{os.environ.get('PORT', '8000')}"
worker_class = "uvicorn.workers.UvicornWorker"
workers = 1
timeout = 120
graceful_timeout = 30
