from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_institutes_keyboard():
    """Клавиатура институтов СФУ с короткими названиями"""
    builder = InlineKeyboardBuilder()
    
    institutes = [
        ("Военно-инженерный институт", "inst:Voen"),
        ("Гуманитарный институт", "inst:Guman"),
        ("ИСИ (Инж.-строительный)", "inst:ISI"),
        ("ИАрхДив (Архитектура и дизайн)", "inst:IAD"),
        ("ИИФиРЭ (Инж. физика и радиоэлектроника)", "inst:IIFIR"),
        ("ИКИТ (Космос и информ. технологии)", "inst:IKIT"),
        ("ИМиФИ (Математика и информатика)", "inst:IMIFI"),
        ("Институт нефти и газа", "inst:INiG"),
        ("ИППС (Педагогика и психология)", "inst:IPPS"),
        ("ИТСУ (Торговля и сфера услуг)", "inst:ITSUs"),
        ("ИУБП (Управление бизнес-процессами)", "inst:IUBP"),
        ("ИФКСиТ (Физкультура и спорт)", "inst:IFKST"),
        ("ИФиЯК (Филология и языки)", "inst:IFIYK"),
        ("ИФБиБ (Биология и биотехнологии)", "inst:IFBB"),
        ("ИЦМиМ (Цветные металлы)", "inst:ICMM"),
        ("ИЭиГ (Экология и география)", "inst:IEG"),
        ("ИЭУиФ (Экономика и финансы)", "inst:IUGIF"),
        ("Политехнический институт", "inst:Poly"),
        ("Проектный офис новых особ. практик", "inst:PONOP"),
        ("Юридический институт", "inst:UrI"),
    ]
    
    for text, callback in institutes:
        builder.button(text=text, callback_data=callback)
        
    builder.adjust(1)
    return builder.as_markup()


def get_courses_keyboard():
    """Клавиатура выбора курса обучения"""
    builder = InlineKeyboardBuilder()
    
    courses = [
        ("1 курс", "course:1"),
        ("2 курс", "course:2"),
        ("3 курс", "course:3"),
        ("4 курс", "course:4"),
        ("5 курс", "course:5"),
    ]
    
    for text, callback in courses:
        builder.button(text=text, callback_data=callback)
        
    builder.adjust(2, 2, 1)
    return builder.as_markup()


def get_subgroup_keyboard():
    """Клавиатура выбора подгруппы."""
    builder = InlineKeyboardBuilder()
    builder.button(text="1 подгруппа", callback_data="subgroup:1")
    builder.button(text="2 подгруппа", callback_data="subgroup:2")
    builder.button(text="3 подгруппа", callback_data="subgroup:3")
    builder.adjust(3)
    return builder.as_markup()

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="📚 Расписание", callback_data="schedule:menu")],
        [
            InlineKeyboardButton(text="📅 На сегодня", callback_data="schedule:today"),
            InlineKeyboardButton(text="📅 На завтра", callback_data="schedule:tomorrow")
        ],
        [
            InlineKeyboardButton(text="📆 На неделю", callback_data="schedule:week"),
        ],
        [
            InlineKeyboardButton(text="⚙️ Сменить данные", callback_data="settings:change_data")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
