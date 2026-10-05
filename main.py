from src.config import BOT_TOKEN
from src.handlers import router as main_router

from src.db.init_db import init_db
from src.db.base import async_session_maker, engine
from src.db.middleware import DatabaseSessionMiddleware

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher


async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    dp.update.outer_middleware(DatabaseSessionMiddleware(async_session_maker))
    dp.include_routers(main_router)

    try:
        await init_db()
        await dp.start_polling(bot)
    finally:
        await engine.dispose()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())