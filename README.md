# Telegram Planner Bot

A simple Telegram bot that stores user phone numbers and provides basic
functionality such as notes, alarms and a future planner section.

## Requirements

- Python 3.8 or higher
- A PostgreSQL (or compatible) database

## Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project root (or set the variables in your
   environment) with the following values:

   ```bash
   BOT_TOKEN=<your telegram bot token>
   DATABASE_URL=<async database url>
   ```

   `BOT_TOKEN` – token from [@BotFather](https://t.me/BotFather).

   `DATABASE_URL` – SQLAlchemy async connection string, e.g.
   `postgresql+asyncpg://user:password@host:5432/dbname`.

## Running locally

Initialize the database and start the bot:

```bash
python bot.py
```

The bot will automatically create required tables on startup via
`init_db()` in `database.py`.

## Running on Heroku

This repository includes a `Procfile` for Heroku. After creating an app on
Heroku and adding `BOT_TOKEN` and `DATABASE_URL` to the app's config vars,
deploy your code. Heroku will run the bot using:

```bash
web: python bot.py
```

