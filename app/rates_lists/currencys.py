"""Info about exchange rates of state currencys like USD or RUB, or EUR"""


import aiohttp


REQUEST_URL = "http://www.floatrates.com/daily/usd.json"


async def rates() -> dict[str:float]:
    async with aiohttp.ClientSession() as session:
        async with session.get(REQUEST_URL) as response:
            data = await response.json()
            result = {data[k]["code"].upper(): data[k]["rate"] for k in data}
            result.update({"USD": 1.0})
            return result
