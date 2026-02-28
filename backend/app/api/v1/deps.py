"""FastAPI 统一依赖注入"""
from functools import lru_cache
from typing import AsyncGenerator, Callable
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.security import decode_token
from app.infrastructure.database import async_session_factory
from app.infrastructure.persistence.repositories import (
    SQLAlchemyOrderRepository,
    SQLAlchemyWalletRepository,
    SQLAlchemyTransactionRepository,
    SQLAlchemyUserRepository,
)
from app.infrastructure.binance.adapters import BinanceMarketAdapter
from app.domain.trading.repositories import IOrderRepository
from app.domain.wallet.repositories import IWalletRepository, ITransactionRepository
from app.domain.user.repositories import IUserRepository


# OAuth2 Scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# Settings
@lru_cache
def get_settings() -> Settings:
    return Settings()


# Database
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Database session dependency"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()


# Repositories
def get_order_repo(db: AsyncSession = Depends(get_db)) -> IOrderRepository:
    """Order repository dependency"""
    return SQLAlchemyOrderRepository(db)


def get_wallet_repo(db: AsyncSession = Depends(get_db)) -> IWalletRepository:
    """Wallet repository dependency"""
    return SQLAlchemyWalletRepository(db)


def get_transaction_repo(db: AsyncSession = Depends(get_db)) -> ITransactionRepository:
    """Transaction repository dependency"""
    return SQLAlchemyTransactionRepository(db)


def get_user_repo(db: AsyncSession = Depends(get_db)) -> IUserRepository:
    """User repository dependency"""
    return SQLAlchemyUserRepository(db)


# Binance Adapter
@lru_cache
def get_market_adapter() -> BinanceMarketAdapter:
    """Binance market data adapter dependency"""
    return BinanceMarketAdapter()


# Current User
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated user"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id_str: str = payload.get("sub")
    if user_id_str is None:
        raise credentials_exception
    
    from uuid import UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise credentials_exception
    
    user_repo = SQLAlchemyUserRepository(db)
    user = await user_repo.get_by_id(user_id)
    
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user = Depends(get_current_user),
):
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user
