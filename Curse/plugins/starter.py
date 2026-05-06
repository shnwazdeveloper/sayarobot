import re
from time import gmtime, strftime, time

from pyrogram import enums, filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.enums import ChatType
from pyrogram.errors import (BadRequest, MediaCaptionTooLong, MessageNotModified,
                             UserIsBlocked)
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)

from Curse import (HELP_COMMANDS, LOGGER, PYROGRAM_VERSION, PYTHON_VERSION,
                    UPTIME, VERSION)
from Curse.bot_class import app
from Curse.utils.custom_filters import command
from Curse.utils.extras import StartVideo
from Curse.utils.kbhelpers import ikb
from Curse.utils.start_utils import (gen_start_kb, get_help_msg,
                                      get_private_note, get_private_rules)
from Curse.utils.text_style import smallcaps, smallcaps_html
from Curse.vars import Config
from Curse.utils.paginate import paginate_modules

C_HANDLER = Config.PREFIX_HANDLER


def _telegram_url(username, query=""):
    username = (username or "").lstrip("@")
    return f"https://t.me/{username}{query}" if username else "https://t.me/"


async def _reply_start_video(message, caption, reply_markup=None, parse_mode=None, quote=True):
    return await message.reply_video(
        video=StartVideo,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode=parse_mode,
        quote=quote,
        supports_streaming=True,
    )


def _back_close_markup(back_callback="start_back"):
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(smallcaps("Back"), callback_data=back_callback),
                InlineKeyboardButton(smallcaps("Close"), callback_data="close_menu"),
            ],
        ]
    )


def _module_help_markup(help_kb):
    rows = ikb(help_kb).inline_keyboard if help_kb else []
    rows.append(
        [
            InlineKeyboardButton(smallcaps("Back"), callback_data="commands"),
            InlineKeyboardButton(smallcaps("Close"), callback_data="close_menu"),
        ]
    )
    return InlineKeyboardMarkup(rows)


@app.on_callback_query(filters.regex("^close_menu$"))
async def close_menu(_, query: CallbackQuery):
    await query.answer()
    await query.message.delete()


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
                if len(help_msg) >= 1026:
                    await m.reply_text(
                        help_msg,
                        parse_mode=enums.ParseMode.MARKDOWN,
                        reply_markup=help_kb,
                        quote=True,
                    )
                    return
                await _reply_start_video(
                    m,
                    caption=help_msg,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=help_kb,
                    quote=True,
                )
                return

        # ── default PM /start ─────────────────────────────────────
        try:
            caption = smallcaps(
                f"""
Hello there, I am {Config.BOT_NAME}.
A magic-powered Telegram bot built to manage your groups and make things fun.
Don't forget to check out the About Me section below for all the cool stuff I can do!
"""
            )

            await _reply_start_video(
                m,
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
            [[InlineKeyboardButton(smallcaps("Click here for help"), url=_telegram_url(Config.BOT_USERNAME, "?start=start"))]]
        )

        await _reply_start_video(
            m,
            caption=smallcaps("I am awake. Use the button below for help."),
            reply_markup=kb,
            parse_mode=enums.ParseMode.MARKDOWN,
            quote=True,
        )


@app.on_callback_query(filters.regex("^start_back$"))
async def start_back(_, q: CallbackQuery):
    try:
        cpt = f"""
Hello there, I am {Config.BOT_NAME}.
A magic-powered Telegram bot built to manage your groups and make things fun.
Don't forget to check out the About Me section below for all the cool stuff I can do!
"""

        await q.edit_message_caption(
            caption=smallcaps(cpt),
            reply_markup=(await gen_start_kb(q.message)),
        )
    except MessageNotModified:
        pass
    await q.answer()
    return


@app.on_callback_query(filters.regex("^commands$"))
async def commands_menu(_, q: CallbackQuery):
    cpt = smallcaps(
        """
Hello.
I'm here to help you manage your groups
Commands available:
"""
    )

    await q.edit_message_caption(
        caption=cpt,
        reply_markup=InlineKeyboardMarkup(paginate_modules(0, HELP_COMMANDS, "help")),
    )
    await q.answer()
    return


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
                    help_msg,
                    parse_mode=enums.ParseMode.MARKDOWN,
                    reply_markup=help_kb,
                    quote=True,
                )
                return
            await _reply_start_video(
                m,
                caption=help_msg,
                parse_mode=enums.ParseMode.MARKDOWN,
                reply_markup=help_kb,
                quote=True,
            )
        else:

            await _reply_start_video(
                m,
                caption=smallcaps(f"Press the button below to get help for {help_option}"),
                reply_markup=InlineKeyboardMarkup(
                  [
                    [
                      InlineKeyboardButton(
                        smallcaps("Help"),
                        url=_telegram_url(Config.BOT_USERNAME, f"?start={help_option}"),
                        ),
                    ],
                  ],
                ),
            )
    else:

        if m.chat.type == ChatType.PRIVATE:
            msg = smallcaps(
                """
Hello.
I'm here to help you manage your groups
Commands available:
"""
            )
            reply_markup = InlineKeyboardMarkup(paginate_modules(0, HELP_COMMANDS, "help"))
        else:
            reply_markup = InlineKeyboardMarkup(
              [
                [
                  InlineKeyboardButton(
                    smallcaps("Help"),
                    url=_telegram_url(Config.BOT_USERNAME, "?start=start_help"),
                  ),
                ],
              ],
            )
            msg = smallcaps("Contact me in PM to get the list of possible commands.")

        await _reply_start_video(
            m,
            caption=msg,
            reply_markup=reply_markup,
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

@app.on_callback_query(filters.regex(r"^plugins\."))
async def get_module_info(c: app, q: CallbackQuery):
    module = q.data.split(".", 1)[1]

    help_msg = HELP_COMMANDS[f"plugins.{module}"]["help_msg"]

    help_kb = HELP_COMMANDS[f"plugins.{module}"]["buttons"]
    try:
      await q.edit_message_caption(
          caption=help_msg,
          parse_mode=enums.ParseMode.MARKDOWN,
          reply_markup=_module_help_markup(help_kb),
      )
    except MediaCaptionTooLong:
      await c.send_message(
          chat_id=q.message.chat.id,
          text=help_msg,
          parse_mode=enums.ParseMode.MARKDOWN,
          reply_markup=_module_help_markup(help_kb),
      )
    await q.answer()
    return

@app.on_callback_query(filters.regex("^details$"))
async def handle_details_callback(_, query: CallbackQuery):
    await query.answer()
    await query.message.edit_caption(
     smallcaps_html(f"""<a href='{_telegram_url(Config.BOT_USERNAME)}'>{Config.BOT_NAME}</a> is a powerful bot crafted for group management with useful extra features.

Built upon the solid foundation of Gojo,
{Config.BOT_NAME} operates under the GNU General Public License v3.0.

Got questions or need some help with the bot?
Hop into the support chat. The help desk is always open."""),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(smallcaps("How to use me"), callback_data="how_to_use"),
                ],
                [
                    InlineKeyboardButton(smallcaps("Ping"), callback_data="bot_curr_info"),
                ],
                [
                    InlineKeyboardButton(smallcaps("Back"), callback_data="start_back"),
                    InlineKeyboardButton(smallcaps("Close"), callback_data="close_menu"),
                ],
            ],
        ),
        parse_mode=enums.ParseMode.HTML,
    )

@app.on_callback_query(filters.regex("^how_to_use$"))
async def handle_how_to_use_callback(_, query: CallbackQuery):
    await query.answer()
    await query.message.edit_caption(
     smallcaps_html(f"""Hey there. My name is {Config.BOT_NAME}. Click on help to know my commands.

I'm here to make your group management fun and easy! I have lots of handy features, such as flood control, a warning system, a note keeping system, and even replies on predetermined filters.

Join the updates channel to keep yourself updated about me.

Any issues or need help related to me? Come visit us in support chat.

You Can Know More About Me By Clicking The Below Buttons.
        """),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(smallcaps("Add me to your group"), url=_telegram_url(Config.BOT_USERNAME, "?startgroup=new")),
                ],
                [
                    InlineKeyboardButton(smallcaps("Back"), callback_data="start_back"),
                    InlineKeyboardButton(smallcaps("Close"), callback_data="close_menu"),
                ],
            ],
        ),
    )

@app.on_callback_query(filters.regex(r"help_(.*?)"))
async def help_button(_,query):
    HELP_STRINGS = smallcaps(
        """I'm here to help you manage your groups
Commands available."""
    )
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
                "**{} {}**:\n".format(
                    smallcaps("Available commands for"),
                    smallcaps(module.replace("_", " ").title()),
                )
                + HELP_COMMANDS[f"plugins.{module}"]["help_msg"]
            )
            await query.message.edit_caption(
                text,
                reply_markup=_back_close_markup("help_back"),
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

        await query.answer()
        return

    except BadRequest as e:
        print(e)
        # pass
