from aiogram import Bot, Dispatcher, executor, types

from config import TOKEN
from rates import rates_dict, rate

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.answer('Start.')

@dp.message_handler(commands=['rates'])
async def get_rates(message: types.Message):
    #message.from_user.id
    rates = '\n'.join(str(rate) for rate in await rates_dict())
    await message.answer(rates)

@dp.message_handler()
async def get_rate(message: types.Message):
    try:
        what, to_what = message.text.upper().split()
    except Exception as e:
        await message.answer('/help to get help.')
    try:
        result = await rate(what, to_what)
    except ValueError as e:
        await message.answer(str(e))
    await message.answer(f'{1} {what} = {result} {to_what}')

def start():
    executor.start_polling(dp, skip_updates=True)