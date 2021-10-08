import aiohttp

from service.config import CORE_API_HOST, CORE_API_PORT, CORE_API_KEY


async def api(path: str = "", method: str = "GET", **vars):
    """
    Get rates data from another microservice.

    Args:
    path - url subdirectory
    vars - query variables

    Return:
    json api response without any changes
    """

    if path.startswith("/"):
        path = path[1:]
    method = method.upper()

    url = f"http://{CORE_API_HOST}:{CORE_API_PORT}/{path}"
    vars["api_key"] = CORE_API_KEY
    if len(vars) > 0:
        args = [f"{key}={vars[key]}" for key in vars]
        url += "?" + "&".join(args)

    async with aiohttp.ClientSession() as session:
        if method == "GET":
            session_method = session.get
        elif method == "OPTIONS":
            session_method = session.options
        elif method == "HEAD":
            session_method = session.head
        elif method == "POST":
            session_method = session.post
        elif method == "PUT":
            session_method = session.put
        elif method == "PATCH":
            session_method = session.patch
        elif method == "DELETE":
            session_method = session.delete
        else:
            raise ValueError(f"Unavailable method={method}")

        async with session_method(url) as response:
            return await response.json()
