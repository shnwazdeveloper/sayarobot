from os import getcwd
from urllib.parse import urlsplit

from prettyconf import Configuration
from prettyconf.loaders import EnvFile, Environment


def _get_str(name, default=None, required=False):
    value = config(name, default=default)
    if isinstance(value, str):
        value = value.strip()
    if value in (None, ""):
        if required:
            raise RuntimeError(f"{name} environment variable is required")
        return default
    return value


def _get_int(name, default=0, required=False):
    value = _get_str(name, default=None if required else str(default), required=required)
    if value in (None, ""):
        return default
    return int(value)


def _get_int_list(name, default=""):
    raw = _get_str(name, default=default)
    if not raw:
        return []
    return [int(item) for item in raw.replace(",", " ").split() if item.strip()]


def _redact_mongo_uri(uri):
    if not uri:
        return "<empty>"
    uri = str(uri)
    if "@" not in uri:
        return uri[:32] + ("..." if len(uri) > 32 else "")
    prefix, host = uri.rsplit("@", 1)
    scheme = prefix.split("://", 1)[0] if "://" in prefix else "mongodb"
    return f"{scheme}://<credentials>@{host[:32]}{'...' if len(host) > 32 else ''}"


def _validate_mongo_host(name, host):
    if not host or "..." in host or ".." in host:
        raise RuntimeError(
            f"{name} has an invalid MongoDB host. Current value starts as: {_redact_mongo_uri(config(name, default=''))}"
        )
    for label in host.split("."):
        if not label or len(label) > 63:
            raise RuntimeError(
                f"{name} has an invalid MongoDB host label. Current value starts as: {_redact_mongo_uri(config(name, default=''))}"
            )


def _get_mongo_uri(name, default=None, required=False):
    uri = _get_str(name, default=default, required=required)
    if not uri:
        return uri
    if "..." in uri:
        raise RuntimeError(
            f"{name} looks like a placeholder. Paste the full MongoDB URI into Railway."
        )
    if not uri.startswith(("mongodb://", "mongodb+srv://")):
        raise RuntimeError(f"{name} must start with mongodb:// or mongodb+srv://")
    try:
        parsed = urlsplit(uri)
    except (UnicodeError, ValueError) as exc:
        raise RuntimeError(f"{name} is not a valid MongoDB URI: {exc}") from exc
    if not parsed.netloc:
        raise RuntimeError(f"{name} is missing the MongoDB host")
    hosts = parsed.netloc.rsplit("@", 1)[-1].split(",")
    for entry in hosts:
        host = entry.rsplit(":", 1)[0].strip("[]")
        _validate_mongo_host(name, host)
    return uri


def _get_telegram_username(name, default=""):
    value = (_get_str(name, default=default) or "").strip()
    for prefix in ("https://t.me/", "http://t.me/", "t.me/"):
        if value.startswith(prefix):
            value = value[len(prefix):]
            break
    return value.strip("/").lstrip("@")


class SupportClass:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

env_file = f"{getcwd()}/.env"
config = Configuration(loaders=[Environment(), EnvFile(filename=env_file)])

class Config:
    """Config class for variables."""
    LOGGER = True
    BOT_TOKEN = _get_str("BOT_TOKEN", required=True)
    API_ID = _get_int("API_ID", required=True)
    API_HASH = _get_str("API_HASH", required=True)
    OWNER_ID = _get_int("OWNER_ID", default=0)
    MESSAGE_DUMP = _get_int("MESSAGE_DUMP", required=True)
    DEV_USERS = _get_int_list("DEV_USERS")
    SUDO_USERS = _get_int_list("SUDO_USERS")
    WHITELIST_USERS = _get_int_list("WHITELIST_USERS")
    GENIUS_API_TOKEN = _get_str("GENIUS_API")
    RMBG_API = _get_str("RMBG_API")
    DB_URI = _get_mongo_uri("DB_URI", required=True)
    DB_NAME = _get_str("DB_NAME", default="sayarobot")
    BDB_URI = _get_mongo_uri("BDB_URI")
    NO_LOAD = _get_str("NO_LOAD", default="").split()
    PREFIX_HANDLER = _get_str("PREFIX_HANDLER", default="/ !").split()
    SUPPORT_GROUP = _get_telegram_username("SUPPORT_GROUP")
    SUPPORT_CHANNEL = _get_telegram_username("SUPPORT_CHANNEL")
    WORKERS = _get_int("WORKERS", default=8)
    TIME_ZONE = _get_str("TIME_ZONE", default="Asia/Kolkata")
    BOT_USERNAME = _get_str("BOT_USERNAME")
    BOT_ID = _get_str("BOT_ID")
    BOT_NAME = "sayarobot"
    owner_username = _get_str("OWNER_USERNAME", default="")


class Development(Config):
    """Backward-compatible local config; values still come from env or .env."""
