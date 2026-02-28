"""Wallet Domain Exceptions"""
from uuid import UUID


class WalletException(Exception):
    """Base exception for wallet domain"""
    pass


class InsufficientBalance(WalletException):
    """Raised when there's insufficient balance for an operation"""
    def __init__(self, available: float, required: float):
        self.available = available
        self.required = required
        super().__init__(f"Insufficient balance: available {available}, required {required}")


class InvalidAmount(WalletException):
    """Raised when an amount is invalid"""
    pass


class WalletNotFoundError(WalletException):
    """Raised when a wallet is not found"""
    def __init__(self, wallet_id: UUID = None, user_id: UUID = None):
        self.wallet_id = wallet_id
        self.user_id = user_id
        identifier = wallet_id or user_id
        super().__init__(f"Wallet not found: {identifier}")


class TransactionNotFoundError(WalletException):
    """Raised when a transaction is not found"""
    def __init__(self, tx_id: UUID):
        self.tx_id = tx_id
        super().__init__(f"Transaction not found: {tx_id}")


class LockedBalanceError(WalletException):
    """Raised when trying to access locked balance"""
    pass
