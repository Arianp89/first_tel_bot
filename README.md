<<<<<<< HEAD
# bot_1st

[🔗مستندات فارسی](README.fa.md)

A Telegram/Bale customer and admin bot for managing project orders, communicating with clients, and tracking development requests.

## About

`bot_1st` is a Python bot built with `pyTelegramBotAPI` and MySQL. It supports two user flows:

- Customer: request bot/project development, send details, submit voice descriptions, and view project status.
- Admin: review orders, manage users and projects, deliver files, send messages, and use OpenAI GPT assistance.

## Features

- Customer onboarding and profile handling
- Project request submission with bot token and details
- Admin review panel for orders and customer support
- Blacklist management for suspicious users
- AI assistance via OpenAI GPT for admin actions
- MySQL database persistence for customers, products, sales, and blacklist records
- Voice message support and project file delivery
- Logs activity to `project.log`

## Requirements

- Python 3.11+
- MySQL server
- `pip` installed
- Environment variables configured

Required packages are listed in `requirements.txt`.

## Installation

1. Clone the repository.
2. Create and activate a virtual environment:

```powershell
python -m venv venv
.\\venv\\Scripts\\Activate.ps1
```

3. Install dependencies:

```powershell
pip install -r requirements.txt
```

## Configuration

Set the following environment variables before running the bot:

- `db_host` — MySQL host address
- `db_user` — MySQL username
- `password` — MySQL password
- `db_name` — MySQL database name
- `tel_token` — Telegram or Bale bot token
- `ai_Token` — OpenAI API token
- `proxy_1` — optional proxy URL
- `proxy_2` — optional proxy URL

Example in PowerShell:

```powershell
$env:db_host = "localhost"
$env:db_user = "root"
$env:password = "secret"
$env:db_name = "bot_database"
$env:tel_token = "YOUR_TELEGRAM_OR_BALE_TOKEN"
$env:ai_Token = "YOUR_OPENAI_API_KEY"
```

> The bot reads configuration values from `confing.py` using environment variables.

## Database Setup

Create the database schema by running:

```powershell
python DDL.py
```

This script creates the following tables:

- `CUSTOMER`
- `PRODUCT`
- `SALE`
- `SALE_ROW`
- `BLACK_LIST`

## Running the Bot

Start the bot with:

```powershell
python main.py
```

The bot listens for incoming messages and automatically handles customer and admin workflows.

## Project Structure

- `main.py` — core bot logic and message handlers
- `confing.py` — environment configuration and admin IDs
- `DDL.py` — database creation scripts
- `DML.py` — data insert/update operations
- `DQL.py` — query operations for reading data
- `Text.py` — bot UI text, buttons, and responses
- `requirements.txt` — Python dependencies
- `Data/voice/` — stored voice message files

## Notes

- The bot uses the Bale API endpoint by default in `main.py`.
- Admin IDs are defined in `confing.py` under `ADMIN`.
- Customize interface text and messages in `Text.py`.

## Contributing

1. Fork the repository.
2. Create a new branch.
3. Make changes and test.
4. Open a pull request.

## License

Add a license file if you plan to publish this repository publicly.
=======
