import asyncio
from contextlib import suppress

from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message, ChatPermissions, InlineKeyboardButton, InlineKeyboardMarkup

from Curse import PREFIX_HANDLER
from Curse.bot_class import pbot as app
from Curse.extras.status import user_admin

C_HANDLER = PREFIX_HANDLER
SPAM_CHATS = []

# chat_id -> task flag (True means spamming)
ACTIVE_TAGS: set[int] = set()

MAX_MENTION_BATCH = 5          # mention 5 users per message
SLEEP_BETWEEN_BATCH = 2        # seconds

# ─────────────────────────────────────────────────────────────
# Tag all / cancel commands
# ─────────────────────────────────────────────────────────────

@app.on_message(
    (filters.command(["tagall", "all"], C_HANDLER) | filters.command("@all", ""))
    & filters.group,
    group=-98765,
)
@user_admin
async def tag_all_users(_, message: Message):
    """Mention every member of the group in chunks, respecting flood‑waits & cancellation."""

    if message.chat.id in ACTIVE_TAGS:
        return await message.reply_text("❗ A tag‑all is already running. Use /cancel to stop it first.")

    # Determine custom text & reply context
    if len(message.command) > 1:
        header_text = message.text.split(None, 1)[1]
    elif message.reply_to_message:
        header_text = message.reply_to_message.text or ""
    else:
        return await message.reply_text("Reply to a message *or* add custom text to tag everyone.")

    ACTIVE_TAGS.add(message.chat.id)

    try:
        batch, count = [], 0
        async for member in app.get_chat_members(message.chat.id):
            if message.chat.id not in ACTIVE_TAGS:
                break  # cancelled

            user = member.user
            # Skip bots & deleted
            if user.is_bot or user.is_deleted:
                continue

            batch.append(f"\n› [{user.first_name}](tg://user?id={user.id})")
            if len(batch) == MAX_MENTION_BATCH:
                await _safe_send(message.chat.id, f"{header_text}{''.join(batch)}")
                batch.clear()
                count += MAX_MENTION_BATCH
                await asyncio.sleep(SLEEP_BETWEEN_BATCH)

        # send remaining names
        if batch and message.chat.id in ACTIVE_TAGS:
            await _safe_send(message.chat.id, f"{header_text}{''.join(batch)}")

    finally:
        # Always clear flag even on error
        with suppress(KeyError):
            ACTIVE_TAGS.remove(message.chat.id)


async def _safe_send(chat_id: int, text: str):
    """Send message and handle FloodWait gracefully."""
    while True:
        try:
            await app.send_message(chat_id, text, parse_mode=enums.ParseMode.MARKDOWN)
            return
        except FloodWait as fw:
            await asyncio.sleep(fw.value + 1)
        except RPCError:
            # Other Telegram errors – best effort skip
            return


@app.on_message(filters.command("cancel", prefixes=C_HANDLER) & filters.group, group=-87654)
@user_admin
async def cancel_tag(_, message: Message):
    chat_id = message.chat.id
    if chat_id in ACTIVE_TAGS:
        ACTIVE_TAGS.remove(chat_id)
        await message.reply_text("✅ Tagall stopped.")
    else:
        await message.reply_text("❕ No tag‑all is currently running.")


__PLUGIN__ = "Tagall"

__HELP__ = """
Tag All members of the group.

• /tagall \\| /all \\| @all  – mention everyone (admin‑only)
  » You can reply to any message or add custom text after the command.
• /cancel – stop an ongoing tag‑all.

The bot paces mentions to avoid FloodWait and allows only one active tag‑all per chat.
"""
