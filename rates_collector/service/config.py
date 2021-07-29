import os


DB_HOST = os.getenv("TGRATESBOT_DB_HOST", "localhost")
DB_PORT = os.getenv("TGRATESBOT_DB_PORT", "5432")
DB_NAME = os.getenv("TGRATESBOT_DB_NAME", "ratesbot")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
