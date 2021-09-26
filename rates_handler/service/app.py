import atexit

from fastapi import FastAPI, Response

from service.postgres import connect, close
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
    return await get_rates()


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
        return {"error": str(e)}
