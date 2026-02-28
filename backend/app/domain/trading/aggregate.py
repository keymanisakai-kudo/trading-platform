"""Trading Domain - Order Aggregate"""
from datetime import datetime
from typing import List, Optional
from uuid import UUID, uuid4
from dataclasses import field, dataclass
from decimal import Decimal

from domain.trading.value_objects import (
    OrderSide,
    OrderType,
    OrderStatus,
    Symbol,
    Price,
    Quantity,
)
from domain.trading.exceptions import (
    InvalidOrderStateTransition,
    InsufficientBalance,
)
from domain.trading.events import (
    OrderCreatedEvent,
    OrderFilledEvent,
    OrderCancelledEvent,
)


@dataclass
class Order:
    """Order Aggregate Root"""
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default=None)
    symbol: Symbol = field(default=None)
    side: OrderSide = field(default=None)
    order_type: OrderType = field(default=None)
    price: Optional[Price] = field(default=None)
    quantity: Quantity = field(default=None)
    filled_quantity: Quantity = field(default=None)
    status: OrderStatus = OrderStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1  # Optimistic locking

    # Domain Events
    _events: List = field(default_factory=list, repr=False)

    # --- Business Rules ---

    def can_fill(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]

    def can_cancel(self) -> bool:
        return self.status == OrderStatus.PENDING

    def can_reject(self) -> bool:
        return self.status == OrderStatus.PENDING

    # --- Factory ---

    @classmethod
    def place(
        cls,
        user_id: UUID,
        symbol: Symbol,
        side: OrderSide,
        order_type: OrderType,
        quantity: Quantity,
        price: Optional[Price] = None,
    ) -> "Order":
        """Factory method to create a new order"""
        if order_type == OrderType.LIMIT and price is None:
            raise ValueError("Limit order requires price")

        if order_type == OrderType.MARKET and price is not None:
            raise ValueError("Market order should not have price")

        order = Order(
            user_id=user_id,
            symbol=symbol,
            side=side,
            order_type=order_type,
            price=price,
            quantity=quantity,
            filled_quantity=Quantity(Decimal(0), symbol),
            status=OrderStatus.PENDING,
        )
        order._events.append(OrderCreatedEvent(
            order_id=order.id,
            symbol=str(symbol),
            side=side.value,
            quantity=float(quantity.value),
        ))
        return order

    # --- Commands ---

    def fill(self, fill_quantity: Quantity, fill_price: Price) -> None:
        """Fill the order (or partially fill)"""
        if not self.can_fill():
            raise InvalidOrderStateTransition(
                f"Cannot fill order with status {self.status}"
            )

        # Check if fully filled
        new_filled = self.filled_quantity.value + fill_quantity.value
        if new_filled >= self.quantity.value:
            self.status = OrderStatus.FILLED
            self.filled_quantity = Quantity(new_filled, self.symbol)
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
            self.filled_quantity = Quantity(new_filled, self.symbol)

        self.updated_at = datetime.utcnow()
        self._events.append(OrderFilledEvent(
            order_id=self.id,
            filled_quantity=float(fill_quantity.value),
            fill_price=float(fill_price.value),
        ))

    def cancel(self) -> None:
        """Cancel the order"""
        if not self.can_cancel():
            raise InvalidOrderStateTransition(
                f"Cannot cancel order with status {self.status}"
            )

        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        self._events.append(OrderCancelledEvent(order_id=self.id))

    def reject(self, reason: str) -> None:
        """Reject the order"""
        if not self.can_reject():
            raise InvalidOrderStateTransition(
                f"Cannot reject order with status {self.status}"
            )

        self.status = OrderStatus.REJECTED
        self.updated_at = datetime.utcnow()

    # --- Optimistic Locking ---

    def increment_version(self) -> None:
        self.version += 1

    def check_version(self, expected_version: int) -> None:
        if self.version != expected_version:
            from domain.trading.exceptions import OptimisticLockError
            raise OptimisticLockError(
                f"Version mismatch: expected {expected_version}, got {self.version}"
            )

    # --- Events ---

    def pull_events(self) -> List:
        events = self._events.copy()
        self._events.clear()
        return events
