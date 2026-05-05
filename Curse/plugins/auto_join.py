from traceback import format_exc
from pyrogram import filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import (
    CallbackQuery,
    ChatJoinRequest,
    InlineKeyboardButton as ikb,
    InlineKeyboardMarkup as ikm,
    Message,
)

from Curse import LOGGER
from Curse.bot_class import app
from Curse.database.autojoin_db import AUTOJOIN
from Curse.supports import get_support_staff
from Curse.utils.custom_filters import admin_filter, auto_join_filter, command


async def start_bot_markup(client):
    bot = getattr(client, "me", None) or await client.get_me()
    return ikm([[ikb(" Start Bot", url=f"https://t.me/{bot.username}?start=start")]])


@app.on_message(command(["joinreq"]) & admin_filter)
async def accept_join_requests(c: app, m: Message):
    if m.chat.id == m.from_user.id:
        await m.reply_text(" This ancient spell is only effective in group chambers.")
        return

    split = m.command
    a_j = AUTOJOIN()

    try:
        status = (await m.chat.get_member(c.me.id)).status
        if status != CMS.ADMINISTRATOR:
            await m.reply_text(" I need magical admin powers to handle enchanted gates.")
            return
    except Exception as ef:
        await m.reply_text(f" A magical mishap occurred.\n<b>Error:</b> <code>{ef}</code>")
        LOGGER.error(ef)
        LOGGER.error(format_exc())
        return

    if len(split) == 1:
        txt = (
            " **MAGICAL USAGE:**\n"
            "`/joinreq [on | off]`\n\n"
            "`on` - Activate join request handling.\n"
            "`off` - Disable magical handling of entries."
        )
    else:
        mode = split[1].lower()
        if mode == "on":
            a_j.update_join_type(m.chat.id, "manual")
            txt = (
                " *Gatekeeper Spell Activated!*\n"
                "Join requests will be reviewed by elders (admins).\n"
                "Use `/joinreqmode auto` to allow automatic entry."
            )
        elif mode == "off":
            a_j.remove_autojoin(m.chat.id)
            txt = (
                " The magical ward is removed.\n"
                "Requests to enter shall be ignored henceforth."
            )
        else:
            txt = (
                " **MAGICAL USAGE:**\n"
                "`/joinreq [on | off]`\n\n"
                "`on` - Activate join request handling.\n"
                "`off` - Disable handling."
            )

    await m.reply_text(txt)


@app.on_message(command("joinreqmode") & admin_filter)
async def join_request_mode(c: app, m: Message):
    if m.chat.id == m.from_user.id:
        await m.reply_text(" This enchantment must be cast in a group chamber.")
        return

    split = m.command
    a_j = AUTOJOIN()

    usage_text = (
        "** Join Request Mode Usage:**\n"
        "`/joinreqmode [auto | manual]`\n\n"
        " `auto` — Automatically allow all who seek passage.\n"
        " `manual` — Notify the magical council to approve or deny."
    )

    if len(split) == 1:
        await m.reply_text(usage_text)
    else:
        mode = split[1].lower()
        if mode not in ["auto", "manual"]:
            await m.reply_text(usage_text)
        else:
            a_j.update_join_type(m.chat.id, mode)
            await m.reply_text(f" Enchantment adjusted to `{mode.upper()}` mode.")


@app.on_chat_join_request(auto_join_filter)
async def join_request_handler(c: app, j: ChatJoinRequest):
    user = j.from_user.id
    userr = j.from_user
    chat = j.chat.id

    aj = AUTOJOIN()
    join_type = aj.get_autojoin(chat) or "manual"
    SUPPORT_STAFF = get_support_staff()

    if not join_type:
        return

    if join_type == "auto" or user in SUPPORT_STAFF:
        try:
            await c.approve_chat_join_request(chat, user)
            await c.send_message(chat, f" {userr.mention} has entered through the magical gates.")
            try:
                await c.send_message(
                    user,
                    f" You’ve been granted entry to **{j.chat.title}**!\nWelcome to the realm of magic and mystery."
                )
            except Exception as dm_error:
                LOGGER.warning(f"Couldn't PM user {user}: {dm_error}")
                await c.send_message(
                    chat,
                    f"Hey {userr.mention}.\n"
                    "Start me in Pm by clicking the button given below.",
                    reply_markup=await start_bot_markup(c),
                )
        except Exception as ef:
            await c.send_message(chat, f" The gates jammed!\n<code>{ef}</code>")
            LOGGER.error(ef)
            LOGGER.error(format_exc())
    elif join_type == "manual":
        txt = (
            f" **A Wand Waver Seeks Entry!**\n"
            f" {userr.mention} (`{user}`) wishes to enter **{j.chat.title}**.\n"
            f"Shall we open the gates?"
        )
        kb = [
            [
                ikb(" Allow Passage", f"accept_joinreq_uest_{user}"),
                ikb(" Deny Entry", f"decline_joinreq_uest_{user}")
            ]
        ]
        await c.send_message(chat, txt, reply_markup=ikm(kb))


@app.on_callback_query(filters.regex("^accept_joinreq_uest_") | filters.regex("^decline_joinreq_uest_"))
async def accept_decline_request(c: app, q: CallbackQuery):
    admin_id = q.from_user.id
    chat = q.message.chat.id

    try:
        user_status = (await q.message.chat.get_member(admin_id)).status
        if user_status not in {CMS.OWNER, CMS.ADMINISTRATOR}:
            await q.answer(" Only an elder of the realm may decide!", show_alert=True)
            return
    except Exception:
        await q.answer(" The magical council does not recognize you.", show_alert=True)
        return

    split = q.data.split("_")
    action = split[0]
    target_user = int(split[-1])

    try:
        userr = await c.get_users(target_user)
    except Exception:
        userr = None

    if action == "accept":
        try:
            await c.approve_chat_join_request(chat, target_user)
            await q.answer(f" Passage granted to {userr.mention if userr else target_user}", show_alert=True)
            await q.edit_message_text(f" {userr.mention if userr else target_user} has entered the realm.")
            try:
                await c.send_message(
                    target_user,
                    f" You’ve been welcomed into **{q.message.chat.title}**.\nPrepare to embrace the world of sorcery!"
                )
            except Exception as dm_error:
                LOGGER.warning(f"Couldn't PM user {target_user}: {dm_error}")
                await c.send_message(
                    chat,
                    f" Hey {userr.mention if userr else target_user}.\n"
                    "Start the bot in Pm to Know more.",
                    reply_markup=await start_bot_markup(c),
                )
        except Exception as ef:
            await c.send_message(chat, f" Error granting access:\n<code>{ef}</code>")
            LOGGER.error(ef)
            LOGGER.error(format_exc())
    elif action == "decline":
        try:
            await c.decline_chat_join_request(chat, target_user)
            await q.answer(" Entry denied by the magical council.", show_alert=True)
            await q.edit_message_text(" Request denied. The gates remain closed.")
        except Exception as ef:
            await c.send_message(chat, f" Error denying access:\n<code>{ef}</code>")
            LOGGER.error(ef)
            LOGGER.error(format_exc())


# Plugin Info
__PLUGIN__ = "Join Requests"
__alt_name__ = ["join_request", "gatekeeper"]
__HELP__ = """
 **Gatekeeper Enchantment — Join Request Handler**

Command the enchanted gates of your group with powerful spells.

** Admin Charms:**
• `/joinreq on` — Activate join request handling (manual mode by default).
• `/joinreq off` — Remove all gatekeeping enchantments.

• `/joinreqmode manual` — Elders (admins) get alerts to approve/decline.
• `/joinreqmode auto` — Automatically allow new seekers to pass.

 Approved users receive an owl post (DM) upon entry.
 Only high wizards (admins) can cast these spells.
"""
