import os


# bot
TOKEN = os.getenv("TGRATEBOTTOKEN")
if TOKEN is None:
    raise ValueError('Set up "TGRATEBOTTOKEN" env variable to your bot token.')

# cache
REDIS_HOST = "redis"
REDIS_PORT = 6379
