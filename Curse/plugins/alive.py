import random
from sys import version_info
from time import time, gmtime, strftime

from pyrogram import __version__ as pver
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Curse import UPTIME
from Curse.bot_class import app
from Curse import PREFIX_HANDLER as COMMAND_HANDLER

UPTIME = time()

MAGIC_PICS = [
    "https://files.catbox.moe/xsra9s.jpg",
    "https://files.catbox.moe/tuld2x.jpg",
    "https://files.catbox.moe/mk6j3p.jpg",
    "https://files.catbox.moe/fzpvz0.jpg",
    "https://files.catbox.moe/rqe5i1.jpg", 
]

MAGIC_QUOTES = [
    "🪄 **“Magic is not a tool, it’s a responsibility.”** – Dumbledore",
    "🧙 **“I'm not just alive, I'm enchantingly operational!”**",
    "⚡ **“Even Voldemort can’t shut me down.”**",
    "🧹 **“Ready to fly on my Firebolt anytime!”**",
    "📜 **“Magic is real. And so am I.”**",
]

MAGIC_BUTTONS = [
    [
        InlineKeyboardButton("⚡ Support Spellbook", url="https://t.me/HarryPotterSupport"),
        InlineKeyboardButton("📢 Magic News", url="https://t.me/hogwarts_updates"),
    ],
    [
        InlineKeyboardButton("➕ Add to Group", url="https://t.me/Harry_RoxBot?startgroup=true"),
    ],
]

@app.on_message(filters.command(["alive", "zinda", "zinda_ho"], COMMAND_HANDLER), group=4678)
async def golden_alive(_, m: Message):
    await m.delete()
    uptime = strftime("%Hh %Mm %Ss", gmtime(time() - UPTIME))
    python_ver = f"{version_info.major}.{version_info.minor}.{version_info.micro}"

    ascii_header = "╔═════════════════════╗\n║     🧙 Harry is ALIVE!    ║\n╚═════════════════════╝"

    await m.reply_photo(
        photo=random.choice(MAGIC_PICS),
        caption=f"""
🧙 Harry is ALIVE!

🎩 **Bot Name:** [Harry Potter](https://t.me/Harry_RoxBot)  
💠 **Status:** `🔮 Magic Online & Flowing`  
🕓 **Uptime:** `{uptime}`  
🐍 **Python:** `{python_ver}`  
📦 **Pyrogram:** `{pver}`

{random.choice(MAGIC_QUOTES)}

🔍 **Use `/help` to browse spells and commands.**
""",
        reply_markup=InlineKeyboardMarkup(MAGIC_BUTTONS),
    )
