"""Application Layer - Orders Commands"""
from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from typing import Optional, TYPE_CHECKING

from domain.trading.value_objects import OrderSide, OrderType, Symbol, Price, Quantity
from domain.trading.aggregate import Order
from domain.trading.repositories import IOrderRepository
from domain.wallet.repositories import IWalletRepository

if TYPE_CHECKING:
    from domain.wallet.aggregate import Wallet


@dataclass
class PlaceOrderCommand:
    """下单命令"""
    user_id: UUID
    symbol: str
    side: str  # "buy" or "sell"
    order_type: str  # "market" or "limit"
    quantity: Decimal
    price: Optional[Decimal] = None


@dataclass
class PlaceOrderResult:
    """下单结果"""
    order_id: UUID
    status: str
    message: str


class PlaceOrderHandler:
    """下单命令处理器"""

    def __init__(
        self,
        order_repository: IOrderRepository,
        wallet_repository: IWalletRepository,
    ):
        self.order_repository = order_repository
        self.wallet_repository = wallet_repository

    async def handle(self, command: PlaceOrderCommand) -> PlaceOrderResult:
        # 1. Parse symbol
        try:
            symbol = Symbol.from_string(command.symbol)
        except ValueError as e:
            return PlaceOrderResult(
                order_id=None,
                status="rejected",
                message=f"Invalid symbol: {e}",
            )

        # 2. Parse enums
        try:
            side = OrderSide(command.side)
            order_type = OrderType(command.order_type)
        except ValueError as e:
            return PlaceOrderResult(
                order_id=None,
                status="rejected",
                message=f"Invalid parameter: {e}",
            )

        # 3. Create value objects
        quantity = Quantity(command.quantity, symbol)
        price = Price(command.price, symbol) if command.price else None

        # 4. Create order aggregate
        try:
            order = Order.place(
                user_id=command.user_id,
                symbol=symbol,
                side=side,
                order_type=order_type,
                quantity=quantity,
                price=price,
            )
        except ValueError as e:
            return PlaceOrderResult(
                order_id=None,
                status="rejected",
                message=str(e),
            )

        # 5. Validate balance for buy orders
        if side == OrderSide.BUY:
            wallet = await self.wallet_repository.get_by_user_id(command.user_id)
            if wallet:
                from domain.trading.services import TradingDomainService
                service = TradingDomainService()
                required = service.calculate_required_balance(order)
                
                if required > wallet.available_balance:
                    order.reject("Insufficient balance")
                    await self.order_repository.save(order)
                    return PlaceOrderResult(
                        order_id=order.id,
                        status="rejected",
                        message=f"Insufficient balance: required {required}, available {wallet.available_balance}",
                    )
                
                # Lock balance for limit orders
                if order_type == OrderType.LIMIT:
                    wallet.lock_for_order(required, order.id)

        # 6. Save order
        await self.order_repository.save(order)

        return PlaceOrderResult(
            order_id=order.id,
            status=order.status.value,
            message="Order placed successfully",
        )


@dataclass
class CancelOrderCommand:
    """取消订单命令"""
    order_id: UUID
    user_id: UUID


@dataclass
class CancelOrderResult:
    """取消订单结果"""
    order_id: UUID
    status: str
    message: str


class CancelOrderHandler:
    """取消订单处理器"""

    def __init__(self, order_repository: IOrderRepository):
        self.order_repository = order_repository

    async def handle(self, command: CancelOrderCommand) -> CancelOrderResult:
        # 1. Get order
        order = await self.order_repository.get_by_id(command.order_id)
        
        if not order:
            return CancelOrderResult(
                order_id=command.order_id,
                status="failed",
                message="Order not found",
            )

        # 2. Verify ownership
        if order.user_id != command.user_id:
            return CancelOrderResult(
                order_id=command.order_id,
                status="failed",
                message="Order does not belong to user",
            )

        # 3. Cancel if possible
        try:
            order.cancel()
        except Exception as e:
            return CancelOrderResult(
                order_id=command.order_id,
                status="failed",
                message=str(e),
            )

        # 4. Save
        await self.order_repository.save(order)

        return CancelOrderResult(
            order_id=order.id,
            status="cancelled",
            message="Order cancelled successfully",
        )
