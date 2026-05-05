import asyncio
from pyrogram import Client, filters
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

from Curse.bot_class import pbot
from Curse.database.chats_db import Chats
from Curse.database.users_db import Users
from Curse import OWNER_ID

# ─────────────────────────────────────────────────────────────
# Helper wrappers to auto‑handle FloodWait
# ─────────────────────────────────────────────────────────────
async def _safe_forward(client: Client, chat_id: int, from_chat: int,
                        msg_id: int, sleep: float = 0.5) -> bool:
    """Forward and survive FloodWait. Return True if succeed."""
    while True:
        try:
            await client.forward_messages(chat_id, from_chat, msg_id)
            await asyncio.sleep(sleep)
            return True
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 1)
        except RPCError:
            return False


async def _safe_send(client: Client, chat_id: int, text: str,
                     reply_id: int | None = None,
                     sleep: float = 0.5) -> bool:
    """Send text safely. Return True if succeed."""
    while True:
        try:
            await client.send_message(chat_id, text, reply_to_message_id=reply_id)
            await asyncio.sleep(sleep)
            return True
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 1)
        except RPCError:
            return False


# ─────────────────────────────────────────────────────────────
# /pcast command
# ─────────────────────────────────────────────────────────────
@pbot.on_message(
    filters.command("pcast") &
    filters.user(OWNER_ID),
    group=12345)
async def broadcast_post(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("Reply to a post to broadcast.")

    if len(message.command) < 2:
        return await message.reply_text("Usage: /pcast <group|users|all>")

    mode = message.command[1].lower()
    target_groups = mode in ("group", "all")
    target_users  = mode in ("users", "all")

    if not (target_groups or target_users):
        return await message.reply_text("Invalid option. Use group / users / all.")

    src_chat_id = message.chat.id
    src_msg_id  = message.reply_to_message.id

    failed_chats = failed_users = 0

    # --- broadcast to groups ---------------------------------
    if target_groups:
        chat_ids = Chats.list_chats_by_id()  # list[int]
        for chat_id in chat_ids:
            ok = await _safe_forward(pbot, chat_id, src_chat_id, src_msg_id)
            if not ok:
                failed_chats += 1

    # --- broadcast to users ----------------------------------
    if target_users:
        user_ids = [user["_id"] for user in Users.list_users()]
        text = "📢 New broadcast message:"
        for uid in user_ids:
            ok = await _safe_send(pbot, uid, text, reply_id=src_msg_id)
            if not ok:
                failed_users += 1

    # --- summary ---------------------------------------------
    summary = []
    if target_groups:
        summary.append(f"Groups failed: {failed_chats}")
    if target_users:
        summary.append(f"Users failed: {failed_users}")

    await message.reply_text("✅ Broadcast finished.\n" + "\n".join(summary))
