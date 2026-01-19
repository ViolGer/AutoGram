from __future__ import annotations

from fastapi import APIRouter
from celery.result import AsyncResult

from app.celery_app import celery_app
from app.tasks import task_parse_html_sources, task_parse_telegram_sources

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("/parse/html")
def enqueue_parse_html():
    job = task_parse_html_sources.delay()
    return {"task_id": job.id, "status": "queued"}


@router.post("/parse/telegram")
def enqueue_parse_telegram(limit_per_channel: int = 20):
    job = task_parse_telegram_sources.delay(limit_per_channel)
    return {"task_id": job.id, "status": "queued"}


@router.get("/{task_id}")
def get_task_status(task_id: str):
    res = AsyncResult(task_id, app=celery_app)
    payload = {
        "task_id": task_id,
        "state": res.state,
    }
    # result может быть dict (у нас так), или ошибка
    if res.successful():
        payload["result"] = res.result
    elif res.failed():
        payload["error"] = str(res.result)
    return payload
