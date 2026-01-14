from __future__ import annotations

import asyncio
from datetime import datetime
from typing import Optional

from telethon import TelegramClient

import os

try:
    from app.core.config import settings  # type: ignore
except Exception:
    settings = None


def _get_cfg() -> tuple[int, str, str]:

    if settings is not None:
        api_id = int(getattr(settings, "TG_API_ID"))
        api_hash = str(getattr(settings, "TG_API_HASH"))
        session_name = str(getattr(settings, "TG_SESSION_NAME", "autogram"))
        return api_id, api_hash, session_name

    api_id = int(os.environ["TG_API_ID"])
    api_hash = os.environ["TG_API_HASH"]
    session_name = os.environ.get("TG_SESSION_NAME", "autogram")
    return api_id, api_hash, session_name


async def main() -> None:
    api_id, api_hash, session_name = _get_cfg()

    channel = "@ui_jedi"
    limit = 15

    async with TelegramClient(session_name, api_id, api_hash) as client:
        # resolve entity (проверка что канал доступен)
        entity = await client.get_entity(channel)

        print(f"✅ Connected. Reading last {limit} messages from {channel} …\n")

        messages = await client.get_messages(entity, limit=limit)

        if not messages:
            print("⚠️ No messages found (empty channel or no access).")
            return

        for m in reversed(messages):
            dt: Optional[datetime] = m.date
            dt_str = dt.strftime("%Y-%m-%d %H:%M:%S") if dt else "no-date"
            text = (m.message or "").replace("\n", " ").strip()
            preview = (text[:120] + "…") if len(text) > 120 else text
            print(f"[{dt_str}] {preview}")


if __name__ == "__main__":
    asyncio.run(main())
