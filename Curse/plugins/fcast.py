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

@app.on_message(command("ping", sudo_cmd=True))
async def ping(_, m: Message):
    LOGGER.info(f"{m.from_user.id} used ping cmd in {m.chat.id}")
    start = time()
    replymsg = await m.reply_text(text="Pinging...", quote=True)
    delta_ping = time() - start
    await replymsg.edit_text(f"<b>Pong!</b>\n{delta_ping * 1000:.3f} ms")
    return

@app.on_message(command("uptime", dev_cmd=True))
async def uptime(_, m: Message):
    up = strftime("%Hh %Mm %Ss", gmtime(time() - UPTIME))
    await m.reply_text(text=f"<b>Uptime:</b> <code>{up}</code>", quote=True)
    return

@app.on_message(command("hcast", dev_cmd=True))
async def chat_broadcast(c: app, m: Message):
    if m.reply_to_message:
        msg = m.reply_to_message.text.markdown
    else:
        await m.reply_text("Reply to a message to broadcast it")
        return

    exmsg = await m.reply_text("Started broadcasting!")
    all_chats = (Chats.list_chats_by_id()) or {}
    err_str, done_broadcast = "", 0

    for chat in all_chats:
        try:
            await c.send_message(chat, msg, disable_web_page_preview=True)
            done_broadcast += 1
            await sleep(0.1)
        except RPCError as ef:
            LOGGER.error(ef)
            err_str += str(ef)
            continue

    await exmsg.edit_text(
        f"Done broadcasting \nSent message to {done_broadcast} chats",
    )

    if err_str:
        with BytesIO(str.encode(await remove_markdown_and_html(err_str))) as f:
            f.name = "error_broadcast.txt"
            await m.reply_document(
                document=f,
                caption="Broadcast Error",
            )

    return

@app.on_message(command("fcast") & filters.user(OWNER_ID), group=383873)
async def forward_type_broadcast(c: app, m: Message):
    repl = m.reply_to_message
    if not repl:
        await m.reply_text("Please reply to message to broadcast it")
        return
    split = m.command

    chat = Chats.list_chats_by_id()
    user = [i["_id"] for i in Users.list_users()]
    alll = chat + user
    if len(split) != 2:
        tag = "all"
    else:
        try:
            if split[0].lower() == "-u":
                tag = "user"
            elif split[0].lower() == "-c":
                tag = "chat"
            else:
                tag = "all"
        except IndexError:
            pass
    if tag == "chat":
        peers = chat
    elif tag == "user":
        peers = user
    else:
        peers = alll

    xx = await m.reply_text("Broadcasting...")

    failed = 0
    total = len(peers)
    for peer in peers:
        try:
            await repl.forward(int(peer))
            await sleep(0.1)
        except Exception:
            failed += 1
            pass
    txt = f"Broadcasted message to {total-failed} peers out of {total}\nFailed to broadcast message to {failed} peers"
    if not failed:
        txt = f"Broadcasted message to {total} peers"
    await m.reply_text(txt)
    try:
        await xx.delete()
    except Exception:
        pass
    return
