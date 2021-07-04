from aiogram import Bot, Dispatcher, executor, types

from config import TOKEN
from rates import rates_list

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.answer('Start.')

@dp.message_handler(commands=['rates'])
async def get_rates(message: types.Message):
    #message.from_user.id
    rates = '\n'.join(str(rate) for rate in await rates_list())
    await message.answer(rates)

def start():
    executor.start_polling(dp, skip_updates=True)