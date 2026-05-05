import requests as r
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup 
from pyrogram import filters 
from Curse.bot_class import app


#SHORTEN THE DISCRIPTION
def shorten(description):
    msg = ""
    if len(description) > 200:
        description = description[0:200] + "..."
        msg += f"⋄ **DESCRIPTION**: {description}..."
    else:
        msg += f"⋄ **DESCRIPTION:** {description}"
    return msg

#HANIME HANDLER
@app.on_message(filters.command("hanime"))
async def hanime(app, message):
    name = message.text[len("/hanime ") :]
    if not name:
       return await message.reply_text("**GIVE A HENTAI NAME**")
    rr = r.get(f"https://black-bay.vercel.app/search?query={name}%20&page=0").json()
    a = rr['response'][0]['id']
    b = rr['response'][0]['name']
    c = rr['response'][0]['description']
    d = rr['response'][0]['cover_url']
    msg = shorten(c)
    TEXT = f"**⋄ NAME:** {b}\n**⋄ ID:** {a}\n\n{msg}"
    rs = r.get(f"https://black-bay.vercel.app/link?id={a}").json()
    e = rs['data'][1]['id']
    f = rs['data'][1]['filesize_mbs']
    g = rs['data'][1]['url']
    h = rs['data'][1]['filename']
    TEXT1 = f"ID: {e}\nNAME: {h}\nSIZE: {f} MB\nQUALITY: 720P\nDOWNLOAD LINK: {g}"
    await message.reply_photo(d , caption= TEXT, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("DOWNLOAD", callback_data = f"hdownload#{a}")],[InlineKeyboardButton ("❌", callback_data=f"hclose#{message.from_user.id}")]]))

#DOWNLOADS CALLBACK
@app.on_callback_query(filters.regex("hdownload"))
async def dhanime(_, cq):
    uid = cq.data.split('#')[1]
    rs = r.get(f"https://black-bay.vercel.app/link?id={uid}").json()
    e = rs['data'][1]['id']
    f = rs['data'][1]['filesize_mbs']
    g = rs['data'][1]['url']
    h = rs['data'][1]['filename']
    TEXT1 = f"**ID:** {e}\n**NAME:** {h}\n**SIZE:** {f} MB\n**QUALITY: 720P**"
    await cq.message.edit(TEXT1, reply_markup=InlineKeyboardMarkup ([[InlineKeyboardButton ("DOWNLOAD LINK", url = f"{g}")],[InlineKeyboardButton ("❌", callback_data=f"hclose#{cq.message.from_user.id}")]]))

#DELETE CALLBACK
@app.on_callback_query(filters.regex("hclose"))
async def hclose(_, cq):
    userid = cq.data.split('#')[1]
    if cq.from_user.id != int(userid):
       return await cq.answer("YOU CANT USE THIS!", True)
    try:
        await cq.message.delete()
    except:
        pass
