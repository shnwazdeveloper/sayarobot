import requests
import asyncio 
import os

from Curse import pbot as app
from Curse.vars import Config as config
from Curse.extras.pastebin import spacebin, batbin
from pyrogram import filters, enums

string = "🌠 Spacebin: [click here]({})\n😼 Batbin: [click here]({})\n💀 Raw View: [click here]({})"

    

@app.on_message(~filters.bot & filters.command("paste",config.PREFIX_HANDLER))
async def paste_code(_, message):
    #share your codes on https://spacebin.in & https://batbin.me
    msg = await message.reply('pasting...')

    if not message.reply_to_message:
          try:
              text = message.text.split(None,1)[1]
          except:
               msg = await message.edit("Eg: .p reply|{text/doc}")
               await asyncio.sleep(5)
               await msg.delete()
               return           
          mm = await spacebin(text)
          bb = await batbin(text)
      
          link = mm["result"]["link"]
          raw = mm["result"]["raw"]          
          return await msg.edit(string.format(sb, bb, raw), parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True)

    elif (message.reply_to_message.document and bool(message.reply_to_message.document.mime_type.startswith("text/"))):
           path = await app.download_media(message.reply_to_message)
           file = open(path, "r")
           text = file.read()
           file.close()
           os.remove(path)

           mm = await spacebin(text)
           bb = await batbin(text)
      
           sb = mm["result"]["link"]
           raw = mm["result"]["raw"]

           return await msg.edit(string.format(sb, bb, raw), parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True)

    elif bool(message.reply_to_message.text or message.reply_to_message.caption):
           if message.reply_to_message.text:
                 text = message.reply_to_message.text
           elif message.reply_to_message.caption:
                 text = message.reply_to_message.caption
        
           mm = await spacebin(text)
           bb = await batbin(text)
      
           sb = mm["result"]["link"]
           raw = mm["result"]["raw"]

           return await msg.edit(string.format(sb, bb, raw), parse_mode=enums.ParseMode.MARKDOWN, disable_web_page_preview=True)
    else:
         return await message.edit('somthing worng')
