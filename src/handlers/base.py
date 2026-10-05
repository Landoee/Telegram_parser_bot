from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Students
from src.keyboards.inline import get_main_menu_keyboard
from loguru import logger

# Создаем роутер для этого модуля
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, session: AsyncSession):
    """Обработчик команды /start."""
    logger.info(f"Пользователь {message.from_user.id} вызвал /start")

    student = await session.get(Students, message.from_user.id)
    if student:
        await message.answer(
            "Здравствуйте! Выберите, какое расписание вам нужно:",
            reply_markup=get_main_menu_keyboard(),
        )
        return

    await message.answer(
        f"Привет, {message.from_user.first_name}! 👋\n"
        "Я бот расписание сфу, и мне нужно чтобы ты прошел маленькую регистрацию.\n"
        "Для этого нажми сюда -> /registration"
    )