# PostBuilder Pro Bot

A professional Telegram bot for building posts and buttons. Users can create visual posts with text, various media types (images, videos, albums, etc.), and complex button layouts. Features include templates, JSON import/export, scheduled posting, premium tools (QR code generation, UTM generator), and a full admin panel.

## Tech Stack

- **Language:** Python 3.11
- **Framework:** aiogram 3.13.0 (async Telegram bot)
- **Database:** SQLite via aiosqlite + SQLAlchemy 2.0 ORM
- **Config:** python-dotenv

## Project Layout

- `postbuilder_bot/main.py` — entry point
- `postbuilder_bot/config.py` — settings loaded from env vars
- `postbuilder_bot/database/db.py` — SQLAlchemy models and DB init
- `postbuilder_bot/handlers/` — bot command/callback handlers
- `postbuilder_bot/keyboards/` — Telegram inline/reply keyboards
- `postbuilder_bot/locales/` — localization strings (AZ, RU, EN)
- `postbuilder_bot/middlewares/` — throttling, logging, maintenance
- `postbuilder_bot/utils/` — helper functions and data models

## Running

The workflow `Start application` runs: `cd postbuilder_bot && python main.py`

## Required Environment Variables

- `BOT_TOKEN` — Telegram bot token from @BotFather (secret)
- `ADMIN_IDS` — comma-separated list of admin Telegram user IDs
- `MAINTENANCE_MODE` — `true` or `false` (default: false)

## User Preferences

- Keep the existing project structure and module layout.
