from app.core.celery_app import celery_app

# This file acts as the entrypoint for the Celery worker
# Run with: celery -A worker.celery_app worker --loglevel=info
