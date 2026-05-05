import io
from re import sub
import sys
import traceback
import subprocess
from traceback import format_exc
import time
from time import gmtime, strftime, time

from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pyrogram.errors import RPCError
from pyrogram.types import Message
from pyrogram import filters, enums
from datetime import datetime

from Curse.bot_class import app 
from Curse import DEV_USERS 
from Curse import MESSAGE_DUMP, LOGFILE, LOGGER
from Curse.supports import get_support_staff
from Curse.utils.custom_filters import command
from Curse.utils.parser import mention_markdown
from Curse.plugins.scheduled_jobs import clean_my_db

SUPPORT_STAFF = get_support_staff()
CHAD = DEV_USERS

async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)

@app.on_message(filters.command(["run","eval", "e"]))
async def eval(client, message):
    if message.from_user.id not in CHAD:
        return
    if len(message.text.split()) < 2:
        return await message.reply_text("`Input Not Found!`")
    
    cmd = message.text.split(maxsplit=1)[1]     
    status_message = await message.reply_text("Processing ...")    
    start = datetime.now()
    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message
    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = io.StringIO()
    redirected_error = sys.stderr = io.StringIO()
    stdout, stderr, exc = None, None, None
    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()
    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"
    end = datetime.now()
    ping = (end-start).microseconds / 1000
    final_output = "<b>📎 Input</b>: "
    final_output += f"<code>{cmd}</code>\n\n"
    final_output += "<b>📒 Output</b>:\n"
    final_output += f"<code>{evaluation.strip()}</code> \n\n"
    final_output += f"<b>✨ Taken Time</b>: {ping}<b>ms</b>"
    if len(final_output) > 4096:
        with io.BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await reply_to_.reply_document(
                document=out_file, caption=cmd, disable_notification=True
            )
    else:
        await status_message.edit_text(final_output)
        

@app.on_message(filters.command("logs"))
async def send_log(c: app, m: Message):
    if m.from_user.id not in SUPPORT_STAFF:
        return    
    replymsg = await m.reply_text("Sending logs...!")
    await c.send_message(
        MESSAGE_DUMP,
        f"#LOGS\n\nUser: {(await mention_markdown(m.from_user.first_name, m.from_user.id))}",
    )
    # Send logs
    with open(LOGFILE) as f:
        raw = ((f.read()))[1]
    await m.reply_document(
        document=LOGFILE,
        quote=True,
    )
    await replymsg.delete()
    return


@app.on_message(filters.command("cleandb"))
async def cleeeen(c:app,m:Message):
    if m.from_user.id not in CHAD:
        return
    x = await m.reply_text("📂")
    try:
        z = await clean_my_db(c,True,m.from_user.id)
        try:
            await x.delete()
        except Exception:
            pass
        await m.reply_text(z)
        return
    except Exception as e:
        await m.reply_text(e)
        await x.delete()
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return
