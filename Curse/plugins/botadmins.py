from asyncio import sleep
from contextlib import suppress

from pyrogram import filters, enums
from pyrogram.errors import FloodWait, RPCError
from pyrogram.types import Message

from Curse import DEV_USERS, LOGGER, OWNER_ID, SUDO_USERS, WHITELIST_USERS
from Curse.bot_class import app
from Curse.supports import get_support_staff
from Curse.utils.parser import mention_html

SUPPORT_STAFF = get_support_staff()


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────
async def _get_user(client, user_id: int):
    """Return user object, handling FloodWait automatically."""
    while True:
        try:
            return await client.get_users(user_id)
        except FloodWait as fw:
            await sleep(fw.value + 1)
        except RPCError:
            return None


# ─────────────────────────────────────────────────────────────
# /botadmins  (visible only to support staff)
# ─────────────────────────────────────────────────────────────
@app.on_message(filters.command("botadmins") & filters.private)
async def botstaff(_, m: Message):
    # Allow only support staff to run
    if (m.from_user and m.from_user.id not in SUPPORT_STAFF) or (
        not m.from_user and m.sender_chat and m.sender_chat.id not in SUPPORT_STAFF
    ):
        return

    sections = []

    # — Supreme Sorcerer (Owner)
    owner = await _get_user(app, OWNER_ID)
    if owner:
        sections.append(
            f" <b> SUPREME SORCERER </b>\n"
            f"• {mention_html(owner.first_name, OWNER_ID)} (<code>{OWNER_ID}</code>)"
        )
    else:
        sections.append(
            " <b> SUPREME SORCERER </b>\n• <i>Could not fetch owner profile.</i>"
        )

    # — Ministry Developers
    dev_lines = []
    for uid in set(DEV_USERS) - {OWNER_ID}:
        user = await _get_user(app, uid)
        if user:
            dev_lines.append(f"•  {mention_html(user.first_name, uid)} (<code>{uid}</code>)")
        else:
            dev_lines.append(f"•  Unknown Dev (<code>{uid}</code>)")
    sections.append(
        " <b>MINISTRY DEVELOPERS</b> (Special‑Grade Magicians):\n"
        + ("\n".join(dev_lines) if dev_lines else "• No registered developers.")
    )

    # — Aurors (Sudo users)
    sudo_lines = []
    for uid in set(SUDO_USERS):
        user = await _get_user(app, uid)
        if user:
            sudo_lines.append(f"•  {mention_html(user.first_name, uid)} (<code>{uid}</code>)")
        else:
            sudo_lines.append(f"•  Unknown Auror (<code>{uid}</code>)")
    sections.append(
        " <b>AURORS</b> (Grade‑A Magicians):\n"
        + ("\n".join(sudo_lines) if sudo_lines else "• No Aurors have been assigned.")
    )

    # — Whitelisted Wizards
    wl_lines = []
    for uid in WHITELIST_USERS:
        user = await _get_user(app, uid)
        if user:
            wl_lines.append(f"•  {mention_html(user.first_name, uid)} (<code>{uid}</code>)")
        else:
            wl_lines.append(f"•  Unknown Spellcaster (<code>{uid}</code>)")
    sections.append(
        " <b>SPELLCASTERS</b> (Whitelisted Wizards):\n"
        + ("\n".join(wl_lines) if wl_lines else "• No Spellcasters listed.")
    )

    text = "\n\n".join(sections)
    await m.reply_text(text, parse_mode=enums.ParseMode.HTML)
    LOGGER.info(f"Staff list invoked by {m.from_user.id if m.from_user else 'anon'}")
