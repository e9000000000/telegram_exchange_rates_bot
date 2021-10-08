import atexit

from fastapi import FastAPI, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyQuery, APIKey
from fastapi_pagination import Page, add_pagination, paginate

from service.config import API_KEY, API_KEY_NAME
from service.postgres import (
    connect,
    close,
    toggle_user_everyday_notification,
    get_user_subscriptions,
    get_notifiable_users_subscriptions,
    toggle_currency_in_subscriptions,
    get_user_currency_statuses,
)
from service.models import Rate, CurrencyStatus


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


@app.get(
    "/users/{user_id}/currency_statuses",
    status_code=200,
    response_model=Page[CurrencyStatus],
    description="Return currency statuses (user subscribed or not).",
)
async def user_currensy_statuses(
    user_id: int,
    api_key: APIKey = Depends(get_api_key),
):
    codes = await get_user_currency_statuses(user_id)
    statuses = [CurrencyStatus(code=code, is_subscribed=codes[code]) for code in codes]
    return paginate(statuses)


@app.get(
    "/users/notifiable/subscriptions",
    status_code=200,
    description="Return users with everyday notifications turned on and currencies they subscribed at.",
)
async def users_subscriptions(api_key: APIKey = Depends(get_api_key)):
    return {"users": await get_notifiable_users_subscriptions()}


@app.get(
    "/users/{user_id}/subscriptions",
    status_code=200,
    response_model=list[Rate],
    description="Return currency codes and rates user subcribed at.",
)
async def user_subscriptions(user_id: int, api_key: APIKey = Depends(get_api_key)):
    rates = await get_user_subscriptions(user_id)
    return [Rate(rate=rates[code], code=code) for code in rates]


@app.patch(
    "/users/{user_id}/subscriptions/{code}",
    status_code=200,
    response_model=dict,
    description="Add/remove currency to/from user subscribes list",
)
async def toggle_currency(
    user_id: int, code: str, api_key: APIKey = Depends(get_api_key)
):
    await toggle_currency_in_subscriptions(user_id, code)
    return {}


@app.patch(
    "/users/{user_id}/toggle_everyday_notifications",
    status_code=200,
    response_model=dict,
    description="Toggle should user receive rates everyday or not.",
)
async def toggle_receive_rates(user_id: int, api_key: APIKey = Depends(get_api_key)):
    await toggle_user_everyday_notification(user_id)
    return {}


add_pagination(app)
