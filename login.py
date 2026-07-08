import asyncio
import getpass
import json
import os
import sys

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError


load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")
STATE_FILE = "login_state.json"
CALL_TIMEOUT_SECONDS = 45


async def wait_for(coro):
    return await asyncio.wait_for(coro, timeout=CALL_TIMEOUT_SECONDS)


async def main() -> None:
    if not API_ID or not API_HASH or not PHONE:
        raise SystemExit("Set TELEGRAM_API_ID, TELEGRAM_API_HASH, and TELEGRAM_PHONE in .env first.")

    client = TelegramClient("telegram_alert_session", int(API_ID), API_HASH)
    print("Connecting to Telegram...", flush=True)
    await wait_for(client.connect())

    if await wait_for(client.is_user_authorized()):
        print("Already logged in.")
        await client.disconnect()
        return

    if len(sys.argv) > 1:
        code = sys.argv[1].strip()
    else:
        print("Requesting a fresh login code...", flush=True)
        sent = await wait_for(client.send_code_request(PHONE))
        with open(STATE_FILE, "w", encoding="utf-8") as file:
            json.dump({"phone_code_hash": sent.phone_code_hash}, file)
        print(f"Code sent via: {type(sent.type).__name__}", flush=True)
        if sent.next_type:
            print(f"Next delivery option: {type(sent.next_type).__name__}", flush=True)
        if sent.timeout:
            print(f"Retry/next option timeout: {sent.timeout} seconds", flush=True)
        print("Run: python login.py YOUR_CODE_HERE", flush=True)
        await client.disconnect()
        return

    print("Signing in with the code...", flush=True)
    try:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE, "r", encoding="utf-8") as file:
                state = json.load(file)
            await wait_for(client.sign_in(PHONE, code, phone_code_hash=state["phone_code_hash"]))
        else:
            await wait_for(client.sign_in(PHONE, code))
    except SessionPasswordNeededError:
        password = (
            sys.argv[2].strip()
            if len(sys.argv) > 2
            else os.getenv("TELEGRAM_2FA_PASSWORD")
            or getpass.getpass("Two-step verification password: ")
        )
        print("Signing in with the two-step verification password...", flush=True)
        await wait_for(client.sign_in(password=password))

    me = await wait_for(client.get_me())
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    print(f"Logged in as {getattr(me, 'first_name', '')} {getattr(me, 'last_name', '')}".strip())
    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
