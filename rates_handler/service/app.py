from datetime import datetime

from fastapi import FastAPI

from service.postgres import get_rates

app = FastAPI()


@app.get("/")
async def root():
    return await get_rates(
        datetime.fromtimestamp(0), datetime.now(), ["RUB", "usd", "Eur"]
    )
