"""SQLAlchemy Models"""
from datetime import datetime
from uuid import uuid4
from decimal import Decimal
from sqlalchemy import String, DateTime, Numeric, Integer, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.persistence.database import Base


class OrderModel(Base):
    """Order ORM Model"""
    __tablename__ = "orders"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)  # BTCUSDT
    side: Mapped[str] = mapped_column(String(10), nullable=False)  # buy, sell
    order_type: Mapped[str] = mapped_column(String(10), nullable=False)  # market, limit
    price: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    filled_quantity: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal(0))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class WalletModel(Base):
    """Wallet ORM Model"""
    __tablename__ = "wallets"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True, index=True)
    currency: Mapped[str] = mapped_column(String(10), default="USDT")
    balance: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal(0))
    locked_balance: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal(0))
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TransactionModel(Base):
    """Transaction ORM Model"""
    __tablename__ = "transactions"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    wallet_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("wallets.id"), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(20), nullable=False)  # deposit, withdrawal, trade
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    fee: Mapped[Decimal] = mapped_column(Numeric(20, 8), default=Decimal(0))
    balance_before: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    balance_after: Mapped[Decimal] = mapped_column(Numeric(20, 8), nullable=False)
    reference_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="pending")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class UserModel(Base):
    """User ORM Model"""
    __tablename__ = "users"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    username: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True)
    is_verified: Mapped[bool] = mapped_column(default=False)
    two_factor_enabled: Mapped[bool] = mapped_column(default=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
