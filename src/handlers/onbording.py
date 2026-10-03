from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from loguru import logger

router = Router() 

@router.message("/register")
async def onboard(message:Message):
    """ловим данные юзера"""
    tg_id = message.from_user.id
    username = message.from_user.username
    
    ...