import pytest

from service.rates_lists.currencies import rates


@pytest.fixture
def mock_api_request(mocker):
    class Response:
        async def json(self):
            return {
                "rub": {
                    "code": "RUB",
                    "alphaCode": "RUB",
                    "numericCode": "643",
                    "name": "Russian Rouble",
                    "rate": 10.0,
                    "date": "Sat, 10 Jul 2021 11:55:01 GMT",
                    "inverseRate": 0.1,
                },
                "eur": {
                    "code": "EUR",
                    "alphaCode": "EUR",
                    "numericCode": "978",
                    "name": "Euro",
                    "rate": 0.5,
                    "date": "Sat, 10 Jul 2021 11:55:01 GMT",
                    "inverseRate": 2,
                },
            }

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            pass

    def get(self, *args, **kwargs):
        return Response()

    mocker.patch("service.rates_lists.currencies.aiohttp.ClientSession.get", get)


@pytest.mark.asyncio
async def test_api_data_parsing(mock_api_request):
    assert sorted(await rates()) == sorted({"RUB": 10.0, "EUR": 0.5, "USD": 1.0})
