# inbjorkBot

A Telegram bot for tracking stock tickers and managing price alerts. Market data is retrieved from Yahoo Finance with `yfinance`; ticker and alert data is stored locally in SQLite.

## Features

- Add, remove, show, and list tracked tickers.
- Set, view, and remove price alerts.
- Check whether configured alerts have been reached.

## Requirements

- Python 3.9 or newer
- A Telegram bot token from [@BotFather](https://t.me/BotFather)

## Setup

1. Clone the repository and enter the project directory.
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

   On Windows PowerShell, activate it with:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Create a `.env` file and set `BOT_TOKEN` to your Telegram bot token:

   ```dotenv
   BOT_TOKEN=your_telegram_bot_token
   ```
5. Start the bot:

   ```bash
   python AssistantBot.py
   ```

The bot creates `bot.db` in the project directory when it first runs. Both `.env` and the local database are ignored by Git; do not commit credentials or personal database contents.

## Telegram commands

| Command | Usage |
| --- | --- |
| `/add` | `/add <TICKER>` |
| `/del` | `/del <TICKER>` |
| `/show` | `/show <TICKER>` |
| `/list` | List tracked tickers |
| `/addal` | `/addal <TICKER> <up/down> <PRICE>` |
| `/delal` | `/delal <TICKER> <up/down/all>` |
| `/showal` | Show configured alerts |
| `/chkal` | Check configured alerts against current prices |
