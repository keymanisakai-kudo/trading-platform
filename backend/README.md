# Trading Platform Backend

FastAPI-based backend for the Trading Platform.

## Setup

1. Create virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment:
```bash
cp .env.example .env
# Edit .env with your settings
```

4. Run database migrations (if using Alembic):
```bash
alembic upgrade head
```

5. Start the server:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
- POST `/api/v1/auth/register` - Register new user
- POST `/api/v1/auth/login` - Login
- POST `/api/v1/auth/refresh` - Refresh token
- GET `/api/v1/auth/me` - Get current user

### Wallet
- GET `/api/v1/wallet/balance` - Get balances
- GET `/api/v1/wallet/deposit/address` - Get deposit address
- POST `/api/v1/wallet/withdraw` - Withdraw
- GET `/api/v1/wallet/transactions` - Transaction history

### Orders
- GET `/api/v1/orders/` - List orders
- POST `/api/v1/orders/limit` - Place limit order
- POST `/api/v1/orders/market` - Place market order
- DELETE `/api/v1/orders/{id}` - Cancel order
- GET `/api/v1/orders/{id}/trades` - Get order trades

## Technology Stack

- FastAPI
- SQLAlchemy 2.0 (async)
- PostgreSQL
- JWT Auth
- Python-Binance (optional)
