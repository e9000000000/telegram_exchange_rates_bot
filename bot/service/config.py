import os


# bot
TOKEN = os.getenv("TGRATESBOT_TOKEN")
if TOKEN is None:
    raise ValueError('Set up "TGRATESBOT_TOKEN" env variable to your bot token.')

# cache
REDIS_HOST = "redis"
REDIS_PORT = 6379
