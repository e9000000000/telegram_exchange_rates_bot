from datetime import datetime

from service import postgres


async def get_rates(
    datetime_from: datetime = None,
    datetime_to: datetime = None,
    currency_codes: list[str] = [],
) -> dict[str:float]:
    """
    Return exchange rates of currencies to USD.

    Args:

    `datetime_from` - start of a time period to get rates (included)

    `datetime_to` - end of a time period to get rates (included)

    `currency_codes` - list of currency codes, something like `["USD", "EUR"]`
    if it's empty list function'll return rates for all currencies

    Return:

    dict like:
    ```
        {
            'USD': 1.0,
            'RUB': 2332.3223,
        }
    ```
    """

    result = await postgres.get_rates(datetime_from, datetime_to, currency_codes)
    if len(result) != 1:
        raise ValueError(
            f"invalid data from database. codes={currency_codes} finded={result}"
        )

    return list(result.values())[0]


async def actual_rate(currency1: str, currency2: str) -> float:
    """
    Return exchange rate of one currency to another or raise exception if args are invalid.

    Args:

    both - a currency codes like `USD` or `RUB`.

    Return:

    rate between currencies like
    1 `currency1` = 23.332 `currency2`
    """

    result = await get_rates(currency_codes=[currency1, currency2])
    if len(result) != 1:
        raise ValueError(
            f"invalid data from database. code1={currency1} code2={currency2} finded={result}"
        )

    rates = list(result.values())[0]
    if currency1 not in rates or currency2 not in rates:
        raise ValueError(
            f"cant find currency codes in database. code1={currency1} code2={currency2} finded={rates}"
        )

    return rates[currency2] / rates[currency1]
