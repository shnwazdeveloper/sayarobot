import os
import httpx
from contextlib import suppress
from pyrogram import filters
from pyrogram.types import Message

from Curse.bot_class import app

async def _dl_media(client, msg, status):
    try:
        return await client.download_media(msg)
    except Exception as e:
        await status.edit(f" Download error: `{e}`")
        return None

async def _cleanup(path):
    with suppress(OSError):
        os.remove(path)


@app.on_message(filters.command("envs") & filters.reply, group=383810)
async def envs_upload(c, m: Message):
    reply = m.reply_to_message
    status = await m.reply(" Uploading to envs.sh …")
    async with httpx.AsyncClient(timeout=30) as hc:
        try:
            if reply.text:
                r = await hc.post("https://envs.sh", content=reply.text.encode())
                await status.edit(f" {r.text.strip()}")
            else:
                fp = await _dl_media(c, reply, status)
                if not fp:
                    return
                files = {"file": open(fp, "rb")}
                r = await hc.post("https://envs.sh", files=files)
                await status.edit(f" {r.text.strip()}")
                await _cleanup(fp)
        except Exception as e:
            await status.edit(f" envs.sh error: `{e}`")
