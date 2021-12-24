from math import ceil

from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from service.core_api import api


RATES_BUTTON = "Rates"
CONFIGURE_SUBSCRIPTIONS_BUTTON = "Configure subscriptions"

start_keyboard = ReplyKeyboardMarkup()
start_keyboard.add(KeyboardButton(RATES_BUTTON))
start_keyboard.add(KeyboardButton(CONFIGURE_SUBSCRIPTIONS_BUTTON))


PAGE_SIZE = 25


async def add_page_control_buttons(
    keyboard: InlineKeyboardMarkup, page: int, page_size: int, total: int, callback: str
) -> None:
    """
    Add "Next" and "Previous" buttons to the keyboard.
    Adds " page {next/prev page num}" to the end of callback.
    """

    is_next_page_exists = total > page * page_size
    next_page = page + 1 if is_next_page_exists else 1
    previous_page = page - 1 if page > 1 else ceil(total / page_size)
    keyboard.row(
        InlineKeyboardButton(
            "⬅Previous", callback_data=callback + f" page {previous_page}"
        ),
        InlineKeyboardButton("Next➡", callback_data=callback + f" page {next_page}"),
    )


async def gen_first_currency_keyboard(page: int = 1) -> InlineKeyboardMarkup:
    """Generate keyboard for selecting first currency in "Configure subscriptions" option"""

    currency_keyboard = InlineKeyboardMarkup(row_width=5)
    result = await api("/tg/rates/USD", page=page, size=PAGE_SIZE)
    codes = map(lambda x: x["code1"], result["items"])
    for code in codes:
        button_text = f"💱{code}"
        currency_keyboard.insert(
            InlineKeyboardButton(button_text, callback_data=f"currency_first {code}")
        )

    total = result["total"]
    await add_page_control_buttons(
        currency_keyboard, page, PAGE_SIZE, total, "first_kb"
    )
    return currency_keyboard


async def gen_second_currency_keyboard(
    user_id: int, first_currency_code: str, page: int = 1
) -> InlineKeyboardMarkup:
    """Generate keyboard for selecting second currency in "Configure subscriptions" option"""

    currency_keyboard = InlineKeyboardMarkup(row_width=5)
    result = await api("/tg/rates/USD", page=page, size=PAGE_SIZE)
    codes = map(lambda x: x["code1"], result["items"])
    subscriptions = await api(f"/tg/users/{user_id}/subscriptions")
    subscriptions = filter(lambda s: s["code1"] == first_currency_code, subscriptions)
    already_subscribed = list(map(lambda s: s["code2"], subscriptions))
    for code in codes:
        if code in already_subscribed:
            button_text = f"✔{code}"
            callback = (
                f"currency_remove first {first_currency_code} second {code} page {page}"
            )
        else:
            button_text = f"✖{code}"
            callback = (
                f"currency_add first {first_currency_code} second {code} page {page}"
            )
        currency_keyboard.insert(
            InlineKeyboardButton(button_text, callback_data=callback)
        )

    total = result["total"]
    await add_page_control_buttons(
        currency_keyboard,
        page,
        PAGE_SIZE,
        total,
        f"second_kb first {first_currency_code}",
    )
    return currency_keyboard
