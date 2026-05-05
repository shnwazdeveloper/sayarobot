from pyrogram import filters

from Curse.bot_class import app
from Curse.database.toggle_mongo import nsfw_off
from Curse.extras.errors import capture_err
from Curse.utils.custom_filters import admin_filter
from Curse.vars import Config


UNAVAILABLE_TEXT = (
    "Anti-NSFW scanning is unavailable because the old ARQ API is no longer "
    "working and has been removed from this bot."
)


@app.on_message(
    (
        filters.sticker 
        | filters.photo
        | filters.document
        | filters.animation
        | filters.video
    )
    & ~filters.private,
    group=8,
)
@capture_err
async def detect_nsfw(_, message):
    return


@app.on_message(filters.command(["nsfwscan", f"nsfwscan@{Config.BOT_USERNAME}"]), group=8121)
@capture_err
async def nsfw_scan_command(_, message):
    await message.reply_text(UNAVAILABLE_TEXT)


@app.on_message(
    filters.command(["antinsfw", f"antinsfw@{Config.BOT_USERNAME}"])
    & ~filters.private
    & admin_filter, group=8122
)
async def nsfw_enable_disable(_, message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /antinsfw [on/off]")
        return
    status = message.text.split(None, 1)[1].strip()
    status = status.lower()
    chat_id = message.chat.id
    if status in ("on", "yes"):
        await message.reply_text(UNAVAILABLE_TEXT)
    elif status in ("off", "no"):
        await nsfw_off(chat_id)
        await message.reply_text("Disabled AntiNSFW System.")
    else:
        await message.reply_text("Unknown Suffix, Use /antinsfw [on/off]")


__PLUGIN__ = "Anti-NSFW"

__HELP__ = """
**🔞 Anti-NSFW scanning is currently unavailable.**

The old ARQ API used by this feature is no longer working and has been removed.

**Usage:**

➥ /antinsfw off: Disables Anti-NSFW for the current chat
➥ /nsfwscan: Shows the unavailable message
"""
