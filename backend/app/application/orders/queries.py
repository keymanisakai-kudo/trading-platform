"""Application Layer - Orders Queries"""
from dataclasses import dataclass
from uuid import UUID
from typing import Optional, List, TYPE_CHECKING
from domain.trading.repositories import IOrderRepository

if TYPE_CHECKING:
    from domain.trading.aggregate import Order


@dataclass
class GetOrderQuery:
    """查询订单"""
    order_id: UUID
    user_id: UUID  # For authorization


@dataclass
class GetOrderResult:
    """查询结果"""
    order: Optional[dict]
    message: str


class GetOrderHandler:
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository

    async def handle(self, query: GetOrderQuery) -> GetOrderResult:
        order = await self.order_repository.get_by_id(query.order_id)
        
        if not order:
            return GetOrderResult(order=None, message="Order not found")
        
        if order.user_id != query.user_id:
            return GetOrderResult(order=None, message="Unauthorized")
        
        return GetOrderResult(
            order={
                "id": str(order.id),
                "symbol": str(order.symbol),
                "side": order.side.value,
                "order_type": order.order_type.value,
                "price": float(order.price.value) if order.price else None,
                "quantity": float(order.quantity.value),
                "filled_quantity": float(order.filled_quantity.value),
                "status": order.status.value,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat(),
            },
            message="Success",
        )


@dataclass
class ListOrdersQuery:
    """查询订单列表"""
    user_id: UUID
    symbol: Optional[str] = None
    status: Optional[str] = None
    limit: int = 50
    offset: int = 0


@dataclass
class ListOrdersResult:
    """查询结果"""
    orders: List[dict]
    total: int
    message: str


class ListOrdersHandler:
    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository

    async def handle(self, query: ListOrdersQuery) -> ListOrdersResult:
        from domain.trading.value_objects import Symbol, OrderStatus
        
        # Parse filters
        symbol = None
        if query.symbol:
            try:
                symbol = Symbol.from_string(query.symbol)
            except ValueError:
                pass
        
        order_status = None
        if query.status:
            try:
                order_status = OrderStatus(query.status)
            except ValueError:
                pass
        
        # Query
        orders, total = await self.order_repository.find_by_user(
            user_id=query.user_id,
            symbol=symbol,
            status=order_status,
            limit=query.limit,
            offset=query.offset,
        )
        
        # Convert to dict
        order_dicts = []
        for order in orders:
            order_dicts.append({
                "id": str(order.id),
                "symbol": str(order.symbol),
                "side": order.side.value,
                "order_type": order.order_type.value,
                "price": float(order.price.value) if order.price else None,
                "quantity": float(order.quantity.value),
                "filled_quantity": float(order.filled_quantity.value),
                "status": order.status.value,
                "created_at": order.created_at.isoformat(),
                "updated_at": order.updated_at.isoformat(),
            })
        
        return ListOrdersResult(
            orders=order_dicts,
            total=total,
            message="Success",
        )
