# Trading Platform Phase 2 - Backend API Design

**Date**: 2026-02-28
**Phase**: Phase 2 - Backend API Development
**Status**: Draft

---

# 1. Architecture Overview

## 1.1 Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL
- **ORM**: SQLAlchemy 2.0
- **Auth**: JWT (python-jose)
- **API Docs**: Swagger UI (built-in)

## 1.2 Project Structure
```
backend/
├── app/
│   ├── api/
│   │   ├── v1/
│   │   │   ├── auth.py      # Authentication endpoints
│   │   │   ├── users.py     # User management
│   │   │   ├── wallet.py    # Wallet & transactions
│   │   │   ├── orders.py    # Order management
│   │   │   └── notifications.py
│   │   └── dependencies.py
│   ├── core/
│   │   ├── config.py        # Settings
│   │   ├── security.py      # JWT, password hashing
│   │   └── database.py      # DB connection
│   ├── models/
│   │   ├── user.py
│   │   ├── wallet.py
│   │   └── order.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── wallet.py
│   │   └── order.py
│   └── services/
│       ├── binance.py       # Binance API integration
│       └── notifications.py
├── alembic/                 # Database migrations
├── requirements.txt
└── main.py
```

---

# 2. API Endpoints

## 2.1 Authentication (`/api/v1/auth`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /register | Email registration |
| POST | /login | JWT login |
| POST | /refresh | Refresh token |
| POST | /logout | Invalidate token |
| POST | /forgot-password | Password reset |
| POST | /verify-email | Email verification |

**Request/Response Examples:**

```json
// POST /api/v1/auth/register
{
  "email": "user@example.com",
  "password": "securepassword123",
  "username": "trader001"
}

// Response
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

## 2.2 Users (`/api/v1/users`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /me | Get current user profile |
| PUT | /me | Update profile |
| PUT | /me/password | Change password |
| POST | /me/2fa/enable | Enable 2FA |
| POST | /me/2fa/disable | Disable 2FA |

## 2.3 Wallet (`/api/v1/wallet`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /balance | Get all balances |
| GET | /deposit/address | Get USDT deposit address |
| POST | /withdraw | Withdraw USDT |
| GET | /transactions | Transaction history |
| GET | /transactions/{id} | Transaction detail |

**Response Example:**
```json
// GET /api/v1/wallet/balance
{
  "balances": [
    {
      "currency": "USDT",
      "available": "1000.00",
      "locked": "50.00",
      "total": "1050.00"
    },
    {
      "currency": "BTC",
      "available": "0.05",
      "locked": "0.00",
      "total": "0.05"
    }
  ],
  "total_usdt_value": "3250.00"
}
```

## 2.4 Orders (`/api/v1/orders`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | List orders |
| POST | /limit | Place limit order |
| POST | /market | Place market order |
| DELETE | /{id} | Cancel order |
| GET | /{id} | Order detail |
| GET | /{id}/trades | Order trades |

**Order Status**: `pending` | `open` | `filled` | `partially_filled` | `cancelled` | `failed`

## 2.5 Notifications (`/api/v1/notifications`)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | List notifications |
| PUT | /{id}/read | Mark as read |
| POST | /price-alerts | Create price alert |
| DELETE | /price-alerts/{id} | Delete alert |

---

# 3. Database Schema

## 3.1 Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    two_factor_enabled BOOLEAN DEFAULT FALSE,
    two_factor_secret VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 3.2 Wallets Table
```sql
CREATE TABLE wallets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    currency VARCHAR(20) NOT NULL,
    balance DECIMAL(20, 8) DEFAULT 0,
    locked DECIMAL(20, 8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(user_id, currency)
);
```

## 3.3 Transactions Table
```sql
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    wallet_id UUID REFERENCES wallets(id),
    type VARCHAR(20) NOT NULL, -- deposit, withdraw, trade
    amount DECIMAL(20, 8) NOT NULL,
    fee DECIMAL(20, 8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    tx_hash VARCHAR(255),
    address VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 3.4 Orders Table
```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL, -- buy, sell
    type VARCHAR(10) NOT NULL, -- limit, market
    price DECIMAL(20, 8),
    amount DECIMAL(20, 8) NOT NULL,
    filled_amount DECIMAL(20, 8) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'pending',
    external_order_id VARCHAR(255), -- Binance order ID
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## 3.5 Trades Table
```sql
CREATE TABLE trades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id UUID REFERENCES orders(id),
    user_id UUID REFERENCES users(id),
    symbol VARCHAR(20) NOT NULL,
    side VARCHAR(10) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    amount DECIMAL(20, 8) NOT NULL,
    fee DECIMAL(20, 8) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

# 4. Binance Integration

## 4.1 Supported Features
- **Spot Trading**: Market & Limit orders
- **Balance Sync**: Real-time balance updates via WebSocket
- **Order Execution**: Place orders through Binance API

## 4.2 Configuration
```python
# config.py
class Settings(BaseSettings):
    BINANCE_API_KEY: str
    BINANCE_SECRET_KEY: str
    BINANCE_TESTNET: bool = True  # Use testnet for development
```

## 4.3 API Wrapper
```python
# services/binance.py
class BinanceService:
    def __init__(self, api_key: str, secret_key: str, testnet: bool = True):
        self.client = BinanceClient(api_key, secret_key, testnet)
    
    async def place_order(self, symbol: str, side: str, order_type: str, quantity: float, price: float = None):
        # Implementation
        pass
    
    async def get_balance(self):
        # Implementation
        pass
```

---

# 5. Authentication Flow

```
┌──────────┐     ┌──────────┐     ┌──────────┐
│  Client  │────▶│  FastAPI │────▶│   DB     │
│          │◀────│  (JWT)   │◀────│(Postgres)│
└──────────┘     └──────────┘     └──────────┘
       │               │
       │               ▼
       │          ┌──────────┐
       │          │ Binance  │
       │          │   API    │
       │          └──────────┘
       │               │
       ▼               ▼
  ┌──────────────────────────┐
  │    JWT Token Structure   │
  │  {                       │
  │    "sub": "user_id",    │
  │    "exp": 1234567890,   │
  │    "type": "access"      │
  │  }                       │
  └──────────────────────────┘
```

---

# 6. Next Steps

1. Initialize FastAPI project
2. Set up database schema
3. Implement auth endpoints
4. Integrate Binance API
5. Build wallet module
6. Build orders module
7. Add notifications

---

# 7. Timeline Estimate

| Phase | Tasks | Est. Time |
|-------|-------|-----------|
| 1 | Project setup + Auth | 2 days |
| 2 | Wallet module | 2 days |
| 3 | Orders module | 3 days |
| 4 | Notifications | 2 days |
| 5 | Testing + Deploy | 2 days |
| **Total** | | **11 days** |
