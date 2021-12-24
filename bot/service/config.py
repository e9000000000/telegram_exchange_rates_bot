import os


# bot
TOKEN = os.getenv("TGRATESBOT_TOKEN", "")
if TOKEN is None:
    raise ValueError('Set up "TGRATESBOT_TOKEN" env variable to your bot token.')

# core api
CORE_API_HOST = "core"
CORE_API_PORT = "8000"
CORE_API_KEY = os.getenv("TGRATESBOT_API_KEY")
