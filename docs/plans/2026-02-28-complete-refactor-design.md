# Trading Platform 完整重构设计文档

**项目**: trading-platform backend  
**版本**: 2.0 (DDD Complete Refactor)  
**日期**: 2026-02-28  
**状态**: 设计中

---

## 1. 重构目标

### 1.1 统一架构
```
当前 (混合):
├── app/models/      # 旧 ORM
├── app/schemas/    # 旧 Pydantic
├── app/domain/     # 新 DDD (未集成)
└── app/infrastructure/  # 新基础设施

重构后:
├── app/domain/          # 领域层 (唯一数据模型)
├── app/application/     # 应用层 (Commands/Queries)
├── app/infrastructure/  # 基础设施 (数据库/API适配器)
└── app/api/            # API 层 (仅路由)
```

### 1.2 删除内容
- `app/models/` - 旧 ORM 模型
- `app/schemas/` - 旧 Pydantic 模型
- `app/services/` - 空目录
- `app/core/database.py` - 合并到 infrastructure

---

## 2. 架构设计

### 2.1 目录结构

```
backend/app/
├── api/
│   └── v1/
│       ├── __init__.py
│       ├── deps.py          # FastAPI 依赖注入
│       ├── auth.py          # 认证路由
│       ├── orders.py        # 订单路由
│       └── wallet.py        # 钱包路由
│
├── application/             # 应用层
│   ├── __init__.py
│   ├── orders/
│   │   ├── __init__.py
│   │   ├── commands.py      # 下单/撤单命令
│   │   └── queries.py      # 查询订单
│   ├── wallet/
│   │   ├── __init__.py
│   │   ├── commands.py      # 充值/提现命令
│   │   └── queries.py       # 查询余额/流水
│   └── users/
│       ├── __init__.py
│       ├── commands.py      # 注册/登录命令
│       └── queries.py       # 用户信息
│
├── domain/                  # 领域层 (核心!)
│   ├── __init__.py
│   ├── shared/
│   │   ├── __init__.py
│   │   ├── events.py       # 领域事件基类
│   │   └── exceptions.py   # 通用异常
│   │
│   ├── trading/            # 交易领域
│   │   ├── __init__.py
│   │   ├── aggregate.py    # Order Aggregate Root
│   │   ├── value_objects.py
│   │   ├── events.py
│   │   ├── repositories.py # 接口
│   │   ├── services.py    # 领域服务
│   │   └── exceptions.py
│   │
│   ├── wallet/            # 钱包领域
│   │   ├── __init__.py
│   │   ├── aggregate.py   # Wallet Aggregate Root
│   │   ├── value_objects.py
│   │   ├── events.py
│   │   ├── repositories.py
│   │   └── exceptions.py
│   │
│   └── user/              # 用户领域
│       ├── __init__.py
│       ├── aggregate.py   # User Aggregate Root
│       ├── value_objects.py
│       ├── events.py
│       ├── repositories.py
│       └── exceptions.py
│
├── infrastructure/         # 基础设施层
│   ├── __init__.py
│   ├── database.py        # SQLAlchemy 引擎/会话
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── models.py     # ORM 模型 (仅基础设施)
│   │   └── repositories/ # Repository 实现
│   │       ├── __init__.py
│   │       ├── order_repo.py
│   │       ├── wallet_repo.py
│   │       └── user_repo.py
│   │
│   ├── binance/           # Binance 适配器
│   │   ├── __init__.py
│   │   └── adapters/
│   │       ├── __init__.py
│   │       ├── market.py
│   │       └── trading.py
│   │
│   └── cache/             # Redis 缓存
│       ├── __init__.py
│       └── redis.py
│
├── core/                   # 核心配置
│   ├── __init__.py
│   ├── config.py          # Settings
│   └── security.py       # JWT/密码
│
└── main.py               # FastAPI 应用入口
```

---

## 3. 依赖关系

```
API Layer
    ↓
Application Layer (Handlers)
    ↓
Domain Layer (Aggregates, Value Objects, Services)
    ↑
    ↑
Infrastructure (Repositories, Adapters)
```

**关键原则**:
- Domain 层不依赖任何外部
- Application 层依赖 Domain
- Infrastructure 实现 Domain 定义的接口
- API 层仅依赖 Application

---

## 4. 核心组件设计

### 4.1 依赖注入 (deps.py)

```python
"""FastAPI 依赖注入"""
from functools import lru_cache
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.infrastructure.database import async_session_factory
from app.infrastructure.persistence.repositories import (
    SQLAlchemyOrderRepository,
    SQLAlchemyWalletRepository,
    SQLAlchemyUserRepository,
)
from app.infrastructure.binance.adapters import BinanceMarketAdapter
from app.domain.trading.repositories import IOrderRepository
from app.domain.wallet.repositories import IWalletRepository, ITransactionRepository
from app.domain.user.repositories import IUserRepository


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


@lru_cache
def get_settings() -> Settings:
    return Settings()


# Repository 工厂
def get_order_repo(db: AsyncSession = Depends(get_db)) -> IOrderRepository:
    return SQLAlchemyOrderRepository(db)


def get_wallet_repo(db: AsyncSession = Depends(get_db)) -> IWalletRepository:
    return SQLAlchemyWalletRepository(db)


def get_user_repo(db: AsyncSession = Depends(get_db)) -> IUserRepository:
    return SQLAlchemyUserRepository(db)


def get_market_adapter() -> BinanceMarketAdapter:
    return BinanceMarketAdapter()
```

### 4.2 Auth 集成

```python
"""Auth 依赖"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.database import get_db
from app.infrastructure.persistence.repositories import SQLAlchemyUserRepository
from app.domain.user.repositories import IUserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    from app.core.security import decode_token
    
    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    from uuid import UUID
    user_repo = SQLAlchemyUserRepository(db)
    user = await user_repo.get_by_id(UUID(user_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return user
```

---

## 5. 测试策略

### 5.1 测试金字塔

```
        /\
       /  \      E2E Tests (10%)
      /____\     
     /      \    
    /        \   Integration Tests (25%)
   /__________\  
  /            \ 
 /              \ Unit Tests (65%)
/________________\
```

### 5.2 覆盖率目标 (85%)

| 模块 | 目标覆盖率 |
|------|----------|
| domain/trading | 90% |
| domain/wallet | 90% |
| domain/user | 85% |
| application/orders | 85% |
| application/wallet | 85% |
| application/users | 85% |
| infrastructure | 70% |
| api | 60% |

### 5.3 测试结构

```
tests/
├── conftest.py              # 共享 fixtures
├── unit/
│   ├── domain/
│   │   ├── trading/
│   │   │   ├── test_order_aggregate.py
│   │   │   ├── test_value_objects.py
│   │   │   └── test_services.py
│   │   ├── wallet/
│   │   │   ├── test_wallet_aggregate.py
│   │   │   └── test_transactions.py
│   │   └── user/
│   │       └── test_user_aggregate.py
│   │
│   └── application/
│       ├── test_place_order_handler.py
│       ├── test_cancel_order_handler.py
│       └── test_deposit_handler.py
│
├── integration/
│   ├── test_orders_api.py
│   ├── test_wallet_api.py
│   └── test_auth_api.py
│
└── e2e/
    └── test_trading_flow.py
```

### 5.4 测试 Fixtures

```python
# tests/conftest.py
import pytest
from decimal import Decimal
from uuid import uuid4

from domain.trading.aggregate import Order
from domain.trading.value_objects import (
    Symbol, OrderSide, OrderType, Quantity, Price
)
from domain.wallet.aggregate import Wallet
from domain.wallet.value_objects import Currency


@pytest.fixture
def sample_symbol():
    return Symbol("BTC", "USDT")


@pytest.fixture
def sample_order(sample_symbol):
    return Order.place(
        user_id=uuid4(),
        symbol=sample_symbol,
        side=OrderSide.BUY,
        order_type=OrderType.LIMIT,
        quantity=Quantity(Decimal("0.1"), sample_symbol),
        price=Price(Decimal("50000"), sample_symbol),
    )


@pytest.fixture
def sample_wallet():
    return Wallet.create(
        user_id=uuid4(),
        currency=Currency.USDT,
    )
```

---

## 6. 实施计划

### Phase 1: 基础设施统一 (预计 30 min)
- [ ] 合并 `database.py` 到 `infrastructure/database.py`
- [ ] 更新 `infrastructure/persistence/models.py` 使用新结构
- [ ] 创建 `api/v1/deps.py` 统一依赖注入
- [ ] 删除 `app/core/database.py`

### Phase 2: Auth DDD 改造 (预计 30 min)
- [ ] 创建 `application/users/commands.py` - RegisterCommand
- [ ] 创建 `application/users/queries.py` - GetCurrentUserQuery
- [ ] 更新 `api/v1/auth.py` 使用 Application Layer
- [ ] 删除 `app/schemas/user.py`

### Phase 3: 清理旧代码 (预计 15 min)
- [ ] 删除 `app/models/`
- [ ] 删除 `app/schemas/`
- [ ] 删除 `app/services/`

### Phase 4: 测试覆盖 (预计 60 min)
- [ ] 添加 Domain Aggregate 单元测试
- [ ] 添加 Application Handler 测试
- [ ] 添加 API Integration 测试

---

## 7. 风险与回滚

### 风险
- **API 兼容**: 现有前端依赖现有 API 格式
- **数据迁移**: 数据库模型变更

### 回滚方案
- 每个 Phase 独立提交，可单独回滚
- 保留旧代码分支 until 新代码验证通过

---

## 8. 验收标准

- [ ] 85% 测试覆盖率
- [ ] 所有 API 端点正常工作
- [ ] 无循环依赖
- [ ] Domain 层零外部依赖
- [ ] 文档更新
