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
                    OWNER_ID, UPTIME)
from Curse.bot_class import app
from Curse.database import MongoDB
from Curse.database.chats_db import Chats
from Curse.database.support_db import SUPPORTS
from Curse.database.users_db import Users
from Curse.plugins.scheduled_jobs import clean_my_db
from Curse.supports import get_support_staff
from Curse.utils.clean_file import remove_markdown_and_html
from Curse.utils.custom_filters import command
from Curse.utils.extract_user import extract_user
from Curse.utils.parser import mention_markdown


def can_change_type(curr, to_user):
    if curr == "dev" and to_user in ["whitelist","sudo"]:
        return True
    elif curr == "sudo" and to_user == "whitelist":
        return True
    else:
        return False

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
    split = m.command
    if reply_to := m.reply_to_message:
        try:
            curr = reply_to.from_user.id
        except Exception:
            await m.reply_text("Reply to an user")
            return
    elif len(split) >= 2:
        try:
            curr = int(split[1])
        except Exception:
            try:
                curr, _, _ = extract_user(m)
            except Exception:
                await m.reply_text("Dunno who u r talking abt")
                return
    else:
        await m.reply_text("**USAGE**\n/rmsupport [reply to user | user id | username]")
        return
    to_user = support.get_support_type(curr)
    can_user = can_change_type(curr_user, to_user)
    if m.from_user.id == int(OWNER_ID) or can_user:
        support.delete_support_user(curr)
        SUPPORT_USERS["Dev"].discard(curr)
        SUPPORT_USERS["Sudo"].discard(curr)
        SUPPORT_USERS["White"].discard(curr)
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


