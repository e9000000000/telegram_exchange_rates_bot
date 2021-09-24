import pytest
from pytest_mock import MockerFixture

from datetime import datetime

from service.rates import actual_rate, actual_rates


@pytest.fixture
def mock_get_rates(mocker: MockerFixture):
    async def new_get_rates(
        datetime_from: datetime = None,
        datetime_to: datetime = None,
        currency_codes: str = [],
    ):
        codes = {
            "RUB": 10.0,
            "USD": 1.0,
            "EUR": 0.5,
        }
        if len(currency_codes) == 0:
            currency_codes = list(codes)
        if not set(currency_codes).issubset(set(codes)):
            return {}
        return {
            "2021-09-01T04:29:57.357980": {
                code: codes[code] for code in currency_codes if code in codes
            }
        }

    mocker.patch(
        "service.rates.get_rates",
        wraps=new_get_rates,
    )


@pytest.mark.asyncio
async def test_all_rates(mock_get_rates):
    assert sorted(await actual_rates()) == sorted({"RUB": 10.0, "USD": 1.0, "EUR": 0.5})


@pytest.mark.asyncio
async def test_rub_to_usd(mock_get_rates):
    assert await actual_rate("RUB", "USD") == 0.1


@pytest.mark.asyncio
async def test_eur_to_rub(mock_get_rates):
    assert await actual_rate("EUR", "RUB") == 20.0


@pytest.mark.asyncio
async def test_invalid_codes(mock_get_rates):
    try:
        await actual_rate("ewfewf", "efwefwwe")
        assert not "Should raise an error"
    except ValueError as e:
        assert (
            str(e)
            == "invalid data from database. code1=ewfewf code2=efwefwwe result={}"
        )
        return
    except Exception as e:
        assert not f"Should raise ValueError, not {type(e)}"
