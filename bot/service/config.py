import os


# bot
TOKEN = os.getenv("TBRATESBOT_TOKEN")
if TOKEN is None:
    raise ValueError('Set up "TBRATESBOT_TOKEN" env variable to your bot token.')

# cache
REDIS_HOST = "redis"
REDIS_PORT = 6379
