from datetime import datetime

import psycopg2

from service.config import DB_HOST, DB_NAME, DB_PASSWORD, DB_PORT, DB_USER


connection = psycopg2.connect(
    host=DB_HOST, port=DB_PORT, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
)
cursor = connection.cursor()


async def close() -> None:
    """Close connection to database."""

    global cursor

    cursor.close()


async def get_rates(
    datetime_from: datetime = None,
    datetime_to: datetime = None,
    currency_codes: str = [],
) -> dict[datetime : dict[str:float]]:
    """
    Get info about currencys rates from database.
    With default args returns newest rates of all currencys.

    Args:
        datatime_from - lower bound of time period to get rates (included).
            if it's None, then lower bound will be absent.

        datatime_to - higher bound of time period to get rates (included).
            if it's None, then higher bound will be absent.

        currency_codes - currency codes (looks like `USD` or `EUR`) which you want to get info about.
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
