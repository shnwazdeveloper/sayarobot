import subprocess as subp
import sys
from asyncio import create_subprocess_shell, sleep, subprocess
from io import BytesIO, StringIO
from os import execvp
from sys import executable
from time import gmtime, strftime, time
from traceback import format_exc

from pyrogram import filters
from pyrogram.errors import (ChannelInvalid, ChannelPrivate, ChatAdminRequired,
                             EntityBoundsInvalid, FloodWait, MessageTooLong,
                             PeerIdInvalid, RPCError)
from pyrogram.types import InlineKeyboardButton as IKB
from pyrogram.types import InlineKeyboardMarkup as IKM
from pyrogram.types import Message

from Curse import (BOT_TOKEN, LOG_DATETIME, LOGFILE, LOGGER, MESSAGE_DUMP,
                    OWNER_ID, SUDO_USERS, UPTIME)
from Curse.bot_class import app
from Curse.database import MongoDB
from Curse.database.chats_db import Chats
from Curse.database.support_db import SUPPORTS
from Curse.database.users_db import Users
from Curse.plugins.scheduled_jobs import clean_my_db
from Curse.supports import get_support_staff
from Curse.utils.clean_file import remove_markdown_and_html
from Curse.utils.custom_filters import SUDO_LEVEL, command
from Curse.utils.parser import mention_markdown


def can_change_type(curr, to_user):
    if curr == "dev" and to_user in ["whitelist","sudo"]:
        return True
    elif curr == "sudo" and to_user == "whitelist":
        return True
    else:
        return False


async def extract_support_target(c: app, m: Message, usage: str):
    if m.reply_to_message and m.reply_to_message.from_user:
        user = m.reply_to_message.from_user
        return user.id, user.first_name or str(user.id), user.username

    if len(m.command) < 2:
        await m.reply_text(f"**USAGE**\n{usage}")
        return None

    user_ref = m.command[1]
    if user_ref.lstrip("-").isdigit():
        user_id = int(user_ref)
        try:
            user = await c.get_users(user_id)
            return user.id, user.first_name or str(user.id), user.username
        except Exception:
            return user_id, str(user_id), None

    try:
        user = await c.get_users(user_ref)
    except Exception:
        await m.reply_text("Dunno who u r talking abt")
        return None

    return user.id, user.first_name or str(user.id), user.username


def add_runtime_sudo(user_id: int) -> None:
    if user_id not in SUDO_USERS:
        SUDO_USERS.append(user_id)
    SUDO_LEVEL.add(user_id)


def remove_runtime_sudo(user_id: int) -> None:
    while user_id in SUDO_USERS:
        SUDO_USERS.remove(user_id)
    SUDO_LEVEL.discard(user_id)


@app.on_message(command("addsudo", owner_cmd=True))
async def add_sudo(c: app, m: Message):
    support = SUPPORTS()

    target = await extract_support_target(
        c,
        m,
        "/addsudo [reply to user | user id | username]",
    )
    if not target:
        return

    user_id, first_name, _ = target
    current_type = support.get_support_type(user_id)
    mention = await mention_markdown(str(first_name), user_id)

    if current_type == "dev":
        await m.reply_text(f"{mention} is already a dev user.")
        return
    if current_type == "sudo":
        add_runtime_sudo(user_id)
        await m.reply_text(f"{mention} is already in the sudo users list.")
        return
    if current_type:
        support.update_support_user_type(user_id, "sudo")
    else:
        support.insert_support_user(user_id, "sudo")

    add_runtime_sudo(user_id)
    await m.reply_text(f"Done! {mention} added to the sudo users list.")
    return


@app.on_message(command(["rmsudo", "removesudo"], owner_cmd=True))
async def remove_sudo(c: app, m: Message):
    support = SUPPORTS()

    target = await extract_support_target(
        c,
        m,
        "/rmsudo [reply to user | user id | username]\n/removesudo [reply to user | user id | username]",
    )
    if not target:
        return

    user_id, first_name, _ = target
    current_type = support.get_support_type(user_id)
    mention = await mention_markdown(str(first_name), user_id)

    if current_type != "sudo":
        remove_runtime_sudo(user_id)
        await m.reply_text(f"{mention} is not in the sudo users list.")
        return

    support.delete_support_user(user_id)
    remove_runtime_sudo(user_id)
    await m.reply_text(f"Done! {mention} removed from the sudo users list.")
    return

@app.on_message(command("chatlist", dev_cmd=True))
async def chats(c: app, m: Message):
    exmsg = await m.reply_text(text="Exporting Charlist...")
    await c.send_message(
        MESSAGE_DUMP,
        f"#CHATLIST\n\n**User:** {(await mention_markdown(m.from_user.first_name, m.from_user.id))}",
    )
    all_chats = (Chats.list_chats_full()) or {}
    chatfile = """List of chats in my database.

        <b>Chat name | Chat ID | Members count</b>"""
    P = 1
    for chat in all_chats:
        try:
            chat_info = await c.get_chat(chat["_id"])
            chat_members = chat_info.members_count
            try:
                invitelink = chat_info.invite_link
            except KeyError:
                invitelink = "No Link!"
            chatfile += f"{P}. {chat['chat_name']} | {chat['_id']} | {chat_members} | {invitelink}\n"
            P += 1
        except ChatAdminRequired:
            pass
        except (ChannelPrivate, ChannelInvalid):
            Chats.remove_chat(chat["_id"])
        except PeerIdInvalid:
            LOGGER.warning(f"Peer not found {chat['_id']}")
        except FloodWait as ef:
            LOGGER.error("FloodWait required, Sleeping for 60s")
            LOGGER.error(ef)
            sleep(60)
        except RPCError as ef:
            LOGGER.error(ef)
            await m.reply_text(f"**Error:**\n{ef}")

    with BytesIO(str.encode(await remove_markdown_and_html(chatfile))) as f:
        f.name = "chatlist.txt"
        await m.reply_document(
            document=f,
            caption="Here is the list of chats in my Database.",
        )
    await exmsg.delete()
    return


@app.on_message(command("rmsupport"))
async def rm_support(c: app, m: Message):
    support = SUPPORTS()
    curr_user = support.get_support_type(m.from_user.id)
    if not curr_user:
        await m.reply_text("Stay in you limit")
        return

    target = await extract_support_target(
        c,
        m,
        "/rmsupport [reply to user | user id | username]",
    )
    if not target:
        return
    curr, _, _ = target

    to_user = support.get_support_type(curr)
    can_user = can_change_type(curr_user, to_user)
    if m.from_user.id == int(OWNER_ID) or can_user:
        support.delete_support_user(curr)
        if to_user == "sudo":
            remove_runtime_sudo(curr)
        await m.reply_text("Done! User now no longer belongs to the support staff")
    else:
        await m.reply_text("Sorry you can't do that...")
    return


@app.on_message(command("leavechat", dev_cmd=True))
async def leave_chat(c: app, m: Message):
    if len(m.text.split()) != 2:
        await m.reply_text("Supply a chat id which I should leave!", quoet=True)
        return

    chat_id = m.text.split(None, 1)[1]

    replymsg = await m.reply_text(f"Trying to leave chat {chat_id}...", quote=True)
    try:
        await c.leave_chat(chat_id)
        await replymsg.edit_text(f"Left <code>{chat_id}</code>.")
    except PeerIdInvalid:
        await replymsg.edit_text("Haven't seen this group in this session!")
    except RPCError as ef:
        LOGGER.error(ef)
        await replymsg.edit_text(f"Failed to leave chat!\nError: <code>{ef}</code>.")
    return


__PLUGIN__ = "Sudo"

__HELP__ = """
/addsudo: ᴀᴅᴅ ᴀ ᴜsᴇʀ ᴛᴏ ᴛʜᴇ sᴜᴅᴏ ᴜsᴇʀs ʟɪsᴛ.
/rmsudo: ʀᴇᴍᴏᴠᴇ ᴀ ᴜsᴇʀ ғʀᴏᴍ ᴛʜᴇ sᴜᴅᴏ ᴜsᴇʀs ʟɪsᴛ.
/removesudo: ʀᴇᴍᴏᴠᴇ ᴀ ᴜsᴇʀ ғʀᴏᴍ ᴛʜᴇ sᴜᴅᴏ ᴜsᴇʀs ʟɪsᴛ.
"""
