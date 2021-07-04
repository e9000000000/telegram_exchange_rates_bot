from aiogram import Bot, Dispatcher, executor, types
import aiohttp

from config import TOKEN

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.answer('Start.')

@dp.message_handler(commands=['ping'])
async def ping(message: types.Message):
    await message.answer('pong')

executor.start_polling(dp, skip_updates=True)