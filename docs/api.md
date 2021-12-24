# CORE API

## for all urls
it will't work without api key
`?api_key={your api key}`

## get rates user subscribed at
GET:
`/tg/users/{telegram user id}/subscriptions`

success:
```json
[
    {
        "code1": "USD",
        "code2": "EUR",
        "rate": 12.15
    },
    ...
]
```

error:
```json
{
    "detail": "reason why"
}
```

## turn user subscription on
POST:
`/tg/users/{telegram user id}/subscriptions/{currency code 1}/{currency code 2}`

success:
```json
{
    "success": 1
}
```

error:
```json
{
    "detail": "reason why"
}
```

## turn user subscription off
DELETE:
`/tg/users/{telegram user id}/subscriptions/{currency code 1}/{currency code 2}`

success:
```json
{
    "success": 1
}
```

error:
```json
{
    "detail": "reason why"
}
```

## get all rates to one currency
GET:
`/tg/rates/{currency code}`

ARGS:
`page` - page number
`page_size` - amount of rates in one page

success:
```json
{
    "total": 314,
    "size": 12,
    "page": 15,
    "items": [
        {
            "code1": "USD",
            "code2": "EUR",
            "rate": 12.15
        },
        ...
    ]
}
```

error:
```json
{
    "detail": "reason why"
}
```
