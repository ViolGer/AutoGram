from __future__ import annotations

import asyncio
from celery import shared_task
from sqlmodel import Session

from app.db.deps import engine
from app.services.html_parser import parse_html_sources
from app.services.telegram_parser import parse_telegram_sources_async


@shared_task(name="parse_html_sources")
def task_parse_html_sources() -> dict:
    with Session(engine) as db:
        return parse_html_sources(db)


@shared_task(name="parse_telegram_sources")
def task_parse_telegram_sources(limit_per_channel: int = 20) -> dict:
    with Session(engine) as db:
        # telethon async → оборачиваем
        return asyncio.run(parse_telegram_sources_async(db, limit_per_channel=limit_per_channel))
