from traceback import format_exc
import requests
from requests import get 
import json
from pyrogram import filters, Client
from pyrogram.types import InputMediaPhoto, Message
from search_engine_parser.core.engines.google import Search as GoogleSearch
from search_engine_parser.core.exceptions import (NoResultsFound,
                                                  NoResultsOrTrafficError)

from Curse import LOGGER, SUPPORT_CHANNEL
from Curse.bot_class import app
from Curse.utils.custom_filters import command
from Curse.utils.http_helper import *
from Curse.utils.kbhelpers import ikb
from Curse.extras.https import fetch
from Curse import PREFIX_HANDLER as COMMAND_HANDLER

#have to add youtube

gsearch = GoogleSearch()


@app.on_message(filters.command(["google", "googlu"], COMMAND_HANDLER), group=101012)
async def g_search(c: app, m: Message):
    split = m.text.split(None, 1)
    if len(split) == 1:
        return await m.reply_text("ʜᴇʏ ɢɪᴠᴇ me a Querry to search")
    to_del = await m.reply_text("⏳")
    query = split[1]
    try:
        result = await gsearch.async_search(query)
        keyboard = ikb(
            [
                [
                    (
                        f"{result[0]['titles']}",
                        f"{result[0]['links']}",
                        "url",
                    ),
                ],
                [
                    (
                        f"{result[1]['titles']}",
                        f"{result[1]['links']}",
                        "url",
                    ),
                ],
                [
                    (
                        f"{result[2]['titles']}",
                        f"{result[2]['links']}",
                        "url",
                    ),
                ],
                [
                    (
                        f"{result[3]['titles']}",
                        f"{result[3]['links']}",
                        "url",
                    ),
                ],
                [
                    (
                        f"{result[4]['titles']}",
                        f"{result[4]['links']}",
                        "url",
                    ),
                ],
            ]
        )

        txt = f"Here are the results of requested query **{query.upper()}**"
        await to_del.delete()
        await m.reply_text(txt, reply_markup=keyboard)
        return
    except NoResultsFound:
        await to_del.delete()
        await m.reply_text("No result found corresponding to your query")
        return
    except NoResultsOrTrafficError:
        await to_del.delete()
        await m.reply_text("No result found due to too many traffic")
        return
    except Exception as e:
        await to_del.delete()
        await m.reply_text(f"Got an error:\nReport it at @{SUPPORT_CHANNEL}")
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return

# ------------------------------------------------------------------------------------- #

from pyrogram import filters
from pyrogram.errors import exceptions
from pyrogram.types import InputMediaPhoto

from Curse.bot_class import app
from Curse.extras.https import fetch


@app.on_message(filters.command(["pinterest", "img"], COMMAND_HANDLER), group=19092)
async def pinterest(_, message):
    chat_id = message.chat.id

    try:
        query = message.text.split(None, 1)[1]
    except:
        return await message.reply("Input image name for search 🔍")

    search_message = await message.reply("💫")

    try:
        response = await fetch.get(f"https://pinterest-api-one.vercel.app/?q={query}")
        images = response.json()
    except Exception as e:
        return await message.reply(f"Error\n{e}")

    images_url = images["images"]

    media_group = []

    for url in images_url[:5]:
        media_group.append(InputMediaPhoto(media=url))

    try:
        await search_message.delete()

        await _.send_media_group(
            chat_id=chat_id, media=media_group, reply_to_message_id=message.id
        )

        media_group = []

        for url in images_url[5:2]:
            media_group.append(InputMediaPhoto(media=url))

        await _.send_media_group(chat_id=chat_id, media=media_group)

    except exceptions.ChatWriteForbidden:
        await message.reply_text("First give me rights to send messages in the chat")
    except exceptions.bad_request_400.WebpageMediaEmpty:
        await message.reply_text(
            "There's been an error. Please try again with a different query."
        )
    except Exception as e:
        await message.reply(f"Error\n{e}")

# ------------------------------------------------------------------------------------- #

# Command handler for the '/bingimg' command
@app.on_message(filters.command(["bingimg", "bimg"], COMMAND_HANDLER), group=2424)
async def bingimg_search(client: Client, message: Message):
    try:
        text = message.text.split(None, 1)[
            1
        ]  # Extract the query from command arguments
    except IndexError:
        return await message.reply_text(
            "Provide me a query to search!"
        )  # Return error if no query is provided

    search_message = await message.reply_text("🔎")  # Display searching message

    # Send request to Bing image search API using fetch function
    bingimg_url = "https://sugoi-api.vercel.app/bingimg?keyword=" + text
    resp = await fetch.get(bingimg_url)
    images = json.loads(resp.text)  # Parse the response JSON into a list of image URLs

    media = []
    count = 0
    for img in images:
        if count == 7:
            break

        # Create InputMediaPhoto object for each image URL
        media.append(InputMediaPhoto(media=img))
        count += 1

    # Send the media group as a reply to the user
    await message.reply_media_group(media=media)

    # Delete the searching message and the original command message
    await search_message.delete()
    await message.delete()


# Command handler for the '/googleimg' command
@app.on_message(filters.command(["googleimg", "gimg"], COMMAND_HANDLER), group=2525)
async def googleimg_search(client: Client, message: Message):
    try:
        text = message.text.split(None, 1)[
            1
        ]  # Extract the query from command arguments
    except IndexError:
        return await message.reply_text(
            "Provide me a query to search!"
        )  # Return error if no query is provided

    search_message = await message.reply_text("💭")  # Display searching message

    # Send request to Google image search API using fetch function
    googleimg_url = "https://sugoi-api.vercel.app/googleimg?keyword=" + text
    resp = await fetch.get(googleimg_url)
    images = json.loads(resp.text)  # Parse the response JSON into a list of image URLs

    media = []
    count = 0
    for img in images:
        if count == 7:
            break

        # Create InputMediaPhoto object for each image URL
        media.append(InputMediaPhoto(media=img))
        count += 1

    # Send the media group as a reply to the user
    await message.reply_media_group(media=media)

    # Delete the searching message and the original command message
    await search_message.delete()
    await message.delete()

# ===================================================================================== #
__PLUGIN__ = "Google"


__alt_name__ = [
    "google",
]

__HELP__ = """
**Search**

**Available commands:**
➥ /google `<query>` : Search the google for the given query.
➥ /img (/pinterest) `<query>` : It retrieves and displays images obtained through a pinterest image search.
➥ /googleimg <search query>: It retrieves and displays images obtained through a Google image search.
➥ /bingimg <search query>: It retrieves and displays images obtained through a Bing image search.
➥ /ig (/instagram , /insta) <reel's url> : Download reel from it's url

**Example:**
`/google SEX`: return top 5 reuslts.
"""
