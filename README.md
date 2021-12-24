# Telegram exchange rates bot
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

![screenshot](https://raw.githubusercontent.com/e9000000000/telegram_exchange_rates_bot/development/docs/screenshot.png)

## About bot
Bot for geting info about exchange currencies rates.
Microservice architecture: `rates_collector` service for geting info about rates and save it to database.
`core` for retrieve data from database and send it via http protocol to another services in json format.
`bot` is a layer between `core` and telegram

Written with `fastapi` and `aiogram`. For database used `postgresql`

## How to run
Install `docker-compose`.

Clone repository
```bash
git clone git@github.com:e9000000000/telegram_exchange_rates_bot.git
```

Setup env variables:
* `TGRATEBOT_TOKEN` - [telegram bot token](https://core.telegram.org/bots/api#authorizing-your-bot)
* `TGRATESBOT_API_KEY` - any secret sequence of numbers and letters
* `POSTGRES_USER` - postgres username
* `POSTGRES_PASSWORD` - postgres password

Optional env variables:
* `TGRATESBOT_DB_HOST` - postgres host
* `TGRATESBOT_DB_PORT` - postgres port
* `TGRATESBOT_DB_NAME` - postgres database name


and run inside repository
```bash
docker-compose up --build
```

maybe you sould create database with name `ratesbot` if it doesn't create automatically
