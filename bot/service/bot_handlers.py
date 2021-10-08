import re

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery

from service.config import TOKEN
from service.core_api import api
from service.bot_keyboards import start_keyboard, gen_currency_keyboard

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: Message):
    """Show keyboard with commands"""

    await message.answer("hi", reply_markup=start_keyboard)


@dp.message_handler(commands=["configure_currency_list"])
async def configure_currency_list(message: Message):
    """Show inline keyboard with subscription list configuration"""

    await message.answer(
        "currencies",
        reply_markup=await gen_currency_keyboard(message.from_user.id),
    )


@dp.message_handler(commands=["rates"])
async def get_rates(message: Message):
    """Send all exchange rates to USD."""

    rates = await api(f"/users/{message.from_user.id}/subscriptions")
    answer = "\n".join(f"{rate['code']} - {rate['rate']}" for rate in rates)
    await message.answer(answer)


@dp.callback_query_handler(lambda c: re.match(r"^toggle \w+ page \d+$", c.data))
async def toggle_currency_button(query: CallbackQuery):
    """Add/remove currency from user subscriptions"""

    args = query.data.split()
    code = args[1]
    page = int(args[3])
    await api(f"users/{query.from_user.id}/subscriptions/{code}", method="PATCH")

    await bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_currency_keyboard(query.from_user.id, page),
    )


@dp.callback_query_handler(lambda c: re.match(r"^currency_kb \d+$", c.data))
async def change_currency_kb(query: CallbackQuery):
    """Change page in currency toggle keyboard"""

    page = int(query.data.split()[-1])
    await bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_currency_keyboard(query.from_user.id, page),
    )


def run():
    """Start a loop or something idk where it handles users messages."""

    executor.start_polling(dp, skip_updates=False)
