from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command

# Импортируем клавиатуры и функцию сохранения из твоей структуры
from src.keyboards.inline import (
    get_institutes_keyboard,
    get_courses_keyboard,
    get_subgroup_keyboard,
    get_main_menu_keyboard
)
from src.db.requests import save_student

class Registration(StatesGroup):
    institute = State()
    course = State()
    group = State()
    subgroup = State()


router = Router() 

async def _show_registration_prompt(
    message: Message,
    state: FSMContext,
    *,
    edit_message: bool = False,
) -> None:
    await state.clear()
    await state.set_state(Registration.institute)
    text = "📚 Давай настроим расписание!\n\nШаг 1 из 4: Выбери свой институт:"
    if edit_message:
        await message.edit_text(text, reply_markup=get_institutes_keyboard())
    else:
        await message.answer(text, reply_markup=get_institutes_keyboard())


# Шаг 1: Старт регистрации (Команда /registration)
@router.message(Command("registration"))
async def registration_start(message: Message, state: FSMContext):
    await _show_registration_prompt(message, state)


@router.callback_query(F.data == "settings:change_data")
async def change_data(callback: CallbackQuery, state: FSMContext):
    if not isinstance(callback.message, Message):
        await callback.answer(
            "Не удалось начать изменение данных. Отправь команду /registration.",
            show_alert=True,
        )
        return

    await _show_registration_prompt(callback.message, state, edit_message=True)
    await callback.answer()

# Шаг 2: Обработка выбора института -> Переход к выбору курса
@router.callback_query(Registration.institute, F.data.startswith("inst:"))
async def process_institute(callback: CallbackQuery, state: FSMContext):
    selected_institute = callback.data.split(":")[1]
    
    # Сохраняем институт во временный кэш FSM
    await state.update_data(institute=selected_institute)
    await state.set_state(Registration.course)
    
    # Меняем сообщение и показываем кнопки выбора курса
    await callback.message.edit_text(
        f"✅ Институт выбран: {selected_institute}\n\nШаг 2 из 4: Выбери свой курс:",
        reply_markup=get_courses_keyboard()
    )
    await callback.answer()

# Шаг 3: Обработка выбора курса -> Запрос ввода группы
@router.callback_query(Registration.course, F.data.startswith("course:"))
async def process_course(callback: CallbackQuery, state: FSMContext):
    selected_course = callback.data.split(":")[1]
    
    # Сохраняем курс в кэш FSM
    await state.update_data(course=selected_course)
    await state.set_state(Registration.group)
    
    # Просим пользователя ввести номер группы текстовым сообщением
    await callback.message.edit_text(
        "✍️ Шаг 3 из 4: Введи полное название группы с сайта СФУ, например КИ26-01. Можно ввести номер 01, если он однозначен для твоего института и курса:"
    )
    await callback.answer()

# Шаг 4: Обработка ввода группы (текст) -> Валидация и переход к подгруппе
@router.message(Registration.group)
async def process_group_input(message: Message, state: FSMContext):
    user_input = (message.text or "").strip()
    
    # Проверяем, не пустая ли строка
    if not user_input:
        await message.answer("❌ Название или номер группы не может быть пустым. Попробуй еще раз:")
        return

    # Ограничение соответствует длине поля group_name в БД.
    if len(user_input) > 50 or user_input.startswith("/"):
        await message.answer("❌ Введи название группы длиной до 50 символов:")
        return

    # Сохраняем группу в кэш FSM
    await state.update_data(group_name=user_input)
    await state.set_state(Registration.subgroup)
    
    # Отправляем клавиатуру выбора подгруппы (Шаг 4)
    await message.answer(
        "👥 Шаг 4 из 4: Группа принята!\nИ последний шаг: выбери свою подгруппу:",
        reply_markup=get_subgroup_keyboard()
    )

# Шаг 5: Финал (Выбор подгруппы) -> Запись в БД и выдача меню расписания
@router.callback_query(Registration.subgroup, F.data.in_({"subgroup:1", "subgroup:2", "subgroup:3"}))
async def finish_registration(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    # Забираем ВСЁ, что накопилось в кэше за предыдущие шаги
    data = await state.get_data()

    if not all(data.get(key) is not None for key in ("institute", "course", "group_name")):
        await callback.answer(
            "Не хватает данных для регистрации. Начни заново командой /registration.",
            show_alert=True
        )
        return
    
    # Сохраняем студента в базу данных через функцию save_student
    await save_student(
        session=session,
        telegram_id=callback.from_user.id,
        username=callback.from_user.username,
        uni_name=data.get("institute"),
        group_name=data.get("group_name"),
        course=int(data.get("course")),
        subgroup_number=int(callback.data.split(":")[1])
    )
    
    # Очищаем кэш FSM, чтобы память не засорялась
    await state.clear()
    
    # Обновляем сообщение: убираем кнопки подгрупп и выводим главное меню расписания
    await callback.message.edit_text(
        "✅ Регистрация успешно завершена! Твои данные сохранены.\n\nВыбери, какое расписание тебя интересует:",
        reply_markup=get_main_menu_keyboard()
    )
    await callback.answer()
