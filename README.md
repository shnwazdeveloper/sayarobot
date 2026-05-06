# sayarobot

[![Python](https://img.shields.io/badge/python-3.10-blue)](https://www.python.org/)
[![Pyrogram](https://img.shields.io/badge/telegram-pyrogram-green)](https://pyrogram.org/)
[![Railway](https://img.shields.io/badge/deploy-railway-purple)](https://railway.app/)
[![License](https://img.shields.io/badge/license-GPL--3.0-lightgrey)](https://www.gnu.org/licenses/gpl-3.0.en.html)

`sayarobot` is a Telegram group-management bot built with Python and Pyrogram. It includes moderation tools, notes, filters, warnings, admin utilities, anime helpers, AI chat support, and a clean video-based start menu.

## Highlights

- Group moderation: bans, mutes, warnings, locks, reports, approvals, blacklist, rules, and admin tools.
- Community tools: notes, filters, birthday messages, welcome helpers, AFK, tagging, and utility commands.
- AI features: Gemini-powered chatbot support through `google-genai`.
- Media experience: video start screen with direct buttons for Add to group, Help, Support, Channel, and Source.
- Deployment-ready: Dockerfile and Railway config are included.
- MongoDB storage: group settings, notes, warnings, disabled commands, chatbot data, and bot state.

## Start Menu

The default `/start` menu uses direct Telegram buttons:

```text
Add me to your group
Help
Support | Channel
Source
```

Telegram controls inline-button colors and URL arrows in the app UI. The bot controls the button text, layout, callback actions, and direct links.

## Deploy On Railway

1. Fork or clone this repository.
2. Create a Railway project from the GitHub repo.
3. Railway will use the included `Dockerfile` and `railway.json`.
4. Add the required environment variables.
5. Deploy the worker service.

Railway start command:

```bash
python -m Curse
```

## Required Variables

Set these in Railway before starting the bot:

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

Important notes:

- `BOT_TOKEN` must be the full token from `@BotFather`.
- `API_ID` and `API_HASH` come from `https://my.telegram.org`.
- `MESSAGE_DUMP` must be a supergroup or channel id starting with `-100`.
- The bot must be added to `MESSAGE_DUMP` and allowed to send messages.
- `DB_URI` must be a full MongoDB URI, not a shortened value such as `mongodb...`.

## Optional Variables

Admin and support:

```env
DEV_USERS=
SUDO_USERS=
WHITELIST_USERS=
SUPPORT_GROUP=YourMoreBotsChannel
SUPPORT_CHANNEL=YourMoreBotsChannel
PREFIX_HANDLER=/ !
TIME_ZONE=Asia/Kolkata
WORKERS=8
```

AI and extras:

```env
GENIUS_API=
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.5-flash
CHATBOT_DB_URI=
CHATBOT_DB_NAME=sayarobot
BDB_URI=
RMBG_API=
```

For lyrics, only `GENIUS_API` is used. Genius Client ID and Client Secret are not needed.

## Local Run

Create a `.env` file from `.env.example`, then install dependencies and start the bot:

```bash
python -m pip install -r requirements.txt
python -m Curse
```

Docker:

```bash
docker build -t sayarobot .
docker run --env-file .env sayarobot
```

## Troubleshooting

`BOT_TOKEN is not a valid Telegram bot token`

Use the full token from `@BotFather`. Do not use a Genius token, OAuth token, client ID, or client secret.

`MESSAGE_DUMP starts wrong`

Use a Telegram supergroup or channel id that starts with `-100`.

`MongoDB host invalid`

Paste the complete MongoDB URI into Railway. Do not paste a shortened or hidden value containing `...`.

`Telegram login failed`

Check `BOT_TOKEN`, `API_ID`, and `API_HASH` in Railway. Redeploy after editing variables.

`Lyrics command does not work`

Set `GENIUS_API` to the Genius Client Access Token.

## Repository

- Source: `https://github.com/shnwazdeveloper/sayarobot.git`
- Support: `https://t.me/YourMoreBotsChannel`
- Updates: `https://t.me/YourMoreBotsChannel`

## License

This project is released under the GNU General Public License v3.0.
