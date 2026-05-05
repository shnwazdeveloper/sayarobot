import os
from asyncio import gather

from pyrogram import filters
from pyrogram.types import Message
from pySmartDL import SmartDL

from Curse.bot_class import app
from Curse.extras.localization import use_chat_lang

C_HANDLER = ["/", "harry ", "harry ", "."]

@app.on_message(filters.command(["webss"], C_HANDLER), group=1234567)
@use_chat_lang()
async def take_ss(_, ctx: Message, strings):
    if len(ctx.command) == 1:
        return await ctx.reply(strings("no_url"))
    url = (
        ctx.command[1]
        if ctx.command[1].startswith("http")
        else f"https://{ctx.command[1]}"
    )
    download_file_path = os.path.join("downloads/", f"webSS_{ctx.from_user.id}.png")
    msg = await ctx.reply(strings("wait_str"))
    try:
        url = f"https://webss.yasirapi.eu.org/api?url={url}&width=1280&height=720"
        downloader = SmartDL(url, download_file_path, progress_bar=False, timeout=10)
        downloader.start(blocking=True)
        await gather(
            *[
                ctx.reply_document(download_file_path),
                ctx.reply_photo(download_file_path, caption=strings("str_credit")),
            ]
        )
        await msg.delete()
        if os.path.exists(download_file_path):
            os.remove(download_file_path)
    except Exception as e:
        await msg.edit(strings("ss_failed_str").format(err=str(e)))
