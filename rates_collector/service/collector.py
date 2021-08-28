from asyncio import sleep

from service.config import UPDATE_DELAY
from service.utils import import_modules_from_dir
from service.postgres import connect, close, add_rates


async def all_rates() -> dict[str:float]:
    """
    Return exchange rates of all currencie to USD.
    Info about rates gets from the internet, so you should have internet connection.
    Cacheing for one hour.

    Return:
    dict like:
        {
            'USD': 1.0,
            'RUB': 2332.3223,
        }
    """

    result = {}
    for module in import_modules_from_dir("service/rates_lists"):
        result.update(await module.rates())

    return result


async def run_forever():
    """Run service forever."""

    await connect()
    while 1:
        await add_rates(await all_rates())
        await sleep(UPDATE_DELAY)
    await close()
