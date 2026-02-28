# Trading Platform 完整重构实施计划

**项目**: trading-platform backend  
**版本**: 2.0  
**日期**: 2026-02-28

---

## Phase 1: 基础设施统一 (Tasks 1-6)

### Task 1: 合并数据库配置
**文件**: `app/infrastructure/database.py`
- 从 `app/core/database.py` 移动数据库引擎配置
- 保持 async SQLAlchemy 设置

### Task 2: 更新 ORM 模型映射
**文件**: `app/infrastructure/persistence/models.py`
- 确保 Domain Aggregate ↔ ORM 模型映射正确
- 添加缺失字段

### Task 3: 创建统一依赖注入
**文件**: `app/api/v1/deps.py`
```python
# 包含:
- get_db()
- get_order_repo()
- get_wallet_repo()
- get_user_repo()
- get_current_user()
- get_settings()
```

### Task 4: 更新 main.py
**文件**: `app/main.py`
- 更新 imports 使用新路径

### Task 5: 更新 core/config.py
**文件**: `app/core/config.py`
- 确保 DATABASE_URL 正确

### Task 6: 删除旧 database.py
**文件**: `app/core/database.py`
- 删除（已合并到 infrastructure）

---

## Phase 2: Auth DDD 改造 (Tasks 7-12)

### Task 7: 创建 Users Commands
**文件**: `app/application/users/commands.py`
```python
class RegisterCommand:
    email: str
    username: str
    password: str

class RegisterHandler:
    - 验证 email/username 不存在
    - 密码哈希
    - 创建 User Aggregate
    - 创建 Wallet
    - 生成 JWT Token

class LoginCommand:
    email: str
    password: str

class LoginHandler:
    - 验证用户存在
    - 验证密码
    - 生成 JWT Token
```

### Task 8: 创建 Users Queries
**文件**: `app/application/users/queries.py`
```python
class GetCurrentUserQuery:
    user_id: UUID

class GetCurrentUserHandler:
    - 返回用户信息 (排除敏感字段)
```

### Task 9: 创建 Users API
**文件**: `app/api/v1/auth.py`
- 重构为使用 Application Layer
- 保留现有 API 格式（兼容前端）

### Task 10: 更新 Orders API
**文件**: `app/api/v1/orders.py`
- 使用新的 `deps.py` 依赖

### Task 11: 更新 Wallet API
**文件**: `app/api/v1/wallet.py`
- 使用新的 `deps.py` 依赖

### Task 12: 测试 Auth Flow
- 注册 → 登录 → 获取用户信息

---

## Phase 3: 清理旧代码 (Tasks 13-16)

### Task 13: 删除 app/models/
```bash
rm -rf app/models/
```
- 验证: `grep -r "from app.models" --include="*.py"` 应无结果

### Task 14: 删除 app/schemas/
```bash
rm -rf app/schemas/
```
- 验证: `grep -r "from app.schemas" --include="*.py"` 应无结果

### Task 15: 删除 app/services/
```bash
rm -rf app/services/
```

### Task 16: 清理空目录
- 确保 `app/` 根目录无冗余文件

---

## Phase 4: 测试覆盖 (Tasks 17-24)

### Task 17: 安装测试依赖
```bash
pip install pytest pytest-asyncio pytest-cov
```

### Task 18: 创建 conftest.py
**文件**: `tests/conftest.py`
- Database fixtures
- Sample data fixtures

### Task 19: Domain Trading Tests
**文件**: `tests/unit/domain/trading/test_order_aggregate.py`
- test_place_limit_order
- test_place_market_order
- test_fill_order
- test_cancel_order
- test_cannot_fill_cancelled_order
- test_optimistic_locking

### Task 20: Domain Wallet Tests
**文件**: `tests/unit/domain/wallet/test_wallet_aggregate.py`
- test_deposit
- test_withdraw
- test_insufficient_balance
- test_lock_for_order

### Task 21: Domain User Tests
**文件**: `tests/unit/domain/user/test_user_aggregate.py`
- test_create_user
- test_verify_user
- test_enable_2fa

### Task 22: Application Orders Tests
**文件**: `tests/unit/application/test_place_order_handler.py`
- test_place_order_success
- test_place_order_insufficient_balance

### Task 23: Application Wallet Tests
**文件**: `tests/unit/application/test_deposit_handler.py`
- test_deposit_creates_wallet
- test_deposit_increases_balance

### Task 24: API Integration Tests
**文件**: `tests/integration/test_orders_api.py`
- test_list_orders
- test_place_order
- test_cancel_order

---

## 实施顺序

1. **每个 Task**: 写测试 → 运行 (fail) → 实现 → 运行 (pass) → commit
2. **每个 Phase**: 完成后运行完整测试 → commit

---

## 验收检查

```bash
# 1. 无旧代码引用
grep -r "from app.models" --include="*.py" backend/app/
grep -r "from app.schemas" --include="*.py" backend/app/

# 2. 测试覆盖率
pytest --cov=app --cov-report=term-missing tests/

# 3. API 工作
curl http://localhost:8000/api/v1/health
```

---

## 预计时间

| Phase | Tasks | 预计时间 |
|-------|-------|---------|
| Phase 1 | 6 | 30 min |
| Phase 2 | 6 | 30 min |
| Phase 3 | 4 | 15 min |
| Phase 4 | 8 | 60 min |
| **总计** | **24** | **~2.5 hours** |
