from math import ceil

from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from service.core_api import api

start_keyboard = ReplyKeyboardMarkup()
start_keyboard.add(KeyboardButton("/rates"))
start_keyboard.add(KeyboardButton("/configure_currency_list"))


async def gen_currency_keyboard(user_id: int, page: int = 1) -> InlineKeyboardMarkup:
    page_size = 25
    add_currency_keyboard = InlineKeyboardMarkup(row_width=5)
    result = await api(f"/users/{user_id}/currency_statuses", page=page, size=page_size)
    items = result["items"]
    for item in items:
        code = item["code"]
        is_subscribed = item["is_subscribed"]
        button_text = f"✔{code}" if is_subscribed else f"✖{code}"
        add_currency_keyboard.insert(
            InlineKeyboardButton(
                button_text, callback_data=f"toggle {code} page {page}"
            )
        )

    is_next_page_exists = result["total"] > result["page"] * page_size
    next_page = page + 1 if is_next_page_exists else 1
    previous_page = page - 1 if page > 1 else ceil(result["total"] / page_size)
    add_currency_keyboard.row(
        InlineKeyboardButton("⬅Previous", callback_data=f"currency_kb {previous_page}"),
        InlineKeyboardButton("Next➡", callback_data=f"currency_kb {next_page}"),
    )
    return add_currency_keyboard
