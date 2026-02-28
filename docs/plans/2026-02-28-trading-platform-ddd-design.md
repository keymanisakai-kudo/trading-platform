# Trading Platform DDD 设计文档

**项目**: trading-platform  
**版本**: 1.0  
**日期**: 2026-02-28  
**状态**: 设计中

---

## 1. 架构概述

### 1.1 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                               │
│                 (FastAPI Routes)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Application Layer                           │
│            (Use Cases / Application Services)               │
│         OrderApplicationService, WalletApplicationService   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐          │
│  │   Trading   │  │   Wallet   │  │    User    │          │
│  │  Aggregate  │  │  Aggregate  │  │  Aggregate  │          │
│  │  Entities   │  │  Entities   │  │  Entities   │          │
│  │Value Objects│  │Value Objects│  │Value Objects│          │
│  │   Events    │  │   Events    │  │   Events    │          │
│  └─────────────┘  └─────────────┘  └─────────────┘          │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Domain Services                          │    │
│  │   TradingDomainService, OrderMatchingService        │    │
│  └─────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              Repository Interfaces                    │    │
│  │   IOrderRepository, IWalletRepository, IUserRepo     │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                 Infrastructure Layer                         │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  Persistence     │  │  External APIs   │                 │
│  │  (SQLAlchemy)    │  │  (Binance)       │                 │
│  └──────────────────┘  └──────────────────┘                 │
│                                                              │
│  ┌──────────────────┐  ┌──────────────────┐                 │
│  │  PostgreSQL      │  │  Redis            │                 │
│  └──────────────────┘  └──────────────────┘                 │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 目录结构

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py
│   │       ├── orders.py
│   │       └── wallet.py
│   ├── application/           # 应用层
│   │   ├── orders/
│   │   │   ├── __init__.py
│   │   │   ├── commands.py
│   │   │   └── queries.py
│   │   ├── wallet/
│   │   │   ├── __init__.py
│   │   │   ├── commands.py
│   │   │   └── queries.py
│   │   └── users/
│   │       ├── __init__.py
│   │       ├── commands.py
│   │       └── queries.py
│   ├── domain/                # 领域层
│   │   ├── trading/
│   │   │   ├── __init__.py
│   │   │   ├── aggregate.py      # Order Aggregate
│   │   │   ├── entities.py       # Trade Entity
│   │   │   ├── value_objects.py  # Price, Quantity, OrderSide, OrderType
│   │   │   ├── events.py         # Domain Events
│   │   │   ├── repositories.py   # IOrderRepository interface
│   │   │   ├── services.py       # TradingDomainService
│   │   │   └── exceptions.py
│   │   ├── wallet/
│   │   │   ├── __init__.py
│   │   │   ├── aggregate.py      # Wallet Aggregate
│   │   │   ├── value_objects.py  # Money, Currency
│   │   │   ├── events.py
│   │   │   ├── repositories.py   # IWalletRepository interface
│   │   │   └── exceptions.py
│   │   ├── user/
│   │   │   ├── __init__.py
│   │   │   ├── aggregate.py      # User Aggregate
│   │   │   ├── value_objects.py
│   │   │   ├── events.py
│   │   │   ├── repositories.py   # IUserRepository interface
│   │   │   └── exceptions.py
│   │   └── shared/
│   │       ├── __init__.py
│   │       ├── base_aggregate.py
│   │       ├── base_entity.py
│   │       ├── base_value_object.py
│   │       └── events.py         # BaseDomainEvent
│   ├── infrastructure/         # 基础设施层
│   │   ├── persistence/
│   │   │   ├── database.py
│   │   │   ├── migrations/
│   │   │   └── repositories/
│   │   │       ├── order_repository.py
│   │   │       ├── wallet_repository.py
│   │   │       └── user_repository.py
│   │   ├── binance/
│   │   │   ├── __init__.py
│   │   │   ├── client.py        # BinanceClient
│   │   │   ├── adapters/
│   │   │   │   ├── market_adapter.py
│   │   │   │   └── trading_adapter.py
│   │   │   └── exceptions.py
│   │   └── cache/
│   │       ├── __init__.py
│   │       └── redis_cache.py
│   ├── core/
│   │   ├── config.py
│   │   ├── security.py
│   │   └── exceptions.py
│   └── main.py
├── requirements.txt
└── .env.example
```

---

## 2. 领域模型设计

### 2.1 Trading 领域

#### Value Objects

```python
# domain/trading/value_objects.py
from enum import Enum
from dataclasses import dataclass
from decimal import Decimal

class OrderSide(str, Enum):
    BUY = "buy"
    SELL = "sell"

class OrderType(str, Enum):
    MARKET = "market"
    LIMIT = "limit"

class OrderStatus(str, Enum):
    PENDING = "pending"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"

@dataclass(frozen=True)
class OrderId:
    value: str

@dataclass(frozen=True)
class Symbol:
    base: str      # BTC
    quote: str     # USDT
    
    def __str__(self) -> str:
        return f"{self.base}{self.quote}"
    
    @classmethod
    def from_string(cls, s: str) -> "Symbol":
        if s.endswith("USDT"):
            return cls(base=s[:-4], quote="USDT")
        raise ValueError(f"Invalid symbol: {s}")

@dataclass(frozen=True)
class Price:
    value: Decimal
    symbol: Symbol
    
    def __mul__(self, other: "Quantity") -> "Money":
        return Money(self.value * other.value, self.symbol.quote)

@dataclass(frozen=True)
class Quantity:
    value: Decimal
    symbol: Symbol
    
    def __mul__(self, other: Price) -> Money:
        return Money(self.value * other.value, other.symbol.quote)
```

#### Aggregate Root

```python
# domain/trading/aggregate.py
from datetime import datetime
from typing import List
from uuid import UUID, uuid4
from dataclasses import field, dataclass
from decimal import Decimal

from .value_objects import *
from .events import OrderCreatedEvent, OrderFilledEvent, OrderCancelledEvent
from .exceptions import InvalidOrderStateTransition, InsufficientBalance

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
    
    _events: List = field(default_factory=list, repr=False)
    
    def can_fill(self) -> bool:
        return self.status in [OrderStatus.PENDING, OrderStatus.PARTIALLY_FILLED]
    
    def can_cancel(self) -> bool:
        return self.status == OrderStatus.PENDING
    
    def place(self, user_id: UUID, symbol: Symbol, side: OrderSide, 
              order_type: OrderType, quantity: Quantity, 
              price: Optional[Price] = None) -> "Order":
        if order_type == OrderType.LIMIT and price is None:
            raise ValueError("Limit order requires price")
        
        order = Order(
            user_id=user_id, symbol=symbol, side=side,
            order_type=order_type, price=price, quantity=quantity,
            filled_quantity=Quantity(Decimal(0), symbol),
            status=OrderStatus.PENDING,
        )
        order._events.append(OrderCreatedEvent(order.id, symbol, side, quantity))
        return order
    
    def fill(self, fill_quantity: Quantity, fill_price: Price) -> None:
        if not self.can_fill():
            raise InvalidOrderStateTransition(f"Cannot fill order with status {self.status}")
        
        new_filled = self.filled_quantity.value + fill_quantity.value
        if new_filled >= self.quantity.value:
            self.status = OrderStatus.FILLED
            self.filled_quantity = Quantity(new_filled, self.symbol)
        else:
            self.status = OrderStatus.PARTIALLY_FILLED
            self.filled_quantity = Quantity(new_filled, self.symbol)
        
        self.updated_at = datetime.utcnow()
        self._events.append(OrderFilledEvent(self.id, fill_quantity, fill_price))
    
    def cancel(self) -> None:
        if not self.can_cancel():
            raise InvalidOrderStateTransition(f"Cannot cancel order with status {self.status}")
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.utcnow()
        self._events.append(OrderCancelledEvent(self.id))
    
    def pull_events(self) -> List:
        events = self._events.copy()
        self._events.clear()
        return events
```

### 2.2 Wallet 领域

```python
# domain/wallet/aggregate.py
from datetime import datetime
from uuid import UUID, uuid4
from dataclasses import field, dataclass
from decimal import Decimal
from typing import List

from .value_objects import Money, Currency
from .events import DepositEvent, WithdrawalEvent, BalanceChangedEvent
from .exceptions import InsufficientBalance, InvalidAmount

@dataclass
class Transaction:
    id: UUID = field(default_factory=uuid4)
    wallet_id: UUID = field(default=None)
    type: str = field(default=None)
    amount: Decimal = field(default=None)
    fee: Decimal = field(default=Decimal(0))
    balance_before: Decimal = field(default=None)
    balance_after: Decimal = field(default=None)
    reference_id: UUID = field(default=None)
    status: str = field(default="pending")
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Wallet:
    id: UUID = field(default_factory=uuid4)
    user_id: UUID = field(default=None)
    currency: Currency = field(default=Currency.USDT)
    balance: Decimal = field(default=Decimal(0))
    locked_balance: Decimal = field(default=Decimal(0))
    version: int = 1
    
    _events: List = field(default_factory=list, repr=False)
    
    @property
    def available_balance(self) -> Decimal:
        return self.balance - self.locked_balance
    
    def deposit(self, amount: Decimal, reference_id: UUID = None) -> Transaction:
        if amount <= 0:
            raise InvalidAmount("Deposit amount must be positive")
        
        balance_before = self.balance
        self.balance += amount
        
        tx = Transaction(
            wallet_id=self.id, type="deposit", amount=amount,
            balance_before=balance_before, balance_after=self.balance,
            reference_id=reference_id, status="completed",
        )
        
        self._events.append(DepositEvent(self.id, amount, tx.id))
        self._events.append(BalanceChangedEvent(self.id, balance_before, self.balance))
        return tx
    
    def withdraw(self, amount: Decimal, reference_id: UUID = None) -> Transaction:
        if amount <= 0:
            raise InvalidAmount("Withdrawal amount must be positive")
        if amount > self.available_balance:
            raise InsufficientBalance(f"Insufficient balance: {self.available_balance} < {amount}")
        
        balance_before = self.balance
        self.balance -= amount
        
        tx = Transaction(
            wallet_id=self.id, type="withdrawal", amount=amount,
            balance_before=balance_before, balance_after=self.balance,
            reference_id=reference_id, status="pending",
        )
        
        self._events.append(WithdrawalEvent(self.id, amount, tx.id))
        self._events.append(BalanceChangedEvent(self.id, balance_before, self.balance))
        return tx
    
    def lock_for_order(self, amount: Decimal, order_id: UUID) -> None:
        if amount > self.available_balance:
            raise InsufficientBalance(f"Insufficient available balance")
        self.locked_balance += amount
    
    def unlock(self, amount: Decimal, order_id: UUID) -> None:
        self.locked_balance = max(Decimal(0), self.locked_balance - amount)
    
    def pull_events(self) -> List:
        events = self._events.copy()
        self._events.clear()
        return events
```

```python
# domain/wallet/value_objects.py
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum

class Currency(str, Enum):
    USDT = "USDT"
    BTC = "BTC"
    ETH = "ETH"

@dataclass(frozen=True)
class Money:
    amount: Decimal
    currency: Currency
    
    def __add__(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("Cannot add different currencies")
        return Money(self.amount + other.amount, self.currency)
```

### 2.3 User 领域

```python
# domain/user/aggregate.py
from datetime import datetime
from uuid import UUID, uuid4
from dataclasses import field, dataclass
from typing import List

@dataclass
class User:
    id: UUID = field(default_factory=uuid4)
    email: str = field(default=None)
    username: str = field(default=None)
    password_hash: str = field(default=None)
    is_active: bool = True
    is_verified: bool = False
    two_factor_enabled: bool = False
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    version: int = 1
    
    _events: List = field(default_factory=list, repr=False)
    
    @classmethod
    def create(cls, email: str, username: str, password_hash: str) -> "User":
        user = User(email=email, username=username, password_hash=password_hash)
        user._events.append(UserRegisteredEvent(user.id, email))
        return user
    
    def verify(self) -> None:
        self.is_verified = True
        self.updated_at = datetime.utcnow()
        self._events.append(UserVerifiedEvent(self.id))
    
    def pull_events(self) -> List:
        events = self._events.copy()
        self._events.clear()
        return events
```

---

## 3. Repository 接口

```python
# domain/trading/repositories.py
from typing import Optional, List
from uuid import UUID
from .aggregate import Order
from .value_objects import Symbol, OrderStatus

class IOrderRepository:
    async def save(self, order: Order) -> Order:
        raise NotImplementedError
    
    async def get_by_id(self, order_id: UUID) -> Optional[Order]:
        raise NotImplementedError
    
    async def find_by_user(
        self, user_id: UUID, symbol: Optional[Symbol] = None,
        status: Optional[OrderStatus] = None,
        limit: int = 50, offset: int = 0,
    ) -> tuple[List[Order], int]:
        raise NotImplementedError
    
    async def find_pending(self, symbol: Symbol) -> List[Order]:
        raise NotImplementedError
```

```python
# domain/wallet/repositories.py
from typing import Optional, List
from uuid import UUID
from .aggregate import Wallet, Transaction

class IWalletRepository:
    async def save(self, wallet: Wallet) -> Wallet:
        raise NotImplementedError
    async def get_by_user_id(self, user_id: UUID) -> Optional[Wallet]:
        raise NotImplementedError

class ITransactionRepository:
    async def save(self, transaction: Transaction) -> Transaction:
        raise NotImplementedError
    async def find_by_wallet(
        self, wallet_id: UUID, limit: int = 50, offset: int = 0,
    ) -> tuple[List[Transaction], int]:
        raise NotImplementedError
```

---

## 4. Domain Services

```python
# domain/trading/services.py
from decimal import Decimal
from .aggregate import Order
from .value_objects import *

class TradingDomainService:
    def validate_order(self, order: Order, available_balance: Decimal) -> None:
        if order.side == OrderSide.BUY:
            required = order.quantity.value * (order.price.value if order.price else Decimal(999999999))
            if required > available_balance:
                raise InsufficientBalance(f"Insufficient balance")
    
    def calculate_fee(self, trade_value: Decimal) -> Decimal:
        return trade_value * Decimal("0.001")
```

---

## 5. Application Layer

```python
# application/orders/commands.py
from dataclasses import dataclass
from uuid import UUID
from decimal import Decimal
from typing import Optional
from domain.trading.value_objects import OrderSide, OrderType
from domain.trading.aggregate import Order
from domain.trading.repositories import IOrderRepository
from domain.wallet.repositories import IWalletRepository

@dataclass
class PlaceOrderCommand:
    user_id: UUID
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: Decimal
    price: Optional[Decimal] = None

class PlaceOrderHandler:
    def __init__(self, order_repo: IOrderRepository, wallet_repo: IWalletRepository, trading_service):
        self.order_repo = order_repo
        self.wallet_repo = wallet_repo
        self.trading_service = trading_service
    
    async def handle(self, cmd: PlaceOrderCommand) -> Order:
        symbol = Symbol.from_string(cmd.symbol)
        quantity = Quantity(cmd.quantity, symbol)
        price = Price(cmd.price, symbol) if cmd.price else None
        
        order = Order().place(
            user_id=cmd.user_id, symbol=symbol, side=cmd.side,
            order_type=cmd.order_type, quantity=quantity, price=price,
        )
        
        # Validate
        wallet = await self.wallet_repo.get_by_user_id(cmd.user_id)
        self.trading_service.validate_order(order, wallet.available_balance)
        
        # Lock balance for buy
        if cmd.side == OrderSide.BUY:
            required = cmd.quantity * (cmd.price or Decimal(999999999))
            await self.wallet_repo.lock(cmd.user_id, required, order.id)
        
        await self.order_repo.save(order)
        
        for event in order.pull_events():
            await self.publish_event(event)
        
        return order
```

---

## 6. Binance Adapter

```python
# infrastructure/binance/adapters/market_adapter.py
from decimal import Decimal
from typing import List, Dict, Any
import httpx

class BinanceMarketAdapter:
    BASE_URL = "https://api.binance.com"
    
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
    
    async def get_symbol_price(self, symbol: str) -> Decimal:
        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/ticker/price",
            params={"symbol": symbol},
        )
        return Decimal(response.json()["price"])
    
    async def get_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List:
        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit},
        )
        return response.json()
    
    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict:
        response = await self.client.get(
            f"{self.BASE_URL}/api/v3/depth",
            params={"symbol": symbol, "limit": limit},
        )
        return response.json()
```

---

## 7. 事件驱动

```python
# domain/shared/events.py
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

@dataclass
class DomainEvent(ABC):
    event_id: UUID
    occurred_at: datetime = None
    
    def __post_init__(self):
        if self.occurred_at is None:
            self.occurred_at = datetime.utcnow()

@dataclass
class OrderCreatedEvent(DomainEvent):
    order_id: UUID
    symbol: str
    side: str
    quantity: float

@dataclass
class OrderFilledEvent(DomainEvent):
    order_id: UUID
    filled_quantity: float
    fill_price: float
