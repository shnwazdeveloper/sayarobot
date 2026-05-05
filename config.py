import os


def _required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"{name} environment variable is required")
    return value


def _bool_env(name: str, default: bool = True) -> bool:
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


BOT_TOKEN = _required("BOT_TOKEN")
API_ID = int(_required("API_ID"))
API_HASH = _required("API_HASH")
SPOILER_MODE = _bool_env("SPOILER_MODE", True)
