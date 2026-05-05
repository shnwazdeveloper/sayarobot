import os
import requests
import aiohttp
import aiofiles
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from telegraph import Telegraph, upload_file
from Curse.bot_class import app
from pyrogram.types import Message

telegraph = Telegraph()

# Remove Background Function
async def RemoveBG(input_file_name):
    headers = {"X-API-Key": "u4x2416NAQVefYsfwbzrw7VE"}  # Replace with your key
    async with aiohttp.ClientSession() as session:
        with open(input_file_name, 'rb') as f:
            data = aiohttp.FormData()
            data.add_field('image_file', f, filename=os.path.basename(input_file_name), content_type='application/octet-stream')
            async with session.post("https://api.remove.bg/v1.0/removebg", headers=headers, data=data) as resp:
                if 'image' in resp.headers.get("content-type", ""):
                    name = input_file_name.replace(".jpg", "_nobg.png")
                    async with aiofiles.open(name, "wb") as out:
                        await out.write(await resp.read())
                    return True, name
                else:
                    return False, await resp.json()


# /rmbg Command
@app.on_message(filters.command("rmbg"), group=383937)
async def rmbg_handler(bot, message):
    msg = await message.reply("Processing...")
    replied = message.reply_to_message

    if not replied or not replied.photo:
        return await msg.edit("Reply to a photo to remove its background.")

    photo = await bot.download_media(replied)
    success, result = await RemoveBG(photo)
    os.remove(photo)

    if not success:
        err = result['errors'][0]
        return await msg.edit(f"ERROR: {err['title']}\nDetails: {err.get('detail', 'No details provided.')}")

    await message.reply_photo(photo=result, caption="Here is your image without background.")
    await message.reply_document(document=result)
    await msg.delete()
    os.remove(result)


# /write Command
@app.on_message(filters.command("write"), group=383982)
async def write_handler(_, message: Message):
    text = message.reply_to_message.text if message.reply_to_message else message.text.split(None, 1)[1]
    m = await message.reply_text("Writing your text... ✍️")
    response = requests.get(f"https://apis.xditya.me/write?text={text}").url
    caption = f"""
✨ ᴛᴇxᴛ ᴡʀɪᴛᴛᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ

❤️ ʙᴏᴛ: [ʜᴀʀʀʏメᴘᴏᴛᴛᴇʀ](https://t.me/harry_RoxBot)
✨ ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ: {message.from_user.mention}
"""
    await m.delete()
    await message.reply_photo(photo=response, caption=caption)



# Plugin Info
__PLUGIN__ = "Media Tools"

__HELP__ = """
**Tools & Media Uploaders:**

Upload media/text to various services:

🌍 **Media Uploaders**
• `/imgbb` – Upload photos to imgBB
• `/envs` – Upload any file or text to envs.sh
• `/catbox` – Upload file to catbox.moe (no DMCA)

🧰 **Extra Tools**
• `/rmbg` – Remove background from a photo
• `/write` – Convert replied text to handwriting style image
"""
