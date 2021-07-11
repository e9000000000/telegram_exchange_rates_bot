# Telegram exchange rates bot
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## About bot
Bot to geting info about exchange rates of currency and cryptocurrency (last coming soon).
Written with `aiogram` and `aiohttp`. Used `redis` for caching.
And all of this placed into `docker` container.

## How to run
Install `docker-compose`.

Clone repository
```bash
git clone git@github.com:e9000000000/telegram_exchange_rates_bot.git
cd telegram_exchange_rates_bot
```
Set `TGRATEBOTTOKEN` env variable to  your [bot token](https://core.telegram.org/bots/api#authorizing-your-bot), then
```bash
docker-compose up
```