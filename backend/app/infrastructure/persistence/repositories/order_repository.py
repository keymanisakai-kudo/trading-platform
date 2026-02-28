"""SQLAlchemy Order Repository"""
from typing import Optional, List, Tuple
from uuid import UUID
from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from domain.trading.aggregate import Order
from domain.trading.value_objects import (
    OrderSide, OrderType, OrderStatus, Symbol, Price, Quantity
)
from domain.trading.repositories import IOrderRepository
from app.infrastructure.persistence.models import OrderModel


class SQLAlchemyOrderRepository(IOrderRepository):
    """SQLAlchemy implementation of OrderRepository"""

    def __init__(self, db: AsyncSession):
        self._db = db

    def _to_domain(self, model: OrderModel) -> Order:
        """Convert ORM model to domain aggregate"""
        symbol = Symbol.from_string(model.symbol)
        
        order = Order(
            id=model.id,
            user_id=model.user_id,
            symbol=symbol,
            side=OrderSide(model.side),
            order_type=OrderType(model.order_type),
            price=Price(model.price, symbol) if model.price else None,
            quantity=Quantity(model.quantity, symbol),
            filled_quantity=Quantity(model.filled_quantity, symbol),
            status=OrderStatus(model.status),
            created_at=model.created_at,
            updated_at=model.updated_at,
            version=model.version,
        )
        return order

    def _to_model(self, order: Order) -> OrderModel:
        """Convert domain aggregate to ORM model"""
        return OrderModel(
            id=order.id,
            user_id=order.user_id,
            symbol=str(order.symbol),
            side=order.side.value,
            order_type=order.order_type.value,
            price=order.price.value if order.price else None,
            quantity=order.quantity.value,
            filled_quantity=order.filled_quantity.value,
            status=order.status.value,
            version=order.version,
            created_at=order.created_at,
            updated_at=order.updated_at,
        )

    async def save(self, order: Order) -> Order:
        """Save or update order"""
        # Check if exists
        existing = await self._db.get(OrderModel, order.id)
        
        if existing:
            # Update
            existing.symbol = str(order.symbol)
            existing.side = order.side.value
            existing.order_type = order.order_type.value
            existing.price = order.price.value if order.price else None
            existing.quantity = order.quantity.value
            existing.filled_quantity = order.filled_quantity.value
            existing.status = order.status.value
            existing.version = order.version
            existing.updated_at = order.updated_at
        else:
            # Insert
            model = self._to_model(order)
            self._db.add(model)
        
        await self._db.flush()
        await self._db.refresh(order.id)
        
        return order

    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        """Get order by ID"""
        model = await self._db.get(OrderModel, order_id)
        if not model:
            return None
        return self._to_domain(model)

    async def find_by_user(
        self,
        user_id: UUID,
        symbol: Optional[Symbol] = None,
        status: Optional[OrderStatus] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> Tuple[List[Order], int]:
        """Find orders by user with filters"""
        # Build query
        query = select(OrderModel).where(OrderModel.user_id == user_id)
        count_query = select(func.count(OrderModel.id)).where(OrderModel.user_id == user_id)

        if symbol:
            query = query.where(OrderModel.symbol == str(symbol))
            count_query = count_query.where(OrderModel.symbol == str(symbol))

        if status:
            query = query.where(OrderModel.status == status.value)
            count_query = count_query.where(OrderModel.status == status.value)

        # Get total
        total = await self._db.scalar(count_query)

        # Get data
        query = query.order_by(OrderModel.created_at.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self._db.execute(query)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models], total

    async def find_pending(self, symbol: Symbol) -> List[Order]:
        """Find pending orders for a symbol"""
        query = select(OrderModel).where(
            OrderModel.symbol == str(symbol),
            OrderModel.status == "pending",
        ).order_by(OrderModel.created_at.asc())

        result = await self._db.execute(query)
        models = result.scalars().all()

        return [self._to_domain(m) for m in models]

    async def delete(self, order_id: UUID) -> bool:
        """Soft delete order"""
        model = await self._db.get(OrderModel, order_id)
        if not model:
            return False
        
        model.status = "deleted"
        await self._db.flush()
        return True
