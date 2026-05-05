import random

from pyrogram import filters
from Curse import pbot


CMDS = [ 'howall', 'sex', 'beauty', 'boobs', 'dick', 'horny', 'gay', 'lezbian', 'noob', 'idiot', 'nigga', 'pro'] 

sex_string = [
  'Wanna sex with me? {}.',
  'Sorry you\'r pussy aren\'t that taste {}.'
  'You are Di*kless, Try Again Later.',
  'Get Lost, Horny.',
  'Masturbation Is Your Only Option.',
  'Kids Do Not Have Sex With Adults.',
  'Get Lost, Horny.',
  'Ahhh... Not There, Ahhhhhh...',
  'Ohh No, You Made Her Pregnant.',
  'Kids Do Not Have Sex With Adults.',
  'Jhaante Na Chuchi, Baatein Uchi-Uchi',
  'Tell Me Your Dads Number, I Gotta Show This To Him.',
  'Your Di*k Is Not Long Enough.',
  'Get Lost, Horny.',
  'Im Ready For A White Shower, Daddy!',
  'Onii-Chan, Yamete Kudasaiii...',
  'Bring Condom First',
  'Tell Me Your Dads Number, I Gotta Show This To Him.',
  'Ohh No, You Made Her Pregnant.',
  'Bring Condom First',
]

@pbot.on_message(filters.command(CMDS), group=1582)
async def howall(_, message):
    reply = message.reply_to_message
    if reply:
        mention = reply.from_user.mention
    else:
        mention = message.from_user.mention

    reply_func = reply if reply else message
    query = message.command[0]
    if query == 'howall':
          text = "**Commands**:\n"
          CMDS.remove('howall')
          for i, string in enumerate(CMDS):
             text += f"{i+1}, {string}\n"
          return await reply_func.reply_text(text)
      
    elif query == 'sex':
          return await reply_func.reply_text(random.choice(sex_string).format(mention))
    else:
        num = random.randint(0, 100)
        default = f'**{mention} You\'re {num}% {query}**'
        url_data = {
            'gay': 'https://telegra.ph//file/489199eab5a922b1e6529.mp4',
            'lezbian': 'https://telegra.ph//file/1d185a148783f364f1ee8.mp4',
            'horny': 'https://telegra.ph//file/1597814837d4f60d6944e.mp4',
            'dick': 'https://telegra.ph//file/3e270d488a6e09ea6e902.mp4',
            'boobs': 'https://telegra.ph//file/6cdb0450dcbc457a9e48f.mp4',
            'noob': 'https://telegra.ph//file/8e4d7e3213ab240f9df0b.mp4',
            'idiot': 'https://telegra.ph//file/71b56eee6b5f4b46d89bb.mp4',
            'nigga': 'https://telegra.ph//file/0e9acff8b61039a857d90.mp4',
            'beauty': 'https://graph.org/file/5f2e2de605dabcba88250.mp4',
            'pro': 'https://graph.org/file/4148eee2228b6932b87d8.mp4'
        }
        if query in url_data:
            url = url_data[query]
            return await reply_func.reply_animation(
                animation=url, caption=default
            )
