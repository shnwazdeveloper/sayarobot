import random
from datetime import datetime

from pyrogram import *
from pyrogram.enums.parse_mode import ParseMode

from Curse.bot_class import app
from Curse.database.karma_mongo import get_couple, save_couple


def dt():
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y %H:%M")
    dt_list = dt_string.split(" ")
    return dt_list


def dt_tom():
    a = (
        str(int(dt()[0].split("/")[0]) + 1)
        + "/"
        + dt()[0].split("/")[1]
        + "/"
        + dt()[0].split("/")[2]
    )
    return a


tomorrow = str(dt_tom())
today = str(dt()[0])

COUPLES_PIC = "https://telegra.ph/file/e458d20773173645b795a-c9c15cf9964bd72681.jpg"
C = """
💌 ᴄᴏᴜᴘʟᴇs ᴏғ ᴛʜᴇ ᴅᴀʏ : :\n
{} + ( Shouko + 花火 + ゼロツー ) = 💘\n
ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12AM {}
"""
CAP = """
💌 ᴄᴏᴜᴘʟᴇs ᴏғ ᴛʜᴇ ᴅᴀʏ : :\n
{} + {} = 💘\n
ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12AM {}
"""

CAP2 = """
💌 ᴄᴏᴜᴘʟᴇs ᴏғ ᴛʜᴇ ᴅᴀʏ : :\n
{} + {} = 💘\n
ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12AM {}
"""


@app.on_message(filters.command(["couple", "couples", "shipping"]) & ~filters.private)
async def nibba_nibbi(_: Client, message):
    if message.from_user.id == 1805959544:
        my_ = await _.get_users("rfxtuv")
        me = await _.get_users(1805959544)
        await message.reply_photo(
            photo=COUPLES_PIC, caption=C.format(me.mention, tomorrow)
        )
    else:
        try:
            chat_id = message.chat.id
            is_selected = await get_couple(chat_id, today)
            if not is_selected:
                list_of_users = []
                async for i in _.get_chat_members(message.chat.id, limit=50):
                    if not i.user.is_bot:
                        list_of_users.append(i.user.id)
                if len(list_of_users) < 2:
                    return await message.reply_text("ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴜsᴇʀs ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.")
                c1_id = random.choice(list_of_users)
                c2_id = random.choice(list_of_users)
                while c1_id == c2_id:
                    c1_id = random.choice(list_of_users)
                c1_mention = (await _.get_users(c1_id)).mention
                c2_mention = (await _.get_users(c2_id)).mention
                await _.send_photo(
                    message.chat.id,
                    photo=COUPLES_PIC,
                    caption=CAP.format(c1_mention, c2_mention, tomorrow),
                )

                couple = {"c1_id": c1_id, "c2_id": c2_id}
                await save_couple(chat_id, today, couple)

            elif is_selected:
                c1_id = int(is_selected["c1_id"])
                c2_id = int(is_selected["c2_id"])

                c1_name = (await _.get_users(c1_id)).first_name
                c2_name = (await _.get_users(c2_id)).first_name
                print(c1_id, c2_id, c1_name, c2_name)
                couple_selection_message = f"""💌 ᴄᴏᴜᴘʟᴇs ᴏғ ᴛʜᴇ ᴅᴀʏ :
[{c1_name}](tg://openmessage?user_id={c1_id}) + [{c2_name}](tg://openmessage?user_id={c2_id}) = 💞
ɴᴇᴡ ᴄᴏᴜᴘʟᴇ ᴏғ ᴛʜᴇ ᴅᴀʏ ᴄᴀɴ ʙᴇ ᴄʜᴏsᴇɴ ᴀᴛ 12AM {tomorrow}"""
                await _.send_photo(
                    message.chat.id,
                    photo=COUPLES_PIC,
                    caption=couple_selection_message,
                    parse_mode=ParseMode.MARKDOWN,
                )
        except Exception as e:
            print(e)
            await message.reply_text(e)
__PLUGIN__ = "Couples"

__HELP__ = """
💘 Choose couples in your chat.

➥ /couple, /couples, /shipping : Choose 2 users and send their names as couples in your chat.
"""
