import os
from pyrogram import filters
from pyrogram.types import Message
from Curse import pbot as bot

# Get the file type
async def FileType(message: Message):
    if message.document:
        type = message.document.mime_type
        return "txt" if type == "text/plain" else type.split("/")[1]
    elif message.photo:
        return "jpg"
    elif message.animation:
        return message.animation.mime_type.split("/")[1]
    elif message.video:
        return message.video.mime_type.split("/")[1]
    return None

@bot.on_message(filters.command("rename", ["/", "!", ".", "?"]), group=16283)
async def rename_file(_, message: Message):
    if not message.reply_to_message:
        return await message.reply_text("❌ Reply to a media message to rename it.")

    # Get the desired filename from command argument, or default to "Serena"
    try:
        new_name = message.text.split(None, 1)[1]
    except IndexError:
        new_name = "Harry Potter"

    # Get file extension
    try:
        file_type = await FileType(message.reply_to_message)
        if not file_type:
            return await message.reply_text("❌ Cannot identify the file type.")
    except Exception as e:
        return await message.reply_text(f"⚠️ Error getting file type:\n<code>{e}</code>")

    filename = f"{new_name}.{file_type}"
    progress = await message.reply_text("⬇️ Downloading file...")

    try:
        file_path = await message.reply_to_message.download(file_name=filename)
    except Exception as e:
        return await progress.edit(f"❌ Download failed: <code>{e}</code>")

    thumb_path = "Curse/extras/Komi(1).jpg"
    if not os.path.exists(thumb_path):
        thumb_path = None  # fallback if thumbnail doesn't exist

    await progress.edit("⬆️ Uploading file...")

    try:
        await message.reply_document(document=file_path, thumb=thumb_path, caption=f"📦 Renamed to: <code>{filename}</code>")
    except Exception as e:
        await progress.edit(f"❌ Upload failed: <code>{e}</code>")
    else:
        await progress.delete()
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
