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

Optional chatbot variables:

```env
GEMINI_API_KEY=
CHATBOT_DB_URI=
CHATBOT_DB_NAME=sayarobot
```

For lyrics, set `GENIUS_API` to your Genius Client Access Token. The Genius
Client ID and Client Secret are not used by this bot.

Optional API integrations:

```env
ARQ_API_KEY=
ARQ_API_URL=arq.hamker.dev
IMGBB_API_KEY=
```

`MESSAGE_DUMP` must be a Telegram supergroup or channel id that starts with
`-100`, and the bot must be able to send messages there.
