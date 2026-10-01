from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

# Создаем роутер для этого модуля
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start."""
    logger.info(f"Пользователь {message.from_user.id} вызвал /start")
    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я твой бот на aiogram с настроенной архитектурой. Всё работает как часы!"
    )