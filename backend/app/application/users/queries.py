"""Application Layer - Users Queries"""
from dataclasses import dataclass
from uuid import UUID
from typing import Optional

from domain.user.repositories import IUserRepository


@dataclass
class GetCurrentUserQuery:
    """获取当前用户"""
    user_id: UUID


@dataclass
class GetCurrentUserResult:
    """用户信息结果"""
    user_id: Optional[UUID]
    email: Optional[str]
    username: Optional[str]
    is_verified: bool
    two_factor_enabled: bool
    message: str


class GetCurrentUserHandler:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def handle(self, query: GetCurrentUserQuery) -> GetCurrentUserResult:
        user = await self.user_repository.get_by_id(query.user_id)

        if not user:
            return GetCurrentUserResult(
                user_id=None,
                email=None,
                username=None,
                is_verified=False,
                two_factor_enabled=False,
                message="User not found",
            )

        return GetCurrentUserResult(
            user_id=user.id,
            email=user.email,
            username=user.username,
            is_verified=user.is_verified,
            two_factor_enabled=user.two_factor_enabled,
            message="Success",
        )


@dataclass
class GetUserByEmailQuery:
    email: str


@dataclass
class GetUserByEmailResult:
    user_id: Optional[UUID]
    email: Optional[str]
    message: str


class GetUserByEmailHandler:
    def __init__(self, user_repository: IUserRepository):
        self.user_repository = user_repository

    async def handle(self, query: GetUserByEmailQuery) -> GetUserByEmailResult:
        user = await self.user_repository.get_by_email(query.email)

        if not user:
            return GetUserByEmailResult(
                user_id=None,
                email=None,
                message="User not found",
            )

        return GetUserByEmailResult(
            user_id=user.id,
            email=user.email,
            message="Success",
        )
