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
    return result


async def rate(what: str, to_what: str) -> float:
    """
    Return exchange rate of one currency to another or raise exception if args are invalid.

    Args:
    both - a currency codes like `USD`, `RUB`.

    Return:
    rate between currencys like
    1 `what` = 23.332 `to_what`
    """

    rates = await all_rates()
    for currency in (what, to_what):
        if currency not in rates:
            raise ValueError(f'Can\'t find exchange rate of "{currency}".')

    return rates[to_what] / rates[what]
