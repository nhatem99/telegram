"""
Telegram Message Filter Bot
Listens to a source group and forwards matching messages to a target group.
"""

import json
import logging
import asyncio
import re
from telethon import TelegramClient, events
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

LINK_PATTERN = re.compile(r"(https?://|www\.|t\.me/)\S+", re.IGNORECASE)

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
    with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def get_group_settings(config: dict, chat_id: int) -> dict:
    """Merge global settings with per-group overrides."""
    base = {
        "keywords":      config.get("keywords", []),
        "blocked_users": config.get("blocked_users", []),
        "allowed_users": config.get("allowed_users", []),
        "allowed_names": config.get("allowed_names", []),
        "block_links":   config.get("block_links", False),
        "strip_links":   config.get("strip_links", False),
        "allow_media":   config.get("allow_media", False),
        "forward_mode":  config.get("forward_mode", "copy"),
        "target_chat_ids": None,
    }
    override = config.get("group_settings", {}).get(str(chat_id), {})
    base.update(override)
    return base


def remove_links(text: str) -> str:
    cleaned = LINK_PATTERN.sub("", text)
    return re.sub(r"\n{3,}", "\n\n", cleaned).strip()


def contains_keyword(text: str, keywords: list) -> list:
    if not keywords:
        return ["(tat ca)"]
    text_lower = text.lower()
    return [kw for kw in keywords if kw.lower() in text_lower]


def is_blocked_user(username: str | None, blocked: list) -> bool:
    if not username or not blocked:
        return False
    return username.lower() in [b.lower() for b in blocked]


def print_header():
    print("=" * 70)
    print("  TELEGRAM MESSAGE FILTER BOT")
    print("=" * 70)


async def main():
    config = load_config()

    source_ids = config.get("source_chat_ids") or [config["source_chat_id"]]
    target_ids = config.get("target_chat_ids") or [config["target_chat_id"]]
    group_settings = config.get("group_settings", {})

    client = TelegramClient("session", config["api_id"], config["api_hash"])
    await client.start(phone=config["phone"])

    print_header()
    me = await client.get_me()
    print(f"\n  Da dang nhap: {me.first_name} (@{me.username})")
    print(f"  Nghe tu     : {len(source_ids)} nhom")
    print(f"  Gui vao     : {target_ids}")
    if group_settings:
        print(f"  Cai dat rieng: {list(group_settings.keys())}")
    print("\n  Bot dang chay - san sang loc tin nhan...\n")
    print("=" * 70 + "\n")

    @client.on(events.NewMessage(chats=source_ids))
    async def handler(event):
        msg = event.message
        text = msg.text or ""
        chat_id = event.chat_id
        gs = get_group_settings(config, chat_id)

        sender = await msg.get_sender()
        sender_username = getattr(sender, "username", None)
        sender_name = (
            getattr(sender, "first_name", None)
            or getattr(sender, "title", None)
            or "Unknown"
        )
        if getattr(sender, "last_name", None):
            sender_name += f" {sender.last_name}"

        # Filter: blocked users
        if is_blocked_user(sender_username, gs["blocked_users"]):
            logger.info(f"  SKIP (user bi chan): {sender_name} | chat={chat_id}")
            return

        # Filter: allowed users whitelist (by username)
        if gs["allowed_users"] and sender_username and sender_username.lower() not in [a.lower() for a in gs["allowed_users"]]:
            logger.info(f"  SKIP (khong trong whitelist): {sender_name} | chat={chat_id}")
            return

        # Filter: allowed names whitelist (by display name)
        if gs["allowed_names"] and sender_name.lower() not in [a.lower() for a in gs["allowed_names"]]:
            logger.info(f"  SKIP (ten khong trong whitelist): {sender_name} | chat={chat_id}")
            return

        # Filter: media-only when not allowed
        has_media = isinstance(msg.media, (MessageMediaPhoto, MessageMediaDocument))
        if has_media and not gs["allow_media"] and not text:
            logger.info(f"  SKIP (chi co media): {sender_name} | chat={chat_id}")
            return

        # Filter: keywords
        matched = contains_keyword(text, gs["keywords"])
        if not matched and gs["keywords"]:
            short = (text[:60] + "...") if len(text) > 60 else text
            print(f"  SKIP  | [{chat_id}] {sender_name}")
            print(f"         | Ly do: Khong co keyword")
            print(f"         | Tin  : {short}\n")
            return

        # Filter: block links (bỏ qua nếu đã khớp keyword)
        has_link = bool(LINK_PATTERN.search(text))
        keyword_matched = bool(gs["keywords"]) and matched != ["(tat ca)"]
        if has_link and gs["block_links"] and not keyword_matched:
            logger.info(f"  SKIP (co link, khong co keyword): {sender_name} | chat={chat_id}")
            return
        if has_link and gs["strip_links"]:
            text = remove_links(text)

        # Forward
        short = (text[:60] + "...") if len(text) > 60 else text
        for target_id in (gs["target_chat_ids"] or target_ids):
            try:
                if gs["forward_mode"] == "forward":
                    await client.forward_messages(target_id, msg)
                else:
                    caption = f"[Tu: {sender_name}]\n{text}" if text else f"[Tu: {sender_name}]"
                    if has_media and gs["allow_media"]:
                        try:
                            await client.send_file(target_id, msg.media, caption=caption)
                        except Exception:
                            notice = caption + "\n⚠️ [Co hinh anh nhung khong the copy]"
                            await client.send_message(target_id, notice)
                    else:
                        await client.send_message(target_id, caption)
            except Exception as e:
                logger.error(f"LOI khi forward toi {target_id}: {e}")

        print(f"  OK    | [{chat_id}] {sender_name}")
        print(f"         | Keyword: {', '.join(matched)}")
        print(f"         | Tin  : {short}\n")
        logger.info(f"FORWARDED | chat={chat_id} | {sender_name} | keywords={matched}")

    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
