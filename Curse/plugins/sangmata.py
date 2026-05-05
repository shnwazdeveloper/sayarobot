import os
from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from Curse.bot_class import app
from Curse.database.sangmata_db import (
    is_sangmata_on,
    sangmata_on,
    sangmata_off,
    cek_userdata,
    add_userdata,
    get_userdata
)
from Curse.extras.localization import use_chat_lang
from Curse.utils.custom_filters import admin_filter
from Curse.vars import Config


#  Track user name/username changes
@app.on_message(filters.group & ~filters.bot & ~filters.via_bot, group=5)
@use_chat_lang()
async def cek_mataa(self: Client, ctx: Message, strings):
    if ctx.sender_chat or not await is_sangmata_on(ctx.chat.id):
        return

    user = ctx.from_user
    if not await cek_userdata(user.id):
        return await add_userdata(user.id, user.username, user.first_name, user.last_name)

    uname_old, fname_old, lname_old = await get_userdata(user.id)
    msg = ""
    has_change = False

    if uname_old != user.username:
        has_change = True
        uname_old_fmt = f"@{uname_old}" if uname_old else strings("no_uname")
        uname_new_fmt = f"@{user.username}" if user.username else strings("no_uname")
        msg += f" <b>Username changed:</b>\n<b>Before:</b> <code>{uname_old_fmt}</code>\n<b>After:</b> <code>{uname_new_fmt}</code>\n\n"

    if fname_old != user.first_name:
        has_change = True
        msg += f" <b>First Name changed:</b>\n<b>Before:</b> <code>{fname_old}</code>\n<b>After:</b> <code>{user.first_name}</code>\n\n"

    lname_old_fmt = lname_old or strings("no_last_name")
    lname_new_fmt = user.last_name or strings("no_last_name")
    if lname_old != user.last_name:
        has_change = True
        msg += f" <b>Last Name changed:</b>\n<b>Before:</b> <code>{lname_old_fmt}</code>\n<b>After:</b> <code>{lname_new_fmt}</code>\n\n"

    if has_change:
        header = f" <b>Imposter Alert!</b>\n User: {user.mention} [<code>{user.id}</code>]\n\n"
        await ctx.reply(header + msg, quote=True)
        await add_userdata(user.id, user.username, user.first_name, user.last_name)


#  Toggle Imposter Tracking (Admin-only)
@app.on_message(
    filters.group &
    filters.command("imposter", Config.PREFIX_HANDLER) &
    admin_filter, group=100101
)
@use_chat_lang()
async def set_mataa(self: Client, ctx: Message, strings):
    if len(ctx.command) == 1:
        is_enabled = await is_sangmata_on(ctx.chat.id)
        status = " ON" if is_enabled else " OFF"
        return await ctx.reply(
            f" <b>Sangmata Detection Status:</b> <code>{status}</code>\n\n"
            + strings("set_sangmata_help").format(cmd=ctx.command[0]),
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(" Enable", callback_data=f"sangmata:on:{ctx.chat.id}"),
                InlineKeyboardButton(" Disable", callback_data=f"sangmata:off:{ctx.chat.id}")
            ]])
        )

    choice = ctx.command[1].lower()
    if choice == "on":
        if await is_sangmata_on(ctx.chat.id):
            await ctx.reply(" Sangmata is already enabled.")
        else:
            await sangmata_on(ctx.chat.id)
            await ctx.reply(" Sangmata Tracking Enabled.")
    elif choice == "off":
        if not await is_sangmata_on(ctx.chat.id):
            await ctx.reply(" Sangmata is already disabled.")
        else:
            await sangmata_off(ctx.chat.id)
            await ctx.reply(" Sangmata Tracking Disabled.")
    else:
        await ctx.reply(strings("wrong_param"))


#  Callback handler for inline toggle buttons
@app.on_callback_query(filters.regex(r"^sangmata:(on|off):"))
async def handle_sangmata_toggle(self: Client, cq: CallbackQuery):
    action, _, chat_id = cq.data.split(":")
    chat_id = int(chat_id)

    if not cq.message.chat:
        return await cq.answer(" This action must be used in a group.", show_alert=True)

    if not await self.get_chat_member(chat_id, cq.from_user.id).can_manage_chat:
        return await cq.answer(" You need to be an admin to do that.", show_alert=True)

    if action == "on":
        if await is_sangmata_on(chat_id):
            await cq.answer(" Already Enabled")
        else:
            await sangmata_on(chat_id)
            await cq.message.edit_text(" Sangmata Tracking has been Enabled.")
            await cq.answer(" Enabled")
    elif action == "off":
        if not await is_sangmata_on(chat_id):
            await cq.answer(" Already Disabled")
        else:
            await sangmata_off(chat_id)
            await cq.message.edit_text(" Sangmata Tracking has been Disabled.")
            await cq.answer(" Disabled")


#  Help and Plugin name
__PLUGIN__ = "Imposter"
__HELP__ = """
 **Imposter Detection Module**

Automatically detect and log when users in your group change their name or username.

**Commands:**

• `/imposter on` – Enable name/username change detection.
• `/imposter off` – Disable tracking.
• `/imposter` – View current status and toggle via buttons.

The bot will alert you whenever:
 A user changes their username
 A user changes their first or last name

Admins only. Powered by your bot!
"""
