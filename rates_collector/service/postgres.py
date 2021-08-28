import psycopg2

from service.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER, TIMEZONE


connection = None
cursor = None


async def connect() -> None:
    """Connect to database and prepare it for using."""

    global connection, cursor

    connection = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cursor = connection.cursor()

    await set_timezone()
    await create_missing_tables()
    await commit_changes()


async def close() -> None:
    """Close connection to database."""

    global cursor

    cursor.close()


async def set_timezone() -> None:
    """Set database timezone to `TIMEZONE` variable from `config.py`."""

    global cursor

    cursor.execute(f"SET TIME ZONE '{TIMEZONE}'")


async def create_missing_tables() -> None:
    """Create missing tables `receiving_datetimes` and `rates` if they does not exist."""

    global cursor

    cursor.execute("SELECT * FROM pg_catalog.pg_tables WHERE schemaname='public'")
    tables = cursor.fetchall()
    table_names = [table[1] for table in tables]

    if "receiving_datetimes" not in table_names:
        cursor.execute(
            "CREATE TABLE receiving_datetimes (\
                id INT GENERATED ALWAYS AS IDENTITY,\
                datetime TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP\
            )"
        )
        cursor.execute("ALTER TABLE receiving_datetimes ADD PRIMARY KEY (id)")
        cursor.execute(
            "CREATE INDEX receiving_datetime_datetime ON receiving_datetimes USING btree (datetime)"
        )

    if "rates" not in table_names:
        cursor.execute(
            "CREATE TABLE rates (\
                id INT GENERATED ALWAYS AS IDENTITY,\
                received_datetime_id INT,\
                code VARCHAR(10),\
                rate FLOAT,\
                FOREIGN KEY(received_datetime_id) REFERENCES receiving_datetimes(id) ON DELETE CASCADE\
            )"
        )
        cursor.execute("ALTER TABLE rates ADD PRIMARY KEY (id)")
        cursor.execute("CREATE INDEX rates_code ON rates USING hash (rate);")


async def commit_changes() -> None:
    """Commit changes to database."""

    global cursor

    cursor.execute("COMMIT")


async def add_rates(rates: dict[str:float], is_commit: bool = False) -> None:
    """
    Put all rates to database to `rates` table, connect them with datetime when function was called.

    Args:
        rates - list of rates to `USD`, example: `{'USD': 1, 'RUB': 111.12}`.
        is_commit - commit changes to database or not.
    """

    global cursor

    cursor.execute("INSERT INTO receiving_datetimes VALUES (DEFAULT)")
    cursor.execute("SELECT id FROM receiving_datetimes ORDER BY datetime DESC LIMIT 1")

    received_datetime_id = cursor.fetchone()[0]

    value_template = "(%s, %s, %s)"
    values_template = ", ".join([value_template for _ in rates])
    values = []
    for code in rates:
        values += [received_datetime_id, code, rates[code]]

    command = (
        "INSERT INTO rates(received_datetime_id, code, rate) VALUES " + values_template
    )
    cursor.execute(command, values)

    if is_commit:
        await commit_changes()
