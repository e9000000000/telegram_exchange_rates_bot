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


def print(*args, **kwargs):
    """without it can't see output in docker-compose"""

    if "flush" in kwargs:
        kwargs.pop("flush")
    __builtins__["print"](*args, **kwargs, flush=True)


@dp.message_handler(commands=["start"])
async def start(message: Message):
    """Show keyboard with commands"""

    username = message.from_user.username

    print(f"[INFO] start {username=}")
    await message.answer("hi", reply_markup=start_keyboard)


@dp.message_handler(lambda message: message.text and RATES_BUTTON in message.text)
async def get_rates(message: Message):
    """Send all exchange rates to USD."""

    username = message.from_user.username

    rates = await api(f"/tg/users/{message.from_user.id}/subscriptions")
    if rates:
        answer = "\n".join(
            f"1 {rate['code1']} = {rate['rate']} {rate['code2']}" for rate in rates
        )
    else:
        answer = "You have no subscriptions."
        print(f"[INFO] have no subscribed rates {username=}")
    print(f"[INFO] request rates {username=}")
    await message.answer(answer)


@dp.message_handler(
    lambda message: message.text and CONFIGURE_SUBSCRIPTIONS_BUTTON in message.text
)
async def configure_currency_list(message: Message):
    """Show inline keyboard with subscription list configuration"""

    username = message.from_user.username

    await message.answer(
        "Select first currency",
        reply_markup=await gen_first_currency_keyboard(),
    )
    print(f"[INFO] configuration currency list {username=}")


@dp.callback_query_handler(lambda c: re.match(r"^currency_first \w+$", c.data))
async def first_kb_currency_selected(query: CallbackQuery):
    """First currency selected"""

    username = query.from_user.username
    selected_code = query.data.split()[-1]

    await bot.edit_message_text(
        f"Select second currency, first was {selected_code}",
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_second_currency_keyboard(
            query.from_user.id, selected_code
        ),
    )
    print(f"[INFO] first currency selected {selected_code=} {username=}")


@dp.callback_query_handler(
    lambda c: re.match(r"^currency_add first \w+ second \w+ page \d+$", c.data)
)
async def add_kb(query: CallbackQuery):
    """Remove rate from user subscriptions"""

    username = query.from_user.username
    args = query.data.split()
    code1 = args[2]
    code2 = args[4]
    page = int(args[-1])

    await api(f"/tg/users/{query.from_user.id}/subscriptions/{code1}/{code2}", "POST")

    await bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_second_currency_keyboard(
            query.from_user.id, code1, page
        ),
    )
    print(f"[INFO] add subscription {code1=} {code2=} {username=}")


@dp.callback_query_handler(
    lambda c: re.match(r"^currency_remove first \w+ second \w+ page \d+$", c.data)
)
async def remove_kb(query: CallbackQuery):
    """Add rate to user subscriptions"""

    username = query.from_user.username
    args = query.data.split()
    code1 = args[2]
    code2 = args[4]
    page = int(args[-1])

    await api(
        f"/tg/users/{query.from_user.id}/subscriptions/{code1}/{code2}",
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
    print(f"[INFO] remove subscription {code1=} {code2=} {username=}")


@dp.callback_query_handler(lambda c: re.match(r"^first_kb page \d+$", c.data))
async def first_kb_change_page(query: CallbackQuery):
    """Change page in first currency keyboard"""

    username = query.from_user.username
    page = int(query.data.split()[-1])

    await bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_first_currency_keyboard(page),
    )
    print(f"[INFO] first keyboard change page {page=} {username=}")


@dp.callback_query_handler(
    lambda c: re.match(r"^second_kb first \w+ page \d+$", c.data)
)
async def second_kb_change_page(query: CallbackQuery):
    """Change page in second currency keyboard"""

    username = query.from_user.username
    page = int(query.data.split()[-1])
    first_code = query.data.split()[2]

    await bot.edit_message_reply_markup(
        query.message.chat.id,
        query.message.message_id,
        query.inline_message_id,
        reply_markup=await gen_second_currency_keyboard(
            query.from_user.id, first_code, page
        ),
    )
    print(f"[INFO] second keyboard change page {page=}, {first_code=} {username=}")


def run():
    """Start a loop or something idk where it handles users messages."""

    print("[INFO] bot started")
    executor.start_polling(dp, skip_updates=False)
