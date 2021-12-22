from datetime import datetime

import psycopg2
from psycopg2._psycopg import connection as Connection
from psycopg2._psycopg import cursor as Cursor

from service.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


connection: Connection | None = None
cursor: Cursor | None = None


def connect() -> None:
    """Connect to database and prepare it for using."""

    global connection, cursor

    connection = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cursor = connection.cursor()

    create_missing_tables()
    commit_changes()


def create_missing_tables() -> None:
    """Create `users` and `users_subscriptions` table if it's missing"""

    if not cursor: raise ValueError("not connected to database")

    cursor.execute("SELECT * FROM pg_catalog.pg_tables WHERE schemaname='public'")
    tables = cursor.fetchall()
    table_names = [table[1] for table in tables]

    if "users" not in table_names:
        cursor.execute(
            "CREATE TABLE users (\
                id SERIAL PRIMARY KEY,\
                tg_id BIGINT\
            )"
        )
        cursor.execute("CREATE INDEX users_tg_id ON users USING hash (tg_id)")

    if "users_subscriptions" not in table_names:
        cursor.execute(
            "CREATE TABLE users_subscriptions (\
                user_id INT,\
                code1 VARCHAR(10),\
                code2 VARCHAR(10),\
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE\
            )"
        )
        cursor.execute(
            "CREATE INDEX users_subscriptions_user_id ON users_subscriptions USING hash (user_id);"
        )

    commit_changes()


def close() -> None:
    """Close connection to database."""

    if not cursor: raise ValueError("not connected to database")
    cursor.close()


def commit_changes() -> None:
    """Commit changes to database."""

    if not cursor: raise ValueError("not connected to database")
    cursor.execute("COMMIT")


async def get_rates(
    datetime_from: datetime = None,
    datetime_to: datetime = None,
    currency_codes: list = [],
) -> dict[datetime, dict[str, float]]:
    """
    Get info about currencys rates from database. (currency to usd)
    With default args returns newest rates of all currencys.

    Args:

    `datatime_from` - lower bound of time period to get rates (included).
    if it's `None`, then lower bound will be absent.

    `datatime_to` - higher bound of time period to get rates (included).
    if it's `None`, then higher bound will be absent.

    `currency_codes` - currency codes (looks like `USD` or `EUR`) which you want to get info about.
    If it's empty list, then rates of all currencys from database will be returned.

    Return:
        {
            "iso formated datetime 1": {
                "currency code 1": rate 1,
                "currency code 2": rate 2,
            },
            "iso formated datetime 2": ...
        }
    """

    if not cursor: raise ValueError("not connected to database")

    sql = """
        SELECT
            datetimes.datetime,
            rates.code,
            rates.rate
        FROM
            receiving_datetimes AS datetimes
        INNER JOIN
            rates
        ON
            rates.received_datetime_id = datetimes.id
        """

    sql_vars = []
    sql_conditions = []

    if datetime_from is None and datetime_to is None:
        sql += """
            AND
                rates.received_datetime_id = (
                    SELECT
                        d.id
                    FROM
                        receiving_datetimes AS d
                    ORDER BY
                        d.datetime DESC
                    LIMIT 1
                )
            """
    else:
        if datetime_to is not None:
            sql_vars.append(datetime_to.isoformat())
            sql_conditions.append("datetimes.datetime <= %s")

        if datetime_from is not None:
            sql_vars.append(datetime_from.isoformat())
            sql_conditions.append("datetimes.datetime >= %s")

    if len(currency_codes) > 0:
        sql_vars += list(map(str.upper, currency_codes))
        codes_sql = ", ".join("%s" for _ in currency_codes)
        sql_conditions.append(f"rates.code IN ({codes_sql})")

    if len(sql_conditions) > 0:
        conditions = """
            AND
            """.join(
            sql_conditions
        )
        sql += f"""
            WHERE
                {conditions}
            """

    cursor.execute(sql, sql_vars)
    data = cursor.fetchall()

    result = {}
    for datetime_, code, rate in data:
        if datetime_ not in result:
            result[datetime_] = {}
        result[datetime_][code] = rate

    return result


async def get_or_create_user_id_by_tg_id(tg_id: int) -> int:
    """
    Return user `id` from `users` table
    Create user if there is no user with this tg_id in database.

    Args:

    tg_id - telegram user id

    Return:

    user id
    """

    if not cursor: raise ValueError("not connected to database")

    for _ in range(2):
        cursor.execute("SELECT id FROM users WHERE tg_id=%s", (tg_id,))
        result = cursor.fetchall()
        if result:
            return result[0][0]
        cursor.execute("INSERT INTO users (tg_id) VALUES (%s)", (tg_id,))
        commit_changes()
    raise psycopg2.DatabaseError("can't get or create user for unknown reasons")


async def get_user_subscriptions(tg_id: int) -> list[dict[str, str | float]]:
    """
    Get currency codes and rates user subscribed at.

    Args:

    tg_id - telegram user id

    Return:

    list of dicts with two currency codes and rate
    """

    if not cursor: raise ValueError("not connected to database")

    user_id = await get_or_create_user_id_by_tg_id(tg_id)

    cursor.execute(
        "SELECT code1, code2 FROM users_subscriptions WHERE user_id = %s ORDER BY code1, code2",
        (user_id,),
    )
    codes = cursor.fetchall()

    all_datetimes = list((await get_rates()).values())
    if len(all_datetimes) < 1: raise ValueError("have no rates")
    all_rates = all_datetimes[0]

    result = []
    for code1, code2 in codes:
        if code1 not in all_rates: raise ValueError(f"wrong {code1=}")
        if code2 not in all_rates: raise ValueError(f"wrong {code2=}")

        usd_to_code1 = all_rates[code1]
        usd_to_code2 = all_rates[code2]
        result.append({
            "code1": code1,
            "code2": code2,
            "rate": usd_to_code2 / usd_to_code1,
        })

    return result


async def turn_subscription_on(tg_id: int, code1: str, code2: str) -> None:
    """
    Add currency codes to `users_subscriptions` table.
    if user already subscribed - raise ValueError.

    Args:

    user_id - telegram user id

    code1 - currency code
    code2 - currency code
    """

    if not cursor: raise ValueError("not connected to database")

    code1 = code1.upper()
    code2 = code2.upper()
    all_datetimes = list((await get_rates()).values())
    if len(all_datetimes) < 1: raise ValueError("have no rates")
    all_rates = all_datetimes[0]
    if code1 not in all_rates: raise ValueError(f"wrong {code1}")
    if code2 not in all_rates: raise ValueError(f"wrong {code2}")
    user_id = await get_or_create_user_id_by_tg_id(tg_id)

    user_subscriptions = await get_user_subscriptions(user_id)
    subscribed_codes = map(lambda x: (x["code1"], x["code2"]), user_subscriptions)
    if (code1, code2) in list(subscribed_codes):
        raise ValueError(f"{code1=} {code2=} already subscribed")
    cursor.execute(
        "INSERT INTO users_subscriptions VALUES (%s, %s, %s)", (user_id, code1, code2)
    )


async def turn_subscription_off(tg_id: int, code1: str, code2: str) -> None:
    """
    Remove currency codes to `users_subscriptions` table.
    if user is not subscribed - raise ValueError.

    Args:

    user_id - telegram user id

    code1 - currency code
    code2 - currency code
    """

    if not cursor: raise ValueError("not connected to database")

    code1 = code1.upper()
    code2 = code2.upper()
    user_id = await get_or_create_user_id_by_tg_id(tg_id)

    user_subscriptions = await get_user_subscriptions(tg_id)
    subscribed_codes = map(lambda x: (x["code1"], x["code2"]), user_subscriptions)
    if (code1, code2) not in list(subscribed_codes):
        raise ValueError(f"{code1=} {code2=} not subscribed")
    cursor.execute(
        "DELETE FROM users_subscriptions WHERE user_id = %s AND code1 = %s AND code2 = %s",
        (user_id, code1, code2),
    )


async def get_rates_to_currency(code: str) -> list[dict[str, str | float]]:
    """
    Get currency rates to `code`.

    Args:

    code - currency code

    Return:

    dict of currency codes as key and rate as value
    """

    if not cursor: raise ValueError("not connected to database")
    code = code.upper()

    all_datetimes = list((await get_rates()).values())
    if len(all_datetimes) < 1: raise ValueError("have no rates")
    all_rates = all_datetimes[0]

    if code not in all_rates:
        raise ValueError(f"wrong {code=}")

    usd_to_code1 = all_rates[code]
    result = []
    for code1 in all_rates:
        result.append({
            "code1": code1,
            "code2": code,
            "rate": usd_to_code1 / all_rates[code1],
        })

    return result
