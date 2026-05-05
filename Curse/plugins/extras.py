import os
from asyncio import gather
import random
import requests
import re

from pyrogram import filters
from pyrogram.enums import ParseMode
from pyrogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from pySmartDL import SmartDL

from Curse.bot_class import app
from Curse.utils.custom_filters import admin_filter
from Curse.extras.localization import use_chat_lang


# Define the command handler for the "/pickwinner" command
@app.on_message(filters.command("pickwinner"), group=1012)
async def pick_winner(_, message):
    # Get the list of participants
    participants = message.text.split()[1:]

    if participants:
        # Select a random winner
        winner = random.choice(participants)

        # Send the winner as a reply
        await message.reply_text(f"🎉 The winner is: {winner}")
    else:
        # If no participants are provided
        await message.reply_text("Please provide a list of participants.")


@app.on_message(filters.command("hyperlink"), group=1013)
async def hyperlink_command(client, message):
    """Process the /hyperlink command."""
    args = message.text.split()[1:]
    if len(args) >= 2:
        text = " ".join(args[:-1])
        link = args[-1]
        hyperlink = f"[{text}]({link})"
        await client.send_message(
            chat_id=message.chat.id,
            text=hyperlink,
            disable_web_page_preview=True,
            parse_mode=ParseMode.MARKDOWN,
        )
    else:
        match = re.search(r"/hyperlink ([^\s]+) (.+)", message.text)
        if match:
            text = match.group(1)
            link = match.group(2)
            hyperlink = f"[{text}]({link})"
            await client.send_message(
                chat_id=message.chat.id,
                text=hyperlink,
                disable_web_page_preview=True,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            await client.send_message(
                chat_id=message.chat.id,
                text="❌ Invalid format! Please use the format: /hyperlink <text> <link>.",
            )


@app.on_message(filters.command("echo") & admin_filter, group=1014)
async def echo(client, message):
    args = message.text.split(None, 1)

    if message.reply_to_message:
        await message.reply_to_message.reply_text(
            args[1],
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    else:
        await message.reply_text(
            args[1],
            quote=False,
            parse_mode=ParseMode.MARKDOWN,
            disable_web_page_preview=True,
        )
    await message.delete()
    

@app.on_message(filters.command("ud"), group=1015)
async def urban(_, m):  
       user_id = m.from_user.id
       if len(m.text.split()) == 1:
         return await m.reply("Enter the text for which you would like to find the definition.")
       text = m.text.split(None,1)[1]
       api = requests.get(f"https://api.urbandictionary.com/v0/define?term={text}").json()
       mm = api["list"]
       if 0 == len(mm):
           return await m.reply("=> No results Found!")
       string = f"🔍 **Ward**: {mm[0].get('word')}\n\n📝 **Definition**: {mm[0].get('definition')}\n\n✏️ **Example**: {mm[0].get('example')}"
       if 1 == len(mm):
           return await m.reply(text=string, quote=True)
       else:
           num = 0
           return await m.reply(text=string, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('next', callback_data=f"udnxt:{user_id}:{text}:{num}")]]), quote=True)
@app.on_callback_query(filters.regex("^udnxt"))   
async def next(_, query):
         user_id = int(query.data.split(":")[1])
         text = str(query.data.split(":")[2])
         num = int(query.data.split(":")[3])+1
         if not query.from_user.id == user_id:
             return await query.answer("This is not for You!")
         api = requests.get(f"https://api.urbandictionary.com/v0/define?term={text}").json()
         mm = api["list"]
         uwu = mm[num]
         if num == len(mm)-1:
             string = f"🔍 **Word**: {uwu.get('word')}\n\n📝 **Definition**: {uwu.get('definition')}\n\n✏️ **Example**: {uwu.get('example')}\n\n"
             string += f"Page: {num+1}/{len(mm)}"
             return await query.message.edit(text=string, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('➡️ Back', callback_data=f"udbck:{query.from_user.id}:{text}:{num}")]]))
         else:
             string = f"🔍 **Word**: {uwu.get('word')}\n\n📝 **Definition**: {uwu.get('definition')}\n\n✏️ **Example**: {uwu.get('example')}\n\n"
             string += f"Page: {num+1}/{len(mm)}"
             buttons = [[
                  InlineKeyboardButton("Back ⏮️", callback_data=f"udbck:{query.from_user.id}:{text}:{num}"),
                  InlineKeyboardButton("Next ⏭️", callback_data=f"udnxt:{query.from_user.id}:{text}:{num}") 
             ]]
             return await query.message.edit(text=string, reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("^udbck"))   
async def back(_, query):
         user_id = int(query.data.split(":")[1])
         text = str(query.data.split(":")[2])
         num = int(query.data.split(":")[3])-1
         if not query.from_user.id == user_id:
             return await query.answer("This is not for You!")
         api = requests.get(f"https://api.urbandictionary.com/v0/define?term={text}").json()
         mm = api["list"]
         uwu = mm[num]
         if num == 0:
             string = f"🔍 **Ward**: {uwu.get('word')}\n\n📝 **Definition**: {uwu.get('definition')}\n\n✏️ **Example**: {uwu.get('example')}\n\n"
             string += f"Page: {num+1}/{len(mm)}"
             return await query.message.edit(text=string, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('➡️ Next', callback_data=f"udnxt:{query.from_user.id}:{text}:{num}")]]))
         else:
             string = f"🔍 **Ward**: {uwu.get('word')}\n\n📝 **Definition**: {uwu.get('definition')}\n\n✏️ **Example**: {uwu.get('example')}\n\n"
             string += f"Page: {num+1}/{len(mm)}"
             buttons = [[
                  InlineKeyboardButton("Back ⏮️", callback_data=f"udbck:{query.from_user.id}:{text}:{num}"),
                  InlineKeyboardButton("Next ⏭️", callback_data=f"udnxt:{query.from_user.id}:{text}:{num}") 
             ]]
             return await query.message.edit(text=string, reply_markup=InlineKeyboardMarkup(buttons))


__PLUGIN__ = "Extras"
__HELP__ = """
**🫧 𝗘𝗫𝗧𝗥𝗔𝗦**

➥ /pickwinner <participant1> <participant2> ... : Picks a random winner from the provided list of participants.
➥ /echo <text> : Echos the message. 
➥ /webss [URL] - Take A Screenshot Of A Webpage.
➥ /ud : Search Urban Dictionary. Usage: /ud [word]
"""

