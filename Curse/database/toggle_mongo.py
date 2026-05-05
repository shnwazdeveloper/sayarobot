from Curse.database.dbname import dbname

nsfwdb = dbname.nsfw
dwelcomedb = dbname.dwelcome
fungamesdb = dbname.fungames
mememodedb = dbname.meme
nekomodedb = dbname.nekomode

"""NSFW System"""


async def is_nsfw_on(chat_id: int) -> bool:
    chat = await nsfwdb.find_one({"chat_id": chat_id})
    return chat


async def nsfw_on(chat_id: int):
    is_nsfw = await is_nsfw_on(chat_id)
    if is_nsfw:
        return
    return await nsfwdb.insert_one({"chat_id": chat_id})


async def nsfw_off(chat_id: int):
    is_nsfw = await is_nsfw_on(chat_id)
    if not is_nsfw:
        return
    return await nsfwdb.delete_one({"chat_id": chat_id})


async def is_nekomode_on(chat_id: int) -> bool:
    chat = await nekomodedb.find_one({"chat_id_toggle": chat_id})
    return not bool(chat)


async def nekomode_on(chat_id: int) -> bool:
    await nekomodedb.delete_one(
        {"chat_id_toggle": chat_id}
    )  # Delete the chat ID from the database


async def nekomode_off(chat_id: int):
    await nekomodedb.insert_one(
        {"chat_id_toggle": chat_id}
    )  # Insert the chat ID into the database


async def is_dwelcome_on(chat_id: int) -> bool:
    chat = await dwelcomedb.find_one({"chat_id_toggle": chat_id})
    return not bool(chat)


async def dwelcome_on(chat_id: int) -> bool:
    await dwelcomedb.delete_one(
        {"chat_id_toggle": chat_id}
    )  # Delete the chat ID from the database


async def dwelcome_off(chat_id: int):
    await dwelcomedb.insert_one(
        {"chat_id_toggle": chat_id}
    )  # Insert the chat ID into the database


async def is_fungames_on(chat_id: int) -> bool:
    chat = await fungamesdb.find_one({"chat_id_toggle": chat_id})
    return not bool(chat)


async def fungames_on(chat_id: int):
    await fungamesdb.delete_one({"chat_id_toggle": chat_id})


async def fungames_off(chat_id: int):
    await fungamesdb.insert_one({"chat_id_toggle": chat_id})


async def is_meme_on(chat_id: int) -> bool:
    chat = await mememodedb.find_one({"chat_id_toggle": chat_id})
    return not bool(chat)


async def meme_on(chat_id: int):
    await mememodedb.delete_one({"chat_id_toggle": chat_id})


async def meme_off(chat_id: int):
    await mememodedb.insert_one({"chat_id_toggle": chat_id})
