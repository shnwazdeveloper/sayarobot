# sayarobot

Telegram group management bot built with Pyrogram.

## Railway

Deploy this repo on Railway from GitHub. The included `Dockerfile` and
`railway.json` run the bot with:

```bash
python -m Curse
```

Set these required Railway variables before starting the service:

```env
ENV=ANYTHING
BOT_TOKEN=
API_ID=
API_HASH=
OWNER_ID=
MESSAGE_DUMP=
DB_URI=
DB_NAME=sayarobot
```

Optional admin/support variables:

```env
DEV_USERS=
SUDO_USERS=
WHITELIST_USERS=
SUPPORT_GROUP=YourMoreBotsChannel
SUPPORT_CHANNEL=YourMoreBotsChannel
```

`SUPPORT_GROUP` and `SUPPORT_CHANNEL` can be either a Telegram username
without `@` or a `https://t.me/...` link; the bot normalizes links at startup.

Optional chatbot variables:

```env
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
CHATBOT_DB_URI=
CHATBOT_DB_NAME=sayarobot
```

For lyrics, set `GENIUS_API` to your Genius Client Access Token. The Genius
Client ID and Client Secret are not used by this bot.

`MESSAGE_DUMP` must be a Telegram supergroup or channel id that starts with
`-100`, and the bot must be able to send messages there.
