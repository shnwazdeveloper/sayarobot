import os
import asyncio
import mimetypes
import httpx
from contextlib import suppress
from pyrogram import filters
from pyrogram.types import Message
from telegraph.upload import upload_file

from Curse.bot_class import app

IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "")
MAX_TGRAPH_SIZE = 5 * 1024 * 1024

async def _dl_media(client, msg, status):
    try:
        return await client.download_media(msg)
    except Exception as e:
        await status.edit(f"❌ Download error: `{e}`")
        return None

async def _cleanup(path):
    with suppress(OSError):
        os.remove(path)


@app.on_message(filters.command("imgbb") & filters.reply, group=38382)
async def imgbb_upload(c, m: Message):
    reply = m.reply_to_message
    if not IMGBB_API_KEY:
        return await m.reply("Set IMGBB_API_KEY.")
    if not reply or not reply.photo:
        return await m.reply("Reply to a photo.")
    status = await m.reply("📤 Uploading to imgbb …")
    fp = await _dl_media(c, reply, status)
    if not fp:
        return
    async with httpx.AsyncClient(timeout=30) as hc:
        try:
            files = {"image": open(fp, "rb")}
            r = await hc.post("https://api.imgbb.com/1/upload", params={"key": IMGBB_API_KEY}, files=files)
            link = r.json()["data"]["url"]
            await status.edit(f"✅ {link}")
        except Exception as e:
            await status.edit(f"❌ imgBB error: `{e}`")
    await _cleanup(fp)

@app.on_message(filters.command("envs") & filters.reply, group=383810)
async def envs_upload(c, m: Message):
    reply = m.reply_to_message
    status = await m.reply("📤 Uploading to envs.sh …")
    async with httpx.AsyncClient(timeout=30) as hc:
        try:
            if reply.text:
                r = await hc.post("https://envs.sh", content=reply.text.encode())
                await status.edit(f"✅ {r.text.strip()}")
            else:
                fp = await _dl_media(c, reply, status)
                if not fp:
                    return
                files = {"file": open(fp, "rb")}
                r = await hc.post("https://envs.sh", files=files)
                await status.edit(f"✅ {r.text.strip()}")
                await _cleanup(fp)
        except Exception as e:
            await status.edit(f"❌ envs.sh error: `{e}`")
