"""
Script to list all Telegram chats and their IDs.
Run this first to find SOURCE_CHAT_ID and TARGET_CHAT_ID.
"""

import json
import asyncio
from telethon import TelegramClient
from telethon.tl.types import Channel, Chat, User

CONFIG_FILE = "telegram_config.json"


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


async def main():
    config = load_config()

    client = TelegramClient(
        "session_getchat",
        config["api_id"],
        config["api_hash"]
    )

    await client.start(phone=config["phone"])
    print("\n" + "=" * 70)
    print("DANH SACH TAT CA CHAT / NHOM / KENH")
    print("=" * 70)
    print(f"{'TEN':<40} {'CHAT ID':<20} {'LOAI'}")
    print("-" * 70)

    async for dialog in client.iter_dialogs():
        entity = dialog.entity
        if isinstance(entity, Channel):
            chat_type = "Kenh" if entity.broadcast else "Nhom"
        elif isinstance(entity, Chat):
            chat_type = "Nhom"
        elif isinstance(entity, User):
            chat_type = "Ca nhan"
        else:
            chat_type = "Khac"

        name = dialog.name[:38] if len(dialog.name) > 38 else dialog.name
        print(f"{name:<40} {dialog.id:<20} {chat_type}")

    print("=" * 70)
    print("\nSao chep Chat ID vao telegram_config.json:")
    print("  source_chat_id: ID nhom NGUON (nhom ban muon nghe)")
    print("  target_chat_id: ID nhom DICH (nhom ban muon gui vao)")
    print()

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
