from pyrogram import filters
from pyrogram.types import Message

from Curse.bot_class import app
from Curse.extras.https import fetch


async def get_cosplay_data():
    cosplay_url = "https://black-bay.vercel.app/cosplay"
    response = await fetch.get(cosplay_url)
    return response.json()


@app.on_message(filters.command("cosplay"))
async def cosplay(_, message: Message):
    try:
        data = await get_cosplay_data()
        photo_url = data.get("url")  # Corrected key: "url" instead of "cosplay_url"
        if photo_url:
            await message.reply_photo(photo=photo_url)
        else:
            await message.reply_text("Could not fetch photo URL.")
    except fetch.FetchError:
        await message.reply_text("Unable to fetch data.")


@app.on_message(filters.command("id"))
async def _id(client, message):
    chat = message.chat
    your_id = message.from_user.id
    mention_user = message.from_user.mention
    message_id = message.id
    reply = message.reply_to_message

    text = f"**๏ [ᴍᴇssᴀɢᴇ ɪᴅ]({message.link})** » `{message_id}`\n"
    text += f"**๏ [{mention_user}](tg://user?id={your_id})** » `{your_id}`\n"

    if not message.command:
        message.command = message.text.split()

    if not message.command:
        message.command = message.text.split()

    if len(message.command) == 2:
        try:
            split = message.text.split(None, 1)[1].strip()
            user_id = (await client.get_users(split)).id
            user_mention = (await client.get_users(split)).mention
            text += f"**๏ [{user_mention}](tg://user?id={user_id})** » `{user_id}`\n"

        except Exception:
            return await message.reply_text("** ᴛʜɪs ᴜsᴇʀ ᴅᴏᴇsɴ'ᴛ ᴇxɪsᴛ.**")

    text += f"**๏ [ᴄʜᴀᴛ ɪᴅ ](https://t.me/{chat.username})** » `{chat.id}`\n\n"

    if not getattr(reply, "empty", True) and not message.forward_from_chat and not reply.sender_chat:
        text += (
            f"**๏ [ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ɪᴅ]({reply.link})** » `{message.reply_to_message.id}`\n"
        )
        text += f"**๏ [ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ ɪᴅ](tg://user?id={reply.from_user.id})** » `{reply.from_user.id}`\n\n"

    if reply and reply.forward_from_chat:
        text += f"๏ ᴛʜᴇ ғᴏʀᴡᴀʀᴅᴇᴅ ᴄʜᴀɴɴᴇʟ, {reply.forward_from_chat.title}, ʜᴀs ᴀɴ ɪᴅ ᴏғ `{reply.forward_from_chat.id}`\n\n"

    if reply and reply.sender_chat:
        text += f"๏ ID ᴏғ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴄʜᴀᴛ/ᴄʜᴀɴɴᴇʟ, ɪs `{reply.sender_chat.id}`"

    await message.reply_photo(
       photo = "https://telegra.ph/file/0e1d42b86f4a167972839-844e0c51a92326ea40.jpg",
       caption=text)


__PLUGIN__ = "Cosplay"
__HELP__ = """
** Cosplay** :

 /cosplay - ᴛᴏ ɢᴇᴛ ᴄᴜᴛᴇ ᴀɴᴅ ʜᴏᴛ ᴄᴏsᴘʟᴀʏ ᴄᴏsᴛᴜᴍᴇ ɪᴍᴀɢᴇs
"""
