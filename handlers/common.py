from aiogram import Router, types
from aiogram.filters import Command
from utils.texts import BotMessages

router = Router()

@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(BotMessages.GREETING)