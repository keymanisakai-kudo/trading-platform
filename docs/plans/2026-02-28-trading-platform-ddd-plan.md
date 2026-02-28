# Trading Platform DDD 实现计划

**项目**: trading-platform backend  
**版本**: 1.0  
**日期**: 2026-02-28

---

## Phase 1: 创建目录结构

### Task 1.1: 创建 Domain Layer 目录
```bash
mkdir -p app/domain/{trading,wallet,user,shared}
mkdir -p app/domain/trading/{entities,value_objects,events,repositories,services,exceptions}
mkdir -p app/domain/wallet/{entities,value_objects,events,repositories,exceptions}
mkdir -p app/domain/user/{value_objects,events,repositories,exceptions}
mkdir -p app/domain/shared
```

### Task 1.2: 创建 Application Layer 目录
```bash
mkdir -p app/application/{orders,wallet,users}
```

### Task 1.3: 创建 Infrastructure Layer 目录
```bash
mkdir -p app/infrastructure/{persistence/repositories,binance/adapters,cache}
```

---

## Phase 2: Domain Layer - Trading

### Task 2.1: 创建 Value Objects
**文件**: `app/domain/trading/value_objects.py`
```python
- OrderSide enum (BUY, SELL)
- OrderType enum (MARKET, LIMIT)
- OrderStatus enum (PENDING, FILLED, PARTIALLY_FILLED, CANCELLED, REJECTED)
- Symbol (base, quote, from_string)
- Price (value, symbol)
- Quantity (value, symbol)
```

### Task 2.2: 创建 Domain Events
**文件**: `app/domain/trading/events.py`
```python
- OrderCreatedEvent
- OrderFilledEvent  
- OrderCancelledEvent
```

### Task 2.3: 创建 Exceptions
**文件**: `app/domain/trading/exceptions.py`
```python
- InvalidOrderStateTransition
- InsufficientBalance
- OrderNotFoundError
- OptimisticLockError
```

### Task 2.4: 创建 Order Aggregate
**文件**: `app/domain/trading/aggregate.py`
```python
- Order class with:
  - place() factory method
  - fill() command
  - cancel() command
  - can_fill(), can_cancel() business rules
  - version for optimistic locking
  - pull_events() for domain events
```

### Task 2.5: 创建 Repository Interface
**文件**: `app/domain/trading/repositories.py`
```python
- IOrderRepository interface
  - save()
  - get_by_id()
  - find_by_user()
  - find_pending()
```

---

## Phase 3: Domain Layer - Wallet

### Task 3.1: 创建 Value Objects
**文件**: `app/domain/wallet/value_objects.py`
```python
- Currency enum (USDT, BTC, ETH)
- Money (amount, currency, operators)
```

### Task 3.2: 创建 Domain Events
**文件**: `app/domain/wallet/events.py`
```python
- DepositEvent
- WithdrawalEvent
- BalanceChangedEvent
```

### Task 3.3: 创建 Exceptions
**文件**: `app/domain/wallet/exceptions.py`
```python
- InsufficientBalance
- InvalidAmount
- WalletNotFoundError
```

### Task 3.4: 创建 Wallet Aggregate
**文件**: `app/domain/wallet/aggregate.py`
```python
- Transaction entity
- Wallet aggregate with:
  - deposit() command
  - withdraw() command
  - lock_for_order() command
  - unlock() command
  - available_balance property
  - pull_events()
```

### Task 3.5: 创建 Repository Interfaces
**文件**: `app/domain/wallet/repositories.py`
```python
- IWalletRepository
- ITransactionRepository
```

---

## Phase 4: Domain Layer - User

### Task 4.1: 创建 User Aggregate
**文件**: `app/domain/user/aggregate.py`
```python
- User aggregate with:
  - create() factory method
  - verify() command
  - enable_2fa(), disable_2fa()
  - deactivate()
```

### Task 4.2: 创建 Repository Interface
**文件**: `app/domain/user/repositories.py`
```python
- IUserRepository interface
```

---

## Phase 5: Domain Services

### Task 5.1: 创建 Trading Domain Service
**文件**: `app/domain/trading/services.py`
```python
- TradingDomainService
  - validate_order()
  - calculate_fee()
```

---

## Phase 6: Application Layer

### Task 6.1: 创建 Orders Commands/Queries
**文件**: `app/application/orders/commands.py`
```python
- PlaceOrderCommand
- PlaceOrderHandler
- CancelOrderCommand
- CancelOrderHandler
```

**文件**: `app/application/orders/queries.py`
```python
- GetOrderQuery + GetOrderHandler
- ListOrdersQuery + ListOrdersHandler
```

### Task 6.2: 创建 Wallet Commands/Queries
**文件**: `app/application/wallet/commands.py`
```python
- DepositCommand + handler
- WithdrawCommand + handler
```

**文件**: `app/application/wallet/queries.py`
```python
- GetBalanceQuery + handler
- ListTransactionsQuery + handler
```

---

## Phase 7: Infrastructure - Persistence

### Task 7.1: 创建 Database Setup
**文件**: `app/infrastructure/persistence/database.py`
```python
- Async engine setup
- Session factory
- get_db() dependency
```

### Task 7.2: 创建 SQLAlchemy Order Repository
**文件**: `app/infrastructure/persistence/repositories/order_repository.py`
```python
- SQLAlchemyOrderRepository implementing IOrderRepository
- ORM model mapping
```

### Task 7.3: 创建 SQLAlchemy Wallet Repository
**文件**: `app/infrastructure/persistence/repositories/wallet_repository.py`
```python
- SQLAlchemyWalletRepository implementing IWalletRepository
- SQLAlchemyTransactionRepository implementing ITransactionRepository
```

### Task 7.4: 创建 SQLAlchemy User Repository
**文件**: `app/infrastructure/persistence/repositories/user_repository.py`
```python
- SQLAlchemyUserRepository implementing IUserRepository
```

---

## Phase 8: Infrastructure - Binance Adapter

### Task 8.1: 创建 Market Adapter
**文件**: `app/infrastructure/binance/adapters/market_adapter.py`
```python
- BinanceMarketAdapter
  - get_symbol_price()
  - get_klines()
  - get_order_book()
  - get_24h_ticker()
```

### Task 8.2: 创建 Trading Adapter
**文件**: `app/infrastructure/binance/adapters/trading_adapter.py`
```python
- BinanceTradingAdapter
  - place_order()
  - cancel_order()
  - get_order()
```

---

## Phase 9: API Integration

### Task 9.1: 更新 Orders API
**文件**: `app/api/v1/orders.py`
```python
- Refactor to use application layer
- PlaceOrder endpoint using PlaceOrderHandler
- ListOrders endpoint using ListOrdersHandler
```

### Task 9.2: 更新 Wallet API
**文件**: `app/api/v1/wallet.py`
```python
- Refactor to use application layer
- GetBalance endpoint
- ListTransactions endpoint
```

---

## 实现顺序

每个 Task:
1. 写测试 (2-5 min)
2. 运行测试 (fail)
3. 实现代码 (pass)
4. Commit

---

## 测试文件结构

```
tests/
├── unit/
│   └── domain/
│       ├── test_order_aggregate.py
│       ├── test_wallet_aggregate.py
│       ├── test_trading_services.py
│       └── test_value_objects.py
├── integration/
│   └── test_orders_api.py
└── conftest.py
```

---

## 预计时间

- Phase 1-2: 30 min
- Phase 3-4: 30 min
- Phase 5: 15 min
- Phase 6: 20 min
- Phase 7-8: 45 min
- Phase 9: 20 min

**总计**: ~3 hours
