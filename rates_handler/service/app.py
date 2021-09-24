import atexit

from fastapi import FastAPI

from service.postgres import connect, close
from service.rates import actual_rate, actual_rates


app = FastAPI()
connect()
atexit.register(close)


@app.get("/")
async def rates():
    return await actual_rates()


@app.get("/rate?first={currency1}&second={currency2}")
async def rate(currency1: str, currency2: str):
    return await actual_rate(currency1.upper(), currency2.upper())
