import asyncio
import os
import sys

from dotenv import load_dotenv
from telethon import TelegramClient


load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")


async def main() -> None:
    if not API_ID or not API_HASH:
        raise SystemExit("Copy .env.example to .env and fill in TELEGRAM_API_ID and TELEGRAM_API_HASH first.")

    client = TelegramClient("telegram_alert_session", int(API_ID), API_HASH)
    await client.start(phone=PHONE)

    print("Your chats:")
    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        username = getattr(entity, "username", None)
        print(f"id={dialog.id} | title={dialog.name} | username={username or ''}")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
