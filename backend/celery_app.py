from celery import Celery
import os

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
CELERY_RESULTS_BACKEND_URL = os.getenv("CELERY_RESULTS_BACKEND_URL", REDIS_URL)

celery_app = Celery(
    "sales_researcher",
    broker=REDIS_URL,
    backend=CELERY_RESULTS_BACKEND_URL,
    include=[
        "backend.tasks.health_check_task", # Keep existing tasks
        "backend.tasks.gemini_tasks", # Add the new Gemini tasks module
        "backend.tasks.gemini_research", # Keep existing tasks
        "backend.tasks.content_extraction" # Keep existing tasks
    ]
)

celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='UTC',
    enable_utc=True,
)