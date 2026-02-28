"""Trading Domain Services"""
from decimal import Decimal

from domain.trading.aggregate import Order
from domain.trading.value_objects import OrderSide, OrderType, Price, Quantity


class TradingDomainService:
    """Trading Domain Service - 交易领域服务"""

    def validate_order(self, order: Order, available_balance: Decimal) -> None:
        """验证订单是否有足够余额"""
        if order.side == OrderSide.BUY:
            if order.order_type == OrderType.MARKET:
                # Market order - need enough balance for a reasonable amount
                # We'll validate at fill time
                return
            
            # Limit order - validate upfront
            required = order.quantity.value * order.price.value
            if required > available_balance:
                from domain.trading.exceptions import InsufficientBalance
                raise InsufficientBalance(
                    f"Insufficient balance for buy order: {available_balance} < {required}"
                )

    def calculate_fill_price(
        self,
        order: Order,
        market_price: Price,
        quantity: Quantity,
    ) -> Price:
        """计算成交价格"""
        if order.order_type == OrderType.MARKET:
            return market_price
        return order.price

    def calculate_fee(self, trade_value: Decimal) -> Decimal:
        """计算手续费 (0.1%)"""
        return trade_value * Decimal("0.001")

    def calculate_required_balance(self, order: Order) -> Decimal:
        """计算订单所需的余额"""
        if order.side == OrderSide.SELL:
            return order.quantity.value
        
        if order.order_type == OrderType.LIMIT:
            return order.quantity.value * order.price.value
        
        # Market order - estimate based on current price (will be validated at fill)
        return Decimal("999999999")
