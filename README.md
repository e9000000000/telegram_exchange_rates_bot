# Telegram exchange rates bot
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## About bot
Bot to geting info about exchange rates of currency and cryptocurrency.
Written with `aiogram` and `aiohttp`. Used `redis` for caching.

## How to run
```bash
git clone git@github.com:e9000000000/telegram_exchange_rates_bot.git
docker run --net=host redis
pip install -r telegram_exchange_rates_bot/requirements.txt
python telegram_exchange_rates_bot
```