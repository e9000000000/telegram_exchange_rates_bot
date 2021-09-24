import os


# bot
TOKEN = os.getenv("TGRATESBOT_TOKEN")
if TOKEN is None:
    raise ValueError('Set up "TGRATESBOT_TOKEN" env variable to your bot token.')

# rates data
RATES_HOST = "rates_handler"
RATES_PORT = "8000"
