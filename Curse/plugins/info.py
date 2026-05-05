import os
from asyncio import sleep
from datetime import datetime
from traceback import format_exc

from pyrogram import *
from pyrogram.errors import *
from pyrogram.raw.functions.users import GetFullUser
from pyrogram.types import *

from Curse import DEV_USERS, LOGGER, OWNER_ID, SUDO_USERS, WHITELIST_USERS
from Curse.bot_class import app
from Curse.supports import get_support_staff
from Curse.database.antispam_db import GBan
from Curse.utils.custom_filters import command
from Curse.utils.extract_user import extract_user
from Curse.vars import Config

gban_db = GBan()
SUPPORT_STAFF = get_support_staff()

async def get_user(c: app, user, already=False):
    if not already:
        user = await c.get_users(user_ids=user)
    user_id = user.id
    userrr = await c.resolve_peer(user_id)
    try:
        full_user = await c.invoke(GetFullUser(id=userrr))
        about = full_user.full_user.about
    except Exception:
        about = " Bio is shrouded in mystery..."
    return user.mention

async def user_info(c: app, user, already=False):
    if not already:
        user = await c.get_users(user_ids=user)

    if not user.first_name:
        return [" This ghost has no name.", None]

    user_id = user.id
    userrr = await c.resolve_peer(user_id)
    try:
        full_user = await c.invoke(GetFullUser(id=userrr))
        about = full_user.full_user.about or " No incantations written yet..."
    except:
        about = " Bio is protected by ancient spells."

    mention = user.mention(user.first_name)
    photo_id = user.photo.big_file_id if user.photo else None

    if user_id == OWNER_ID:
        role = " The Chosen One (Bot Master)"
    elif user_id == Config.BOT_ID:
        role = " Enchanted Assistant (Bot)"
    elif user_id in DEV_USERS:
        role = " Order of Developers"
    elif user_id in SUDO_USERS:
        role = " Support Council (Sudo)"
    elif user_id in WHITELIST_USERS:
        role = " Sacred Whitelist"
    else:
        role = " Muggle / Unknown Wizard"

    if user.status == enums.UserStatus.ONLINE:
        status = " Wand Active (Online)"
    elif user.status == enums.UserStatus.OFFLINE:
        status = f" Last spell cast at {datetime.fromtimestamp(user.status.date).strftime('%Y-%m-%d %H:%M:%S')}"
    elif user.status == enums.UserStatus.RECENTLY:
        status = " Spotted Recently"
    elif user.status == enums.UserStatus.LAST_WEEK:
        status = " Vanished (Last Week)"
    elif user.status == enums.UserStatus.LAST_MONTH:
        status = " Disappeared (Last Month)"
    elif user.status == enums.UserStatus.LONG_AGO:
        status = " Missing From the Realm"
    else:
        status = " Status Concealed"

    gban_status, gban_reason = gban_db.get_gban(user_id)
    gban_status = " Cursed (GBanned)" if gban_status else " No Dark Magic Detected"
    gban_reason = gban_reason or " No known offense."

    caption = f"""
 <b><i>『 𝙒𝙞𝙯𝙖𝙧𝙙 𝙋𝙧𝙤𝙛𝙞𝙡𝙚 』</i></b>
━━━━━━━━━━━━━━━━━━━━━━
 <b>Name:</b> {user.first_name} {user.last_name or ''}
 <b>Username:</b> @{user.username or "None"}
 <b>User ID:</b> <code>{user_id}</code>
 <b>Mention:</b> {mention}

 <b>Bio:</b> <i>{about}</i>
 <b>Role:</b> {role}
 <b>Support Staff:</b> {" Yes" if user_id in SUPPORT_STAFF else " No"}

 <b>Status:</b> {status}
 <b>GBan Status:</b> {gban_status}
 <b>GBan Reason:</b> <i>{gban_reason}</i>

 <b>Data Center:</b> <code>{user.dc_id if user.dc_id else "Unknown"}</code>
 <b>Verified:</b> {"" if user.is_verified else ""}
 <b>Bot:</b> {"" if user.is_bot else ""}
 <b>Fake:</b> {"" if user.is_fake else ""}
 <b>Scam:</b> {"" if user.is_scam else ""}
 <b>Restricted:</b> {"" if user.is_restricted else ""}

━━━━━━━━━━━━━━━━━━━━━━
 <i>“I solemnly swear that I am up to no good.”</i>
"""
    return caption, photo_id

@app.on_message(command(["info", "whois"]))
async def info_func(c: app, message: Message):
    user, _, user_name = await extract_user(c, message)
    if not user:
        return await message.reply_text(" You need to specify a target for the reveal spell!")

    m = await message.reply_text(" Casting Revelio Charm... please wait...")

    try:
        info_caption, photo_id = await user_info(c, user)
    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return await m.edit(" The spell backfired!\n\n" + str(e))

    await m.delete()
    await sleep(1.5)

    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton(" Close Grimoire", callback_data="close_info")]
    ])

    if not photo_id:
        return await message.reply_text(info_caption, disable_web_page_preview=True, reply_markup=reply_markup)

    photo = await c.download_media(photo_id)
    try:
        await message.reply_photo(
            photo, caption=info_caption, quote=False, reply_markup=reply_markup
        )
    except MediaCaptionTooLong:
        await message.reply_photo(photo)
        await message.reply_text(info_caption)
    except Exception as e:
        await message.reply_text(" Error sending magical scroll:\n" + str(e))
        LOGGER.error(e)

    os.remove(photo)

@app.on_callback_query(filters.regex(pattern=r"close_info"))
async def close_info_button(c: app, callback_query: CallbackQuery):
    await callback_query.answer(" Closing the Marauder’s Map...")
    await callback_query.message.delete()


__PLUGIN__ = "Wizard Info"
__alt_name__ = ["info", "whois", "revelio"]
__HELP__ = """
 <b><u>Wizard Identity Spells</u></b>

 <code>/info</code> or <code>/whois</code>
‣ Reveal magical identity and background of any wizard (user).

 Includes:
- House Role (Owner, Dev, Sudo, etc.)
- Bio (if written on the Scrolls)
- Scam/Fake/Bot status
- Online/offline timestamps
- Gban curse detection
"""
