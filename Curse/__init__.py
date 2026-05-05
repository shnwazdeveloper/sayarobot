from datetime import datetime
from importlib import import_module as imp_mod
from logging import INFO, WARNING, FileHandler, StreamHandler, basicConfig, getLogger
from os import environ, listdir, mkdir, path as os_path
from platform import python_version
from random import choice
from sys import exit as sysexit, stdout, version_info
from time import time
from traceback import format_exc
from pyrogram import Client, filters
import lyricsgenius
import pyrogram
import pytz
import asyncio

# Logging configuration
LOG_DATETIME = datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
LOGDIR = f"{__name__}/logs"

# Make Logs directory if it does not exist
if not os_path.isdir(LOGDIR):
    mkdir(LOGDIR)

LOGFILE = f"{LOGDIR}/{__name__}_{LOG_DATETIME}_log.txt"
file_handler = FileHandler(filename=LOGFILE)
stdout_handler = StreamHandler(stdout)

basicConfig(
    format="%(asctime)s - [Tosu] - %(levelname)s - %(message)s",
    level=INFO,
    handlers=[file_handler, stdout_handler],
)

getLogger("pyrogram").setLevel(WARNING)
LOGGER = getLogger(__name__)

# Check Python version
if version_info[0] < 3 or version_info[1] < 7:
    LOGGER.error("You MUST have a Python Version of at least 3.7!\nMultiple features depend on this. Bot quitting.")
    sysexit(1)

# Load configuration
try:
    if environ.get("ENV"):
        from Curse.vars import Config
    else:
        from Curse.vars import Development as Config
except Exception as ef:
    LOGGER.error("Error loading configuration: %s", ef)
    LOGGER.error(format_exc())
    sysexit(1)

# Timezone setup
TIME_ZONE = pytz.timezone(Config.TIME_ZONE)

# Version handling
version_path = "./Version"
version_files = [i for i in listdir(version_path) if i.startswith("version") and i.endswith("md")]
VERSION = sorted(version_files)[-1][8:-3] if version_files else "unknown"

# Logging version information
PYTHON_VERSION = python_version()
PYROGRAM_VERSION = pyrogram.__version__
LOGGER.info("------------------------")
LOGGER.info("|      Tosu     |")
LOGGER.info("------------------------")
LOGGER.info(f"Version: {VERSION}")
LOGGER.info(f"Owner: {str(Config.OWNER_ID)}")
LOGGER.info(f"Time zone set to {Config.TIME_ZONE}")
LOGGER.info("Checking lyrics genius api...")

# API based clients
if Config.GENIUS_API_TOKEN:
    LOGGER.info("Found genius api token, initializing client")
    genius_lyrics = lyricsgenius.Genius(
        Config.GENIUS_API_TOKEN,
        skip_non_songs=True,
        excluded_terms=["(Remix)", "(Live)"],
        remove_section_headers=True,
    )
    is_genius_lyrics = True
    genius_lyrics.verbose = False
    LOGGER.info("Client setup complete")
else:
    LOGGER.error("Genius API token not found; lyrics command will not work")
    is_genius_lyrics = False
    genius_lyrics = None

# API for Audd and RMBG
is_audd = bool(Config.AuDD_API)
Audd = Config.AuDD_API if is_audd else None
if is_audd:
    LOGGER.info("Found Audd API")

is_rmbg = bool(Config.RMBG_API)
RMBG = Config.RMBG_API if is_rmbg else None

# Account Related
BOT_TOKEN = Config.BOT_TOKEN
API_ID = Config.API_ID
API_HASH = Config.API_HASH

# General Config
MESSAGE_DUMP = Config.MESSAGE_DUMP
SUPPORT_GROUP = Config.SUPPORT_GROUP
SUPPORT_CHANNEL = Config.SUPPORT_CHANNEL

# Users Config
OWNER_ID = Config.OWNER_ID
BOT_USERNAME = Config.BOT_USERNAME
BOT_ID = Config.BOT_ID
DEV = Config.DEV_USERS
DEVS_USER = set(DEV)
SUDO_USERS = Config.SUDO_USERS
WHITELIST_USERS = Config.WHITELIST_USERS
default_dev = set([int(OWNER_ID)])
DEVS = DEVS_USER | default_dev
DEV_USERS = list(DEVS)

# Plugins, DB and Workers
DB_URI = Config.DB_URI
DB_NAME = Config.DB_NAME
NO_LOAD = Config.NO_LOAD
WORKERS = Config.WORKERS
BDB_URI = Config.BDB_URI

# Prefixes
PREFIX_HANDLER = Config.PREFIX_HANDLER
HELP_COMMANDS = {}
UPTIME = time()  # Check bot uptime

# Scheduler setup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
scheduler = AsyncIOScheduler(timezone=TIME_ZONE)

async def load_cmds(all_plugins):
    """Loads all the plugins in the bot."""
    for single in all_plugins:
        if single.lower() in [i.lower() for i in Config.NO_LOAD]:
            LOGGER.warning(f"Not loading '{single}' as it's added in NO_LOAD list")
            continue
        try:
            imported_module = imp_mod(f"Curse.plugins.{single}")
            if not hasattr(imported_module, "__PLUGIN__"):
                continue
            
            plugin_name = imported_module.__PLUGIN__.lower()
            plugin_dict_name = f"plugins.{plugin_name}"
            plugin_help = imported_module.__HELP__

            if plugin_dict_name in HELP_COMMANDS:
                raise Exception(f"Can't have two plugins with the same name! Please change one\nError while importing '{imported_module.__name__}'")

            HELP_COMMANDS[plugin_dict_name] = {
                "buttons": [],
                "disablable": [],
                "alt_cmds": [],
                "help_msg": plugin_help,
            }

            if hasattr(imported_module, "__buttons__"):
                HELP_COMMANDS[plugin_dict_name]["buttons"] = imported_module.__buttons__
            if hasattr(imported_module, "_DISABLE_CMDS_"):
                HELP_COMMANDS[plugin_dict_name]["disablable"] = imported_module._DISABLE_CMDS_
            if hasattr(imported_module, "__alt_name__"):
                HELP_COMMANDS[plugin_dict_name]["alt_cmds"] = imported_module.__alt_name__

            HELP_COMMANDS[plugin_dict_name]["alt_cmds"].append(plugin_name)

        except Exception as e:
            LOGGER.error(f"Failed to load plugin {single}: {e}")

    if NO_LOAD:
        LOGGER.warning(f"Not loading Plugins - {NO_LOAD}")

    return ", ".join((i.split(".")[1]).capitalize() for i in list(HELP_COMMANDS.keys())) + "\n"

pbot = Client(
    "idkwhattowrite",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)
