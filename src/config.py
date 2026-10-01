import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла в корне проекта
load_dotenv()

# Получаем токен бота
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Строгая проверка: если токен не задан, сообщаем об этом разработчику
if not BOT_TOKEN:
    raise ValueError(
        "❌ Ошибка: Переменная окружения BOT_TOKEN не найдена! "
        "Убедись, что файл .env создан в корне проекта и в нем прописан токен."
    )

# Здесь в будущем можно будет добавить другие ключи, например для gspread:
# GOOGLE_SHEETS_CREDENTIALS_FILE = os.getenv("GOOGLE_SHEETS_CREDENTIALS_FILE", "credentials.json")