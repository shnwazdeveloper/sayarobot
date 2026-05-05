import os
import textwrap
import time
from datetime import datetime

from PIL import Image, ImageChops, ImageDraw
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from Curse import SUDO_USERS
from Curse.bot_class import app
from Curse.database.toggle_mongo import dwelcome_off, dwelcome_on, is_dwelcome_on
from Curse.extras.utils import temp
from Curse.utils.custom_filters import admin_filter

BOT_USERNAME = "Harry_Roxbot"
LOG_CHANNEL = -1002324687097


def circle(pfp, size=(250, 250)):
    pfp = pfp.resize(size, Image.ANTIALIAS).convert("RGBA")
    bigsize = (pfp.size[0] * 3, pfp.size[1] * 3)
    mask = Image.new("L", bigsize, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + bigsize, fill=255)
    mask = mask.resize(pfp.size, Image.ANTIALIAS)
    mask = ImageChops.darker(mask, pfp.split()[-1])
    pfp.putalpha(mask)
    return pfp


def draw_multiple_line_text(image, text, font, text_start_height):
    """
    From unutbu on [python PIL draw multiline text on image](https://stackoverflow.com/a/7698300/395857)
    """
    draw = ImageDraw.Draw(image)
    image_width, image_height = image.size
    y_text = text_start_height
    lines = textwrap.wrap(text, width=50)
    for line in lines:
        line_width, line_height = font.getsize(line)
        draw.text(
            ((image_width - line_width) / 2, y_text), line, font=font, fill="black"
        )
        y_text += line_height


def welcomepic(pic, user, chat, user_id):
    background = Image.open(
        "Curse/extras/bg.png"
    )  # <- Background Image (Should be PNG)
    background = background.resize(
        (background.size[0], background.size[1]), Image.ANTIALIAS
    )
    pfp = Image.open(pic).convert("RGBA")
    pfp = circle(pfp, size=(600, 600))  # Adjust the size of the circle pfp here
    pfp_x = 180  # Adjust the X coordinate to position the profile picture on the left
    pfp_y = (background.size[1] - pfp.size[1]) // 2 + 121
    background.paste(
        pfp, (pfp_x, pfp_y), pfp
    )  # Pastes the Profilepicture on the Background Image
    welcome_image_path = f"downloads/welcome_{user_id}.png"
    background.save(
        welcome_image_path
    )  # Saves the finished Image in the folder with the filename
    return welcome_image_path


@app.on_chat_member_updated(filters.group)
async def member_has_joined(client, member: ChatMemberUpdated):
    if (
        not member.new_chat_member
        or member.new_chat_member.status in {"banned", "left", "restricted"}
        or member.old_chat_member
    ):
        return
    user = member.new_chat_member.user if member.new_chat_member else member.from_user
    if user.id in SUDO_USERS:
        await client.send_message(member.chat.id, "**ᴍʏ Bᴇsᴛo ғʀɪᴇɴᴅᴏ Jᴏɪɴᴇᴅ ᴛʜᴇ ᴄʜᴀᴛ!**")
        return
    elif user.is_bot:
        return  # ignore bots
    else:
        chat_id = member.chat.id
        welcome_enabled = await is_dwelcome_on(chat_id)
        if not welcome_enabled:
            return  # Welcome message is disabled for this chat

        if f"welcome-{chat_id}" in temp.MELCOW:
            try:
                await temp.MELCOW[f"welcome-{chat_id}"].delete()
            except:
                pass
        mention = f"<a href='tg://user?id={user.id}'>{user.first_name}</a>"
        joined_date = datetime.fromtimestamp(time.time()).strftime("%Y.%m.%d %H:%M:%S")
        first_name = (
            f"{user.first_name} {user.last_name}" if user.last_name else user.first_name
        )
        user_id = user.id
        dc = user.dc_id
        try:
            pic = await client.download_media(
                user.photo.big_file_id, file_name=f"pp{user_id}.png"
            )
        except AttributeError:
            pic = "Curse/extras/profilepic.png"
        try:
            welcomeimg = welcomepic(pic, user.first_name, member.chat.title, user_id)
            temp.MELCOW[f"welcome-{chat_id}"] = await client.send_photo(
                member.chat.id,
                photo=welcomeimg,
                caption=f"""Hᴇʏ ᴅᴇᴀʀ  {mention}, Wᴇʟᴄᴏᴍᴇ ᴛᴏ {member.chat.title} Gʀᴏᴜᴘ. \n
┏━━━━»»❀
♛ ɴᴀᴍᴇ : {first_name}
⍟ I'ᴅ : {user_id}
⍟ ᴅᴀᴛᴇ Jᴏɪɴᴇᴅ : {joined_date}
┕━━━━━━━━━━━━»»❀ """)
        except Exception as e:
            print(e)
        try:
            os.remove(f"downloads/welcome_{user_id}.png")
            os.remove(f"downloads/pp{user_id}.png")
        except Exception:
            pass


@app.on_message(filters.command("dwelcome on") & admin_filter)
async def enable_welcome(_, message: Message):
    chat_id = message.chat.id
    welcome_enabled = await is_dwelcome_on(chat_id)
    if welcome_enabled:
        await message.reply_text("Default welcome is already enabled")
        return
    await dwelcome_on(chat_id)
    await message.reply_text("New default welcome message enabled for this chat.")


@app.on_message(filters.command("dwelcome off") & admin_filter)
async def disable_welcome(_, message: Message):
    chat_id = message.chat.id
    welcome_enabled = await is_dwelcome_on(chat_id)
    if not welcome_enabled:
        await message.reply_text("Default welcome is already disabled")
        return
    await dwelcome_off(chat_id)
    await message.reply_text("New default welcome disabled for this chat.")


@app.on_callback_query(filters.regex(r"^normal_welcome$"))
async def normal_welcome_callback(_, query: CallbackQuery, todo="commands"):
    await query.answer()
    await query.message.edit_text(
        "**Admin Commands:**\n"
        "➥ /setwelcome < reply > : Sets a custom welcome message.\n"
        "➥ /setgoodbye < reply > : Sets a custom goodbye message.\n"
        "➥ /resetwelcome : Resets to bot default welcome message.\n"
        "➥ /resetgoodbye : Resets to bot default goodbye message.\n"
        "➥ /welcome [on - off] | noformat : enable/disable | Shows the current welcome message | settings.\n"
        "➥ /goodbye [on - off] | noformat : enable/disable | Shows the current goodbye message | settings.\n"
        "➥ /cleanwelcome [on - off] : Shows or sets the current clean welcome settings.\n"
        "➥ /cleangoodbye [on - off] : Shows or sets the current clean goodbye settings.\n\n"
        "**Cleaner:**\n"
        "➥ /cleanservice [on - off] : Use it to clean all service messages automatically or to view current status.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⌦ 𝘽𝘼𝘾𝙆", todo),
                ],
            ],
        ),
    )


__PLUGIN__ = "Welcome"
__alt_name__ = ["welcome", "dwelcome", "goodbye", "cleanservice"]
__buttons__ = [
    [("Normal Welcome", "normal_welcome")],
]

__HELP__ = """
**🎊 Greetings**

**💫 Default Welcome**
➥ /dwelcome on: turns on default new welcome
➥ /dwelcome off: turns off default new welcome

Customize your group's welcome / goodbye messages that can be personalised in multiple ways.

**Note:**

× app must be an admin to greet and goodbye users.
"""
