"""Test Configuration"""
import pytest
from decimal import Decimal
from uuid import uuid4


# Import fixtures
@pytest.fixture
def user_id():
    return uuid4()


@pytest.fixture
def sample_symbol():
    from domain.trading.value_objects import Symbol
    return Symbol("BTC", "USDT")


@pytest.fixture
def sample_quantity(sample_symbol):
    from domain.trading.value_objects import Quantity
    return Quantity(Decimal("0.1"), sample_symbol)


@pytest.fixture
def sample_price(sample_symbol):
    from domain.trading.value_objects import Price
    return Price(Decimal("50000"), sample_symbol)


@pytest.fixture
def sample_wallet(user_id):
    from domain.wallet.aggregate import Wallet
    from domain.wallet.value_objects import Currency
    return Wallet.create(user_id=user_id, currency=Currency.USDT)


@pytest.fixture
def sample_user(user_id):
    from domain.user.aggregate import User
    return User.create(
        email="test@example.com",
        username="testuser",
        password_hash="hashed_password",
    )
