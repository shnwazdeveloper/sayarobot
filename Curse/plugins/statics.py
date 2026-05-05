from pyrogram import enums, filters
from pyrogram.types import Message

from Curse import PREFIX_HANDLER
from Curse.bot_class import app
from Curse.database.antispam_db import GBan
from Curse.database.approve_db import Approve
from Curse.database.blacklist_db import Blacklist
from Curse.database.chats_db import Chats
from Curse.database.disable_db import Disabling
from Curse.database.filters_db import Filters
from Curse.database.greetings_db import Greetings
from Curse.database.notes_db import Notes, NotesSettings
from Curse.database.pins_db import Pins
from Curse.database.rules_db import Rules
from Curse.database.users_db import Users
from Curse.database.warns_db import Warns, WarnSettings
from Curse.utils.custom_filters import command
from Curse.supports import get_support_staff

SUPPORT_STAFF = get_support_staff()
C_HANDLER = PREFIX_HANDLER

@app.on_message(filters.command(["stats"], C_HANDLER), group=9696)
async def get_stats(_, m: Message):
    if m.from_user.id not in SUPPORT_STAFF:
        return

    # Initializing magic scrolls
    bldb = Blacklist
    gbandb = GBan()
    notesdb = Notes()
    grtdb = Greetings
    rulesdb = Rules
    userdb = Users
    dsbl = Disabling
    appdb = Approve
    chatdb = Chats
    fldb = Filters()
    pinsdb = Pins
    notesettings_db = NotesSettings()
    warns_db = Warns
    warns_settings_db = WarnSettings

    replymsg = await m.reply_text("🧙‍♂️ Summoning Magical Metrics... Please wait...", quote=True)

    rply = (
        "🪄 <b>𝙃𝙤𝙜𝙬𝙖𝙧𝙩𝙨 Magical Records</b>\n\n"
        "📜 <b>Here lies the current state of our enchanted realm:</b>\n\n"
        f"👥 <b>Wizards Registered:</b> <code>{userdb.count_users()}</code> in <code>{chatdb.count_chats()}</code> covens\n"
        f"📌 <b>Anti-Channel Pin Curse:</b> Active in <code>{pinsdb.count_chats('antichannelpin')}</code> covens\n"
        f"🧹 <b>Linked Message Cleaning Charm:</b> Active in <code>{pinsdb.count_chats('cleanlinked')}</code> covens\n"
        f"📖 <b>Spell Scrolls (Filters):</b> <code>{fldb.count_filters_all()}</code> across <code>{fldb.count_filters_chats()}</code> covens\n"
        f"🪶 <b>Alias Spells:</b> <code>{fldb.count_filter_aliases()}</code>\n"
        f"☠️ <b>Blacklisted Curses:</b> <code>{bldb.count_blacklists_all()}</code> in <code>{bldb.count_blackists_chats()}</code> covens\n"
        f"    🔍 <b>With Effects:</b>\n"
        f"        💤 <b>None:</b> <code>{bldb.count_action_bl_all('none')}</code>\n"
        f"        🦶 <b>Kick:</b> <code>{bldb.count_action_bl_all('kick')}</code>\n"
        f"        ⚠️ <b>Warn:</b> <code>{bldb.count_action_bl_all('warn')}</code>\n"
        f"        🚫 <b>Ban:</b> <code>{bldb.count_action_bl_all('ban')}</code>\n"
        f"📚 <b>Rules Enchanted In:</b> <code>{rulesdb.count_chats_with_rules()}</code> covens\n"
        f"🔒 <b>Private Decrees:</b> <code>{rulesdb.count_privrules_chats()}</code>\n"
        f"⚔️ <b>Warnings Cast:</b> <code>{warns_db.count_warns_total()}</code> across <code>{warns_db.count_all_chats_using_warns()}</code> covens\n"
        f"🔍 <b>Users Warned:</b> <code>{warns_db.count_warned_users()}</code>\n"
        f"    🧾 <b>Action Details:</b>\n"
        f"        🦶 <b>Kick:</b> <code>{warns_settings_db.count_action_chats('kick')}</code>\n"
        f"        🔇 <b>Mute:</b> <code>{warns_settings_db.count_action_chats('mute')}</code>\n"
        f"        🚫 <b>Ban:</b> <code>{warns_settings_db.count_action_chats('ban')}</code>\n"
        f"🗒 <b>Notes Stored:</b> <code>{notesdb.count_all_notes()}</code> in <code>{notesdb.count_notes_chats()}</code> covens\n"
        f"🔐 <b>Private Notes:</b> <code>{notesettings_db.count_chats()}</code>\n"
        f"⛔️ <b>Globally Banished Wizards:</b> <code>{gbandb.count_gbans()}</code>\n"
        f"🎉 <b>Welcoming Charms Active In:</b> <code>{grtdb.count_chats('welcome')}</code> covens\n"
        f"✅ <b>Approved Companions:</b> <code>{appdb.count_all_approved()}</code> across <code>{appdb.count_approved_chats()}</code> covens\n"
        f"🪄 <b>Disabling Hexes:</b> <code>{dsbl.count_disabled_all()}</code> items across <code>{dsbl.count_disabling_chats()}</code> covens\n"
        f"     🔍 <b>Del Actions:</b> <code>{dsbl.count_action_dis_all('del')}</code> covens\n\n"
        "🏰 <a href='https://t.me/THE_HOGWART'>𝗧𝗛𝗘 𝗛𝗢𝗚𝗪𝗔𝗥𝗧𝗦 — Central Archives</a>\n\n"
        "🧙‍♂️ <i>Compiled with wand and wisdom by:</i> <a href='t.me/its_damiann'>𝗗𝗮𝗺𝗶𝗮𝗻 ❤‍🩹🌙</a>\n"
    )

    await replymsg.edit_text(
        rply, parse_mode=enums.ParseMode.HTML, disable_web_page_preview=True
    )
