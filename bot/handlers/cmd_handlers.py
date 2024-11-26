from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

cmd_router = Router()


@cmd_router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Добро пожаловать в бот!')


@cmd_router.message(Command(commands=['help']))
async def cmd_help(message: Message):
    await message.answer('Помощь по боту')
