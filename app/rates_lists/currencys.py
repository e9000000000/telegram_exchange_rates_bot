import aiohttp


REQUEST_URL = 'http://www.floatrates.com/daily/usd.json'


async def rates_list():
    async with aiohttp.ClientSession() as session:
        async with session.get(REQUEST_URL) as response:
            data = await response.json()
            return [{data[k]['code']: data[k]['rate']} for k in data] + [{'USD': 1.0}]
