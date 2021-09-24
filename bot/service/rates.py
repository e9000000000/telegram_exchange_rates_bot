import aiohttp

from service.config import RATES_HOST, RATES_PORT


async def api(path: str = "", **vars):
    """
    Get rates data from another microservice.

    Args:
    path - url subdirectory
    vars - query variables

    Return:
    json api response without any changes
    """

    url = f"http://{RATES_HOST}:{RATES_PORT}/{path}"
    if len(vars) > 0:
        args = [f"{key}={vars[key]}" for key in vars]
        url += "?" + "&".join(args)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()
