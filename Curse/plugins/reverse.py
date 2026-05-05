import asyncio
import os
import uuid

import httpx
from pyrogram.enums import MessageMediaType
from pyrogram.types import (
    Message,
    InlineKeyboardButton,
    InlineKeyboardMarkup
    )
from pyrogram import Client, filters

# Replace "YourRobot" with your module name.
from Curse.bot_class import app as pbot

ENDPOINT = "https://sasta-api.vercel.app/googleImageSearch"
httpx_client = httpx.AsyncClient(timeout=60)

COMMANDS = [
    "reverse",
    "grs",
    "gis",
    "pp",
    "p",
    ]

class STRINGS:
    REPLY_TO_MEDIA = "ℹ️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛʜᴀᴛ ᴄᴏɴᴛᴀɪɴs ᴏɴᴇ ᴏғ ᴛʜᴇ sᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ ᴛʏᴘᴇs, sᴜᴄʜ ᴀs ᴀ ᴘʜᴏᴛᴏ, sᴛɪᴄᴋᴇʀ, ᴏʀ ɪᴍᴀɢᴇ ғɪʟᴇ."
    UNSUPPORTED_MEDIA_TYPE = "⚠️ <b>Uɴsᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ!</b>\nℹ️ Pʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴀ sᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴇᴅɪᴀ ᴛʏᴘᴇ: ɪᴍᴀɢᴇ, sᴛɪᴄᴋᴇʀ, ᴏʀ ɪᴍᴀɢᴇ Fɪʟᴇ."
    
    REQUESTING_API_SERVER = "📡"
    
    DOWNLOADING_MEDIA = "⏳"
    UPLOADING_TO_API_SERVER = "📂"
    PARSING_RESULT = "📥"
    
    EXCEPTION_OCCURRED = "❌ <b>Exception occurred!</b>\n\n<b>Exception:</b> {}"
    
    RESULT = """
<b>Qᴜᴇʀʏ:</b> {query}
<b>Gᴏᴏɢʟᴇ Pᴀɢᴇ:</b> <a href="{search_url}">Link</a>
    """
    OPEN_SEARCH_PAGE = "Gᴏᴏɢʟᴇ"

@pbot.on_message(filters.command(["p", "pp", "reverse", "sauce", "grs"]), group=9999)
async def on_google_lens_search(client: Client, message: Message) -> None:
    if len(message.command) > 1:
        image_url = message.command[1]
        params = {
            "image_url": image_url
        }
        status_msg = await message.reply(STRINGS.REQUESTING_API_SERVER)
        start_time = asyncio.get_event_loop().time()
        response = await httpx_client.get(ENDPOINT, params=params)
        
    elif (reply := message.reply_to_message):
        if reply.media not in (MessageMediaType.PHOTO, MessageMediaType.STICKER, MessageMediaType.DOCUMENT):
            await message.reply(STRINGS.UNSUPPORTED_MEDIA_TYPE)
            return
        
        status_msg = await message.reply(STRINGS.DOWNLOADING_MEDIA)
        file_path = f"temp/{uuid.uuid4()}"
        try:
            await reply.download(file_path)
        except Exception as exc:
            text = STRINGS.EXCEPTION_OCCURRED.format(exc)
            await message.reply(text)
            
            try:
                os.remove(file_path)
            except FileNotFoundError:
                pass
            return
        
        with open(file_path, "rb") as image_file:
            start_time = asyncio.get_event_loop().time()
            files = {"file": image_file}
            await status_msg.edit(STRINGS.UPLOADING_TO_API_SERVER)
            response = await httpx_client.post(ENDPOINT, files=files)
        
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass
    
    if response.status_code == 404:
        text = STRINGS.EXCEPTION_OCCURRED.format(response.json()["error"])
        await message.reply(text)
        await status_msg.delete()
        return
    elif response.status_code != 200:
        text = STRINGS.EXCEPTION_OCCURRED.format(response.text)
        await message.reply(text)
        await status_msg.delete()
        return
    
    await status_msg.edit(STRINGS.PARSING_RESULT)
    response_json = response.json()
    query = response_json["query"]
    search_url = response_json["search_url"]
    
    end_time = asyncio.get_event_loop().time() - start_time
    time_taken = "{:.2f}".format(end_time)
    
    text = STRINGS.RESULT.format(
        query=f"<code>{query}</code>" if query else "<i>Name not found</i>",
        search_url=search_url,
        time_taken=time_taken
        )
    buttons = [
        [InlineKeyboardButton(STRINGS.OPEN_SEARCH_PAGE, url=search_url)]
        ]
    await message.reply(text, disable_web_page_preview=True, reply_markup=InlineKeyboardMarkup(buttons))
    await status_msg.delete()
