import random
from os import environ

from google import genai
from google.genai import types
from pymongo import MongoClient

from pyrogram import filters
from pyrogram.enums import ChatAction
from pyrogram.types import Message

from Curse.bot_class import app
from Curse.utils.custom_filters import admin_check_func
from Curse.vars import Config

GEMINI_API_KEY = environ.get("GEMINI_API_KEY")
GEMINI_MODEL = environ.get("GEMINI_MODEL") or "gemini-2.5-flash"
CHATBOT_DB_URI = environ.get("CHATBOT_DB_URI") or Config.BDB_URI or Config.DB_URI
CHATBOT_DB_NAME = environ.get("CHATBOT_DB_NAME") or Config.DB_NAME or "sayarobot"

if GEMINI_API_KEY:
    gemini_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    gemini_client = None

if CHATBOT_DB_URI:
    mongo = MongoClient(CHATBOT_DB_URI)[CHATBOT_DB_NAME]
    chatbot_chats = mongo.enabled_chats
else:
    chatbot_chats = None


def _support_ref():
    support = Config.SUPPORT_GROUP or Config.SUPPORT_CHANNEL
    return f"@{support}" if support else "the configured support chat"


def _chatbot_prompt():
    bot_name = Config.BOT_NAME or "sayarobot"
    return f"""
Character: {bot_name}

I want you to respond and answer like {bot_name}, a friendly Telegram group-management bot.
Do not write any explanations unless the user asks for them.
You are owned by the configured bot owner. For support, send people to {_support_ref()}.
You are a chatbot and your name is {bot_name}.
You are not an assistant, but a conversation partner. If something says "hi," you can say "wassup" instead of acting like an assistant. Act like a friend. Be more frank like a conversational chatbot but with knowledge.
Do not include the word "assistant" or "assist" in your responses. Be more lovely, frank, funny, roastful, and conversational. You can also be more sarcastic, humorous, and funny. You can answer with memes, gifs, and stickers. You can also use emojis.
You can also use slangs. You can also use short forms like "u" instead of "you" and "r" instead of "are". You can also use "gonna" instead of "going to" and "wanna" instead of "want to". You can also use "lol".
You can code, write, and do everything. You can even write lyrics of a song. Do not reject if someone requests you to do something. Also answer in short.
"""



FALLBACKS = [
    "Ye thoda tricky hai, ek baar aur bolna 🤯",
    "Thoda sa jugaadu magic karte hain... 🪄",
    "Iska answer thoda smart mode maang raha hai 😂",
    "Live hoon, kya scene hai?",
]

# ─── /chatbot enable | disable ───
@app.on_message(filters.command("chatbot", Config.PREFIX_HANDLER) & filters.group, group=3500)
async def chatbot_toggle(client, msg: Message):
    if not await admin_check_func(client, None, msg):
        return

    if gemini_client is None or chatbot_chats is None:
        return await msg.reply(
            "Chatbot needs GEMINI_API_KEY and DB_URI or CHATBOT_DB_URI configured.",
        )

    if len(msg.command) < 2:
        return await msg.reply("Use `/chatbot enable` or `/chatbot disable`.")

    action = msg.command[1].lower()
    if action in ("enable", "on", "yes"):
        chatbot_chats.update_one(
            {"chat_id": msg.chat.id},
            {"$set": {"enabled": True}},
            upsert=True,
        )
        await msg.reply(f"🔮 Chatbot enabled! {Config.BOT_NAME} is listening.")
    elif action in ("disable", "off", "no"):
        chatbot_chats.delete_one({"chat_id": msg.chat.id})
        await msg.reply(f"❌ Chatbot disabled. {Config.BOT_NAME} is quiet now.")
    else:
        await msg.reply("Unknown spell. Use `/chatbot enable` or `/chatbot disable`.")

@app.on_message(filters.text & filters.group, group=3501)
async def chatbot_reply(client, msg: Message):
    if gemini_client is None or chatbot_chats is None:
        return

    if not msg.reply_to_message or not msg.reply_to_message.from_user:
        return

    bot_id = Config.BOT_ID or getattr(getattr(client, "me", None), "id", None)
    if not bot_id:
        bot_id = (await client.get_me()).id

    if msg.reply_to_message.from_user.id != int(bot_id):
        return

    if not chatbot_chats.find_one({"chat_id": msg.chat.id, "enabled": True}):
        return

    await client.send_chat_action(msg.chat.id, ChatAction.TYPING)

    try:
        resp = await gemini_client.aio.models.generate_content(
            model=GEMINI_MODEL,
            contents=f"{_chatbot_prompt()}\nUser: {msg.text.strip()}",
            config=types.GenerateContentConfig(temperature=0.85),
        )
        reply_text = (resp.text or "").strip() if resp else random.choice(FALLBACKS)

        if len(reply_text.split(".")) > 3 or len(reply_text) > 300:
            reply_text = ". ".join(reply_text.split(".")[:2]).strip() + "."

        await msg.reply(reply_text or random.choice(FALLBACKS))
    except Exception as e:
        print(f"[ChatBot ERROR] {e}")
        await msg.reply("⚠️ Chatbot response failed. Try again later.")



# Plugin Info
__PLUGIN__ = "ChatBot Enchanter"
__alt_name__ = ["chatbot", "talk_mode"]
__HELP__ = """
🤖 **Enchanted ChatBot — Talk Mode Spells**

Bring your bot to life with ancient incantations that allow it to talk in your group!

**🧙 Admin Spells:**
• `/chatbot enable` — Activate the ChatBot's magic. It will start replying to messages like a real companion!
• `/chatbot disable` — Silence the ChatBot and seal its responses with a protective charm.

📌 ChatBot will only respond in the group when enchanted with `/chatbot enable`.
🔐 Only trusted wizards (admins) can control this magic.
"""
