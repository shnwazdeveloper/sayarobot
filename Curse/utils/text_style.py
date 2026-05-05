import re


SMALLCAPS_CHARS = {
    "a": "ᴀ",
    "b": "ʙ",
    "c": "ᴄ",
    "d": "ᴅ",
    "e": "ᴇ",
    "f": "ꜰ",
    "g": "ɢ",
    "h": "ʜ",
    "i": "ɪ",
    "j": "ᴊ",
    "k": "ᴋ",
    "l": "ʟ",
    "m": "ᴍ",
    "n": "ɴ",
    "o": "ᴏ",
    "p": "ᴘ",
    "q": "ǫ",
    "r": "ʀ",
    "s": "ꜱ",
    "t": "ᴛ",
    "u": "ᴜ",
    "v": "ᴠ",
    "w": "ᴡ",
    "x": "x",
    "y": "ʏ",
    "z": "ᴢ",
}
SMALLCAPS = str.maketrans(
    {
        **SMALLCAPS_CHARS,
        **{char.upper(): styled for char, styled in SMALLCAPS_CHARS.items()},
    }
)

EMOJI_RE = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"
    "\U0001F300-\U0001FAFF"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "\u2B00-\u2BFF"
    "\u2300-\u23FF"
    "\u200D"
    "\uFE0F"
    "]+"
)
HTML_TAG_RE = re.compile(r"(<[^>]+>)")


def strip_emoji(text):
    return EMOJI_RE.sub("", text)


def smallcaps(text):
    return strip_emoji(text).translate(SMALLCAPS)


def smallcaps_html(text):
    return "".join(
        part if part.startswith("<") and part.endswith(">") else smallcaps(part)
        for part in HTML_TAG_RE.split(text)
    )
