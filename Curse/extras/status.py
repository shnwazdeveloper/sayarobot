from functools import wraps
from pyrogram import Client
from pyrogram.enums import ChatType
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from Curse import BOT_ID
from Curse.bot_class import app
from Curse.supports import get_support_staff

SUPPORT_STAFF = get_support_staff()

COMMANDERS = [ChatMemberStatus.ADMINISTRATOR,ChatMemberStatus.OWNER]


# def user_has_permission(permission):
#     def decorator(func):
#         @wraps(func)
#         async def wrapper(client, message: Message):
#             user_id = message.reply_to_message.from_user.id
#             chat_id = message.chat.id

#             x = await client.get_chat_member(chat_id, user_id)
#             privileges = x.privileges.__dict__

#             if permission in privileges and privileges[permission]:
#                 await func(client, message)
#             else:
#                 print(f"User does not have the permission: {permission}")

#         return wrapper

#     return decorator



async def user_has_permission(chat_title : str, chat_id: int, user_id: int, permission: str,bot=True) -> tuple[bool, str]:
    try:
        if user_id in SUPPORT_STAFF:
            have_permission = True
        else:
            chat_member = await app.get_chat_member(chat_id, user_id)
            chat_permissions = chat_member.privileges
            if permission == "can_delete_messages":
                have_permission = chat_permissions.can_delete_messages
            elif permission == "can_manage_chat":
                have_permission = chat_permissions.can_manage_chat
            elif permission == "can_manage_video_chats":
                have_permission = chat_permissions.can_manage_video_chats
            elif permission == "can_restrict_members":
                have_permission = chat_permissions.can_restrict_members
            elif permission == "can_promote_members":
                have_permission = chat_permissions.can_promote_members
            elif permission == "can_change_info":
                have_permission = chat_permissions.can_change_info
            elif permission == "can_post_messages":
                have_permission = chat_permissions.can_post_messages
            elif permission == "can_edit_messages":
                have_permission = chat_permissions.can_edit_messages
            elif permission == "can_invite_users":
                have_permission = chat_permissions.can_invite_users
            elif permission == "can_pin_messages":
                have_permission = chat_permissions.can_pin_messages
            else:
                have_permission = False

    except Exception as e:
        print(e)
        have_permission = False

    if not have_permission:
        if bot:
            txt = f"ʜᴇʏ ʙᴀʙʏ, I ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ʀɪɢʜᴛ:\n**__{permission}__**\nɪɴ **{chat_title}**. Pʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ᴀɴᴅ ɢʀᴀɴᴛ ᴍᴇ ᴛʜᴇ ʀɪɢʜᴛ."
        else:
            txt = f"ʜᴇʏ ʙᴀʙʏ, ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ʀɪɢʜᴛ:\n{permission}\nɪɴ {chat_title}.sᴏ ɪ ᴡᴏɴ'ᴛ ʙᴇ ᴀʙʟᴇ ᴛᴏ ᴘᴇʀғᴏᴍ ᴛʜɪs ᴀᴄᴛɪᴏɴ ғᴏʀ ʏᴏᴜ"
        return have_permission, txt
    else:
        return have_permission, None


def bot_admin(func):
    @wraps(func)
    async def is_bot_admin(app : Client, message : Message,*args,**kwargs):
        chat_type = message.chat.type
        if chat_type == ChatType.PRIVATE:
            return await message.reply("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴀs ᴍᴀᴅᴇ ᴜᴘ ғᴏʀ ɢʀᴏᴜᴘs ɴᴏᴛ ғᴏʀ ᴘʀɪᴠᴀᴛᴇ")
        BOT = await app.get_chat_member(message.chat.id,BOT_ID)
        if BOT.status != ChatMemberStatus.ADMINISTRATOR:
            await message.reply_text(f"ʜᴇʏ ʙᴀʙᴇs ɪ'ᴍ ɴᴏᴛ ᴀᴅᴍɪɴ ɪɴ **{message.chat.title}**")
            return
        return await func(app,message,*args,**kwargs)
    return is_bot_admin

def bot_can_ban(func):
    @wraps(func)
    async def can_restrict(app : Client, message : Message,*args,**kwargs):
        BOT = await app.get_chat_member(message.chat.id,BOT_ID)

        if not BOT.privileges.can_restrict_members:
            await message.reply_text(f"ʜᴇʏ ʙᴀʙʏ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛs ᴛᴏ ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀ ɪɴ **{message.chat.title}**. ᴄʜᴇᴄᴋ ᴀɴᴅ ɢɪᴠᴇ ᴍᴇ ᴛʜᴇ ʀɪɢʜᴛ ᴘʟᴇᴀsᴇ.")
            return
        return await func(app,message,*args,**kwargs)
    return can_restrict

def bot_can_change_info(func):
    @wraps(func)
    async def can_change_info(app : Client, message : Message,*args,**kwargs):
        BOT = await app.get_chat_member(message.chat.id,BOT_ID)

        if not BOT.privileges.can_change_info:
            await message.reply_text(f"ʜᴇʏ ʙᴀʙʏ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛs ᴛᴏ ᴄʜᴀɴɢᴇ ɪɴғᴏ ᴏғ **{message.chat.title}**. ᴄʜᴇᴄᴋ ᴀɴᴅ ɢɪᴠᴇ ᴍᴇ ᴛʜᴇ ʀɪɢʜᴛ ᴘʟᴇᴀsᴇ.")
            return
        return await func(app,message,*args,**kwargs)
    return can_change_info


def bot_can_promote(func):
    @wraps(func)
    async def can_promote(app : Client, message : Message,*args,**kwargs):
        BOT = await app.get_chat_member(message.chat.id,BOT_ID)

        if not BOT.privileges.can_promote_members:
            await message.reply_text(f"ʜᴇʏ ʙᴀʙʏ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛs ᴛᴏ **ᴘʀᴏᴍᴏᴛᴇ ᴜsᴇʀs** ɪɴ **{message.chat.title}**. ᴄʜᴇᴄᴋ ᴀɴᴅ ɢɪᴠᴇ ᴍᴇ ᴛʜᴇ ʀɪɢʜᴛ ᴘʟᴇᴀsᴇ.")
            return
        return await func(app,message,*args,**kwargs)
    return can_promote


def bot_can_pin(func):
    @wraps(func)
    async def can_pin(app : Client, message : Message,*args,**kwargs):
        BOT = await app.get_chat_member(message.chat.id,BOT_ID)

        if not BOT.privileges.can_pin_messages:
            await message.reply_text(f"ʜᴇʏ ʙᴀʙʏ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛs ᴛᴏ **ᴘɪɴ ᴍᴇssᴀɢᴇs** ɪɴ **{message.chat.title}**. ᴄʜᴇᴄᴋ ᴀɴᴅ ɢɪᴠᴇ ᴍᴇ ᴛʜᴇ ʀɪɢʜᴛ ᴘʟᴇᴀsᴇ.")
            return
        return await func(app,message,*args,**kwargs)
    return can_pin

def bot_can_del(func):
    @wraps(func)
    async def can_delete(app : Client, message : Message,*args,**kwargs):
        BOT = await app.get_chat_member(message.chat.id,BOT_ID)

        if not BOT.privileges.can_delete_messages:
            await message.reply_text(f"ʜᴇʏ ʙᴀʙʏ ɪ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛs ᴛᴏ **ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs** ɪɴ **{message.chat.title}**. ᴄʜᴇᴄᴋ ᴀɴᴅ ɢɪᴠᴇ ᴍᴇ ᴛʜᴇ ʀɪɢʜᴛ ᴘʟᴇᴀsᴇ.")
            return
        return await func(app,message,*args,**kwargs)
    return can_delete

def user_admin(mystic):
    @wraps(mystic)
    async def wrapper(app : Client, message : Message,*args,**kwargs):
        chat_type = message.chat.type
        if chat_type == ChatType.PRIVATE:
            return await message.reply("ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴀs ᴍᴀᴅᴇ ᴜᴘ ғᴏʀ ɢʀᴏᴜᴘs ɴᴏᴛ ғᴏʀ ᴘʀɪᴠᴀᴛᴇ")
        if message.sender_chat:
            if message.sender_chat.id == message.chat.id:
                return await message.reply("ʏᴏᴜ ᴀʀᴇ ᴀɴ ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ. I ᴄᴀɴɴᴏᴛ ᴘᴇʀғᴏʀᴍ ʏᴏᴜʀ ᴛᴀsᴋ. ᴘʟᴇᴀsᴇ ᴜsᴇ ᴀ ʀᴇᴀʟ ID.")
            else:
                return await message.reply_text("sᴛᴀʏ ɪɴ ʏᴏᴜʀ ʟɪᴍɪᴛs. ʙᴇᴄᴏᴍᴇ **ᴀᴅᴍɪɴ** ғɪʀsᴛ.")

        else:
            user_id = message.from_user.id
            chat_id = message.chat.id
            user = await app.get_chat_member(chat_id,user_id)

            if (user.status not in COMMANDERS) and user_id not in SUPPORT_STAFF:
                return await message.reply_text("sᴛᴀʏ ɪɴ ʏᴏᴜʀ ʟɪᴍɪᴛs. ʙᴇᴄᴏᴍᴇ **ᴀᴅᴍɪɴ** ғɪʀsᴛ.")

        return await mystic(app,message,*args,**kwargs)

    return wrapper

def user_can_ban(mystic):
    @wraps(mystic)
    async def wrapper(app : Client, message : Message,*args,**kwargs):
        user_id = message.from_user.id
        chat_id = message.chat.id
        user = await app.get_chat_member(chat_id,user_id)

        if (user.privileges and not user.privileges.can_restrict_members) and user_id not in SUPPORT_STAFF:

            return await message.reply_text("ʜᴇʏ ɴᴏᴏʙ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛ ᴛᴏ **ʀᴇsᴛʀɪᴄᴛ ᴜsᴇʀs**. ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

        return await mystic(app,message,*args,**kwargs)
    return wrapper

def user_can_del(mystic):
    @wraps(mystic)
    async def wrapper(app : Client, message : Message,*args,**kwargs):
        user_id = message.from_user.id
        chat_id = message.chat.id
        user = await app.get_chat_member(chat_id,user_id)

        if (user.status in COMMANDERS and not user.privileges.can_delete_messages) and user_id not in SUPPORT_STAFF:
            return await message.reply_text("ʜᴇʏ ɴᴏᴏʙ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛ ᴛᴏ **ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs**. ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

        return await mystic(app,message,*args,**kwargs)
    return wrapper


def user_can_change_info(mystic):
    @wraps(mystic)
    async def wrapper(app : Client, message : Message,*args,**kwargs):
        user_id = message.from_user.id
        chat_id = message.chat.id
        user = await app.get_chat_member(chat_id,user_id)

        if (user.status in COMMANDERS and not user.privileges.can_change_info) and user_id not in SUPPORT_STAFF:
            return await message.reply_text("ʜᴇʏ ɴᴏᴏʙ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛ ᴛᴏ **ᴄʜᴀɴɢᴇ ɪɴғᴏ** ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ. ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ")

        return await mystic(app,message,*args,**kwargs)
    return wrapper

def user_can_promote(mystic):
    @wraps(mystic)
    async def wrapper(app : Client, message : Message,*args,**kwargs):
        user_id = message.from_user.id
        chat_id = message.chat.id
        user = await app.get_chat_member(chat_id,user_id)

        if (user.status in COMMANDERS and not user.privileges.can_promote_members) and user_id not in SUPPORT_STAFF:
            return await message.reply_text("ʜᴇʏ ɴᴏᴏʙ ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ʀɪɢʜᴛ ᴛᴏ **ᴘʀᴏᴍᴏᴛᴇ ᴜsᴇʀs** ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ. ʏᴏᴜ ᴄᴀɴ'ᴛ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ")

        return await mystic(app,message,*args,**kwargs)
    return wrapper

