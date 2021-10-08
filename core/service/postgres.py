from datetime import datetime

import psycopg2

from service.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


connection = None
cursor = None


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

    global cursor

    cursor.execute("SELECT * FROM pg_catalog.pg_tables WHERE schemaname='public'")
    tables = cursor.fetchall()
    table_names = [table[1] for table in tables]

    if "users" not in table_names:
        cursor.execute(
            "CREATE TABLE users (\
                id INT PRIMARY KEY,\
                everyday_notification BOOLEAN DEFAULT FALSE\
            )"
        )
        cursor.execute(
            "CREATE INDEX users_everyday_notification ON users USING hash (everyday_notification)"
        )

    if "users_subscriptions" not in table_names:
        cursor.execute(
            "CREATE TABLE users_subscriptions (\
                user_id BIGINT,\
                code VARCHAR(10),\
                FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE\
            )"
        )
        cursor.execute(
            "CREATE INDEX users_subscriptions_user_id ON users_subscriptions USING hash (user_id);"
        )


def close() -> None:
    """Close connection to database."""

    cursor.close()


def commit_changes() -> None:
    """Commit changes to database."""

    cursor.execute("COMMIT")


async def get_rates(
    datetime_from: datetime = None,
    datetime_to: datetime = None,
    currency_codes: str = [],
) -> dict[datetime : dict[str:float]]:
    """
    Get info about currencys rates from database.
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


async def create_user_if_not_exists(id: int) -> None:
    """
    Create user if there is no user with this id in database.

    Args:

    id - telegram user id
    """

    cursor.execute("SELECT id FROM users WHERE id=%s", (id,))
    result = cursor.fetchall()
    if len(result) <= 0:
        cursor.execute("INSERT INTO users VALUES (%s)", (id,))
        commit_changes()


async def toggle_user_everyday_notification(id: int) -> bool:
    """
    Toggle should we send rates everyday to user or not.

    Args:

    `id` - telegram user id

    Return:

    `True` if notifications turned on after toggling else `False`
    """

    await create_user_if_not_exists(id)

    cursor.execute("SELECT everyday_notification FROM users WHERE id=%s", (id,))
    result = cursor.fetchall()
    if len(result) > 0 and len(result[0]) > 0:
        old_value = result[0][0]
        cursor.execute(
            "UPDATE users SET everyday_notification=%s WHERE id=%s", (not old_value, id)
        )

        commit_changes()
        return not old_value
    raise ValueError(f"Can't find user with id={id}")


async def get_user_subscriptions(user_id: int) -> dict[str:float]:
    """
    Get currency codes and rates user subscribed at.

    Args:

    user_id - telegram user id

    Return:

    dict of currency codes as keys and rates
    """

    await create_user_if_not_exists(user_id)

    cursor.execute(
        "SELECT code FROM users_subscriptions WHERE user_id = %s ORDER BY code",
        (user_id,),
    )
    result = cursor.fetchall()
    subscribed_rates = [code for (code,) in result]
    all_rates = await get_rates()
    for key in all_rates:
        rates = all_rates[key]
        return {code: rates[code] for code in rates if code in subscribed_rates}


async def get_notifiable_users_subscriptions() -> dict[int : list[str]]:
    """
    Get user ids and user subscriptions. Only for users with `everyday_notification` true.

    Return:

        {
            user id: [currency code 1, currency code 2],
            1215: ["USD", "RUB", "EUR"],
        }

    """

    users = {}
    cursor.execute(
        "SELECT user_id, code FROM users_subscriptions WHERE user_id IN \
        (SELECT user_id FROM users WHERE users.everyday_notification = true)"
    )
    result = cursor.fetchall()
    for user_id, code in result:
        if user_id not in users:
            users[user_id] = []

        users[user_id].append(code)

    return users


async def toggle_currency_in_subscriptions(user_id: int, code: str) -> None:
    """
    Add currency code to `users_subscriptions` table.
    if user already subscribed - delete code from table.

    Args:

    user_id - telegram user id

    code - currency code
    """

    code = code.upper()

    user_subscriptions = await get_user_subscriptions(user_id)
    if code in user_subscriptions:
        cursor.execute(
            "DELETE FROM users_subscriptions WHERE user_id = %s AND code = %s",
            (user_id, code),
        )
    else:
        cursor.execute(
            "INSERT INTO users_subscriptions VALUES (%s, %s)", (user_id, code)
        )


async def get_user_currency_statuses(user_id: int) -> dict[str:bool]:
    """
    Get currencies status (user subscribed or not).

    Args:

    user_id - telegram user id

    Return:

    dict of currency codes as key and is user subscribed to this currency
    """

    result = await get_rates()
    for key in result:
        all_codes = result[key]
    if len(result) <= 0:
        return []

    subscriptions = await get_user_subscriptions(user_id)

    return {code: code in subscriptions for code in sorted(all_codes)}