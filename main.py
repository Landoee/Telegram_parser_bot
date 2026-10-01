from src.config import BOT_TOKEN
from src.handlers import router as main_router

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

    await dp.start_polling(bot)

if __name__ == "__name__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())