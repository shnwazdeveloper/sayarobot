import shortuuid
from pyrogram import filters
from pyrogram.types import *

from Curse.bot_class import app
from Curse.database.whisper_db import Whispers


@app.on_inline_query()
async def mainwhisper(_, query):
    if not query.query:
        return await query.answer(
            [],
            switch_pm_text="Give me a username or ID!",
            switch_pm_parameter="ghelp_whisper",
        )

    text = query.query.split(" ")
    user = text[0]
    first = True
    message = ""
    if not user.startswith("@") and not user.isdigit():
        user = text[-1]
        first = False
    if first:
        message = " ".join(text[1:])
    else:
        text.pop()
        message = " ".join(text)
    if len(message) > 200:
        return

    usertype = "username"
    whisperType = "inline"
    if user.startswith("@"):
        usertype = "username"
    elif user.isdigit():
        usertype = "id"

    if user.isdigit():
        try:
            user_obj = await app.get_users(int(user))
            if not user_obj:
                raise ValueError("User not found.")
            if not user_obj.username:
                # No username found
                if user_obj.is_bot:
                    user = f"{user_obj.first_name}"
                else:
                    # Check if user started the bot by sending a chat action
                    try:
                        await app.send_chat_action(user_obj.id, "typing")
                        user = str(user_obj.id)  # OK to use ID
                    except:
                        return await query.answer(
                            [],
                            switch_pm_text="User must start the bot first!",
                            switch_pm_parameter="ghelp_whisper",
                        )
            else:
                user = f"@{user_obj.username}"
        except Exception:
            return await query.answer(
                [],
                switch_pm_text="Invalid user ID.",
                switch_pm_parameter="ghelp_whisper",
            )

    if len(message) > 200:
        await query.answer(
            [],
            switch_pm_text="Only text up to 200 characters is allowed!",
            switch_pm_parameter="ghelp_whisper",
        )
        return

    whisperData = {
        "user": query.from_user.id,
        "withuser": user,
        "usertype": usertype,
        "type": "inline",
        "message": message,
    }
    whisperId = shortuuid.uuid()

    # Add the whisper to the database
    await Whispers.add_whisper(whisperId, whisperData)

    answers = [
        InlineQueryResultArticle(
            title=f"\U0001F510 Send a whisper message to {user}!",
            description="Only they can see it!",
            input_message_content=InputTextMessageContent(
                f"\U0001F510 A Whisper Message For {user}\nOnly they can see it!"
            ),
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "\U0001F92B Show Whisper",
                            callback_data=f"whisper_{whisperId}",
                        )
                    ]
                ]
            ),
        )
    ]

    await query.answer(answers)


@app.on_callback_query(filters.regex("^whisper_"))
async def showWhisper(_, callback_query):
    whisperId = callback_query.data.split("_")[-1]
    whisper = await Whispers.get_whisper(whisperId)

    if not whisper:
        await callback_query.answer("This whisper is not valid anymore!")
        return

    userType = whisper["usertype"]

    if callback_query.from_user.id == whisper["user"]:
        # Sender can always see the whisper
        await callback_query.answer(whisper["message"], show_alert=True)
    elif (
        userType == "username"
        and callback_query.from_user.username
        and callback_query.from_user.username.lower()
        == whisper["withuser"].replace("@", "").lower()
    ):
        # Recipient by username
        await callback_query.answer(whisper["message"], show_alert=True)
        await Whispers.del_whisper(whisperId)
        await callback_query.edit_message_text(
            f"{whisper['withuser']} read the Whisper."
        )
    elif userType == "id" and callback_query.from_user.id == int(whisper["withuser"]):
        # Recipient by user ID
        user = await app.get_users(int(whisper["withuser"]))
        username = user.username or user.first_name
        await callback_query.answer(whisper["message"], show_alert=True)
        await Whispers.del_whisper(whisperId)
        await callback_query.edit_message_text(f"{username} read the whisper.")
    else:
        await callback_query.answer("Not your Whisper!", show_alert=True)


__PLUGIN__ = "Whisper"

__HELP__ = """

**Whisper Inline Function For Secret Chats.**

**Commands**

`botname < your message > @username OR UserID`

`botname @username OR UserID < your message >`

❗ Note: When using UserID, the user must have started the bot before to receive whispers.
"""
