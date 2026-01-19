from __future__ import annotations

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "autogram",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Минимальные настройки
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
)

# Автоподхват задач из app/tasks.py
celery_app.autodiscover_tasks(["app"])


from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    # каждые 10 минут парсим html
    "parse-html-every-10-min": {
        "task": "parse_html_sources",
        "schedule": crontab(minute="*/10"),
    },
    # telegram можно включить позже (пока выключено)
    # "parse-telegram-every-30-min": {
    #     "task": "parse_telegram_sources",
    #     "schedule": crontab(minute="*/30"),
    #     "args": (5,),  # limit_per_channel
    # },
}
