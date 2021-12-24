# database rates

## tables

`users`
- `id`
- `tg_id` - BIGINT

`users_subscriptions`
- `user_id` - INT (primary key on `users.id`)
- `code1` - VARCHAR(10)
- `code2` - VARCHAR(10)

`received_datetimes`
- `id`
- `datetime` TIMESTAMP

`rates`
- `id`
- `received_datetime_id` - INT (primary key on `received_datetimes.id`)
- `code` - VARCHAR(10)
- `rate` - FLOAT
