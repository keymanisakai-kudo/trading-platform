"""Integration Tests for Orders API"""
import pytest
from decimal import Decimal
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from httpx import AsyncClient, ASGITransport


@pytest.fixture
async def mock_db():
    """Mock database session"""
    db = AsyncMock()
    return db


@pytest.fixture
async def mock_order_repo():
    """Mock order repository"""
    repo = AsyncMock()
    return repo


@pytest.fixture
async def mock_wallet_repo():
    """Mock wallet repository"""
    repo = AsyncMock()
    return repo


@pytest.fixture
async def mock_user():
    """Mock current user"""
    from domain.user.aggregate import User
    user = User(
        id=uuid4(),
        email="test@example.com",
        username="testuser",
        password_hash="hashed",
    )
    return user


class TestOrdersAPI:
    """Test Orders API endpoints"""

    @pytest.mark.asyncio
    async def test_list_orders_empty(self):
        """Test listing orders when empty"""
        # This would require proper async setup
        # For now, testing the handler directly
        pass

    @pytest.mark.asyncio
    async def test_get_order_not_found(self):
        """Test getting non-existent order"""
        from application.orders.queries import GetOrderQuery, GetOrderHandler
        from application.orders.queries import GetOrderResult

        # Create mock repository
        mock_repo = AsyncMock()
        mock_repo.get_by_id = AsyncMock(return_value=None)

        handler = GetOrderHandler(mock_repo)

        query = GetOrderQuery(
            order_id=uuid4(),
            user_id=uuid4(),
        )

        result = await handler.handle(query)

        assert result.order is None
        assert result.message == "Order not found"

    @pytest.mark.asyncio
    async def test_get_order_success(self):
        """Test getting existing order"""
        from application.orders.queries import GetOrderQuery, GetOrderHandler
        from domain.trading.aggregate import Order
        from domain.trading.value_objects import (
            Symbol, OrderSide, OrderType, Quantity, OrderStatus
        )

        user_id = uuid4()
        symbol = Symbol("BTC", "USDT")
        
        mock_order = Order(
            id=uuid4(),
            user_id=user_id,
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Quantity(Decimal("0.1"), symbol),
            status=OrderStatus.PENDING,
        )

        mock_repo = AsyncMock()
        mock_repo.get_by_id = AsyncMock(return_value=mock_order)

        handler = GetOrderHandler(mock_repo)

        query = GetOrderQuery(
            order_id=mock_order.id,
            user_id=user_id,
        )

        result = await handler.handle(query)

        assert result.order is not None
        assert result.order["symbol"] == "BTCUSDT"
        assert result.order["side"] == "buy"


class TestPlaceOrderHandler:
    """Test PlaceOrderHandler"""

    @pytest.mark.asyncio
    async def test_place_order_invalid_symbol(self):
        """Test placing order with invalid symbol"""
        from application.orders.commands import PlaceOrderCommand, PlaceOrderHandler

        mock_order_repo = AsyncMock()
        mock_wallet_repo = AsyncMock()

        handler = PlaceOrderHandler(mock_order_repo, mock_wallet_repo)

        command = PlaceOrderCommand(
            user_id=uuid4(),
            symbol="INVALID",
            side="buy",
            order_type="limit",
            quantity=Decimal("0.1"),
            price=Decimal("50000"),
        )

        result = await handler.handle(command)

        assert result.status == "rejected"
        assert "Invalid symbol" in result.message

    @pytest.mark.asyncio
    async def test_place_order_market_success(self):
        """Test placing market order"""
        from application.orders.commands import PlaceOrderCommand, PlaceOrderHandler

        mock_order_repo = AsyncMock()
        mock_order_repo.save = AsyncMock()
        
        mock_wallet_repo = AsyncMock()
        mock_wallet_repo.get_by_user_id = AsyncMock(return_value=None)

        handler = PlaceOrderHandler(mock_order_repo, mock_wallet_repo)

        command = PlaceOrderCommand(
            user_id=uuid4(),
            symbol="BTCUSDT",
            side="buy",
            order_type="market",
            quantity=Decimal("0.1"),
        )

        result = await handler.handle(command)

        assert result.status == "pending"


class TestCancelOrderHandler:
    """Test CancelOrderHandler"""

    @pytest.mark.asyncio
    async def test_cancel_order_not_found(self):
        """Test canceling non-existent order"""
        from application.orders.commands import CancelOrderCommand, CancelOrderHandler

        mock_order_repo = AsyncMock()
        mock_order_repo.get_by_id = AsyncMock(return_value=None)

        handler = CancelOrderHandler(mock_order_repo)

        command = CancelOrderCommand(
            order_id=uuid4(),
            user_id=uuid4(),
        )

        result = await handler.handle(command)

        assert result.status == "failed"
        assert "not found" in result.message.lower()

    @pytest.mark.asyncio
    async def test_cancel_order_unauthorized(self):
        """Test canceling order owned by another user"""
        from application.orders.commands import CancelOrderCommand, CancelOrderHandler
        from domain.trading.aggregate import Order
        from domain.trading.value_objects import (
            Symbol, OrderSide, OrderType, Quantity, OrderStatus
        )

        user_id = uuid4()
        other_user_id = uuid4()
        symbol = Symbol("BTC", "USDT")

        mock_order = Order(
            id=uuid4(),
            user_id=other_user_id,  # Different user
            symbol=symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=Quantity(Decimal("0.1"), symbol),
            status=OrderStatus.PENDING,
        )

        mock_order_repo = AsyncMock()
        mock_order_repo.get_by_id = AsyncMock(return_value=mock_order)

        handler = CancelOrderHandler(mock_order_repo)

        command = CancelOrderCommand(
            order_id=mock_order.id,
            user_id=user_id,  # Current user
        )

        result = await handler.handle(command)

        assert result.status == "failed"
        assert "not belong" in result.message.lower()
