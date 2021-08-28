import pytest

from service.collector import all_rates


@pytest.fixture
def mock_import_modules_from_dir(mocker):
    class Module1:
        async def rates(self):
            return {"RUB": 3.0}

    class Module2:
        async def rates(self):
            return {"USD": 1.0}

    mocker.patch(
        "service.collector.import_modules_from_dir", return_value=[Module1(), Module2()]
    )


@pytest.mark.asyncio
async def test_all_rates(mock_import_modules_from_dir):
    assert sorted(await all_rates()) == sorted({"RUB": 3.0, "USD": 1.0})
