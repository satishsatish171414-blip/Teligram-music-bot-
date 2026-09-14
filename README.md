# Telegram Music Bot — Hosting Ready

## Features
- /play <song or YouTube URL>
- /queue
- /skip
- /stop
- Docker + auto-restart configuration

## Important
Voice-chat playback normally requires a Telegram user session in addition to the bot credentials. Never publish your Bot Token, API Hash, or session file.

## Environment
Copy `.env.example` to `.env` and fill in:
- BOT_TOKEN
- API_ID
- API_HASH

## Run with Docker
```bash
docker compose up -d --build
```

The first user-session login may require an interactive login step. Complete that securely on the server and keep the generated session file private.
