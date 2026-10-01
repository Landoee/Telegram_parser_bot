from src.config import BOT_TOKEN
from src.handlers import router as main_router

from src.db.init_db import init_db
from src.db.models import User
from src.db.base import engine

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.include_routers(main_router)

    await init_db()
    await dp.start_polling(bot)
    await engine.dispose()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())