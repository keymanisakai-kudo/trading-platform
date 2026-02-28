"""Trading Domain - Repository Interfaces"""
from typing import Protocol, Optional, List
from uuid import UUID

from domain.trading.aggregate import Order
from domain.trading.value_objects import Symbol, OrderStatus


class IOrderRepository(Protocol):
    """Order Repository Interface"""

    async def save(self, order: Order) -> Order:
        """Save or update order"""
        ...

    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID"""
        ...

    async def find_by_user(
        self,
        user_id: UUID,
        symbol: Optional[Symbol] = None,
        status: Optional[OrderStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[List[Order], int]:
        """Find orders by user with filters"""
        ...

    async def find_pending(self, symbol: Symbol) -> List[Order]:
        """Find pending orders for a symbol (for matching)"""
        ...

    async def delete(self, order_id: UUID) -> bool:
        """Soft delete order"""
        ...
