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
from Curse.utils.text_style import smallcaps, smallcaps_html
from Curse.supports import get_support_staff
from Curse.vars import Config

SUPPORT_STAFF = get_support_staff()
C_HANDLER = PREFIX_HANDLER


def _telegram_url(username):
    username = (username or "").lstrip("@")
    return f"https://t.me/{username}" if username else "https://t.me/"


@app.on_message(filters.command(["stats"], C_HANDLER), group=9696)
async def get_stats(_, m: Message):
    if m.from_user.id not in SUPPORT_STAFF:
        return

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

    replymsg = await m.reply_text(
        smallcaps("Collecting bot statistics. Please wait..."),
        quote=True,
    )

    rply = (
        f"<b>{Config.BOT_NAME} records</b>\n\n"
        "<b>Current state of this bot:</b>\n\n"
        f"<b>Users registered:</b> <code>{userdb.count_users()}</code> in <code>{chatdb.count_chats()}</code> chats\n"
        f"<b>Anti-channel pin:</b> active in <code>{pinsdb.count_chats('antichannelpin')}</code> chats\n"
        f"<b>Linked message cleaning:</b> active in <code>{pinsdb.count_chats('cleanlinked')}</code> chats\n"
        f"<b>Filters:</b> <code>{fldb.count_filters_all()}</code> across <code>{fldb.count_filters_chats()}</code> chats\n"
        f"<b>Filter aliases:</b> <code>{fldb.count_filter_aliases()}</code>\n"
        f"<b>Blacklists:</b> <code>{bldb.count_blacklists_all()}</code> in <code>{bldb.count_blackists_chats()}</code> chats\n"
        f"    <b>Blacklist actions:</b>\n"
        f"        <b>None:</b> <code>{bldb.count_action_bl_all('none')}</code>\n"
        f"        <b>Kick:</b> <code>{bldb.count_action_bl_all('kick')}</code>\n"
        f"        <b>Warn:</b> <code>{bldb.count_action_bl_all('warn')}</code>\n"
        f"        <b>Ban:</b> <code>{bldb.count_action_bl_all('ban')}</code>\n"
        f"<b>Rules in:</b> <code>{rulesdb.count_chats_with_rules()}</code> chats\n"
        f"<b>Private rules:</b> <code>{rulesdb.count_privrules_chats()}</code>\n"
        f"<b>Warnings:</b> <code>{warns_db.count_warns_total()}</code> across <code>{warns_db.count_all_chats_using_warns()}</code> chats\n"
        f"<b>Users warned:</b> <code>{warns_db.count_warned_users()}</code>\n"
        f"    <b>Warn actions:</b>\n"
        f"        <b>Kick:</b> <code>{warns_settings_db.count_action_chats('kick')}</code>\n"
        f"        <b>Mute:</b> <code>{warns_settings_db.count_action_chats('mute')}</code>\n"
        f"        <b>Ban:</b> <code>{warns_settings_db.count_action_chats('ban')}</code>\n"
        f"<b>Notes stored:</b> <code>{notesdb.count_all_notes()}</code> in <code>{notesdb.count_notes_chats()}</code> chats\n"
        f"<b>Private notes:</b> <code>{notesettings_db.count_chats()}</code>\n"
        f"<b>Global bans:</b> <code>{gbandb.count_gbans()}</code>\n"
        f"<b>Welcomes active in:</b> <code>{grtdb.count_chats('welcome')}</code> chats\n"
        f"<b>Approved users:</b> <code>{appdb.count_all_approved()}</code> across <code>{appdb.count_approved_chats()}</code> chats\n"
        f"<b>Disabled commands:</b> <code>{dsbl.count_disabled_all()}</code> items across <code>{dsbl.count_disabling_chats()}</code> chats\n"
        f"     <b>Delete actions:</b> <code>{dsbl.count_action_dis_all('del')}</code> chats\n\n"
        f"<a href='{_telegram_url(Config.SUPPORT_CHANNEL or Config.SUPPORT_GROUP)}'>{Config.BOT_NAME} central archive</a>\n\n"
        f"<i>Compiled by:</i> <b>{Config.BOT_NAME}</b>\n"
    )

    await replymsg.edit_text(
        smallcaps_html(rply),
        parse_mode=enums.ParseMode.HTML,
        disable_web_page_preview=True,
    )
