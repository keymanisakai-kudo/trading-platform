"""Wallet Domain - Wallet Aggregate"""
from datetime import datetime
from uuid import UUID, uuid4
from dataclasses import field, dataclass
from decimal import Decimal
from typing import List, Optional

from domain.wallet.value_objects import Money, Currency
from domain.wallet.exceptions import InsufficientBalance, InvalidAmount
from domain.wallet.events import (
    DepositEvent,
    WithdrawalEvent,
    BalanceChangedEvent,
)


@dataclass
class Transaction:
    """Transaction Entity - 流水记录"""
    id: UUID = field(default_factory=uuid4)
    wallet_id: UUID = field(default=None)
    type: str = field(default=None)  # deposit, withdrawal, trade, lock, unlock
    amount: Decimal = field(default=None)
    fee: Decimal = field(default=Decimal(0))
    balance_before: Decimal = field(default=None)
    balance_after: Decimal = field(default=None)
    reference_id: UUID = field(default=None)  # order_id or external tx
    status: str = field(default="pending")
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class Wallet:
    """Wallet Aggregate Root"""
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default=None)
    currency: Currency = field(default=Currency.USDT)
    balance: Decimal = field(default=Decimal(0))
    locked_balance: Decimal = field(default=Decimal(0))  # Locked for pending orders
    version: int = 1

    _events: List = field(default_factory=list, repr=False)

    @property
    def available_balance(self) -> Decimal:
        return self.balance - self.locked_balance

    # --- Factory ---

    @classmethod
    def create(cls, user_id: UUID, currency: Currency = Currency.USDT) -> "Wallet":
        """Create a new wallet for a user"""
        return Wallet(user_id=user_id, currency=currency)

    # --- Commands ---

    def deposit(self, amount: Decimal, reference_id: UUID = None) -> Transaction:
        """充值"""
        if amount <= 0:
            raise InvalidAmount("Deposit amount must be positive")

        balance_before = self.balance
       
 self.balance += amount        self.version += 1

        tx = Transaction(
            wallet_id=self.id,
            type="deposit",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.balance,
            reference_id=reference_id,
            status="completed",
        )

        self._events.append(DepositEvent(
            wallet_id=self.id,
            amount=float(amount),
            transaction_id=tx.id,
        ))
        self._events.append(BalanceChangedEvent(
            wallet_id=self.id,
            balance_before=float(balance_before),
            balance_after=float(self.balance),
        ))

        return tx

    def withdraw(self, amount: Decimal, reference_id: UUID = None) -> Transaction:
        """提现"""
        if amount <= 0:
            raise InvalidAmount("Withdrawal amount must be positive")

        if amount > self.available_balance:
            raise InsufficientBalance(
                available=float(self.available_balance),
                required=float(amount),
            )

        balance_before = self.balance
        self.balance -= amount
        self.version += 1

        tx = Transaction(
            wallet_id=self.id,
            type="withdrawal",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.balance,
            reference_id=reference_id,
            status="pending",  # Pending confirmation
        )

        self._events.append(WithdrawalEvent(
            wallet_id=self.id,
            amount=float(amount),
            transaction_id=tx.id,
        ))
        self._events.append(BalanceChangedEvent(
            wallet_id=self.id,
            balance_before=float(balance_before),
            balance_after=float(self.balance),
        ))

        return tx

    def lock_for_order(self, amount: Decimal, order_id: UUID) -> None:
        """锁定余额用于订单"""
        if amount <= 0:
            raise InvalidAmount("Lock amount must be positive")

        if amount > self.available_balance:
            raise InsufficientBalance(
                available=float(self.available_balance),
                required=float(amount),
            )

        self.locked_balance += amount
        self.version += 1

    def unlock(self, amount: Decimal, order_id: UUID) -> None:
        """解锁余额"""
        if amount <= 0:
            return

        self.locked_balance = max(Decimal(0), self.locked_balance - amount)
        self.version += 1

    def deduct(self, amount: Decimal, order_id: UUID) -> Transaction:
        """扣除余额 (用于买家成交)"""
        if amount > self.balance:
            raise InsufficientBalance(
                available=float(self.balance),
                required=float(amount),
            )

        balance_before = self.balance
        self.balance -= amount
        self.version += 1

        tx = Transaction(
            wallet_id=self.id,
            type="trade_deduct",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.balance,
            reference_id=order_id,
            status="completed",
        )

        self._events.append(BalanceChangedEvent(
            wallet_id=self.id,
            balance_before=float(balance_before),
            balance_after=float(self.balance),
        ))

        return tx

    def add_proceeds(self, amount: Decimal, order_id: UUID) -> Transaction:
        """增加交易收益 (用于卖家成交)"""
        balance_before = self.balance
        self.balance += amount
        self.version += 1

        tx = Transaction(
            wallet_id=self.id,
            type="trade_proceeds",
            amount=amount,
            balance_before=balance_before,
            balance_after=self.balance,
            reference_id=order_id,
            status="completed",
        )

        self._events.append(BalanceChangedEvent(
            wallet_id=self.id,
            balance_before=float(balance_before),
            balance_after=float(self.balance),
        ))

        return tx

    # --- Events ---

    def pull_events(self) -> List:
        events = self._events.copy()
        self._events.clear()
        return events
