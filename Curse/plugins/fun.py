from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from Curse.bot_class import app
from Curse.database.toggle_mongo import fungames_off, fungames_on, is_fungames_on
from Curse.utils.custom_filters import admin_filter


@app.on_message(filters.command("games on") & admin_filter)
async def enable_game_commands(client, message: Message):
    chat_id = message.chat.id
    await fungames_on(chat_id)
    await message.reply("Game commands have been enabled.")


@app.on_message(filters.command("games off") & admin_filter)
async def disable_game_commands(client, message: Message):
    chat_id = message.chat.id
    await fungames_off(chat_id)
    await message.reply("Game commands have been disabled.")


@app.on_message(filters.command("dice"))
async def throw_dice(client, message: Message):
    chat_id = message.chat.id
    enabled = await is_fungames_on(chat_id)
    if enabled:
        await client.send_dice(chat_id, "🎲")


@app.on_message(filters.command("dart"))
async def throw_dart(client, message: Message):
    chat_id = message.chat.id
    enabled = await is_fungames_on(chat_id)
    if enabled:
        await client.send_dice(chat_id, "🎯")


@app.on_message(filters.command("basket"))
async def throw_basketball(client, message: Message):
    chat_id = message.chat.id
    enabled = await is_fungames_on(chat_id)
    if enabled:
        await client.send_dice(chat_id, "🏀")


@app.on_message(filters.command("bowling"))
async def throw_bowling_ball(client, message: Message):
    chat_id = message.chat.id
    enabled = await is_fungames_on(chat_id)
    if enabled:
        await client.send_dice(chat_id, "🎳")


@app.on_message(filters.command("slot"))
async def play_slot_machine(client, message: Message):
    chat_id = message.chat.id
    enabled = await is_fungames_on(chat_id)
    if enabled:
        await client.send_dice(chat_id, "🎰")


@app.on_callback_query(filters.regex(r"^fun_games$"))
async def fun_games_callback(_, query: CallbackQuery, todo="commands"):
    await query.answer()
    await query.message.edit_text(
        "**Use these commands and try to score:**\n\n"
        "➥ /games on : Enables fun games mode.\n"
        "➥ /games off : Disables fun games mode.\n\n"
        "❍ /dice - dice 🎲\n"
        "❍ /dart - dart 🎯\n"
        "❍ /basket - basket ball 🏀\n"
        "❍ /bowling - bowling ball 🎳\n"
        "❍ /slot - spin slot machine 🎰\n",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⌦ 𝘽𝘼𝘾𝙆", todo),
                ],
            ],
        ),
    )


@app.on_callback_query(filters.regex(r"^fun_memes$"))
async def fun_memes_callback(_, query: CallbackQuery, todo="commands"):
    await query.answer()
    await query.message.edit_text(
        "**😂 Meme Commands:**\n\n"
        "➥ /mememode on : Enables fun meme mode.\n"
        "➥ /mememode off : Disables fun meme mode.\n\n"
        "❍ /memes - Retrieves a random meme from various meme subreddits.\n"
        "❍ /dank - Retrieves a random meme from the dankmemes subreddit.\n"
        "❍ /lolimeme - Retrieves a random meme from the lolimemes subreddit.\n"
        "❍ /hornyjail - Retrieves a random meme from the Hornyjail subreddit.\n"
        "❍ /wmeme - Retrieves a random meme from the wholesomememes subreddit.\n"
        "❍ /fbi - Retrieves a random meme from the fbi subreddit.\n"
        "❍ /teen - Retrieves a random meme from the teenagers subreddit.\n"
        "❍ /shitposting - Retrieves a random meme from the shitposting subreddit.\n"
        "❍ /hmeme - Retrieves a random meme from the Hmemes subreddit.\n"
        "❍ /cursed - Retrieves a random meme from the cursedcomments subreddit.\n"
        "❍ /pewds - Retrieves a random meme from the Pewds subreddit.\n",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⌦ 𝘽𝘼𝘾𝙆", todo),
                ],
            ],
        ),
    )


__PLUGIN__ = "Fun"
__buttons__ = [
    [
        ("Fun Games", "fun_games"),
        ("Memes", "fun_memes"),
    ],
]

_DISABLE_CMDS_ = [
    "weebify",
    "decide",
    "react",
    "bluetext",
    "toss",
    "yes",
    "no",
    "roll",
    "runs",
    "shout",
    "insult",
    "shrug",
]

__HELP__ = """
**🥳 Fun**

➥ /runs: reply a random string from an array of replies.
➥ /insult: to insult a user, or get insulted if not a reply
➥ /shrug : get shrug XD.
➥ /cosplay : sends cosplay images.
➥ /decide : Randomly answers yes/no/maybe
➥ /toss : Tosses A coin
➥ /yes : check urself :V
➥ /no : check urself :V
➥ /bluetext : check urself :V
➥ /roll : Roll a dice.
➥ /react : Random Reaction
➥ /shout `<keyword>`: write anything you want to give loud shout."""

