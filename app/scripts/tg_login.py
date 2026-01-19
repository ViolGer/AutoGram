import asyncio
from telethon import TelegramClient

from app.core.config import settings


async def main():
    client = TelegramClient(settings.TG_SESSION_NAME, settings.TG_API_ID, settings.TG_API_HASH)
    await client.start()
    print("✅ Telegram session created:", settings.TG_SESSION_NAME + ".session")
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
