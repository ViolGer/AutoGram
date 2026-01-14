from __future__ import annotations

from datetime import datetime, timezone

from telethon import TelegramClient
from sqlmodel import Session, select, or_

from app.core.config import settings
from app.models import NewItem, Source


def _tg_username_from_url(url: str) -> str:

    u = url.strip()
    u = u.replace("https://t.me/", "").replace("http://t.me/", "")
    u = u.replace("t.me/", "")
    u = u.lstrip("@").strip("/")

    if "/" in u:
        u = u.split("/", 1)[0]
    return u


def _as_aware(dt: datetime | None) -> datetime:
    if dt is None:
        return datetime.now(timezone.utc)
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _looks_like_content(text: str) -> bool:
    return len(text) >= 20


async def parse_telegram_sources_async(db: Session, limit_per_channel: int = 20) -> dict:
    sources = db.exec(
        select(Source).where(Source.enabled == True, Source.type == "telegram")  # noqa: E712
    ).all()

    if not sources:
        return {"sources": 0, "added": 0}

    added_total = 0

    client = TelegramClient(
        settings.TG_SESSION_NAME,
        settings.TG_API_ID,
        settings.TG_API_HASH,
    )

    async with client:
        for src in sources:
            username = _tg_username_from_url(src.url)

            entity = await client.get_entity(username)
            messages = await client.get_messages(entity, limit=limit_per_channel)

            for m in messages:
                text = (m.message or "").strip()
                if not text or not _looks_like_content(text):
                    continue

                post_url = f"https://t.me/{username}/{m.id}"
                published_at = _as_aware(m.date)

                title = text.splitlines()[0][:200]
                summary = text[:500]

                # Дедуп:
                # 1) по url (основной)
                # 2) fallback: по (source, published_at, title) — на случай, если структура поменяется
                exists = db.exec(
                    select(NewItem).where(
                        or_(
                            NewItem.url == post_url,
                            (NewItem.source == src.name) &
                            (NewItem.published_at == published_at) &
                            (NewItem.title == title),
                        )
                    )
                ).first()
                if exists:
                    continue

                db.add(
                    NewItem(
                        title=title,
                        url=post_url,
                        summary=summary,
                        source=src.name,
                        published_at=published_at,
                        raw_text=text,
                    )
                )
                added_total += 1

    db.commit()

    return {"sources": len(sources), "added": added_total}
