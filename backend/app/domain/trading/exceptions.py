"""Trading Domain Exceptions"""


class TradingException(Exception):
    """Base exception for trading domain"""
    pass


class InvalidOrderStateTransition(TradingException):
    """Raised when an invalid state transition is attempted"""
    pass


class InsufficientBalance(TradingException):
    """Raised when there's insufficient balance for an operation"""
    pass


class OrderNotFoundError(TradingException):
    """Raised when an order is not found"""
    def __init__(self, order_id):
        self.order_id = order_id
        super().__init__(f"Order not found: {order_id}")


class OptimisticLockError(TradingException):
    """Raised when optimistic locking fails"""
    pass


class InvalidPriceError(TradingException):
    """Raised when price is invalid"""
    pass


class InvalidQuantityError(TradingException):
    """Raised when quantity is invalid"""
    pass
