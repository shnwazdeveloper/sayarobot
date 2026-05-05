from pyrogram import Client,filters
import requests
import re
import config

SPOILER = config.SPOILER_MODE
slangf = 'slang_words.txt'
with open(slangf, 'r') as f:
    slang_words = set(line.strip().lower() for line in f)

Bot = Client(
    "antinude",
    bot_token=config.BOT_TOKEN,
    api_id=config.API_ID,
    api_hash=config.API_HASH
)

#--------------------------------------------------------------------------------------------------

@Bot.on_message(filters.group & filters.text)
async def slang(bot, message):
    sender = await Bot.get_chat_member(message.chat.id, message.from_user.id)
    isadmin = sender.privileges
    if not isadmin:
        sentence = message.text
        sent = re.sub(r'\W+', ' ', sentence)
        isslang = False
        for word in sent.split():
            if word.lower() in slang_words:
                isslang = True
                await message.delete()
                sentence = sentence.replace(word, f'||{word}||')
        if isslang:
            name = message.from_user.mention
            msgtxt = f"""{name} your message has been deleted due to the presence of inappropriate language. Here is a censored version of your message:

{sentence}
            """
            if SPOILER:
                await message.reply(msgtxt)

#--------------------------------------------------------------------------------------------------

Bot.run()
