from pyrogram import filters

from Curse.bot_class import app
from Curse.database.toggle_mongo import is_meme_on, meme_off, meme_on
from Curse.extras.https import fetch
from Curse.utils.custom_filters import admin_filter

subreddit_mapping = {
    "memes": "Animemes",
    "dank": "dankmemes",
    "lolimeme": "LoliMemes",
    "hornyjail": "Hornyjail",
    "wmeme": "wholesomememes",
    "pewds": "PewdiepieSubmissions",
    "hmeme": "hornyresistance",
    "teen": "teenagers",
    "fbi": "FBI_Memes",
    "shitposting": "shitposting",
    "cursed": "cursedcomments",
}


async def get_random_meme(subreddit):
    meme_url = f"https://meme-api.com/gimme/{subreddit}"
    response = await fetch.get(meme_url)
    if response and response.status_code == 200:
        data = response.json()
        return data
    else:
        return None


@app.on_message(filters.command(list(subreddit_mapping.keys())))
async def mimi(client, message):
    chat_id = message.chat.id
    functionality_enabled = await is_meme_on(chat_id)

    try:
        if not functionality_enabled:
            return

        command = message.command[0].lower()
        subreddit = subreddit_mapping.get(command)

        if subreddit:
            meme_data = await get_random_meme(subreddit)
            if meme_data:
                photo_url = meme_data.get("url")
                title = meme_data.get("title")
                if photo_url and title:
                    await client.send_photo(chat_id, photo=photo_url, caption=title)
                else:
                    await client.send_message(chat_id, "Failed to fetch meme.")
            else:
                await client.send_message(chat_id, "Failed to fetch meme.")
        else:
            await client.send_message(chat_id, "Invalid command.")

    except Exception as e:
        print(e)


@app.on_message(filters.command(["mememode"]) & admin_filter)
async def toggle_functionality(client, message):
    chat_id = message.chat.id

    if len(message.command) < 2:
        await client.send_message(chat_id, "Usage: /mememode [on|off]")
        return

    option = message.command[1].lower()

    functionality_enabled = await is_meme_on(chat_id)

    if option == "on":
        if functionality_enabled:
            await client.send_message(chat_id, "Mememode is already enabled.")
        else:
            await meme_on(chat_id)
            await client.send_message(chat_id, "Mememode functionalities enabled.")
    elif option == "off":
        if not functionality_enabled:
            await client.send_message(chat_id, "Mememode is already disabled.")
        else:
            await meme_off(chat_id)
            await client.send_message(chat_id, "Mememode functionalities disabled.")
    else:
        await client.send_message(chat_id, "Invalid option. Use either 'on' or 'off'.")

