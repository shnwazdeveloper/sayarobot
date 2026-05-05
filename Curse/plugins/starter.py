import os
import re
from random import choice
from time import gmtime, strftime, time

from pyrogram import enums, filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.enums import ChatType
from pyrogram.errors import (MediaCaptionTooLong, MessageNotModified,
                             QueryIdInvalid, UserIsBlocked)
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)

from Curse import (HELP_COMMANDS, LOGGER, PYROGRAM_VERSION, PYTHON_VERSION,
                    UPTIME, VERSION)
from Curse.bot_class import app
from Curse.utils.custom_filters import command
from Curse.utils.extras import StartPic
from Curse.utils.kbhelpers import ikb
from Curse.utils.start_utils import (gen_cmds_kb, gen_start_kb, get_help_msg,
                                      get_private_note, get_private_rules)
from Curse.vars import Config
from Curse.utils.paginate import paginate_modules

C_HANDLER = Config.PREFIX_HANDLER


def _telegram_url(username, query=""):
    username = (username or "").lstrip("@")
    return f"https://t.me/{username}{query}" if username else "https://t.me/"


@app.on_callback_query(filters.regex("^donate$"))
async def handle_donate_callback(_, query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(
        f"""
        Hey dude! 😄
So glad to hear you wanna donate! 💖

You can directly contact my developer for donation info,
or just hop into our [support chat]({_telegram_url(Config.SUPPORT_GROUP)}) and ask there — we’ll help you out! 🙌

Thanks for supporting the magic! 🪄✨""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Support", url=_telegram_url(Config.SUPPORT_GROUP)),
                ],
                [InlineKeyboardButton("Back", callback_data="start_back")],
            ],
        ),
    )

    LOGGER.info(f"{query.from_user.id} fetched donation text")
    return


@app.on_callback_query(filters.regex("^close_admin$"))
async def close_admin_callback(_, q: CallbackQuery):
    user_id = q.from_user.id
    user_status = (await q.message.chat.get_member(user_id)).status
    if user_status not in {CMS.OWNER, CMS.ADMINISTRATOR}:
        await q.answer(
            "Yᴏᴜ'ʀᴇ ɴᴏᴛ ᴇᴠᴇɴ ᴀɴ ᴀᴅᴍɪɴ, ᴅᴏɴ'ᴛ ᴛʀʏ ᴛʜɪs ᴇxᴘʟᴏsɪᴠᴇ sʜɪᴛ!",
            show_alert=True,
        )
        return
    if user_status != CMS.OWNER:
        await q.answer(
            "You're just an admin, not owner\nStay in your limits!",
            show_alert=True,
        )
        return
    await q.message.edit_text("Closed!")
    await q.answer("Closed menu!", show_alert=True)
    return


@app.on_message(filters.command(["start"], C_HANDLER), group=696969)
async def start(c: app, m: Message):

    # ── PRIVATE CHAT (deep‑link handling) ─────────────────────────
    if m.chat.type == ChatType.PRIVATE:

        # deep‑link or help flag
        if len(m.text.split(maxsplit=1)) > 1:
            help_option = m.text.split(None, 1)[1].lower()

            if help_option.startswith("note") and help_option not in ("note", "notes"):
                await get_private_note(c, m, help_option)
                return

            if help_option.startswith("rules"):
                LOGGER.info(f"{m.from_user.id} fetched private rules in {m.chat.id}")
                await get_private_rules(c, m, help_option)
                return

            # module help
            help_msg, help_kb = await get_help_msg(m, help_option)
            if help_msg:
                sent = await m.reply_photo(
                    photo=str(choice(StartPic)),
                    caption=help_msg,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=help_kb,
                    quote=True,
                )
                return

        # ── default PM /start ─────────────────────────────────────
        try:
            caption = f"""
Hello There, I'm {Config.BOT_NAME} 🧙
A magic-powered Telegram bot built to manage your groups and make things fun.
Don't forget to check out the About Me section below for all the cool stuff I can do!
"""

            sent = await m.reply_photo(
                photo=str(choice(StartPic)),
                caption=caption,
                reply_markup=await gen_start_kb(m),
                parse_mode=enums.ParseMode.MARKDOWN,
                quote=True,
            )

        except UserIsBlocked:
            LOGGER.warning(f"Bot blocked by {m.from_user.id}")

    # ── GROUP CONTEXT ────────────────────────────────────────────
    else:
        kb = InlineKeyboardMarkup(
            [[InlineKeyboardButton("✨ Click here for help", url=_telegram_url(Config.BOT_USERNAME, "?start=start"))]]
        )

        await m.reply_photo(
            photo=str(choice(StartPic)),
            caption=f"🧙 I’m awake! For updates and details, visit [Updates]({_telegram_url(Config.SUPPORT_CHANNEL)}).",
            reply_markup=kb,
            parse_mode=enums.ParseMode.MARKDOWN,
            quote=True,
        )


@app.on_callback_query(filters.regex("^start_back$"))
async def start_back(_, q: CallbackQuery):
    try:
        cpt = f"""
Hello There, I'm {Config.BOT_NAME} 🧙
A magic-powered Telegram bot built to manage your groups and make things fun.
Don't forget to check out the About Me section below for all the cool stuff I can do!
"""

        await q.edit_message_caption(
            caption=cpt,
            reply_markup=(await gen_start_kb(q.message)),
        )
    except MessageNotModified:
        pass
    await q.answer()
    return


@app.on_callback_query(filters.regex("^commands$"))
async def commands_menu(_, q: CallbackQuery):
    # ou = await gen_cmds_kb(q.message)
    # keyboard = ikb(ou, True)
    # try:
        cpt = f"""
Hello, .
I'm here to help you manage your groups
Commands available:"""

        await q.edit_message_caption(
            caption=cpt,
            reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELP_COMMANDS, "help")
                ),
        )
    # except MessageNotModified:
    #     pass
    # except QueryIdInvalid:
    #     await q.message.reply_photo(
    #         photo=str(choice(StartPic)), caption=cpt, reply_markup=keyboard
    #     )

    # await q.answer()
    # return


@app.on_message(filters.command(["help"], C_HANDLER), group=1001)
async def help_menu(_, m: Message):
    if len(m.text.split()) >= 2:
        textt = m.text.replace(" ","_",).replace("_"," ",1)
        help_option = (textt.split(None)[1]).lower()
        help_msg, help_kb = await get_help_msg(m, help_option)

        if not help_msg:
            LOGGER.error(f"No help_msg found for help_option - {help_option}!!")
            return

        LOGGER.info(
            f"{m.from_user.id} fetched help for '{help_option}' text in {m.chat.id}",
        )

        if m.chat.type == ChatType.PRIVATE:
            if len(help_msg) >= 1026:
                await m.reply_text(
                    help_msg, parse_mode=enums.ParseMode.MARKDOWN, quote=True
                )
            await m.reply_photo(
                photo=str(choice(StartPic)),
                caption=help_msg,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=help_kb,
                quote=True,
            )
        else:

            await m.reply_photo(
                photo=str(choice(StartPic)),
                caption=f"Press the button below to get help for <i>{help_option}</i>",
                reply_markup=InlineKeyboardMarkup(
                  [
                    [
                      InlineKeyboardButton(
                        "Help",
                        url=_telegram_url(Config.BOT_USERNAME, f"?start={help_option}"),
                        ),
                    ],
                  ],
                ),
            )
    else:

        if m.chat.type == ChatType.PRIVATE:
            msg = f"""
Hello, .
I'm here to help you manage your groups
Commands available:
"""
        else:
            keyboard = InlineKeyboardMarkup(
              [
                [
                  InlineKeyboardButton(
                    "Help", 
                    url=_telegram_url(Config.BOT_USERNAME, "?start=start_help"),
                  ),
                ],
              ],
            )
            msg = "Contact me in PM to get the list of possible commands."

        await m.reply_photo(
            photo=str(choice(StartPic)),
            caption=msg,
            reply_markup = InlineKeyboardMarkup(
                    paginate_modules(0, HELP_COMMANDS, "help")
                ),
        )

    return

@app.on_callback_query(filters.regex("^bot_curr_info$"))
async def give_curr_info(c: app, q: CallbackQuery):
    start = time()
    up = strftime("%Hh %Mm %Ss", gmtime(time() - UPTIME))
    x = await c.send_message(q.message.chat.id, "Pinging..")
    delta_ping = time() - start
    await x.delete()
    txt = f"""Pɪɴɢ: {delta_ping * 1000:.3f} ms
   Uᴘᴛɪᴍᴇ : {up}
   Bᴏᴛ's ᴠᴇʀsɪᴏɴ: {VERSION}
   Pʏᴛʜᴏɴ's ᴠᴇʀsɪᴏɴ : {PYTHON_VERSION}
   Pʏʀᴏɢʀᴀᴍ's ᴠᴇʀsɪᴏɴ : {PYROGRAM_VERSION}
    """
    await q.answer(txt, show_alert=True)
    return

@app.on_callback_query(filters.regex("^plugins."))
async def get_module_info(c: app, q: CallbackQuery):
    module = q.data.split(".", 1)[1]

    help_msg = HELP_COMMANDS[f"plugins.{module}"]["help_msg"]

    help_kb = HELP_COMMANDS[f"plugins.{module}"]["buttons"]
    try:
      await q.edit_message_caption(
          caption=help_msg,
          parse_mode=enums.ParseMode.MARKDOWN,
          reply_markup=ikb(help_kb, True, todo="commands"),
      )
    except MediaCaptionTooLong:
      await c.send_message(chat_id=q.message.chat.id,text=help_msg,)
    await q.answer()
    return

@app.on_callback_query(filters.regex("^details$"))
async def handle_details_callback(_, query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(
     f"""[{Config.BOT_NAME}]({_telegram_url(Config.BOT_USERNAME)}) is a powerful, anime-inspired bot crafted for group management with tons of extra magical features. 🧙‍♂️✨

Built upon the solid foundation of [Gojo](https://github.com/Gojo-Bots/Gojo_Satoru),
{Config.BOT_NAME} operates under the GNU General Public License v3.0 🛡️

Got questions or need some help with the bot?
Hop into the [Support Chat]({_telegram_url(Config.SUPPORT_GROUP)}) — the help desk is always open! 💬🔮""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("How to use me", callback_data="how_to_use"),
                ],
                [
                    InlineKeyboardButton("♨️ Ping", callback_data="bot_curr_info"),
                    InlineKeyboardButton("↩️ Back ↩️", callback_data="start_back"),
                ],
            ],
        ),
    )

@app.on_callback_query(filters.regex("^how_to_use$"))
async def handle_how_to_use_callback(_, query: CallbackQuery):
    await query.answer()
    await query.message.edit_text(
     f"""Hey there! my name is {Config.BOT_NAME}. Click on Help button to know my commands

I'm here to make your group management fun and easy! I have lots of handy features, such as flood control, a warning system, a note keeping system, and even replies on predetermined filters.

 Join [Updates Channel]({_telegram_url(Config.SUPPORT_CHANNEL)}) To Keep Yourself Updated About me.

Any issues or need help related to me? Come visit us in [Support Chat]({_telegram_url(Config.SUPPORT_GROUP)})

You Can Know More About Me By Clicking The Below Buttons.
        """,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("Add Me to Your Group", url=_telegram_url(Config.BOT_USERNAME, "?startgroup=new")),
                ],
                [InlineKeyboardButton("Back", callback_data="start_back")],
            ],
        ),
    )

@app.on_callback_query(filters.regex(r"help_(.*?)"))
async def help_button(_,query):  
    HELP_STRINGS = f"""I'm here to help you manage your groups
Commands available."""
    mod_match = re.match(r"help_module\((.+?)\)", query.data)
    prev_match = re.match(r"help_prev\((.+?)\)", query.data)
    next_match = re.match(r"help_next\((.+?)\)", query.data)
    back_match = re.match(r"help_back", query.data) 
    try:
        if back_match:
           await query.message.edit_caption(
                HELP_STRINGS,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(0, HELP_COMMANDS, "help")
                ),
            )            
        elif mod_match:
            module = mod_match.group(1)
            text = (
                "» **ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs ꜰᴏʀ** **{}** :\n".format(
                    module.title()
                )
                + HELP_COMMANDS[f"plugins.{module}"]["help_msg"]
            )
            await query.message.edit_caption(
                text,               
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton(text="Back", callback_data="help_back")]]
                ),
            )

        elif prev_match:
            curr_page = int(prev_match.group(1))
            await query.message.edit_caption(
                HELP_STRINGS,
                reply_markup=InlineKeyboardMarkup(paginate_modules(curr_page - 1, HELP_COMMANDS, "help")
             ),
          )
                                   
        elif next_match:
            next_page = int(next_match.group(1))
            await query.message.edit_caption(
                HELP_STRINGS,
                reply_markup=InlineKeyboardMarkup(
                    paginate_modules(next_page + 1, HELP_COMMANDS, "help")
                ),
            )                   

        return await _.answer_callback_query(query.id)

    except errors.BadRequest as e:
        print(e)
        # pass
