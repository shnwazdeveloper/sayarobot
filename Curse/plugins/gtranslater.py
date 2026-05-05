# plugins/translator.py
from googletrans import Translator
from pyrogram import filters, enums
from pyrogram.types import Message
from Curse.bot_class import app

translator = Translator()  # googletrans 4.0.2

@app.on_message(filters.command(["tr", "tl"]) & filters.reply, group=38400)
async def translate_handler(_, message: Message):
    """
    Translate text using Google Translate API
    Usage:
    • /tr              → Auto-detect source → English
    • /tr hi           → Auto-detect → Hindi
    • /tr es//en       → Spanish → English
    """
    working = await message.reply(" Translating…")

    reply = message.reply_to_message
    if not reply:
        return await working.edit(" Reply to a text message to translate it.")

    to_translate = reply.text or reply.caption
    if not to_translate:
        return await working.edit(" No text found to translate.")

    try:
        raw_args = message.text.split(maxsplit=1)[1].strip().lower()
    except IndexError:
        raw_args = ""

    try:
        if "//" in raw_args:
            src_lang, dest_lang = raw_args.split("//", 1)
        else:
            detection = await translator.detect(to_translate)
            src_lang = detection.lang
            dest_lang = raw_args or "en"
    except Exception as e:
        return await working.edit(f" Detection error: `{e}`")

    try:
        result = await translator.translate(to_translate, src=src_lang, dest=dest_lang)
        text = (
            f"**Translated** `{src_lang}` → `{dest_lang}`\n\n"
            f"`{result.text}`"
        )
        await working.edit(text, parse_mode=enums.ParseMode.MARKDOWN)
    except Exception as e:
        await working.edit(f" Translation failed: `{e}`")
