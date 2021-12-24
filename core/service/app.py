import atexit
import functools

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyQuery, APIKey
from fastapi_pagination import Page, add_pagination, paginate

from service.config import API_KEY, API_KEY_NAME
from service.postgres import (
    connect,
    close,
    get_user_subscriptions,
    turn_subscription_on,
    turn_subscription_off,
    get_rates_to_currency,
)
from service.models import Rate


api_key_query = APIKeyQuery(name=API_KEY_NAME)
app = FastAPI(
    title="rates",
    version="1",
)
connect()
atexit.register(close)


async def get_api_key(api_key_query: str = Security(api_key_query)):
    if api_key_query == API_KEY:
        return api_key_query
    raise HTTPException(403, "Invalid api_key")


def error_handler(func):
    @functools.wraps(func)
    async def wrapped(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ValueError as e:
            print(f"[WARNING] {e}")
            raise HTTPException(status_code=422, detail=str(e))
        except Exception as e:
            print(f"[ERROR] {e}")
            raise HTTPException(status_code=500, detail="server error")

    return wrapped


@app.get(
    "/tg/users/{tg_user_id}/subscriptions",
    status_code=200,
    response_model=list[Rate],
    description="Get rates user subscribed at.",
)
@error_handler
async def get_user_subscribed_rates(
    tg_user_id: int,
    api_key: APIKey = Depends(get_api_key),
):
    return await get_user_subscriptions(tg_user_id)


@app.post(
    "/tg/users/{tg_user_id}/subscriptions/{code1}/{code2}",
    status_code=200,
    description="Turn user subscription on.",
)
@error_handler
async def turn_on_subscription(
    tg_user_id: int, code1: str, code2: str, api_key: APIKey = Depends(get_api_key)
):
    await turn_subscription_on(tg_user_id, code1, code2)
    return {"succsess": 1}


@app.delete(
    "/tg/users/{tg_user_id}/subscriptions/{code1}/{code2}",
    status_code=200,
    description="Turn user subscription off.",
)
@error_handler
async def turn_off_subscription(
    tg_user_id: int, code1: str, code2: str, api_key: APIKey = Depends(get_api_key)
):
    await turn_subscription_off(tg_user_id, code1, code2)
    return {"succsess": 1}


@app.get(
    "/tg/rates/{code}",
    status_code=200,
    response_model=Page[Rate],
    description="Get all rates to one currency.",
)
@error_handler
async def toggle_currency(code: str, api_key: APIKey = Depends(get_api_key)):
    rates = await get_rates_to_currency(code)
    rates.sort(key=lambda x: x["code1"])
    return paginate(list(map(lambda x: Rate(**x), rates)))


add_pagination(app)
