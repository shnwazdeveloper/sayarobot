from platform import python_version
from threading import RLock
from time import gmtime, strftime, time

from pyrogram import Client, __version__
from pyrogram.errors import RPCError
from pyrogram.raw.all import layer
from pyrogram.types import BotCommand

from Curse import (API_HASH, API_ID, BDB_URI, BOT_TOKEN, LOG_DATETIME,
                    LOGFILE, LOGGER, MESSAGE_DUMP, NO_LOAD, OWNER_ID, UPTIME,
                    WORKERS, load_cmds, scheduler,pbot)
import Curse as curse_module
from Curse.database import MongoDB
from Curse.plugins import all_plugins
from Curse.plugins.scheduled_jobs import *
from Curse.supports import *
from Curse.vars import Config

INITIAL_LOCK = RLock()
TOKEN_ERROR_NAMES = {
    "AccessTokenExpired",
    "AccessTokenInvalid",
    "BotTokenInvalid",
    "TokenInvalid",
}
CONFIG_ERROR_NAMES = {"ApiIdInvalid", "ApiIdPublishedFlood"}


def _log_pyrogram_start_error(client_name, exc):
    error_name = exc.__class__.__name__
    details = str(exc).strip()
    normalized_error = f"{error_name} {details}".upper()
    if (
        error_name in TOKEN_ERROR_NAMES
        or "ACCESS_TOKEN" in normalized_error
        or "BOT_TOKEN" in normalized_error
    ):
        LOGGER.error(
            "%s login failed: Telegram rejected BOT_TOKEN (%s).",
            client_name,
            error_name,
        )
        LOGGER.error(
            "Fix Railway variable BOT_TOKEN with the full token from @BotFather, not a Genius/OAuth token."
        )
        return
    if error_name in CONFIG_ERROR_NAMES:
        LOGGER.error(
            "%s login failed: check API_ID and API_HASH in Railway (%s).",
            client_name,
            error_name,
        )
        return
    if details:
        LOGGER.error("%s login failed with %s: %s", client_name, error_name, details)
    else:
        LOGGER.error("%s login failed with %s.", client_name, error_name)


async def _run_pyrogram_start(start_call, client_name):
    try:
        await start_call()
    except RPCError as exc:
        _log_pyrogram_start_error(client_name, exc)
        raise SystemExit(1) from exc

# Check if MESSAGE_DUMP is correct
if MESSAGE_DUMP == -100 or not str(MESSAGE_DUMP).startswith("-100"):
    raise Exception(
        "Please enter a vaild Supergroup ID, A Supergroup ID starts with -100",
    )



class app(Client):
    """Starts the Pyrogram Client on the Bot Token when we do 'python3 -m Curse'"""

    def __init__(self):
        # name = Curse

        super().__init__(
            "app",
            bot_token=BOT_TOKEN,
            plugins=dict(root="Curse.plugins", exclude=NO_LOAD),
            api_id=API_ID,
            api_hash=API_HASH,
            workers=WORKERS,
        )

    async def start(self):
        """Start the bot."""
        await _run_pyrogram_start(pbot.start, "Auxiliary Pyrogram client")
        await _run_pyrogram_start(super().start, "Main Pyrogram client")
        await self.set_bot_commands(
            [
                BotCommand("start", "Sᴛᴀʀᴛ's Tʜᴇ Bᴏᴛ"),
                BotCommand("alive", "for Checking bot alive or not"),
                BotCommand("play", "play music"),
                BotCommand("help", "Cᴏᴍᴍᴀɴᴅ Lɪsᴛ"),
                BotCommand("afk","Aᴡᴀʏ Fʀᴏᴍ Cʜᴀᴛ")
            ]
        )
        meh = await self.get_me()  # Get bot info from pyrogram client
        LOGGER.info("Starting bot...")
        Config.BOT_ID = meh.id
        Config.BOT_NAME = meh.first_name
        Config.BOT_USERNAME = meh.username
        curse_module.BOT_ID = meh.id
        curse_module.BOT_NAME = meh.first_name
        curse_module.BOT_USERNAME = meh.username
        startmsg = await self.send_message(MESSAGE_DUMP, "<i>Starting Bot...</i>")

        # Show in Log that bot has started
        LOGGER.info(
            f"Pyrogram v{__version__} (Layer - {layer}) started on {meh.username}",
        )
        LOGGER.info(f"Python Version: {python_version()}\n")

        # Get cmds and keys
        cmd_list = await load_cmds(await all_plugins())
        await load_support_users()
        LOGGER.info(f"Plugins Loaded: {cmd_list}")
        scheduler.add_job(clean_my_db,'cron',[self],hour=3,minute=0,second=0)
        if BDB_URI:
            scheduler.add_job(send_wishish,'cron',[self],hour=0,minute=0,second=0)
            scheduler.start()
        # Send a message to MESSAGE_DUMP telling that the
        # bot has started and has loaded all plugins!
        await startmsg.edit_text(
            (
                f"<b><i>@{meh.username} started on Pyrogram v{__version__} (Layer - {layer})</i></b>\n"
                f"\n<b>Python:</b> <u>{python_version()}</u>\n"
                "\n<b>Loaded Plugins:</b>\n"
                f"<i>{cmd_list}</i>\n"
            ),
        )

        LOGGER.info("Bot Started Successfully!\n")

    async def stop(self):
        """Stop the bot and send a message to MESSAGE_DUMP telling that the bot has stopped."""
        runtime = strftime("%Hh %Mm %Ss", gmtime(time() - UPTIME))
        LOGGER.info("Uploading logs before stopping...!\n")
        # Send Logs to MESSAGE_DUMP and LOG_CHANNEL
        await self.send_document(
            MESSAGE_DUMP,
            document=LOGFILE,
            caption=(
                "Bot Stopped!\n\n" f"Uptime: {runtime}\n" f"<code>{LOG_DATETIME}</code>"
            ),
        )
        scheduler.remove_all_jobs()
        if MESSAGE_DUMP:
            # LOG_CHANNEL is not necessary
            await self.send_document(
                MESSAGE_DUMP,
                document=LOGFILE,
                caption=f"Uptime: {runtime}",
            )
        await super().stop()
        MongoDB.close()
        LOGGER.info(
            f"""Bot Stopped.
            Logs have been uploaded to the MESSAGE_DUMP Group!
            Runtime: {runtime}s\n
        """,
  )
