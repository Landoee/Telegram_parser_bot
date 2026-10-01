```markdown
# SFU Schedule Telegram Bot

Telegram bot designed for students of Siberian Federal University (SFU) to retrieve and navigate class schedules. The application parses schedule data, maintains user context via finite state machine (FSM), and provides interactive daily navigation.

---

## Technical Stack

* **Language:** Python 3.13
* **Bot Framework:** aiogram 3
* **Parsing:** requests, BeautifulSoup4 (bs4)
* **Package Management:** uv
* **Logging:** loguru
* **Configuration:** python-dotenv

---

## Project Structure

```text
├── logs/
│   └── bot.log
├── src/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── schedule.py
│   ├── services/
│   │   └── parser.py
│   ├── config.py
│   └── main.py
├── .env
├── requirements.txt
└── README.md

```

---

## Core Features

* **Sequential Input (FSM):** Guides the user through a multi-step input process to capture their institute and academic group.
* **Schedule Parsing:** Fetches raw HTML data from the SFU schedule portal and extracts lesson details using BeautifulSoup.
* **Interactive Navigation:** Generates inline keyboards with days of the week, allowing users to switch days dynamically without flooding the chat history.
* **Context Preservation:** Stores active institute and group states per user session.

---

## Installation and Setup

1. Clone the repository and navigate to the project directory.
2. Initialize and install dependencies using `uv`:
```bash
uv sync

```


3. Create a `.env` file in the root directory and add your Telegram bot token:
```env
BOT_TOKEN=your_telegram_bot_token_here

```


4. Run the application:
```bash
uv run src/main.py

```
