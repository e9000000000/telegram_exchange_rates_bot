import os


DB_HOST = os.getenv("TGRATESBOT_DB_HOST", "localhost")
DB_PORT = os.getenv("TGRATESBOT_DB_PORT", "5432")
DB_NAME = os.getenv("TGRATESBOT_DB_NAME", "ratesbot")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# your timezone, should be like "UTC-3" or "UTC" or "UTC+5"
TIMEZONE = "UTC-3"

# time delay between updating rates (in seconds)
UPDATE_DELAY = 60 * 60
