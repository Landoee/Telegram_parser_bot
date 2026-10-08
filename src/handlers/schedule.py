"""Меню расписания и вывод текущей недели по профилю студента."""
from datetime import datetime, timedelta

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import Students
from src.keyboards.inline import get_main_menu_keyboard
from src.services.parser import DAYS, TZ, Schedule, ScheduleError, get_schedule

router = Router()


def render_schedule(schedule: Schedule, period: str) -> list[str]:
    today = datetime.now(TZ).date()
    start = today + timedelta(days=1) if period == 'tomorrow' else today
    if period == 'week':
        start = today - timedelta(days=today.weekday())
    sections = [f'📚 {schedule.group}\nВремя Красноярска.\n']
    for offset in range(7 if period == 'week' else 1):
        day = start + timedelta(days=offset)
        lessons = schedule.for_day(day)
        sections.append(f'📅 {DAYS[day.weekday()]}, {day:%d.%m.%Y}\n' + (
            '\n\n'.join(f'{item.number} пара • {item.time}\n{item.text}' for item in lessons)
            if lessons else 'Занятий нет.'))
    sections.append('Источник: https://edu.sfu-kras.ru/timetable\nПримечания и ограничения дат — в тексте занятий.')
    # Запас относительно лимита Telegram; plain text не требует разрезания HTML.
    text = '\n\n'.join(sections)
    chunks = []
    while text:
        end = min(len(text), 3500)
        if end < len(text):
            split = text.rfind('\n', 0, end)
            if split > 0:
                end = split
        chunks.append(text[:end])
        text = text[end:].lstrip('\n')
    return chunks


@router.message(Command('schedule'))
@router.message(F.text.casefold().in_({'расписание', '📅 расписание'}))
async def schedule_menu(message: Message):
    await message.answer('Выбери период расписания:', reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data == 'schedule:menu')
async def schedule_menu_callback(callback: CallbackQuery):
    await callback.answer()
    if isinstance(callback.message, Message):
        await callback.message.answer('Выбери период расписания:', reply_markup=get_main_menu_keyboard())


@router.callback_query(F.data.in_({'schedule:today', 'schedule:tomorrow', 'schedule:week'}))
async def show_schedule(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    if not isinstance(callback.message, Message):
        return
    student = await session.get(Students, callback.from_user.id)
    if student is None or not student.group_name:
        await callback.message.answer('Сначала укажи свою группу: /registration')
        return
    try:
        schedule = await get_schedule(student.group_name, student.uni_name, student.course, student.subgroup_number)
        chunks = render_schedule(schedule, callback.data.split(':')[1])
    except ScheduleError as exc:
        logger.warning('Не удалось получить расписание: {}', exc)
        await callback.message.answer(str(exc), parse_mode=None, reply_markup=get_main_menu_keyboard())
        return
    for index, chunk in enumerate(chunks):
        markup = get_main_menu_keyboard() if index == len(chunks) - 1 else None
        if index == 0:
            try:
                await callback.message.edit_text(chunk, parse_mode=None, reply_markup=markup)
            except TelegramBadRequest as exc:
                if 'message is not modified' not in str(exc):
                    raise
        else:
            await callback.message.answer(chunk, parse_mode=None, reply_markup=markup)
