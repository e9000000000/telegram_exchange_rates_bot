from aiocache import cached
import importlib
from os import listdir
from os.path import dirname, basename

import rates_lists


@cached(60*60)
async def rates_dict() -> dict[str: float]:
    '''
    Return exchange rates of all currencys to USD. 
    Info about rates gets from the internet, so you should have internet connection. 
    Cacheing for one hour. 

    Return:
        dict like:
        {
            'USD': 1.0,
            'RUB': 2332.3223,
        }
    '''

    result = {}
    rates_lists_dir = dirname(rates_lists.__file__)
    module_files = listdir(rates_lists_dir)
    for module_file in module_files:
        if not module_file.endswith('.py') or module_file.endswith('__init__.py'):
            continue

        module = importlib.import_module(basename(rates_lists_dir) + '.' + module_file[:-3])
        result.update(await module.rates())

    return result

async def rate(what: str, to_what: str) -> float:
    '''
    Return exchange rate of one currency to another or raise exception if args are invalid.

    Args:
        a currency codes like `USD`, `RUB`.

    Return:
        rate between currencys like
        1 `what` = 23.332 `to_what`
    '''

    rates = await rates_dict()
    for currency in (what, to_what):
        if currency not in rates:
            raise ValueError(f'Can\'t find exchange rate of "{currency}".')

    return rates[to_what] / rates[what]