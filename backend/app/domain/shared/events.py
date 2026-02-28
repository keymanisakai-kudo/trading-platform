"""Domain Events"""
from abc import ABC
from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4


@dataclass
class DomainEvent(ABC):
    event_id: UUID = field(default_factory=uuid4)
    occurred_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.utcnow()


# Trading Events
@dataclass
class OrderCreatedEvent(DomainEvent):
    order_id: UUID = None
    symbol: str = None
    side: str = None
    quantity: float = None


@dataclass
class OrderFilledEvent(DomainEvent):
    order_id: UUID = None
    filled_quantity: float = None
    fill_price: float = None


@dataclass
class OrderCancelledEvent(DomainEvent):
    order_id: UUID = None


# Wallet Events
@dataclass
class DepositEvent(DomainEvent):
    wallet_id: UUID = None
    amount: float = None
    transaction_id: UUID = None


@dataclass
class WithdrawalEvent(DomainEvent):
    wallet_id: UUID = None
    amount: float = None
    transaction_id: UUID = None


@dataclass
class BalanceChangedEvent(DomainEvent):
    wallet_id: UUID = None
    balance_before: float = None
    balance_after: float = None


# User Events
@dataclass
class UserRegisteredEvent(DomainEvent):
    user_id: UUID = None
    email: str = None


@dataclass
class UserVerifiedEvent(DomainEvent):
    user_id: UUID = None
