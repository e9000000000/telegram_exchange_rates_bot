import pytest

from app.bot import start, get_rate, get_rates, HELP_MESSAGE


class MockMessage:
    def __init__(self, user_text: str):
        self.text = user_text
        self.recived_messages = []

    async def answer(self, text: str, *args, **kwargs):
        self.recived_messages.append(text)


@pytest.fixture
def mock_all_rates_in_bot(mocker):
    mocker.patch(
        "app.bot.all_rates",
        return_value={
            "RUB": 10.0,
            "EUR": 0.5,
            "USD": 1.0,
        },
    )


@pytest.fixture
def mock_all_rates_in_rates(mocker):
    mocker.patch(
        "app.rates.all_rates",
        return_value={
            "RUB": 10.0,
            "EUR": 0.5,
            "USD": 1.0,
        },
    )


@pytest.fixture
def mock_rate(mocker):
    mocker.patch("app.bot.rate", return_value=1)


@pytest.mark.asyncio
async def test_start():
    msg = MockMessage("/start")
    await start(msg)

    assert msg.recived_messages[0] == HELP_MESSAGE


@pytest.mark.asyncio
async def test_get_rates(mock_all_rates_in_bot):
    msg = MockMessage("/rates")
    await get_rates(msg)

    assert msg.recived_messages[0] == "RUB - 10.0\nEUR - 0.5\nUSD - 1.0"


@pytest.mark.asyncio
async def test_eur_to_usd(mock_all_rates_in_rates):
    msg = MockMessage("EUR USD")
    await get_rate(msg)

    assert msg.recived_messages[0] == "1 EUR = 2.0 USD"


@pytest.mark.asyncio
async def test_wrong_codes(mock_all_rates_in_rates):
    msg = MockMessage("FEF FEWWE")
    await get_rate(msg)

    assert msg.recived_messages[0] == 'Can\'t find exchange rate of "FEF".'


@pytest.mark.asyncio
async def test_absolute_invalid_input(mock_all_rates_in_rates):
    msg = MockMessage("ewfewfwef")
    await get_rate(msg)

    assert msg.recived_messages[0] == "/help to get help."
