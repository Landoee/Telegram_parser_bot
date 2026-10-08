from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from .base import router as base_router
from .schedule import router as schedule_router
from .onbording import router as onbord_router


"""Создаем main_router"""
router = Router()

""" Здесь подключаем все хендлеры"""
router.include_routers(base_router)
router.include_routers(schedule_router, onbord_router)
