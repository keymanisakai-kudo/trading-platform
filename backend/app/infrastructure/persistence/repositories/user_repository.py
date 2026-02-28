"""SQLAlchemy User Repository"""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from domain.user.aggregate import User
from domain.user.repositories import IUserRepository
from app.infrastructure.persistence.models import UserModel


class SQLAlchemyUserRepository(IUserRepository):
    """SQLAlchemy implementation of UserRepository"""

    def __init__(self, db: AsyncSession):
        self._db = db

    def _to_domain(self, model: UserModel) -> User:
        user = User(
            id=model.id,
            email=model.email,
            username=model.username,
            password_hash=model.password_hash,
            is_active=model.is_active,
            is_verified=model.is_verified,
            two_factor_enabled=model.two_factor_enabled,
            version=model.version,
        )
        return user

    def _to_model(self, user: User) -> UserModel:
        return UserModel(
            id=user.id,
            email=user.email,
            username=user.username,
            password_hash=user.password_hash,
            is_active=user.is_active,
            is_verified=user.is_verified,
            two_factor_enabled=user.two_factor_enabled,
            version=user.version,
        )

    async def save(self, user: User) -> User:
        existing = await self._db.get(UserModel, user.id)
        
        if existing:
            existing.email = user.email
            existing.username = user.username
            existing.password_hash = user.password_hash
            existing.is_active = user.is_active
            existing.is_verified = user.is_verified
            existing.two_factor_enabled = user.two_factor_enabled
            existing.version = user.version
        else:
            model = self._to_model(user)
            self._db.add(model)
        
        await self._db.flush()
        return user

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        model = await self._db.get(UserModel, user_id)
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_email(self, email: str) -> Optional[User]:
        query = select(UserModel).where(UserModel.email == email)
        result = await self._db.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        return self._to_domain(model)

    async def get_by_username(self, username: str) -> Optional[User]:
        query = select(UserModel).where(UserModel.username == username)
        result = await self._db.execute(query)
        model = result.scalar_one_or_none()
        
        if not model:
            return None
        return self._to_domain(model)

    async def exists_by_email(self, email: str) -> bool:
        query = select(UserModel.id).where(UserModel.email == email)
        result = await self._db.execute(query)
        return result.scalar_one_or_none() is not None

    async def exists_by_username(self, username: str) -> bool:
        query = select(UserModel.id).where(UserModel.username == username)
        result = await self._db.execute(query)
        return result.scalar_one_or_none() is not None
