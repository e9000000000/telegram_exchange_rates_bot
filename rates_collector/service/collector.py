import psycopg2

from service.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


connection = psycopg2.connect(
    host=DB_HOST, port=DB_PORT, database="test", user=DB_USER, password=DB_PASSWORD
)


def run():
    cur = connection.cursor()
    cur.execute("SELECT version()")
    version = cur.fetchone()
    print(version)
