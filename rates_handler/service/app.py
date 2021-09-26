import atexit

from fastapi import FastAPI, Response

from service.postgres import connect, close, toggle_user_everyday_notification
from service.rates import actual_rate, get_rates


app = FastAPI(
    title="rates",
    version="1",
)
connect()
atexit.register(close)


@app.get(
    "/actual_rates",
    status_code=200,
    description="Return latest exchange rates of currencies to USD.",
)
async def actual_rates():
    rates = await get_rates()
    return {"rates": rates}


@app.get(
    "/rate",
    status_code=200,
    description="Return latest exchange rate of one currency to another",
)
async def rate(currency1: str, currency2: str, response: Response):
    try:
        rate = await actual_rate(currency1.upper(), currency2.upper())
        return {"rate": rate}
    except ValueError as e:
        response.status_code = 422
        return {"datail": str(e)}


@app.patch(
    "/users/{user_id}/toggle_everyday_notifications",
    status_code=200,
    description="Toggle should user receive rates everyday or not.",
)
async def toggle_receive_rates(user_id: int, response: Response):
    try:
        is_user_notified = await toggle_user_everyday_notification(user_id)
        return {"is_user_notified": is_user_notified}
    except Exception as e:
        response.status_code = 500
        return {"detail": str(e)}
