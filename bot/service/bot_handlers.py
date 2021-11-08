import re

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, CallbackQuery

from service.config import TOKEN
from service.core_api import api
from service.bot_keyboards import (
    start_keyboard,
    gen_first_currency_keyboard,
    gen_second_currency_keyboard,
    RATES_BUTTON,
    CONFIGURE_SUBSCRIPTIONS_BUTTON,
)

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start"])
async def start(message: Message):
    """Show keyboard with commands"""

    await message.answer("hi", reply_markup=start_keyboard)


@dp.message_handler(lambda message: message.text and RATES_BUTTON in message.text)
async def get_rates(message: Message):
    """Send all exchange rates to USD."""

    rates = await api(f"/tg/users/{message.from_user.id}/subscriptions")
    answer = "\n".join(
        f"1 {rate['code1']} = {rate['rate']} {rate['code2']}" for rate in rates
    )
    await message.answer(answer)


@dp.message_handler(
    lambda message: message.text and CONFIGURE_SUBSCRIPTIONS_BUTTON in message.text
)
async def configure_currency_list(message: Message):
    """Show inline keyboard with subscription list configuration"""

    await message.answer(
        "Select first currency",
        reply_markup=await gen_first_currency_keyboard(),
    )


@dp.callback_query_handler(lambda c: re.match(r"^currency_first \w+$", c.data))
async def first_kb_currency_selected(query: CallbackQuery):
    """First currency selected"""

    selected_code = query.data.split()[-1]

    await bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_second_currency_keyboard(
            query.from_user.id, selected_code
        ),
    )
    await bot.edit_message_text(
        f"Select second currency, first was {selected_code}",
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
    )


@dp.callback_query_handler(
    lambda c: re.match(r"^currency_add first \w+ second \w+ page \d+$", c.data)
)
async def add_kb(query: CallbackQuery):
    """Remove rate from user subscriptions"""

    args = query.data.split()
    code1 = args[2]
    code2 = args[4]
    page = int(args[-1])

    await api(
        f"/tg/users/{query.message.from_user.id}/subscriptions/{code1}/{code2}", "POST"
    )

    await bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_second_currency_keyboard(
            query.from_user.id, code1, page
        ),
    )


@dp.callback_query_handler(
    lambda c: re.match(r"^currency_remove first \w+ second \w+ page \d+$", c.data)
)
async def remove_kb(query: CallbackQuery):
    """Add rate to user subscriptions"""

    args = query.data.split()
    code1 = args[2]
    code2 = args[4]
    page = int(args[-1])

    await api(
        f"/tg/users/{query.message.from_user.id}/subscriptions/{code1}/{code2}",
        "DELETE",
    )

    await bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_second_currency_keyboard(
            query.from_user.id, code1, page
        ),
    )


@dp.callback_query_handler(lambda c: re.match(r"^first_kb page \d+$", c.data))
async def first_kb_change_page(query: CallbackQuery):
    """Change page in first currency keyboard"""

    page = int(query.data.split()[-1])
    await bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_first_currency_keyboard(page),
    )


@dp.callback_query_handler(
    lambda c: re.match(r"^second_kb first \w+ page \d+$", c.data)
)
async def second_kb_change_page(query: CallbackQuery):
    """Change page in second currency keyboard"""

    page = int(query.data.split()[-1])
    first_code = query.data.split()[2]
    await bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_second_currency_keyboard(
            query.message.from_user.id, first_code, page
        ),
    )


def run():
    """Start a loop or something idk where it handles users messages."""

    executor.start_polling(dp, skip_updates=False)
