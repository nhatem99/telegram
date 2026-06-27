"""
Telegram Message Filter Bot
Listens to a source group and forwards matching messages to a target group.
"""

import json
import logging
import asyncio
from datetime import datetime
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

CONFIG_FILE = "telegram_config.json"
LOG_FILE = "filter_log.txt"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def contains_keyword(text: str, keywords: list[str]) -> list[str]:
    if not keywords:
        return ["(tat ca)"]
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def is_blocked_user(sender_username: str | None, blocked: list[str]) -> bool:
    if not sender_username or not blocked:
        return False
    return sender_username.lower() in [b.lower() for b in blocked]


def print_header():
    print("=" * 70)
    print("  TELEGRAM MESSAGE FILTER BOT")
    print("=" * 70)


async def main():
    config = load_config()

    source_id = config["source_chat_id"]
    target_id = config["target_chat_id"]
    keywords = config.get("keywords", [])
    blocked = config.get("blocked_users", [])
    allow_media = config.get("allow_media", False)
    forward_mode = config.get("forward_mode", "copy")

    client = TelegramClient("session", config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"])

    print_header()
    me = await client.get_me()
    print(f"\n  Da dang nhap: {me.first_name} (@{me.username})")
    print(f"  Nghe tu chat : {source_id}")
    print(f"  Gui vao chat : {target_id}")
    print(f"  Keywords     : {keywords if keywords else '(tat ca tin nhan)'}")
    print(f"  Cho phep media: {allow_media}")
    print(f"  Che do forward: {forward_mode}")
    print("\n  Bot dang chay - san sang loc tin nhan...\n")
    print("=" * 70 + "\n")

    @client.on(events.NewMessage(chats=source_id))
    async def handler(event):
        msg = event.message
        text = msg.text or ""
        sender = await msg.get_sender()

        sender_username = getattr(sender, "username", None)
        sender_name = getattr(sender, "first_name", "Unknown")
        if getattr(sender, "last_name", None):
            sender_name += f" {sender.last_name}"

        # Filter 1: blocked users
        if is_blocked_user(sender_username, blocked):
            logger.info(f"  SKIP (user bi chan): {sender_name}")
            return

        # Filter 2: media-only messages when media not allowed
        has_media = isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument))
        if has_media and not allow_media:
            if not text:
                logger.info(f"  SKIP (chi co media): {sender_name}")
                return

        # Filter 3: keyword check (text messages only checked against text)
        matched = contains_keyword(text, keywords)
        if not matched and keywords:
            short = (text[:60] + "...") if len(text) > 60 else text
            print(f"  SKIP  | Tu: {sender_name}")
            print(f"         | Ly do: Khong co keyword")
            print(f"         | Tin  : {short}\n")
            return

        # Forward the message
        try:
            if forward_mode == "forward":
                await client.forward_messages(target_id, msg)
            else:
                caption = f"[Tu: {sender_name}]\n{text}" if text else f"[Tu: {sender_name}]"
                if has_media and allow_media:
                    await client.send_file(target_id, msg.media, caption=caption)
                else:
                    await client.send_message(target_id, caption)

            short = (text[:60] + "...") if len(text) > 60 else text
            print(f"  OK    | Tu: {sender_name}")
            print(f"         | Keyword: {', '.join(matched)}")
            print(f"         | Tin  : {short}\n")
            logger.info(f"FORWARDED | {sender_name} | keywords={matched}")

        except Exception as e:
            logger.error(f"LOI khi forward: {e}")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
