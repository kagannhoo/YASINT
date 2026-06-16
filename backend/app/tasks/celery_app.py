from celery import Celery
from celery.schedules import crontab

from ..config import get_settings

settings = get_settings()

celery_app = Celery(
    "yasint",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.tasks.analysis_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    beat_schedule={
        "cleanup-old-uploads": {
            "task": "app.tasks.analysis_tasks.cleanup_old_uploads",
            "schedule": crontab(hour=3, minute=0),
        },
    },
)

# Görevlerin worker'a kayıt olmasını garanti et
import app.tasks.analysis_tasks  # noqa: E402, F401
