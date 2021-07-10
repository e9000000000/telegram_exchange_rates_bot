import pytest

from app.rates import rate, all_rates


@pytest.fixture
def mock_all_rates(mocker):
    mocker.patch(
        "app.rates.all_rates",
        return_value={
            "RUB": 10.0,
            "USD": 1.0,
            "EUR": 0.5,
        },
    )


@pytest.fixture
def mock_import_modules_from_dir(mocker):
    class Module1:
        async def rates(self):
            return {"RUB": 3.0}

    class Module2:
        async def rates(self):
            return {"USD": 1.0}

    mocker.patch(
        "app.rates.import_modules_from_dir", return_value=[Module1(), Module2()]
    )


@pytest.mark.asyncio
async def test_all_rates(mock_import_modules_from_dir):
    assert sorted(await all_rates()) == sorted({"RUB": 3.0, "USD": 1.0})


@pytest.mark.asyncio
async def test_rub_to_usd(mock_all_rates):
    assert await rate("RUB", "USD") == 0.1


@pytest.mark.asyncio
async def test_eur_to_rub(mock_all_rates):
    assert await rate("EUR", "RUB") == 20.0


@pytest.mark.asyncio
async def test_invalid_codes(mock_all_rates):
    try:
        await rate("ewfewf", "efwefwwe")
    except ValueError as e:
        assert str(e) == 'Can\'t find exchange rate of "ewfewf".'
        return

    assert not "error raised"
