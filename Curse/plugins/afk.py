import re
import time

from pyrogram import Client, enums, filters
from pyrogram.types import Message

from Curse.bot_class import app
from Curse.database.afk_db import (
    add_afk,
    cleanmode_off,
    cleanmode_on,
    is_afk,
    remove_afk,
)
from Curse.extras.errors import capture_err
from Curse.extras.human_read import get_readable_time2
from Curse.extras.localization import use_chat_lang
from Curse.extras.util import put_cleanmode
from Curse.utils.custom_filters import admin_filter
from Curse.vars import Config


# Handle set AFK Command
@capture_err
@app.on_message(filters.command(["afk"]))
@use_chat_lang()
async def active_afk(self: Client, ctx: Message, strings):
    if ctx.sender_chat:
        return await ctx.reply(strings("no_channel"))
    user_id = ctx.from_user.id
    verifier, reasondb = await is_afk(user_id)
    if verifier:
        await remove_afk(user_id)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time2((int(time.time() - timeafk)))
            if afktype == "animation":
                send = (
                    await ctx.reply_animation(
                        data,
                        caption=strings("on_afk_msg_no_r").format(
                            usr=ctx.from_user.mention, id=ctx.from_user.id, tm=seenago
                        ),
                    )
                    if str(reasonafk) == "None"
                    else await ctx.reply_animation(
                        data,
                        caption=strings("on_afk_msg_with_r").format(
                            usr=ctx.from_user.mention,
                            id=ctx.from_user.id,
                            tm=seenago,
                            reas=reasonafk,
                        ),
                    )
                )
            elif afktype == "photo":
                send = (
                    await ctx.reply_photo(
                        photo=f"downloads/{user_id}.jpg",
                        caption=strings("on_afk_msg_no_r").format(
                            usr=ctx.from_user.mention, id=ctx.from_user.id, tm=seenago
                        ),
                    )
                    if str(reasonafk) == "None"
                    else await ctx.reply_photo(
                        photo=f"downloads/{user_id}.jpg",
                        caption=strings("on_afk_msg_with_r").format(
                            usr=ctx.from_user.first_name, tm=seenago, reas=reasonafk
                        ),
                    )
                )
            elif afktype == "text":
                send = await ctx.reply_text(
                    strings("on_afk_msg_no_r").format(
                        usr=ctx.from_user.mention, id=ctx.from_user.id, tm=seenago
                    ),
                    disable_web_page_preview=True,
                )
            elif afktype == "text_reason":
                send = await ctx.reply_text(
                    strings("on_afk_msg_with_r").format(
                        usr=ctx.from_user.mention,
                        id=ctx.from_user.id,
                        tm=seenago,
                        reas=reasonafk,
                    ),
                    disable_web_page_preview=True,
                )
        except Exception:
            send = await ctx.reply_text(
                strings("is_online").format(
                    usr=ctx.from_user.first_name, id=ctx.from_user.id
                ),
                disable_web_page_preview=True,
            )
        await put_cleanmode(ctx.chat.id, send.id)
        return
    if len(ctx.command) == 1 and not ctx.reply_to_message:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    elif len(ctx.command) > 1 and not ctx.reply_to_message:
        _reason = (ctx.text.split(None, 1)[1].strip())[:100]
        details = {
            "type": "text_reason",
            "time": time.time(),
            "data": None,
            "reason": _reason,
        }
    elif len(ctx.command) == 1 and ctx.reply_to_message.animation:
        _data = ctx.reply_to_message.animation.file_id
        details = {
            "type": "animation",
            "time": time.time(),
            "data": _data,
            "reason": None,
        }
    elif len(ctx.command) > 1 and ctx.reply_to_message.animation:
        _data = ctx.reply_to_message.animation.file_id
        _reason = (ctx.text.split(None, 1)[1].strip())[:100]
        details = {
            "type": "animation",
            "time": time.time(),
            "data": _data,
            "reason": _reason,
        }
    elif len(ctx.command) == 1 and ctx.reply_to_message.photo:
        await self.download_media(ctx.reply_to_message, file_name=f"{user_id}.jpg")
        details = {
            "type": "photo",
            "time": time.time(),
            "data": None,
            "reason": None,
        }
    elif len(ctx.command) > 1 and ctx.reply_to_message.photo:
        await self.download_media(ctx.reply_to_message, file_name=f"{user_id}.jpg")
        _reason = ctx.text.split(None, 1)[1].strip()
        details = {
            "type": "photo",
            "time": time.time(),
            "data": None,
            "reason": _reason,
        }
    elif len(ctx.command) == 1 and ctx.reply_to_message.sticker:
        if ctx.reply_to_message.sticker.is_animated:
            details = {
                "type": "text",
                "time": time.time(),
                "data": None,
                "reason": None,
            }
        else:
            await self.download_media(ctx.reply_to_message, file_name=f"{user_id}.jpg")
            details = {
                "type": "photo",
                "time": time.time(),
                "data": None,
                "reason": None,
            }
    elif len(ctx.command) > 1 and ctx.reply_to_message.sticker:
        _reason = (ctx.text.split(None, 1)[1].strip())[:100]
        if ctx.reply_to_message.sticker.is_animated:
            details = {
                "type": "text_reason",
                "time": time.time(),
                "data": None,
                "reason": _reason,
            }
        else:
            await self.download_media(ctx.reply_to_message, file_name=f"{user_id}.jpg")
            details = {
                "type": "photo",
                "time": time.time(),
                "data": None,
                "reason": _reason,
            }
    else:
        details = {
            "type": "text",
            "time": time.time(),
            "data": None,
            "reason": None,
        }

    await add_afk(user_id, details)
    send = await ctx.reply(
        strings("now_afk").format(usr=ctx.from_user.mention, id=ctx.from_user.id)
    )
    await put_cleanmode(ctx.chat.id, send.id)


@app.on_message(
    filters.command("afkdel") & filters.group & admin_filter
)
@use_chat_lang()
async def afk_state(self: Client, ctx: Message, strings):
    if not ctx.from_user:
        return
    if len(ctx.command) == 1:
        return await ctx.reply(strings("afkdel_help").format(cmd=ctx.command[0]))
    chat_id = ctx.chat.id
    state = ctx.text.split(None, 1)[1].strip()
    state = state.lower()
    if state == "enable":
        await cleanmode_on(chat_id)
        await ctx.reply(strings("afkdel_enable"))
    elif state == "disable":
        await cleanmode_off(chat_id)
        await ctx.reply(strings("afkdel_disable"))
    else:
        await ctx.reply(strings("afkdel_help").format(cmd=ctx.command[0]))


# Detect user that AFK based on Yukki Repo
@app.on_message(
    filters.group & ~filters.bot & ~filters.via_bot,
    group=1,
)
@use_chat_lang()
async def afk_watcher_func(self: Client, ctx: Message, strings):
    if ctx.sender_chat:
        return
    userid = ctx.from_user.id
    user_name = ctx.from_user.mention
    if ctx.entities:
        possible = ["/afk", f"/afk@{self.me.username}", "!afk"]
        message_text = ctx.text or ctx.caption
        for entity in ctx.entities:
            if entity.type == enums.MessageEntityType.BOT_COMMAND:
                if (message_text[0 : 0 + entity.length]).lower() in possible:
                    return

    msg = ""
    replied_user_id = 0

    # Self AFK
    verifier, reasondb = await is_afk(userid)
    if verifier:
        await remove_afk(userid)
        try:
            afktype = reasondb["type"]
            timeafk = reasondb["time"]
            data = reasondb["data"]
            reasonafk = reasondb["reason"]
            seenago = get_readable_time2((int(time.time() - timeafk)))
            if afktype == "text":
                msg += strings("on_afk_msg_no_r").format(
                    usr=user_name, id=userid, tm=seenago
                )
            if afktype == "text_reason":
                msg += strings("on_afk_msg_with_r").format(
                    usr=user_name, id=userid, tm=seenago, reas=reasonafk
                )
            if afktype == "animation":
                if str(reasonafk) == "None":
                    send = await ctx.reply_animation(
                        data,
                        caption=strings("on_afk_msg_no_r").format(
                            usr=user_name, id=userid, tm=seenago
                        ),
                    )
                else:
                    send = await ctx.reply_animation(
                        data,
                        caption=strings("on_afk_msg_with_r").format(
                            usr=user_name, id=userid, tm=seenago, reas=reasonafk
                        ),
                    )
            if afktype == "photo":
                if str(reasonafk) == "None":
                    send = await ctx.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=strings("on_afk_msg_no_r").format(
                            usr=user_name, id=userid, tm=seenago
                        ),
                    )
                else:
                    send = await ctx.reply_photo(
                        photo=f"downloads/{userid}.jpg",
                        caption=strings("on_afk_msg_with_r").format(
                            usr=user_name, id=userid, tm=seenago, reas=reasonafk
                        ),
                    )
        except:
            msg += strings("is_online").format(usr=user_name, id=userid)

    # Replied to a User which is AFK
    if ctx.reply_to_message:
        try:
            replied_first_name = ctx.reply_to_message.from_user.mention
            replied_user_id = ctx.reply_to_message.from_user.id
            verifier, reasondb = await is_afk(replied_user_id)
            if verifier:
                try:
                    afktype = reasondb["type"]
                    timeafk = reasondb["time"]
                    data = reasondb["data"]
                    reasonafk = reasondb["reason"]
                    seenago = get_readable_time2((int(time.time() - timeafk)))
                    if afktype == "text":
                        msg += strings("is_afk_msg_no_r").format(
                            usr=replied_first_name, id=replied_user_id, tm=seenago
                        )
                    if afktype == "text_reason":
                        msg += strings("is_afk_msg_with_r").format(
                            usr=replied_first_name,
                            id=replied_user_id,
                            tm=seenago,
                            reas=reasonafk,
                        )
                    if afktype == "animation":
                        if str(reasonafk) == "None":
                            send = await ctx.reply_animation(
                                data,
                                caption=strings("is_afk_msg_no_r").format(
                                    usr=replied_first_name,
                                    id=replied_user_id,
                                    tm=seenago,
                                ),
                            )
                        else:
                            send = await ctx.reply_animation(
                                data,
                                caption=strings("is_afk_msg_with_r").format(
                                    usr=replied_first_name,
                                    id=replied_user_id,
                                    tm=seenago,
                                    reas=reasonafk,
                                ),
                            )
                    if afktype == "photo":
                        if str(reasonafk) == "None":
                            send = await ctx.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=strings("is_afk_msg_no_r").format(
                                    usr=replied_first_name,
                                    id=replied_user_id,
                                    tm=seenago,
                                ),
                            )
                        else:
                            send = await ctx.reply_photo(
                                photo=f"downloads/{replied_user_id}.jpg",
                                caption=strings("is_afk_msg_with_r").format(
                                    usr=replied_first_name,
                                    id=replied_user_id,
                                    tm=seenago,
                                    reas=reasonafk,
                                ),
                            )
                except Exception:
                    msg += strings("is_afk").format(
                        usr=replied_first_name, id=replied_user_id
                    )
        except:
            pass

    # If username or mentioned user is AFK
    if ctx.entities:
        entity = ctx.entities
        j = 0
        for x in range(len(entity)):
            if (entity[j].type) == enums.MessageEntityType.MENTION:
                found = re.findall("@([_0-9a-zA-Z]+)", ctx.text)
                try:
                    get_user = found[j]
                    user = await app.get_users(get_user)
                    if user.id == replied_user_id:
                        j += 1
                        continue
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user.id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time2((int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += strings("is_afk_msg_no_r").format(
                                usr=user.first_name[:25], id=user.id, tm=seenago
                            )
                        if afktype == "text_reason":
                            msg += strings("is_afk_msg_with_r").format(
                                usr=user.first_name[:25],
                                id=user.id,
                                tm=seenago,
                                reas=reasonafk,
                            )
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                send = await ctx.reply_animation(
                                    data,
                                    caption=strings("is_afk_msg_no_r").format(
                                        usr=user.first_name[:25], id=user.id, tm=seenago
                                    ),
                                )
                            else:
                                send = await ctx.reply_animation(
                                    data,
                                    caption=strings("is_afk_msg_with_r").format(
                                        usr=user.first_name[:25],
                                        id=user.id,
                                        tm=seenago,
                                        reas=reasonafk,
                                    ),
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                send = await ctx.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=strings("is_afk_msg_no_r").format(
                                        usr=user.first_name[:25], id=user.id, tm=seenago
                                    ),
                                )
                            else:
                                send = await ctx.reply_photo(
                                    photo=f"downloads/{user.id}.jpg",
                                    caption=strings("is_afk_msg_with_r").format(
                                        usr=user.first_name[:25],
                                        id=user.id,
                                        tm=seenago,
                                        reas=reasonafk,
                                    ),
                                )
                    except:
                        msg += strings("is_afk").format(
                            usr=user.first_name[:25], id=user.id
                        )
            elif (entity[j].type) == enums.MessageEntityType.TEXT_MENTION:
                try:
                    user_id = entity[j].user.id
                    if user_id == replied_user_id:
                        j += 1
                        continue
                    first_name = entity[j].user.first_name
                except:
                    j += 1
                    continue
                verifier, reasondb = await is_afk(user_id)
                if verifier:
                    try:
                        afktype = reasondb["type"]
                        timeafk = reasondb["time"]
                        data = reasondb["data"]
                        reasonafk = reasondb["reason"]
                        seenago = get_readable_time2((int(time.time() - timeafk)))
                        if afktype == "text":
                            msg += strings("is_afk_msg_no_r").format(
                                usr=first_name[:25], id=user_id, tm=seenago
                            )
                        if afktype == "text_reason":
                            msg += strings("is_afk_msg_with_r").format(
                                usr=first_name[:25],
                                id=user_id,
                                tm=seenago,
                                reas=reasonafk,
                            )
                        if afktype == "animation":
                            if str(reasonafk) == "None":
                                send = await ctx.reply_animation(
                                    data,
                                    caption=strings("is_afk_msg_no_r").format(
                                        usr=first_name[:25], id=user_id, tm=seenago
                                    ),
                                )
                            else:
                                send = await ctx.reply_animation(
                                    data,
                                    caption=strings("is_afk_msg_with_r").format(
                                        usr=first_name[:25],
                                        id=user_id,
                                        tm=seenago,
                                        reas=reasonafk,
                                    ),
                                )
                        if afktype == "photo":
                            if str(reasonafk) == "None":
                                send = await ctx.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=strings("is_afk_msg_no_r").format(
                                        usr=first_name[:25], id=user_id, tm=seenago
                                    ),
                                )
                            else:
                                send = await ctx.reply_photo(
                                    photo=f"downloads/{user_id}.jpg",
                                    caption=strings("is_afk_msg_with_r").format(
                                        usr=first_name[:25],
                                        id=user_id,
                                        tm=seenago,
                                        reas=reasonafk,
                                    ),
                                )
                    except:
                        msg += strings("is_afk").format(usr=first_name[:25], id=user_id)
            j += 1
    if msg != "":
        try:
            send = await ctx.reply_text(msg, disable_web_page_preview=True)
        except:
            pass
    try:
        await put_cleanmode(ctx.chat.id, send.id)
    except:
        pass

__PLUGIN__ = "Afk"
__HELP__ = """
**Afk :**
➥ /afk [Reason > Optional] - Tell others that you are AFK (Away From Keyboard)
➥ /afk [reply to media] - AFK with media.
➥ /afkdel - Enable auto delete AFK message in group (Only for group admin). Default is **Enable**
Just type something in group to remove AFK Status
"""
