"""Tests for Order Aggregate"""
import pytest
from decimal import Decimal
from uuid import uuid4

from domain.trading.aggregate import Order
from domain.trading.value_objects import (
    Symbol, OrderSide, OrderType, Quantity, Price, OrderStatus
)
from domain.trading.exceptions import InvalidOrderStateTransition


class TestOrderPlace:
    """Test Order placement"""

    def test_place_limit_order_success(self, sample_symbol):
        """Test placing a limit order"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)
        price = Price(Decimal("50000"), sample_symbol)

        order = Order.place(
            user_id=uuid4(),
            symbol=sample_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
        )

        assert order.status == OrderStatus.PENDING
        assert order.quantity == quantity
        assert order.price == price
        assert order.filled_quantity.value == Decimal(0)

    def test_place_market_order_success(self, sample_symbol):
        """Test placing a market order"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)

        order = Order.place(
            user_id=uuid4(),
            symbol=sample_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.MARKET,
            quantity=quantity,
        )

        assert order.status == OrderStatus.PENDING
        assert order.price is None

    def test_place_limit_order_without_price_fails(self, sample_symbol):
        """Test that limit order requires price"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)

        with pytest.raises(ValueError, match="Limit order requires price"):
            Order.place(
                user_id=uuid4(),
                symbol=sample_symbol,
                side=OrderSide.BUY,
                order_type=OrderType.LIMIT,
                quantity=quantity,
            )

    def test_place_market_order_with_price_fails(self, sample_symbol):
        """Test that market order should not have price"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)
        price = Price(Decimal("50000"), sample_symbol)

        with pytest.raises(ValueError, match="Market order should not have price"):
            Order.place(
                user_id=uuid4(),
                symbol=sample_symbol,
                side=OrderSide.BUY,
                order_type=OrderType.MARKET,
                quantity=quantity,
                price=price,
            )


class TestOrderFill:
    """Test Order fill"""

    def test_fill_order_success(self, sample_symbol):
        """Test filling an order"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)
        price = Price(Decimal("50000"), sample_symbol)

        order = Order.place(
            user_id=uuid4(),
            symbol=sample_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
        )

        order.fill(quantity, price)

        assert order.status == OrderStatus.FILLED
        assert order.filled_quantity == quantity

    def test_fill_partially(self, sample_symbol):
        """Test partial fill"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)
        price = Price(Decimal("50000"), sample_symbol)

        order = Order.place(
            user_id=uuid4(),
            symbol=sample_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
        )

        # Partial fill 0.05
        partial_qty = Quantity(Decimal("0.05"), sample_symbol)
        order.fill(partial_qty, price)

        assert order.status == OrderStatus.PARTIALLY_FILLED
        assert order.filled_quantity.value == Decimal("0.05")

    def test_fill_cancelled_order_fails(self, sample_symbol):
        """Test that filling a cancelled order fails"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)
        price = Price(Decimal("50000"), sample_symbol)

        order = Order.place(
            user_id=uuid4(),
            symbol=sample_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
        )

        order.cancel()

        with pytest.raises(InvalidOrderStateTransition):
            order.fill(quantity, price)


class TestOrderCancel:
    """Test Order cancellation"""

    def test_cancel_pending_order_success(self, sample_symbol):
        """Test cancelling a pending order"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)
        price = Price(Decimal("50000"), sample_symbol)

        order = Order.place(
            user_id=uuid4(),
            symbol=sample_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
        )

        order.cancel()

        assert order.status == OrderStatus.CANCELLED

    def test_cancel_filled_order_fails(self, sample_symbol):
        """Test that cancelling a filled order fails"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)
        price = Price(Decimal("50000"), sample_symbol)

        order = Order.place(
            user_id=uuid4(),
            symbol=sample_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
        )

        order.fill(quantity, price)

        with pytest.raises(InvalidOrderStateTransition):
            order.cancel()


class TestDomainEvents:
    """Test Domain Events"""

    def test_order_created_event(self, sample_symbol):
        """Test OrderCreatedEvent is emitted"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)
        price = Price(Decimal("50000"), sample_symbol)

        order = Order.place(
            user_id=uuid4(),
            symbol=sample_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
        )

        events = order.pull_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "OrderCreatedEvent"

    def test_order_filled_event(self, sample_symbol):
        """Test OrderFilledEvent is emitted"""
        quantity = Quantity(Decimal("0.1"), sample_symbol)
        price = Price(Decimal("50000"), sample_symbol)

        order = Order.place(
            user_id=uuid4(),
            symbol=sample_symbol,
            side=OrderSide.BUY,
            order_type=OrderType.LIMIT,
            quantity=quantity,
            price=price,
        )

        order.fill(quantity, price)

        events = order.pull_events()
        assert len(events) == 1
        assert events[0].__class__.__name__ == "OrderFilledEvent"
