import asyncio
import os
import re
import sys
from datetime import datetime

from dotenv import load_dotenv
from telethon import TelegramClient, events
from winotify import Notification, audio


load_dotenv()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")
TARGET_CHATS_RAW = [item.strip() for item in os.getenv("TARGET_CHATS", "").split(",") if item.strip()]
KEYWORDS = [item.strip() for item in os.getenv("KEYWORDS", "").split(",") if item.strip()]


def require_config() -> None:
    missing = []
    if not API_ID:
        missing.append("TELEGRAM_API_ID")
    if not API_HASH:
        missing.append("TELEGRAM_API_HASH")
    if not KEYWORDS:
        missing.append("KEYWORDS")
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(f"Missing required setting(s): {joined}. Copy .env.example to .env and fill them in.")


def build_keyword_pattern(keywords: list[str]) -> re.Pattern[str]:
    escaped = []
    for keyword in sorted(keywords, key=len, reverse=True):
        parts = [re.escape(part) for part in keyword.split()]
        escaped.append(r"\s+".join(parts))
    return re.compile(rf"(?<!\w)({'|'.join(escaped)})(?!\w)", re.IGNORECASE)


def parse_target_chats(targets: list[str]) -> list[int | str]:
    parsed = []
    for target in targets:
        try:
            parsed.append(int(target))
        except ValueError:
            parsed.append(target)
    return parsed


def show_notification(title: str, message: str) -> None:
    toast = Notification(
        app_id="Telegram Keyword Alert",
        title=title[:64],
        msg=message[:240],
        duration="long",
    )
    toast.set_audio(audio.Default, loop=False)
    toast.show()


async def main() -> None:
    require_config()
    pattern = build_keyword_pattern(KEYWORDS)

    client = TelegramClient("telegram_alert_session", int(API_ID), API_HASH)

    target_chats = parse_target_chats(TARGET_CHATS_RAW)
    chats_filter = target_chats or None

    @client.on(events.NewMessage(chats=chats_filter, incoming=True))
    async def handler(event: events.NewMessage.Event) -> None:
        text = event.raw_text or ""
        match = pattern.search(text)
        if not match:
            return

        chat = await event.get_chat()
        sender = await event.get_sender()
        chat_title = getattr(chat, "title", None) or getattr(chat, "username", None) or "Telegram"
        sender_name = "Unknown sender"
        if sender:
            first_name = getattr(sender, "first_name", "") or ""
            last_name = getattr(sender, "last_name", "") or ""
            username = getattr(sender, "username", "") or ""
            sender_name = " ".join(part for part in [first_name, last_name] if part).strip() or username or sender_name

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        alert_title = f"{match.group(0)} in {chat_title}"
        alert_message = f"{sender_name}: {text}"

        print(f"[{timestamp}] {alert_title}\n{alert_message}\n")
        show_notification(alert_title, alert_message)

    print("Starting Telegram keyword watcher...")
    print(f"Watching: {', '.join(TARGET_CHATS_RAW) if TARGET_CHATS_RAW else 'all accessible chats'}")
    print(f"Keywords: {', '.join(KEYWORDS)}")
    print("The first run will ask for your Telegram phone number, login code, and maybe 2FA password.")

    await client.start(phone=PHONE)
    print("Connected. Leave this window open to keep alerts running.")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
