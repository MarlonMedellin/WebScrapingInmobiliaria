import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "worker",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=["tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Bogota",
    enable_utc=True,
    beat_schedule={
        "cleanup-stale-properties-daily": {
            "task": "cleanup_stale_properties",
            "schedule": 86400.0, # Every 24 hours
            "args": (3,), # Age in days
        },
    },
)

# Import tasks so they are registered
# from scrapers.tasks import scrape_fincaraiz_task
