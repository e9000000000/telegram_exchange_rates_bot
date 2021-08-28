from aiogram import Bot, Dispatcher, executor, types

from service.config import TOKEN
from service.rates import all_rates, rate


HELP_MESSAGE = """
Bot to get exchange rates.

/start - show this message
/rates - get all awailable rates
CODE1 CODE2 - get rate CODE1 to CODE2 where CODE1 and CODE2 are currency codes like EUR or USD
"""

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=["start", "help"])
async def start(message: types.Message):
    """Start and help message about "how to use this bot"."""

    await message.answer(HELP_MESSAGE)


@dp.message_handler(commands=["rates"])
async def get_rates(message: types.Message):
    """Send all exchange rates to USD."""

    rates = await all_rates()
    answer = "\n".join(f"{code} - {rates[code]}" for code in await all_rates())
    await message.answer(answer)


@dp.message_handler()
async def get_rate(message: types.Message):
    """
    Send a exchange rate of one currency to another.
    If currency codes is invalid send error.

    Examples:
    ```
        User: RUB USD
        Bot: 2433.32234

        User: FEIIFEEWF FEIWIF
        Bot: "FEIIFEEWF" is wrong code.

        User: few fwef wef wef
        Bot: write "/help"
    ```
    """

    codes = message.text.upper().split()
    if len(codes) != 2:
        await message.answer("/help to get help.")
        return

    what, to_what = codes[0], codes[1]
    try:
        result = await rate(what, to_what)
    except ValueError as e:
        await message.answer(str(e))
        return
    await message.answer(f"{1} {what} = {result} {to_what}")


def run():
    """Start a loop or something idk where it handles bot messages."""

    executor.start_polling(dp, skip_updates=True)
